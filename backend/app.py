from flask import Flask, request, jsonify
from flask_cors import CORS
import jwt, datetime
from functools import wraps

app = Flask(__name__)
CORS(app)
SECRET_KEY = "secret-key"

users = [{"id": 0, "username": "demo", "email": "demo@test.com", "password": "pass"}]
projects, tasks, comments, project_members = [], [], [], []
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

def _find_member(pid, uid):
    for m in project_members:
        if m["project_id"] == pid and m["user_id"] == uid:
            return m
    return None

def is_project_member(pid, uid):
    p = _find(projects, pid)
    if p and p["user_id"] == uid:
        return True
    return _find_member(pid, uid) is not None

def is_project_admin(pid, uid):
    p = _find(projects, pid)
    if p and p["user_id"] == uid:
        return True
    m = _find_member(pid, uid)
    return m is not None and m["role"] == "admin"

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
    token = jwt.encode({"user_id": u["id"], "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=24)}, SECRET_KEY, algorithm="HS256")
    return jsonify({"token": token, "user": {"id": u["id"], "username": u["username"]}})

@app.route("/login", methods=["POST"])
def login():
    d = request.json
    for u in users:
        if u["email"] == d["email"] and u["password"] == d["password"]:
            token = jwt.encode({"user_id": u["id"], "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=24)}, SECRET_KEY, algorithm="HS256")
            return jsonify({"token": token, "user": {"id": u["id"], "username": u["username"]}})
    return jsonify({"message": "Invalid credentials"}), 401

@app.route("/users")
@require_auth
def get_users():
    return jsonify([{"id": u["id"], "username": u["username"], "email": u["email"]} for u in users])

@app.route("/projects", methods=["GET", "POST"])
@require_auth
def handle_projects():
    global ids
    cu = request.current_user
    if request.method == "GET":
        result = []
        for p in projects:
            if is_project_member(p["id"], cu["id"]):
                members = [m for m in project_members if m["project_id"] == p["id"]]
                result.append({**p, "member_count": len(members) + 1})
        return jsonify(result)
    d = request.json
    p = {"id": ids["project"], "name": d["name"], "description": d.get("description", ""), "user_id": cu["id"]}
    projects.append(p)
    ids["project"] += 1
    project_members.append({"project_id": p["id"], "user_id": cu["id"], "role": "admin"})
    return jsonify(p)

@app.route("/projects/<int:pid>", methods=["PUT", "DELETE"])
@require_auth
def update_project(pid):
    cu = request.current_user
    p = _find(projects, pid)
    if not p:
        return jsonify({"message": "Not found"}), 404
    if not is_project_admin(pid, cu["id"]):
        return jsonify({"message": "Unauthorized"}), 403
    if request.method == "DELETE":
        projects.remove(p)
        global project_members
        project_members = [m for m in project_members if m["project_id"] != pid]
        return jsonify({"message": "Deleted"})
    d = request.json
    if "name" in d: p["name"] = d["name"]
    if "description" in d: p["description"] = d["description"]
    return jsonify(p)

@app.route("/projects/<int:pid>/members", methods=["GET", "POST"])
@require_auth
def handle_members(pid):
    cu = request.current_user
    p = _find(projects, pid)
    if not p:
        return jsonify({"message": "Not found"}), 404
    if request.method == "GET":
        if not is_project_member(pid, cu["id"]):
            return jsonify({"message": "Unauthorized"}), 403
        result = []
        result.append({"user_id": p["user_id"], "username": next((u["username"] for u in users if u["id"] == p["user_id"]), "?"), "role": "admin"})
        for m in project_members:
            if m["project_id"] == pid:
                uname = next((u["username"] for u in users if u["id"] == m["user_id"]), "?")
                result.append({"user_id": m["user_id"], "username": uname, "role": m["role"]})
        return jsonify(result)
    if not is_project_admin(pid, cu["id"]):
        return jsonify({"message": "Unauthorized"}), 403
    d = request.json
    uid = d["user_id"]
    if _find_member(pid, uid) or p["user_id"] == uid:
        return jsonify({"message": "Already a member"}), 400
    project_members.append({"project_id": pid, "user_id": uid, "role": d.get("role", "member")})
    uname = next((u["username"] for u in users if u["id"] == uid), "?")
    return jsonify({"user_id": uid, "username": uname, "role": "member"})

@app.route("/projects/<int:pid>/members/<int:uid>", methods=["DELETE"])
@require_auth
def remove_member(pid, uid):
    cu = request.current_user
    p = _find(projects, pid)
    if not p:
        return jsonify({"message": "Not found"}), 404
    if not is_project_admin(pid, cu["id"]):
        return jsonify({"message": "Unauthorized"}), 403
    if uid == p["user_id"]:
        return jsonify({"message": "Cannot remove owner"}), 400
    m = _find_member(pid, uid)
    if not m:
        return jsonify({"message": "Not a member"}), 404
    project_members.remove(m)
    return jsonify({"message": "Removed"})

@app.route("/tasks", methods=["GET", "POST"])
@require_auth
def handle_tasks():
    global ids
    cu = request.current_user
    if request.method == "GET":
        pid = request.args.get("project_id", type=int)
        if not is_project_member(pid, cu["id"]):
            return jsonify({"message": "Unauthorized"}), 403
        result = []
        for t in tasks:
            if t["project_id"] == pid:
                t_copy = dict(t)
                assignee = next((u for u in users if u["id"] == t.get("assignee_id")), None)
                creator = next((u for u in users if u["id"] == t["user_id"]), None)
                t_copy["assignee_name"] = assignee["username"] if assignee else None
                t_copy["creator_name"] = creator["username"] if creator else "?"
                result.append(t_copy)
        return jsonify(result)
    d = request.json
    pid = d["project_id"]
    if not is_project_member(pid, cu["id"]):
        return jsonify({"message": "Unauthorized"}), 403
    t = {"id": ids["task"], "title": d["title"], "description": d.get("description", ""), "status": "Todo", "priority": d.get("priority", "Medium"), "project_id": pid, "user_id": cu["id"], "assignee_id": d.get("assignee_id")}
    tasks.append(t)
    ids["task"] += 1
    assignee = next((u for u in users if u["id"] == t["assignee_id"]), None)
    t["assignee_name"] = assignee["username"] if assignee else None
    t["creator_name"] = cu["username"]
    return jsonify(t)

@app.route("/tasks/<int:tid>", methods=["PUT", "DELETE"])
@require_auth
def update_task(tid):
    cu = request.current_user
    t = _find(tasks, tid)
    if not t:
        return jsonify({"message": "Not found"}), 404
    if not is_project_member(t["project_id"], cu["id"]):
        return jsonify({"message": "Unauthorized"}), 403
    if request.method == "DELETE":
        if t["user_id"] != cu["id"] and not is_project_admin(t["project_id"], cu["id"]):
            return jsonify({"message": "Unauthorized"}), 403
        tasks.remove(t)
        return jsonify({"message": "Deleted"})
    d = request.json
    for k in ("status", "title", "description", "priority", "assignee_id"):
        if k in d:
            t[k] = d[k]
    assignee = next((u for u in users if u["id"] == t.get("assignee_id")), None)
    t["assignee_name"] = assignee["username"] if assignee else None
    return jsonify(t)

@app.route("/comments", methods=["GET", "POST"])
@require_auth
def handle_comments():
    global ids
    cu = request.current_user
    if request.method == "GET":
        tid = request.args.get("task_id", type=int)
        t = _find(tasks, tid)
        if not t or not is_project_member(t["project_id"], cu["id"]):
            return jsonify({"message": "Unauthorized"}), 403
        result = []
        for c in comments:
            if c["task_id"] == tid:
                c_copy = dict(c)
                user = next((u for u in users if u["id"] == c["user_id"]), None)
                c_copy["username"] = user["username"] if user else "?"
                result.append(c_copy)
        return jsonify(result)
    d = request.json
    tid = d["task_id"]
    t = _find(tasks, tid)
    if not t or not is_project_member(t["project_id"], cu["id"]):
        return jsonify({"message": "Unauthorized"}), 403
    c = {"id": ids["comment"], "task_id": tid, "user_id": cu["id"], "comment": d["comment"], "username": cu["username"]}
    comments.append(c)
    ids["comment"] += 1
    return jsonify(c)

@app.route("/stats")
@require_auth
def get_stats():
    cu = request.current_user
    user_project_ids = set()
    for p in projects:
        if is_project_member(p["id"], cu["id"]):
            user_project_ids.add(p["id"])
    user_tasks = [t for t in tasks if t["project_id"] in user_project_ids and (t["user_id"] == cu["id"] or t.get("assignee_id") == cu["id"] or is_project_admin(t["project_id"], cu["id"]))]
    return jsonify({"total_projects": len(user_project_ids), "total_tasks": len(user_tasks), "completed_tasks": len([t for t in user_tasks if t["status"] == "Done"])})

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
