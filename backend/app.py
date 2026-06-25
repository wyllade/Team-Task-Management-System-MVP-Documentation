from flask import Flask, request, jsonify
from flask_cors import CORS
import jwt, datetime
from functools import wraps

app = Flask(__name__)
CORS(app)
SECRET_KEY = "secret-key"

# In-memory storage
users = [{"id": 0, "username": "demo", "email": "demo@test.com", "password": "pass"}]
projects = []
tasks = []
comments = []
project_members = []
next_id = {"user": 1, "project": 1, "task": 1, "comment": 1}

# ============================================================
# Helper Functions
# ============================================================

def create_token(user_id):
    """Create a JWT token that expires in 24 hours."""
    return jwt.encode(
        {"user_id": user_id, "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=24)},
        SECRET_KEY, algorithm="HS256"
    )

def find_by_id(items, item_id):
    """Find an item in a list by its 'id' field."""
    return next((item for item in items if item["id"] == item_id), None)

def find_project_member(project_id, user_id):
    """Find a membership record for a user in a project."""
    return next(
        (m for m in project_members if m["project_id"] == project_id and m["user_id"] == user_id),
        None
    )

def get_username(user_id):
    """Get a user's username by their ID. Returns '?' if not found."""
    user = next((u for u in users if u["id"] == user_id), None)
    return user["username"] if user else "?"

def is_member(project_id, user_id):
    """Check if a user is a member of a project (creator or invited)."""
    project = find_by_id(projects, project_id)
    if project and project["user_id"] == user_id:
        return True
    return find_project_member(project_id, user_id) is not None

def is_admin(project_id, user_id):
    """Check if a user is an admin of a project."""
    project = find_by_id(projects, project_id)
    if project and project["user_id"] == user_id:
        return True
    member = find_project_member(project_id, user_id)
    return member is not None and member["role"] == "admin"

def require_auth(f):
    """Decorator that checks for a valid JWT token."""
    @wraps(f)
    def wrapper(*args, **kw):
        auth = request.headers.get("Authorization", "")
        if not auth.startswith("Bearer "):
            return jsonify({"message": "Unauthorized"}), 401
        try:
            data = jwt.decode(auth[7:], SECRET_KEY, algorithms=["HS256"])
            user = next((u for u in users if u["id"] == data["user_id"]), None)
            if user:
                request.current_user = user
                return f(*args, **kw)
        except jwt.InvalidTokenError:
            pass
        return jsonify({"message": "Unauthorized"}), 401
    return wrapper

# ============================================================
# Routes
# ============================================================

@app.route("/")
def home():
    return jsonify({"message": "Project Management System API"})

@app.route("/register", methods=["POST"])
def register():
    """Create a new user and return a JWT token."""
    global next_id
    data = request.json
    user = {"id": next_id["user"], "username": data["username"], "email": data["email"], "password": data["password"]}
    users.append(user)
    next_id["user"] += 1
    return jsonify({"token": create_token(user["id"]), "user": {"id": user["id"], "username": user["username"]}})

@app.route("/login", methods=["POST"])
def login():
    """Log in with email and password. Returns a JWT token."""
    data = request.json
    user = next((u for u in users if u["email"] == data["email"] and u["password"] == data["password"]), None)
    if not user:
        return jsonify({"message": "Invalid credentials"}), 401
    return jsonify({"token": create_token(user["id"]), "user": {"id": user["id"], "username": user["username"]}})

@app.route("/users")
@require_auth
def get_users():
    """Return all users (for the member-add dropdown)."""
    return jsonify([{"id": u["id"], "username": u["username"], "email": u["email"]} for u in users])

@app.route("/projects", methods=["GET", "POST"])
@require_auth
def handle_projects():
    """GET: list user's projects. POST: create a new project."""
    global next_id
    user = request.current_user
    if request.method == "GET":
        result = []
        for p in projects:
            if is_member(p["id"], user["id"]):
                count = sum(1 for m in project_members if m["project_id"] == p["id"])
                result.append({**p, "member_count": count})
        return jsonify(result)
    data = request.json
    project = {"id": next_id["project"], "name": data["name"], "description": data.get("description", ""), "user_id": user["id"]}
    projects.append(project)
    next_id["project"] += 1
    project_members.append({"project_id": project["id"], "user_id": user["id"], "role": "admin"})
    return jsonify(project)

@app.route("/projects/<int:project_id>", methods=["PUT", "DELETE"])
@require_auth
def update_project(project_id):
    """PUT: edit project name/description. DELETE: remove project. Admin only."""
    global project_members
    user = request.current_user
    project = find_by_id(projects, project_id)
    if not project:
        return jsonify({"message": "Not found"}), 404
    if not is_admin(project_id, user["id"]):
        return jsonify({"message": "Unauthorized"}), 403
    if request.method == "DELETE":
        projects.remove(project)
        project_members = [m for m in project_members if m["project_id"] != project_id]
        return jsonify({"message": "Deleted"})
    data = request.json
    if "name" in data: project["name"] = data["name"]
    if "description" in data: project["description"] = data["description"]
    return jsonify(project)

@app.route("/projects/<int:project_id>/members", methods=["GET", "POST"])
@require_auth
def handle_members(project_id):
    """GET: list members. POST: add a member (admin only)."""
    user = request.current_user
    project = find_by_id(projects, project_id)
    if not project:
        return jsonify({"message": "Not found"}), 404
    if request.method == "GET":
        if not is_member(project_id, user["id"]):
            return jsonify({"message": "Unauthorized"}), 403
        members = [{"user_id": project["user_id"], "username": get_username(project["user_id"]), "role": "admin"}]
        for m in project_members:
            if m["project_id"] == project_id and m["user_id"] != project["user_id"]:
                members.append({"user_id": m["user_id"], "username": get_username(m["user_id"]), "role": m["role"]})
        return jsonify(members)
    if not is_admin(project_id, user["id"]):
        return jsonify({"message": "Unauthorized"}), 403
    data = request.json
    uid = data["user_id"]
    if find_project_member(project_id, uid) or project["user_id"] == uid:
        return jsonify({"message": "Already a member"}), 400
    project_members.append({"project_id": project_id, "user_id": uid, "role": data.get("role", "member")})
    return jsonify({"user_id": uid, "username": get_username(uid), "role": "member"})

@app.route("/projects/<int:project_id>/members/<int:user_id>", methods=["DELETE"])
@require_auth
def remove_member(project_id, user_id):
    """Remove a member. Admin only. Cannot remove the project owner."""
    user = request.current_user
    project = find_by_id(projects, project_id)
    if not project:
        return jsonify({"message": "Not found"}), 404
    if not is_admin(project_id, user["id"]):
        return jsonify({"message": "Unauthorized"}), 403
    if user_id == project["user_id"]:
        return jsonify({"message": "Cannot remove owner"}), 400
    member = find_project_member(project_id, user_id)
    if not member:
        return jsonify({"message": "Not a member"}), 404
    project_members.remove(member)
    return jsonify({"message": "Removed"})

@app.route("/tasks", methods=["GET", "POST"])
@require_auth
def handle_tasks():
    """GET: list tasks for a project. POST: create a task."""
    global next_id
    user = request.current_user
    if request.method == "GET":
        pid = request.args.get("project_id", type=int)
        if not is_member(pid, user["id"]):
            return jsonify({"message": "Unauthorized"}), 403
        result = []
        for t in tasks:
            if t["project_id"] == pid:
                t = dict(t)
                t["assignee_name"] = get_username(t.get("assignee_id"))
                t["creator_name"] = get_username(t["user_id"])
                result.append(t)
        return jsonify(result)
    data = request.json
    pid = data["project_id"]
    if not is_member(pid, user["id"]):
        return jsonify({"message": "Unauthorized"}), 403
    task = {"id": next_id["task"], "title": data["title"], "description": data.get("description", ""), "status": "Todo", "priority": data.get("priority", "Medium"), "project_id": pid, "user_id": user["id"], "assignee_id": data.get("assignee_id")}
    tasks.append(task)
    next_id["task"] += 1
    task["assignee_name"] = get_username(task["assignee_id"])
    task["creator_name"] = user["username"]
    return jsonify(task)

@app.route("/tasks/<int:task_id>", methods=["PUT", "DELETE"])
@require_auth
def update_task(task_id):
    """PUT: update task fields. DELETE: delete task (creator or admin only)."""
    user = request.current_user
    task = find_by_id(tasks, task_id)
    if not task:
        return jsonify({"message": "Not found"}), 404
    if not is_member(task["project_id"], user["id"]):
        return jsonify({"message": "Unauthorized"}), 403
    if request.method == "DELETE":
        if task["user_id"] != user["id"] and not is_admin(task["project_id"], user["id"]):
            return jsonify({"message": "Unauthorized"}), 403
        tasks.remove(task)
        return jsonify({"message": "Deleted"})
    data = request.json
    for field in ("status", "title", "description", "priority", "assignee_id"):
        if field in data:
            task[field] = data[field]
    task["assignee_name"] = get_username(task.get("assignee_id"))
    return jsonify(task)

@app.route("/comments", methods=["GET", "POST"])
@require_auth
def handle_comments():
    """GET: list comments for a task. POST: add a comment."""
    global next_id
    user = request.current_user
    if request.method == "GET":
        tid = request.args.get("task_id", type=int)
        t = find_by_id(tasks, tid)
        if not t or not is_member(t["project_id"], user["id"]):
            return jsonify({"message": "Unauthorized"}), 403
        result = []
        for c in comments:
            if c["task_id"] == tid:
                c = dict(c)
                c["username"] = get_username(c["user_id"])
                result.append(c)
        return jsonify(result)
    data = request.json
    tid = data["task_id"]
    t = find_by_id(tasks, tid)
    if not t or not is_member(t["project_id"], user["id"]):
        return jsonify({"message": "Unauthorized"}), 403
    comment = {"id": next_id["comment"], "task_id": tid, "user_id": user["id"], "comment": data["comment"], "username": user["username"]}
    comments.append(comment)
    next_id["comment"] += 1
    return jsonify(comment)

@app.route("/stats")
@require_auth
def get_stats():
    """Return project/task counts for the current user."""
    user = request.current_user
    project_ids = {p["id"] for p in projects if is_member(p["id"], user["id"])}
    user_tasks = [t for t in tasks if t["project_id"] in project_ids and (t["user_id"] == user["id"] or t.get("assignee_id") == user["id"] or is_admin(t["project_id"], user["id"]))]
    return jsonify({"total_projects": len(project_ids), "total_tasks": len(user_tasks), "completed_tasks": sum(1 for t in user_tasks if t["status"] == "Done")})

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
