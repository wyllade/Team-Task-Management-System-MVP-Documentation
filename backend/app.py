from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# =========================
# Fake Database
# =========================

users = []
projects = []
tasks = []

user_id = 1
project_id = 1
task_id = 1


# =========================
# Home Route
# =========================

@app.route("/")
def home():
    return jsonify({
        "message": "Simple Project Management API"
    })


# =========================
# Register User
# =========================

@app.route("/register", methods=["POST"])
def register():

    global user_id

    data = request.json

    # Check if email already exists
    for user in users:
        if user["email"] == data["email"]:
            return jsonify({
                "message": "Email already exists"
            }), 400

    new_user = {
        "id": user_id,
        "username": data["username"],
        "email": data["email"],
        "password": data["password"]
    }

    users.append(new_user)

    user_id += 1

    return jsonify({
        "message": "User registered successfully",
        "user": new_user
    })


# =========================
# Login User
# =========================

@app.route("/login", methods=["POST"])
def login():

    data = request.json

    for user in users:

        if (
            user["email"] == data["email"]
            and user["password"] == data["password"]
        ):

            return jsonify({
                "message": "Login successful",
                "user": user
            })

    return jsonify({
        "message": "Invalid email or password"
    }), 401


# =========================
# Get All Users
# =========================

@app.route("/users")
def get_users():

    return jsonify(users)


# =========================
# Create Project
# =========================

@app.route("/projects", methods=["POST"])
def create_project():

    global project_id

    data = request.json

    project = {
        "id": project_id,
        "name": data["name"],
        "description": data.get("description", ""),
        "owner_id": data["owner_id"]
    }

    projects.append(project)

    project_id += 1

    return jsonify(project)


# =========================
# Get All Projects
# =========================

@app.route("/projects")
def get_projects():

    return jsonify(projects)


# =========================
# Get Single Project
# =========================

@app.route("/projects/<int:id>")
def get_project(id):

    for project in projects:

        if project["id"] == id:
            return jsonify(project)

    return jsonify({
        "message": "Project not found"
    }), 404


# =========================
# Delete Project
# =========================

@app.route("/projects/<int:id>", methods=["DELETE"])
def delete_project(id):

    for project in projects:

        if project["id"] == id:

            projects.remove(project)

            return jsonify({
                "message": "Project deleted"
            })

    return jsonify({
        "message": "Project not found"
    }), 404


# =========================
# Create Task
# =========================

@app.route("/tasks", methods=["POST"])
def create_task():

    global task_id

    data = request.json

    task = {
        "id": task_id,
        "title": data["title"],
        "description": data.get("description", ""),
        "status": "Todo",
        "project_id": data["project_id"]
    }

    tasks.append(task)

    task_id += 1

    return jsonify(task)


# =========================
# Get Tasks By Project
# =========================

@app.route("/tasks")
def get_tasks():

    project_id = request.args.get("project_id")

    # If no project id is provided
    if project_id is None:
        return jsonify(tasks)

    project_tasks = []

    for task in tasks:

        if task["project_id"] == int(project_id):
            project_tasks.append(task)

    return jsonify(project_tasks)


# =========================
# Get Single Task
# =========================

@app.route("/tasks/<int:id>")
def get_task(id):

    for task in tasks:

        if task["id"] == id:
            return jsonify(task)

    return jsonify({
        "message": "Task not found"
    }), 404


# =========================
# Update Task
# =========================

@app.route("/tasks/<int:id>", methods=["PUT"])
def update_task(id):

    data = request.json

    for task in tasks:

        if task["id"] == id:

            # Update only fields provided
            if "title" in data:
                task["title"] = data["title"]

            if "description" in data:
                task["description"] = data["description"]

            if "status" in data:
                task["status"] = data["status"]

            return jsonify(task)

    return jsonify({
        "message": "Task not found"
    }), 404


# =========================
# Delete Task
# =========================

@app.route("/tasks/<int:id>", methods=["DELETE"])
def delete_task(id):

    for task in tasks:

        if task["id"] == id:

            tasks.remove(task)

            return jsonify({
                "message": "Task deleted"
            })

    return jsonify({
        "message": "Task not found"
    }), 404


# =========================
# Dashboard Stats
# =========================

@app.route("/stats")
def stats():

    total_projects = len(projects)
    total_tasks = len(tasks)

    completed_tasks = 0

    for task in tasks:

        if task["status"] == "Done":
            completed_tasks += 1

    return jsonify({
        "total_projects": total_projects,
        "total_tasks": total_tasks,
        "completed_tasks": completed_tasks
    })


# =========================
# Run App
# =========================

if __name__ == "__main__":
    app.run(debug=True)