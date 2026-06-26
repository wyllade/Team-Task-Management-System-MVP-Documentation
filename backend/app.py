from flask import Flask, request, jsonify
from flask_cors import CORS
import jwt, datetime
from functools import wraps

app = Flask(__name__)
CORS(app)

# Secret key for creating tokens
SECRET_KEY = "my-secret-key"

# Fake Database
users = []
projects = []
tasks = []
comments = []
project_members = []

user_id_counter = 1
project_id_counter = 1
task_id_counter = 1
comment_id_counter = 1

# Helper Functions
def create_token(user_id):
    """Creates a JWT token that expires in 24 hours."""
    payload = {
        "user_id": user_id,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=24)
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
    return token


def get_username(user_id):
    """Looks up a user's username by their ID. Returns 'Unknown' if not found."""
    for user in users:
        if user["id"] == user_id:
            return user["username"]
    return "Unknown"


def is_project_member(project_id, user_id):
    # Check if user is the project owner
    for project in projects:
        if project["id"] == project_id and project["owner_id"] == user_id:
            return True

    # Check if user is an invited member
    for member in project_members:
        if member["project_id"] == project_id and member["user_id"] == user_id:
            return True

    return False


def is_project_admin(project_id, user_id):
    # Project owner is always an admin
    for project in projects:
        if project["id"] == project_id and project["owner_id"] == user_id:
            return True

    # Check if user has admin role in project members
    for member in project_members:
        if member["project_id"] == project_id and member["user_id"] == user_id and member["role"] == "admin":
            return True

    return False


def require_auth(f):
    """Decorator that checks for a valid JWT token in the Authorization header."""
    @wraps(f)
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")

        if not auth_header.startswith("Bearer "):
            return jsonify({"message": "Unauthorized"}), 401

        token = auth_header[7:]  # Remove "Bearer " from the string

        try:
            data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            user_id = data["user_id"]

            # Find the user
            for user in users:
                if user["id"] == user_id:
                    request.current_user = user
                    return f(*args, **kwargs)

        except jwt.InvalidTokenError:
            pass

        return jsonify({"message": "Unauthorized"}), 401

    return wrapper

# Routes
@app.route("/")
def home():
    return jsonify({"message": "Simple Project Management API"})


# Authentication
@app.route("/register", methods=["POST"])
def register():
    """Creates a new user account and returns a JWT token."""
    global user_id_counter

    data = request.json

    # Check if email already exists
    for user in users:
        if user["email"] == data["email"]:
            return jsonify({"message": "Email already exists"}), 400

    new_user = {
        "id": user_id_counter,
        "username": data["username"],
        "email": data["email"],
        "password": data["password"]
    }

    users.append(new_user)
    user_id_counter += 1

    # Return a token so the user is logged in right after registering
    token = create_token(new_user["id"])

    return jsonify({
        "token": token,
        "user": {
            "id": new_user["id"],
            "username": new_user["username"]
        }
    })


@app.route("/login", methods=["POST"])
def login():
    """Logs in an existing user and returns a JWT token."""
    data = request.json

    # Find user with matching email and password
    for user in users:
        if user["email"] == data["email"] and user["password"] == data["password"]:
            token = create_token(user["id"])

            return jsonify({
                "token": token,
                "user": {
                    "id": user["id"],
                    "username": user["username"]
                }
            })

    return jsonify({"message": "Invalid email or password"}), 401


# Users
@app.route("/users")
@require_auth
def get_users():
    """Returns a list of all users (for the member add dropdown)."""
    user_list = []

    for user in users:
        user_list.append({
            "id": user["id"],
            "username": user["username"],
            "email": user["email"]
        })

    return jsonify(user_list)


# Projects
@app.route("/projects", methods=["GET", "POST"])
@require_auth
def handle_projects():
    """GET: list all projects the user belongs to. POST: create a new project."""
    global project_id_counter
    current_user = request.current_user

    if request.method == "GET":
        user_projects = []

        for project in projects:
            if is_project_member(project["id"], current_user["id"]):
                # Count how many members are in this project
                member_count = 0
                for member in project_members:
                    if member["project_id"] == project["id"]:
                        member_count += 1

                # Add the owner as a member too
                member_count += 1

                project_copy = {
                    "id": project["id"],
                    "name": project["name"],
                    "description": project["description"],
                    "owner_id": project["owner_id"],
                    "member_count": member_count
                }

                user_projects.append(project_copy)

        return jsonify(user_projects)

    # POST: Create a new project
    data = request.json

    new_project = {
        "id": project_id_counter,
        "name": data["name"],
        "description": data.get("description", ""),
        "owner_id": current_user["id"]
    }

    projects.append(new_project)
    project_id_counter += 1

    return jsonify(new_project)


@app.route("/projects/<int:project_id>", methods=["PUT", "DELETE"])
@require_auth
def update_project(project_id):
    """PUT: edit project name/description. DELETE: delete project. Admin only."""
    global project_members
    current_user = request.current_user

    # Find the project
    found_project = None
    for project in projects:
        if project["id"] == project_id:
            found_project = project
            break

    if found_project is None:
        return jsonify({"message": "Project not found"}), 404

    # Check if user is an admin
    if not is_project_admin(project_id, current_user["id"]):
        return jsonify({"message": "Unauthorized"}), 403

    if request.method == "DELETE":
        # Remove the project
        projects.remove(found_project)

        # Remove all member records for this project
        updated_members = []
        for member in project_members:
            if member["project_id"] != project_id:
                updated_members.append(member)
        project_members = updated_members

        return jsonify({"message": "Project deleted"})

    # PUT: Edit project
    data = request.json

    if "name" in data:
        found_project["name"] = data["name"]

    if "description" in data:
        found_project["description"] = data["description"]

    return jsonify(found_project)


# Project Members
@app.route("/projects/<int:project_id>/members", methods=["GET", "POST"])
@require_auth
def handle_members(project_id):
    """GET: list members. POST: add a member (admin only)."""
    current_user = request.current_user

    # Find the project
    found_project = None
    for project in projects:
        if project["id"] == project_id:
            found_project = project
            break

    if found_project is None:
        return jsonify({"message": "Project not found"}), 404

    if request.method == "GET":
        # Any project member can view the list
        if not is_project_member(project_id, current_user["id"]):
            return jsonify({"message": "Unauthorized"}), 403

        member_list = []

        # Add the project owner first
        member_list.append({
            "user_id": found_project["owner_id"],
            "username": get_username(found_project["owner_id"]),
            "role": "admin"
        })

        # Add invited members
        for member in project_members:
            if member["project_id"] == project_id and member["user_id"] != found_project["owner_id"]:
                member_list.append({
                    "user_id": member["user_id"],
                    "username": get_username(member["user_id"]),
                    "role": member["role"]
                })

        return jsonify(member_list)

    # POST: Add a member (admin only)
    if not is_project_admin(project_id, current_user["id"]):
        return jsonify({"message": "Unauthorized"}), 403

    data = request.json
    user_id_to_add = data["user_id"]

    # Check if user is already a member
    if is_project_member(project_id, user_id_to_add):
        return jsonify({"message": "Already a member"}), 400

    project_members.append({
        "project_id": project_id,
        "user_id": user_id_to_add,
        "role": "member"
    })

    return jsonify({
        "user_id": user_id_to_add,
        "username": get_username(user_id_to_add),
        "role": "member"
    })


@app.route("/projects/<int:project_id>/members/<int:member_user_id>", methods=["DELETE"])
@require_auth
def remove_member(project_id, member_user_id):
    """Removes a member from the project. Admin only. Cannot remove the owner."""
    current_user = request.current_user

    # Find the project
    found_project = None
    for project in projects:
        if project["id"] == project_id:
            found_project = project
            break

    if found_project is None:
        return jsonify({"message": "Project not found"}), 404

    # Check if user is an admin
    if not is_project_admin(project_id, current_user["id"]):
        return jsonify({"message": "Unauthorized"}), 403

    # Cannot remove the project owner
    if member_user_id == found_project["owner_id"]:
        return jsonify({"message": "Cannot remove the project owner"}), 400

    # Find and remove the member record
    member_found = None
    for member in project_members:
        if member["project_id"] == project_id and member["user_id"] == member_user_id:
            member_found = member
            break

    if member_found is None:
        return jsonify({"message": "Member not found"}), 404

    project_members.remove(member_found)
    return jsonify({"message": "Member removed"})


# Tasks
@app.route("/tasks", methods=["GET", "POST"])
@require_auth
def handle_tasks():
    """GET: list tasks for a project. POST: create a new task."""
    global task_id_counter
    current_user = request.current_user

    if request.method == "GET":
        project_id = request.args.get("project_id", type=int)

        if not is_project_member(project_id, current_user["id"]):
            return jsonify({"message": "Unauthorized"}), 403

        project_tasks = []

        for task in tasks:
            if task["project_id"] == project_id:
                # Add extra info before returning
                task_copy = dict(task)
                task_copy["assignee_name"] = get_username(task.get("assignee_id"))
                task_copy["creator_name"] = get_username(task["user_id"])
                project_tasks.append(task_copy)

        return jsonify(project_tasks)

    # POST: Create a new task
    data = request.json
    project_id = data["project_id"]

    if not is_project_member(project_id, current_user["id"]):
        return jsonify({"message": "Unauthorized"}), 403

    new_task = {
        "id": task_id_counter,
        "title": data["title"],
        "description": data.get("description", ""),
        "status": "Todo",
        "priority": data.get("priority", "Medium"),
        "project_id": project_id,
        "user_id": current_user["id"],
        "assignee_id": data.get("assignee_id")
    }

    tasks.append(new_task)
    task_id_counter += 1

    new_task["assignee_name"] = get_username(new_task["assignee_id"])
    new_task["creator_name"] = current_user["username"]

    return jsonify(new_task)


@app.route("/tasks/<int:task_id>", methods=["GET", "PUT", "DELETE"])
@require_auth
def handle_task(task_id):
    """GET: single task details. PUT: update task. DELETE: delete task."""
    current_user = request.current_user

    # Find the task
    found_task = None
    for task in tasks:
        if task["id"] == task_id:
            found_task = task
            break

    if found_task is None:
        return jsonify({"message": "Task not found"}), 404

    # Must be a project member to access this task
    if not is_project_member(found_task["project_id"], current_user["id"]):
        return jsonify({"message": "Unauthorized"}), 403

    if request.method == "GET":
        task_copy = dict(found_task)
        task_copy["assignee_name"] = get_username(found_task.get("assignee_id"))
        task_copy["creator_name"] = get_username(found_task["user_id"])
        return jsonify(task_copy)

    if request.method == "DELETE":
        # Only the task creator or a project admin can delete
        if found_task["user_id"] != current_user["id"] and not is_project_admin(found_task["project_id"], current_user["id"]):
            return jsonify({"message": "Unauthorized"}), 403

        tasks.remove(found_task)
        return jsonify({"message": "Task deleted"})

    # PUT: Update task fields
    data = request.json

    # Only update fields that were sent in the request
    if "title" in data:
        found_task["title"] = data["title"]

    if "description" in data:
        found_task["description"] = data["description"]

    if "status" in data:
        found_task["status"] = data["status"]

    if "priority" in data:
        found_task["priority"] = data["priority"]

    if "assignee_id" in data:
        found_task["assignee_id"] = data["assignee_id"]

    found_task["assignee_name"] = get_username(found_task.get("assignee_id"))

    return jsonify(found_task)


# Comments
@app.route("/comments", methods=["GET", "POST"])
@require_auth
def handle_comments():
    """GET: list comments for a task. POST: add a comment."""
    global comment_id_counter
    current_user = request.current_user

    if request.method == "GET":
        task_id = request.args.get("task_id", type=int)

        # Find the task and check membership
        found_task = None
        for task in tasks:
            if task["id"] == task_id:
                found_task = task
                break

        if found_task is None:
            return jsonify({"message": "Task not found"}), 404

        if not is_project_member(found_task["project_id"], current_user["id"]):
            return jsonify({"message": "Unauthorized"}), 403

        task_comments = []

        for comment in comments:
            if comment["task_id"] == task_id:
                comment_copy = dict(comment)
                comment_copy["username"] = get_username(comment["user_id"])
                task_comments.append(comment_copy)

        return jsonify(task_comments)

    # POST: Add a new comment
    data = request.json
    task_id = data["task_id"]

    # Find the task and check membership
    found_task = None
    for task in tasks:
        if task["id"] == task_id:
            found_task = task
            break

    if found_task is None:
        return jsonify({"message": "Task not found"}), 404

    if not is_project_member(found_task["project_id"], current_user["id"]):
        return jsonify({"message": "Unauthorized"}), 403

    new_comment = {
        "id": comment_id_counter,
        "task_id": task_id,
        "user_id": current_user["id"],
        "comment": data["comment"],
        "username": current_user["username"]
    }

    comments.append(new_comment)
    comment_id_counter += 1

    return jsonify(new_comment)


@app.route("/stats")
@require_auth
def get_stats():
    """Returns project and task statistics for the current user."""
    current_user = request.current_user

    # Collect project IDs the user belongs to
    user_project_ids = []

    for project in projects:
        if is_project_member(project["id"], current_user["id"]):
            user_project_ids.append(project["id"])

    total_projects = len(user_project_ids)

    # Count tasks in those projects
    total_tasks = 0
    completed_tasks = 0

    for task in tasks:
        if task["project_id"] in user_project_ids:
            # Only count tasks the user created, is assigned to, or is admin of
            if task["user_id"] == current_user["id"] or task.get("assignee_id") == current_user["id"] or is_project_admin(task["project_id"], current_user["id"]):
                total_tasks += 1

                if task["status"] == "Done":
                    completed_tasks += 1

    return jsonify({
        "total_projects": total_projects,
        "total_tasks": total_tasks,
        "completed_tasks": completed_tasks
    })


# Run App
if __name__ == "__main__":
    app.run(debug=True)
