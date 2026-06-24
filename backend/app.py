from flask import Flask, request, jsonify
from flask_cors import CORS
import jwt
import datetime

app = Flask(__name__)
CORS(app)

SECRET_KEY = "secret-key"

users = []
projects = []
tasks = []
comments = []

next_user_id = 1
next_project_id = 1
next_task_id = 1
next_comment_id = 1


def get_user_from_token():
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return None
    token = auth_header.split(" ")[1]
    try:
        data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        for user in users:
            if user["id"] == data["user_id"]:
                return user
    except jwt.InvalidTokenError:
        return None
    return None


@app.route("/register", methods=["POST"])
def register():
    global next_user_id
    data = request.json
    user = {
        "id": next_user_id,
        "username": data["username"],
        "email": data["email"],
        "password": data["password"],
    }
    users.append(user)
    next_user_id += 1
    return jsonify({"message": "User registered"})


@app.route("/login", methods=["POST"])
def login():
    data = request.json
    for user in users:
        if user["email"] == data["email"] and user["password"] == data["password"]:
            token = jwt.encode(
                {
                    "user_id": user["id"],
                    "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=24),
                },
                SECRET_KEY,
                algorithm="HS256",
            )
            return jsonify({"token": token, "user": {"id": user["id"], "username": user["username"]}})
    return jsonify({"message": "Invalid credentials"}), 401


@app.route("/projects", methods=["GET"])
def get_projects():
    current_user = get_user_from_token()
    if not current_user:
        return jsonify({"message": "Unauthorized"}), 401
    user_projects = [p for p in projects if p["user_id"] == current_user["id"]]
    return jsonify(user_projects)


@app.route("/projects", methods=["POST"])
def create_project():
    global next_project_id
    current_user = get_user_from_token()
    if not current_user:
        return jsonify({"message": "Unauthorized"}), 401
    data = request.json
    project = {
        "id": next_project_id,
        "name": data["name"],
        "description": data.get("description", ""),
        "user_id": current_user["id"],
    }
    projects.append(project)
    next_project_id += 1
    return jsonify(project)


@app.route("/projects/<int:project_id>", methods=["DELETE"])
def delete_project(project_id):
    current_user = get_user_from_token()
    if not current_user:
        return jsonify({"message": "Unauthorized"}), 401
    for project in projects:
        if project["id"] == project_id:
            if project["user_id"] != current_user["id"]:
                return jsonify({"message": "Unauthorized"}), 403
            projects.remove(project)
            return jsonify({"message": "Project deleted"})
    return jsonify({"message": "Project not found"}), 404


@app.route("/tasks", methods=["GET"])
def get_tasks():
    current_user = get_user_from_token()
    if not current_user:
        return jsonify({"message": "Unauthorized"}), 401
    project_id = request.args.get("project_id", type=int)
    if not project_id:
        return jsonify([])
    project = None
    for p in projects:
        if p["id"] == project_id:
            project = p
            break
    if not project or project["user_id"] != current_user["id"]:
        return jsonify({"message": "Unauthorized"}), 403
    project_tasks = [t for t in tasks if t["project_id"] == project_id]
    return jsonify(project_tasks)


@app.route("/tasks", methods=["POST"])
def create_task():
    global next_task_id
    current_user = get_user_from_token()
    if not current_user:
        return jsonify({"message": "Unauthorized"}), 401
    data = request.json
    task = {
        "id": next_task_id,
        "title": data["title"],
        "description": data.get("description", ""),
        "status": "Todo",
        "priority": data.get("priority", "Medium"),
        "project_id": data["project_id"],
        "user_id": current_user["id"],
    }
    tasks.append(task)
    next_task_id += 1
    return jsonify(task)


@app.route("/tasks/<int:task_id>", methods=["PUT"])
def update_task(task_id):
    current_user = get_user_from_token()
    if not current_user:
        return jsonify({"message": "Unauthorized"}), 401
    data = request.json
    for task in tasks:
        if task["id"] == task_id:
            if task["user_id"] != current_user["id"]:
                return jsonify({"message": "Unauthorized"}), 403
            if "status" in data:
                task["status"] = data["status"]
            if "title" in data:
                task["title"] = data["title"]
            if "description" in data:
                task["description"] = data["description"]
            if "priority" in data:
                task["priority"] = data["priority"]
            return jsonify(task)
    return jsonify({"message": "Task not found"}), 404


@app.route("/tasks/<int:task_id>", methods=["DELETE"])
def delete_task(task_id):
    current_user = get_user_from_token()
    if not current_user:
        return jsonify({"message": "Unauthorized"}), 401
    for task in tasks:
        if task["id"] == task_id:
            if task["user_id"] != current_user["id"]:
                return jsonify({"message": "Unauthorized"}), 403
            tasks.remove(task)
            return jsonify({"message": "Task deleted"})
    return jsonify({"message": "Task not found"}), 404


@app.route("/comments", methods=["GET"])
def get_comments():
    current_user = get_user_from_token()
    if not current_user:
        return jsonify({"message": "Unauthorized"}), 401
    task_id = request.args.get("task_id", type=int)
    if not task_id:
        return jsonify([])
    task_comments = [c for c in comments if c["task_id"] == task_id]
    return jsonify(task_comments)


@app.route("/comments", methods=["POST"])
def add_comment():
    global next_comment_id
    current_user = get_user_from_token()
    if not current_user:
        return jsonify({"message": "Unauthorized"}), 401
    data = request.json
    comment = {
        "id": next_comment_id,
        "task_id": data["task_id"],
        "user_id": current_user["id"],
        "comment": data["comment"],
    }
    comments.append(comment)
    next_comment_id += 1
    return jsonify(comment)


@app.route("/stats", methods=["GET"])
def get_stats():
    current_user = get_user_from_token()
    if not current_user:
        return jsonify({"message": "Unauthorized"}), 401
    user_projects = [p for p in projects if p["user_id"] == current_user["id"]]
    user_tasks = [t for t in tasks if t["user_id"] == current_user["id"]]
    completed_tasks = len([t for t in user_tasks if t["status"] == "Done"])
    return jsonify({
        "total_projects": len(user_projects),
        "total_tasks": len(user_tasks),
        "completed_tasks": completed_tasks,
    })


if __name__ == "__main__":
    app.run(debug=True)
