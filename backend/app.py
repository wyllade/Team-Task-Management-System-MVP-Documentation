from flask import Flask, request, jsonify
from flask_cors import CORS
import jwt
import datetime
from functools import wraps

# ============================================================
# Flask Application Setup
# ============================================================

app = Flask(__name__)
CORS(app)

# In a real project, this would be stored in an environment variable
SECRET_KEY = "secret-key"

# ============================================================
# Database (In-Memory Lists)
# ============================================================

# A demo user is pre-loaded so you can log in immediately
users = [
    {
        "id": 0,
        "username": "demo",
        "email": "demo@test.com",
        "password": "pass"
    }
]

projects = []
tasks = []
comments = []
project_members = []

# Counters for generating unique IDs
ids = {
    "user": 1,
    "project": 1,
    "task": 1,
    "comment": 1
}

# ============================================================
# Authentication Decorator
# ============================================================

def require_auth(view_function):
    """
    This decorator checks if the user is logged in.
    It reads the JWT token from the Authorization header.
    If the token is valid, it attaches the user to the request.
    """
    @wraps(view_function)
    def wrapper(*args, **kwargs):

        # Get the Authorization header from the request
        auth_header = request.headers.get("Authorization", "")

        # The header must start with "Bearer " followed by the token
        if not auth_header.startswith("Bearer "):
            return jsonify({"message": "Unauthorized"}), 401

        try:
            # Extract the token by removing the "Bearer " prefix
            token = auth_header[7:]

            # Decode the token to get the user ID
            token_data = jwt.decode(
                token,
                SECRET_KEY,
                algorithms=["HS256"]
            )

            # Find the user with the matching ID
            for stored_user in users:
                if stored_user["id"] == token_data["user_id"]:
                    # Attach the user to the request so routes can access it
                    request.current_user = stored_user
                    return view_function(*args, **kwargs)

        except jwt.InvalidTokenError:
            # If the token is expired or invalid, fall through to the error
            pass

        return jsonify({"message": "Unauthorized"}), 401

    return wrapper

# ============================================================
# Helper Functions
# ============================================================

def find_by_id(items, item_id):
    """
    Search a list of dictionaries for an item with a matching ID.
    Returns the item if found, otherwise returns None.

    Example:
        project = find_by_id(projects, 3)
    """
    for item in items:
        if item["id"] == item_id:
            return item
    return None


def find_project_member(project_id, user_id):
    """
    Check if a user is listed as a member of a project.
    Returns the membership record if found, otherwise None.
    """
    for member_record in project_members:
        if (
            member_record["project_id"] == project_id
            and member_record["user_id"] == user_id
        ):
            return member_record
    return None


def is_project_member(project_id, user_id):
    """
    Returns True if the user is a member of the project.
    The project creator is always considered a member.
    """
    # Check if the user is the project creator
    project = find_by_id(projects, project_id)
    if project is not None and project["user_id"] == user_id:
        return True

    # Check if the user is in the project_members list
    member_record = find_project_member(project_id, user_id)
    return member_record is not None


def is_project_admin(project_id, user_id):
    """
    Returns True if the user is an admin of the project.
    The project creator is always an admin.
    """
    # Check if the user is the project creator
    project = find_by_id(projects, project_id)
    if project is not None and project["user_id"] == user_id:
        return True

    # Check if the user has the "admin" role in project_members
    member_record = find_project_member(project_id, user_id)
    if member_record is not None and member_record["role"] == "admin":
        return True

    return False

# ============================================================
# Routes
# ============================================================

@app.route("/")
def home():
    """
    Root endpoint — used to verify the server is running.
    """
    return jsonify({"message": "Project Management System API"})


@app.route("/register", methods=["POST"])
def register():
    """
    Create a new user account.
    Expects JSON: { "username": "...", "email": "...", "password": "..." }
    Returns a JWT token so the user is automatically logged in.
    """
    global ids

    # Get the registration data sent from the frontend
    request_data = request.json

    # Create a new user dictionary with a unique ID
    user = {
        "id": ids["user"],
        "username": request_data["username"],
        "email": request_data["email"],
        "password": request_data["password"]
    }

    # Save the user and increment the ID counter
    users.append(user)
    ids["user"] += 1

    # Create a JWT token that expires in 24 hours
    token = jwt.encode(
        {
            "user_id": user["id"],
            "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=24)
        },
        SECRET_KEY,
        algorithm="HS256"
    )

    # Return the token and basic user info
    return jsonify({
        "token": token,
        "user": {
            "id": user["id"],
            "username": user["username"]
        }
    })


@app.route("/login", methods=["POST"])
def login():
    """
    Log in with an existing account.
    Expects JSON: { "email": "...", "password": "..." }
    Returns a JWT token if credentials are valid.
    """
    # Get the login data sent from the frontend
    request_data = request.json

    # Search for a user with matching email and password
    for stored_user in users:
        if (
            stored_user["email"] == request_data["email"]
            and stored_user["password"] == request_data["password"]
        ):

            # Create a JWT token that expires in 24 hours
            token = jwt.encode(
                {
                    "user_id": stored_user["id"],
                    "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=24)
                },
                SECRET_KEY,
                algorithm="HS256"
            )

            # Return the token and basic user info
            return jsonify({
                "token": token,
                "user": {
                    "id": stored_user["id"],
                    "username": stored_user["username"]
                }
            })

    # If no user matched, return an error
    return jsonify({"message": "Invalid credentials"}), 401


@app.route("/users")
@require_auth
def get_users():
    """
    Return a list of all registered users.
    Used by the frontend to show who can be added as a project member.
    Passwords are NOT included in the response.
    """
    user_list = []

    for stored_user in users:
        user_list.append({
            "id": stored_user["id"],
            "username": stored_user["username"],
            "email": stored_user["email"]
        })

    return jsonify(user_list)


@app.route("/projects", methods=["GET", "POST"])
@require_auth
def handle_projects():
    """
    GET  /projects  — Return all projects the user is a member of.
    POST /projects — Create a new project. The creator is added as an admin member.
    """
    global ids

    current_user = request.current_user

    # ----- Handle GET request -----
    if request.method == "GET":

        visible_projects = []

        # Check each project to see if the current user is a member
        for project in projects:
            if is_project_member(project["id"], current_user["id"]):

                # Count how many members this project has
                member_count = 0
                for member_record in project_members:
                    if member_record["project_id"] == project["id"]:
                        member_count += 1

                # Build a project object with the member count included
                project_with_count = {
                    "id": project["id"],
                    "name": project["name"],
                    "description": project["description"],
                    "user_id": project["user_id"],
                    "member_count": member_count
                }

                visible_projects.append(project_with_count)

        return jsonify(visible_projects)

    # ----- Handle POST request -----
    request_data = request.json

    # Create a new project with a unique ID
    project = {
        "id": ids["project"],
        "name": request_data["name"],
        "description": request_data.get("description", ""),
        "user_id": current_user["id"]
    }

    projects.append(project)
    ids["project"] += 1

    # The creator is automatically added as an admin member
    project_members.append({
        "project_id": project["id"],
        "user_id": current_user["id"],
        "role": "admin"
    })

    return jsonify(project)


@app.route("/projects/<int:project_id>", methods=["PUT", "DELETE"])
@require_auth
def update_project(project_id):
    """
    PUT    /projects/<id> — Update the project name and description.
    DELETE /projects/<id> — Delete the project and all member records.
    Only project admins can perform these actions.
    """
    current_user = request.current_user

    # Find the project by ID
    project = find_by_id(projects, project_id)

    if project is None:
        return jsonify({"message": "Not found"}), 404

    # Only admins can edit or delete a project
    if not is_project_admin(project_id, current_user["id"]):
        return jsonify({"message": "Unauthorized"}), 403

    # ----- Handle DELETE request -----
    if request.method == "DELETE":
        global project_members

        # Remove the project from the list
        projects.remove(project)

        # Remove all member records associated with this project
        project_members = [
            member_record
            for member_record in project_members
            if member_record["project_id"] != project_id
        ]

        return jsonify({"message": "Deleted"})

    # ----- Handle PUT request -----
    request_data = request.json

    # Update the name if provided
    if "name" in request_data:
        project["name"] = request_data["name"]

    # Update the description if provided
    if "description" in request_data:
        project["description"] = request_data["description"]

    return jsonify(project)


@app.route("/projects/<int:project_id>/members", methods=["GET", "POST"])
@require_auth
def handle_members(project_id):
    """
    GET  /projects/<id>/members       — Return all members of the project.
    POST /projects/<id>/members       — Add a user as a member (admin only).
    """
    current_user = request.current_user

    # Find the project by ID
    project = find_by_id(projects, project_id)

    if project is None:
        return jsonify({"message": "Not found"}), 404

    # ----- Handle GET request -----
    if request.method == "GET":

        # Only members can view the member list
        if not is_project_member(project_id, current_user["id"]):
            return jsonify({"message": "Unauthorized"}), 403

        member_list = []

        # Add the project creator as the first member (always admin)
        creator_username = "?"
        for stored_user in users:
            if stored_user["id"] == project["user_id"]:
                creator_username = stored_user["username"]
                break

        member_list.append({
            "user_id": project["user_id"],
            "username": creator_username,
            "role": "admin"
        })

        # Add all other members from the project_members list
        for member_record in project_members:
            if member_record["project_id"] == project_id:

                # Skip the creator since they were already added above
                if member_record["user_id"] == project["user_id"]:
                    continue

                # Find the member's username
                member_username = "?"
                for stored_user in users:
                    if stored_user["id"] == member_record["user_id"]:
                        member_username = stored_user["username"]
                        break

                member_list.append({
                    "user_id": member_record["user_id"],
                    "username": member_username,
                    "role": member_record["role"]
                })

        return jsonify(member_list)

    # ----- Handle POST request -----
    # Only admins can add new members
    if not is_project_admin(project_id, current_user["id"]):
        return jsonify({"message": "Unauthorized"}), 403

    request_data = request.json
    user_id_to_add = request_data["user_id"]

    # Check if the user is already a member
    existing_member = find_project_member(project_id, user_id_to_add)
    if existing_member is not None or project["user_id"] == user_id_to_add:
        return jsonify({"message": "Already a member"}), 400

    # Add the user as a member with the default "member" role
    project_members.append({
        "project_id": project_id,
        "user_id": user_id_to_add,
        "role": request_data.get("role", "member")
    })

    # Find the new member's username for the response
    new_member_username = "?"
    for stored_user in users:
        if stored_user["id"] == user_id_to_add:
            new_member_username = stored_user["username"]
            break

    return jsonify({
        "user_id": user_id_to_add,
        "username": new_member_username,
        "role": "member"
    })


@app.route("/projects/<int:project_id>/members/<int:user_id>", methods=["DELETE"])
@require_auth
def remove_member(project_id, user_id):
    """
    Remove a user from a project's member list.
    Only admins can remove members, and the project creator cannot be removed.
    """
    current_user = request.current_user

    # Find the project by ID
    project = find_by_id(projects, project_id)

    if project is None:
        return jsonify({"message": "Not found"}), 404

    # Only admins can remove members
    if not is_project_admin(project_id, current_user["id"]):
        return jsonify({"message": "Unauthorized"}), 403

    # The project creator cannot be removed
    if user_id == project["user_id"]:
        return jsonify({"message": "Cannot remove owner"}), 400

    # Find the membership record
    member_record = find_project_member(project_id, user_id)

    if member_record is None:
        return jsonify({"message": "Not a member"}), 404

    # Remove the membership record
    project_members.remove(member_record)

    return jsonify({"message": "Removed"})


@app.route("/tasks", methods=["GET", "POST"])
@require_auth
def handle_tasks():
    """
    GET  /tasks?project_id=X  — Return all tasks for a project.
    POST /tasks               — Create a new task inside a project.
    """
    global ids

    current_user = request.current_user

    # ----- Handle GET request -----
    if request.method == "GET":

        # Get the project ID from the query string
        project_id = request.args.get("project_id", type=int)

        # Only members can view tasks
        if not is_project_member(project_id, current_user["id"]):
            return jsonify({"message": "Unauthorized"}), 403

        task_list = []

        # Loop through all tasks and find ones belonging to this project
        for task in tasks:
            if task["project_id"] == project_id:

                # Make a copy so we don't modify the original
                task_with_names = dict(task)

                # Find the assignee's username (if someone is assigned)
                assignee_name = None
                if task.get("assignee_id") is not None:
                    for stored_user in users:
                        if stored_user["id"] == task["assignee_id"]:
                            assignee_name = stored_user["username"]
                            break

                task_with_names["assignee_name"] = assignee_name

                # Find the creator's username
                creator_name = "?"
                for stored_user in users:
                    if stored_user["id"] == task["user_id"]:
                        creator_name = stored_user["username"]
                        break

                task_with_names["creator_name"] = creator_name

                task_list.append(task_with_names)

        return jsonify(task_list)

    # ----- Handle POST request -----
    request_data = request.json
    project_id = request_data["project_id"]

    # Only members can create tasks
    if not is_project_member(project_id, current_user["id"]):
        return jsonify({"message": "Unauthorized"}), 403

    # Create a new task with a unique ID
    task = {
        "id": ids["task"],
        "title": request_data["title"],
        "description": request_data.get("description", ""),
        "status": "Todo",
        "priority": request_data.get("priority", "Medium"),
        "project_id": project_id,
        "user_id": current_user["id"],
        "assignee_id": request_data.get("assignee_id")
    }

    tasks.append(task)
    ids["task"] += 1

    # Find the assignee's username for the response
    assignee_name = None
    if task["assignee_id"] is not None:
        for stored_user in users:
            if stored_user["id"] == task["assignee_id"]:
                assignee_name = stored_user["username"]
                break

    task["assignee_name"] = assignee_name
    task["creator_name"] = current_user["username"]

    return jsonify(task)


@app.route("/tasks/<int:task_id>", methods=["PUT", "DELETE"])
@require_auth
def update_task(task_id):
    """
    PUT    /tasks/<id> — Update task fields (status, title, description, etc.).
    DELETE /tasks/<id> — Delete a task (only creator or admin can delete).
    """
    current_user = request.current_user

    # Find the task by ID
    task = find_by_id(tasks, task_id)

    if task is None:
        return jsonify({"message": "Not found"}), 404

    # Only project members can update tasks
    if not is_project_member(task["project_id"], current_user["id"]):
        return jsonify({"message": "Unauthorized"}), 403

    # ----- Handle DELETE request -----
    if request.method == "DELETE":

        # Only the task creator or a project admin can delete a task
        can_delete = (
            task["user_id"] == current_user["id"]
            or is_project_admin(task["project_id"], current_user["id"])
        )

        if not can_delete:
            return jsonify({"message": "Unauthorized"}), 403

        tasks.remove(task)
        return jsonify({"message": "Deleted"})

    # ----- Handle PUT request -----
    request_data = request.json

    # Update each field if it was provided in the request
    fields_to_update = ["status", "title", "description", "priority", "assignee_id"]

    for field in fields_to_update:
        if field in request_data:
            task[field] = request_data[field]

    # Find the assignee's username for the response
    assignee_name = None
    if task.get("assignee_id") is not None:
        for stored_user in users:
            if stored_user["id"] == task["assignee_id"]:
                assignee_name = stored_user["username"]
                break

    task["assignee_name"] = assignee_name

    return jsonify(task)


@app.route("/comments", methods=["GET", "POST"])
@require_auth
def handle_comments():
    """
    GET  /comments?task_id=X  — Return all comments for a task.
    POST /comments            — Add a comment to a task.
    """
    global ids

    current_user = request.current_user

    # ----- Handle GET request -----
    if request.method == "GET":

        # Get the task ID from the query string
        task_id = request.args.get("task_id", type=int)
        task = find_by_id(tasks, task_id)

        # Only project members can view comments
        if task is None or not is_project_member(task["project_id"], current_user["id"]):
            return jsonify({"message": "Unauthorized"}), 403

        comment_list = []

        # Loop through all comments and find ones belonging to this task
        for comment in comments:
            if comment["task_id"] == task_id:

                # Make a copy so we don't modify the original
                comment_with_username = dict(comment)

                # Find the commenter's username
                commenter_name = "?"
                for stored_user in users:
                    if stored_user["id"] == comment["user_id"]:
                        commenter_name = stored_user["username"]
                        break

                comment_with_username["username"] = commenter_name

                comment_list.append(comment_with_username)

        return jsonify(comment_list)

    # ----- Handle POST request -----
    request_data = request.json
    task_id = request_data["task_id"]
    task = find_by_id(tasks, task_id)

    # Only project members can add comments
    if task is None or not is_project_member(task["project_id"], current_user["id"]):
        return jsonify({"message": "Unauthorized"}), 403

    # Create a new comment with a unique ID
    comment = {
        "id": ids["comment"],
        "task_id": task_id,
        "user_id": current_user["id"],
        "comment": request_data["comment"],
        "username": current_user["username"]
    }

    comments.append(comment)
    ids["comment"] += 1

    return jsonify(comment)


@app.route("/stats")
@require_auth
def get_stats():
    """
    Return summary statistics for the current user:
    - Total number of projects the user belongs to
    - Total number of tasks the user is involved with
    - Number of completed tasks
    """
    current_user = request.current_user

    # Find all projects where the user is a member
    user_project_ids = set()

    for project in projects:
        if is_project_member(project["id"], current_user["id"]):
            user_project_ids.add(project["id"])

    # Find all tasks in those projects that involve the user
    user_tasks = []

    for task in tasks:
        if task["project_id"] in user_project_ids:

            # Include tasks the user created, is assigned to,
            # or is an admin of the project
            is_involved = (
                task["user_id"] == current_user["id"]
                or task.get("assignee_id") == current_user["id"]
                or is_project_admin(task["project_id"], current_user["id"])
            )

            if is_involved:
                user_tasks.append(task)

    # Count completed tasks
    completed_count = 0
    for task in user_tasks:
        if task["status"] == "Done":
            completed_count += 1

    return jsonify({
        "total_projects": len(user_project_ids),
        "total_tasks": len(user_tasks),
        "completed_tasks": completed_count
    })


# ============================================================
# Application Entry Point
# ============================================================

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
