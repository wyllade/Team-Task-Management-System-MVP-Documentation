import { useState, useEffect } from "react";
import { useParams, Link } from "react-router-dom";

const API = "http://localhost:5000";
const COLUMNS = ["Todo", "In Progress", "Review", "Done"];

function TaskCard({ task, onMove, onDelete, isAdmin }) {
  const next = { "Todo": "In Progress", "In Progress": "Review", "Review": "Done" };
  return (
    <div className="task-card">
      <Link to={`/task/${task.id}`} className="task-link"><h4>{task.title}</h4></Link>
      <span className="pill">{task.priority}</span>
      {task.assignee_name && <span className="pill assignee">Assigned: {task.assignee_name}</span>}
      {task.description && <p>{task.description}</p>}
      {onMove && task.status !== "Done" && <button className="btn small" onClick={() => onMove(task.id, next[task.status])}>{next[task.status]}</button>}
      {onDelete && isAdmin && <button className="btn small danger" onClick={() => onDelete(task.id)}>X</button>}
    </div>
  );
}

function ProjectPage() {
  const { id } = useParams();
  const token = localStorage.getItem("token");
  const headers = { Authorization: `Bearer ${token}` };
  const user = JSON.parse(localStorage.getItem("user") || "{}");

  const [tasks, setTasks] = useState([]);
  const [comments, setComments] = useState({});
  const [title, setTitle] = useState("");
  const [desc, setDesc] = useState("");
  const [priority, setPriority] = useState("Medium");
  const [ctext, setCtext] = useState({});
  const [assigneeId, setAssigneeId] = useState("");

  const [members, setMembers] = useState([]);
  const [allUsers, setAllUsers] = useState([]);
  const [addUserId, setAddUserId] = useState("");
  const [isAdmin, setIsAdmin] = useState(false);

  useEffect(() => { loadAll(); }, []);

  async function loadAll() {
    await loadMembers();
    await loadUsers();
    await load();
  }

  async function load() {
    const t = await fetch(`${API}/tasks?project_id=${id}`, { headers }).then(r => r.json());
    setTasks(t);
    t.forEach(task => loadComments(task.id));
  }

  async function loadComments(tid) {
    const c = await fetch(`${API}/comments?task_id=${tid}`, { headers }).then(r => r.json());
    setComments(prev => ({ ...prev, [tid]: c }));
  }

  async function loadMembers() {
    const m = await fetch(`${API}/projects/${id}/members`, { headers }).then(r => r.json());
    setMembers(m);
    const cur = m.find(mm => mm.user_id === user.id);
    setIsAdmin(cur && cur.role === "admin");
  }

  async function loadUsers() {
    const u = await fetch(`${API}/users`, { headers }).then(r => r.json());
    setAllUsers(u);
  }

  function api(path, opts) {
    return fetch(`${API}${path}`, { headers: { ...headers, "Content-Type": "application/json" }, ...opts }).then(r => r.json());
  }

  async function addTask() {
    const body = { title, description: desc, priority, project_id: +id };
    if (assigneeId) body.assignee_id = +assigneeId;
    await api("/tasks", { method: "POST", body: JSON.stringify(body) });
    setTitle(""); setDesc(""); setPriority("Medium"); setAssigneeId(""); load();
  }

  async function move(tid, status) {
    await api(`/tasks/${tid}`, { method: "PUT", body: JSON.stringify({ status }) });
    load();
  }

  async function del(tid) {
    await api(`/tasks/${tid}`, { method: "DELETE" });
    load();
  }

  async function addComment(tid) {
    const text = ctext[tid];
    if (!text) return;
    await api("/comments", { method: "POST", body: JSON.stringify({ task_id: tid, comment: text }) });
    setCtext(prev => ({ ...prev, [tid]: "" }));
    loadComments(tid);
  }

  async function addMember() {
    if (!addUserId) return;
    await api(`/projects/${id}/members`, { method: "POST", body: JSON.stringify({ user_id: +addUserId }) });
    setAddUserId("");
    loadMembers();
  }

  async function removeMember(uid) {
    await api(`/projects/${id}/members/${uid}`, { method: "DELETE" });
    loadMembers();
  }

  const memberIds = members.map(m => m.user_id);
  const nonMemberUsers = allUsers.filter(u => !memberIds.includes(u.id));

  return (
    <div className="page">
      <nav className="navbar">
        <Link to="/dashboard">&larr; Back</Link>
        <h2>Project #{id}</h2>
      </nav>

      {isAdmin && (
        <div className="card members-section">
          <h3>Members</h3>
          <div className="member-list">
            {members.map(m => (
              <div key={m.user_id} className="member-item">
                <span>{m.username} <span className="pill">{m.role}</span></span>
                {isAdmin && m.role !== "admin" && <button className="btn small danger" onClick={() => removeMember(m.user_id)}>Remove</button>}
              </div>
            ))}
          </div>
          {nonMemberUsers.length > 0 && (
            <div className="row add-member">
              <select value={addUserId} onChange={e => setAddUserId(e.target.value)}>
                <option value="">-- Add member --</option>
                {nonMemberUsers.map(u => <option key={u.id} value={u.id}>{u.username} ({u.email})</option>)}
              </select>
              <button className="btn small" onClick={addMember}>Add</button>
            </div>
          )}
        </div>
      )}

      <div className="card create-form">
        <h3>Add Task</h3>
        <div className="row">
          <input placeholder="Title" value={title} onChange={e => setTitle(e.target.value)} />
          <select value={priority} onChange={e => setPriority(e.target.value)}><option>Low</option><option>Medium</option><option>High</option><option>Critical</option></select>
          <select value={assigneeId} onChange={e => setAssigneeId(e.target.value)}>
            <option value="">Assign to...</option>
            {members.map(m => <option key={m.user_id} value={m.user_id}>{m.username}</option>)}
          </select>
          <button className="btn" onClick={addTask}>Add</button>
        </div>
        <input placeholder="Description" value={desc} onChange={e => setDesc(e.target.value)} />
      </div>

      <div className="kanban">
        {COLUMNS.map(col => (
          <div key={col} className="kanban-col">
            <h3>{col}</h3>
            {tasks.filter(t => t.status === col).map(task => (
              <div key={task.id}>
                <TaskCard task={task} onMove={move} onDelete={del} isAdmin={isAdmin} />
                <div className="comment-section">
                  <div className="row"><input placeholder="Comment..." value={ctext[task.id] || ""} onChange={e => setCtext(p => ({ ...p, [task.id]: e.target.value }))} /><button className="btn small" onClick={() => addComment(task.id)}>Post</button></div>
                  {(comments[task.id] || []).map(c => <p key={c.id} className="comment"><strong>{c.username}:</strong> {c.comment}</p>)}
                </div>
              </div>
            ))}
          </div>
        ))}
      </div>
    </div>
  );
}

export default ProjectPage;
