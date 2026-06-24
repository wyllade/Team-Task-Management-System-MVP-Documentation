from flask import Flask, request, jsonify
from flask_cors import CORS
import jwt, datetime
from functools import wraps

app = Flask(__name__)
CORS(app)
SECRET_KEY = "secret-key"

users, projects, tasks, comments = [], [], [], []
ids = {"user": 1, "project": 1, "task": 1, "comment": 1}

def require_auth(f):
    @wraps(f)
    def wrapper(*args, **kw):
        auth = request.headers.get("Authorization", "")
        if not auth.startswith("Bearer "):
            return jsonify({"message": "Unauthorized"}), 401
        try:
            data = jwt.decode(auth[7:], SECRET_KEY, algorithms=["HS256"])
            for u in users:
                if u["id"] == data["user_id"]:
                    request.current_user = u
                    return f(*args, **kw)
        except jwt.InvalidTokenError:
            pass
        return jsonify({"message": "Unauthorized"}), 401
    return wrapper

def _find(lst, id):
    for item in lst:
        if item["id"] == id:
            return item
    return None

@app.route("/")
def home():
    return jsonify({"message": "Project Management System API"})

@app.route("/register", methods=["POST"])
def register():
    global ids
    d = request.json
    u = {"id": ids["user"], "username": d["username"], "email": d["email"], "password": d["password"]}
    users.append(u)
    ids["user"] += 1
    return jsonify({"message": "User registered"})

@app.route("/login", methods=["POST"])
def login():
    d = request.json
    for u in users:
        if u["email"] == d["email"] and u["password"] == d["password"]:
            token = jwt.encode({"user_id": u["id"], "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=24)}, SECRET_KEY, algorithm="HS256")
            return jsonify({"token": token, "user": {"id": u["id"], "username": u["username"]}})
    return jsonify({"message": "Invalid credentials"}), 401

@app.route("/projects", methods=["GET", "POST"])
@require_auth
def handle_projects():
    global ids
    if request.method == "GET":
        return jsonify([p for p in projects if p["user_id"] == request.current_user["id"]])
    d = request.json
    p = {"id": ids["project"], "name": d["name"], "description": d.get("description", ""), "user_id": request.current_user["id"]}
    projects.append(p)
    ids["project"] += 1
    return jsonify(p)

@app.route("/projects/<int:pid>", methods=["DELETE"])
@require_auth
def delete_project(pid):
    p = _find(projects, pid)
    if not p:
        return jsonify({"message": "Not found"}), 404
    if p["user_id"] != request.current_user["id"]:
        return jsonify({"message": "Unauthorized"}), 403
    projects.remove(p)
    return jsonify({"message": "Deleted"})

@app.route("/tasks", methods=["GET", "POST"])
@require_auth
def handle_tasks():
    global ids
    if request.method == "GET":
        pid = request.args.get("project_id", type=int)
        p = _find(projects, pid)
        if not p or p["user_id"] != request.current_user["id"]:
            return jsonify({"message": "Unauthorized"}), 403
        return jsonify([t for t in tasks if t["project_id"] == pid])
    d = request.json
    t = {"id": ids["task"], "title": d["title"], "description": d.get("description", ""), "status": "Todo", "priority": d.get("priority", "Medium"), "project_id": d["project_id"], "user_id": request.current_user["id"]}
    tasks.append(t)
    ids["task"] += 1
    return jsonify(t)

@app.route("/tasks/<int:tid>", methods=["PUT", "DELETE"])
@require_auth
def update_task(tid):
    t = _find(tasks, tid)
    if not t:
        return jsonify({"message": "Not found"}), 404
    if t["user_id"] != request.current_user["id"]:
        return jsonify({"message": "Unauthorized"}), 403
    if request.method == "DELETE":
        tasks.remove(t)
        return jsonify({"message": "Deleted"})
    d = request.json
    for k in ("status", "title", "description", "priority"):
        if k in d:
            t[k] = d[k]
    return jsonify(t)

@app.route("/comments", methods=["GET", "POST"])
@require_auth
def handle_comments():
    global ids
    if request.method == "GET":
        return jsonify([c for c in comments if c["task_id"] == request.args.get("task_id", type=int)])
    d = request.json
    c = {"id": ids["comment"], "task_id": d["task_id"], "user_id": request.current_user["id"], "comment": d["comment"]}
    comments.append(c)
    ids["comment"] += 1
    return jsonify(c)

@app.route("/stats")
@require_auth
def get_stats():
    ut = [t for t in tasks if t["user_id"] == request.current_user["id"]]
    return jsonify({"total_projects": len([p for p in projects if p["user_id"] == request.current_user["id"]]), "total_tasks": len(ut), "completed_tasks": len([t for t in ut if t["status"] == "Done"])})

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
