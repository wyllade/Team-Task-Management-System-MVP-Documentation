import { useState, useEffect } from "react";
import { useParams, Link } from "react-router-dom";

const API = "http://localhost:5000";
const COLUMNS = ["Todo", "In Progress", "Review", "Done"];

function TaskCard({ task, onMove, onDelete }) {
  const next = { "Todo": "In Progress", "In Progress": "Review", "Review": "Done" };
  return (
    <div className="task-card">
      <h4>{task.title}</h4>
      <span className="pill">{task.priority}</span>
      {task.description && <p>{task.description}</p>}
      {onMove && task.status !== "Done" && <button className="btn small" onClick={() => onMove(task.id, next[task.status])}>{next[task.status]}</button>}
      {onDelete && <button className="btn small danger" onClick={() => onDelete(task.id)}>X</button>}
    </div>
  );
}

function ProjectPage() {
  const { id } = useParams();
  const token = localStorage.getItem("token");
  const headers = { Authorization: `Bearer ${token}` };
  const [tasks, setTasks] = useState([]);
  const [comments, setComments] = useState({});
  const [title, setTitle] = useState("");
  const [desc, setDesc] = useState("");
  const [priority, setPriority] = useState("Medium");
  const [ctext, setCtext] = useState({});

  useEffect(() => { load(); }, []);

  async function load() {
    const t = await fetch(`${API}/tasks?project_id=${id}`, { headers }).then(r => r.json());
    setTasks(t);
    t.forEach(task => loadComments(task.id));
  }

  async function loadComments(tid) {
    const c = await fetch(`${API}/comments?task_id=${tid}`, { headers }).then(r => r.json());
    setComments(prev => ({ ...prev, [tid]: c }));
  }

  function api(path, opts) {
    return fetch(`${API}${path}`, { headers: { ...headers, "Content-Type": "application/json" }, ...opts }).then(r => r.json());
  }

  async function addTask() {
    await api("/tasks", { method: "POST", body: JSON.stringify({ title, description: desc, priority, project_id: +id }) });
    setTitle(""); setDesc(""); setPriority("Medium"); load();
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

  return (
    <div className="page">
      <nav className="navbar">
        <Link to="/dashboard">&larr; Back</Link>
        <h2>Project #{id}</h2>
      </nav>
      <div className="card create-form">
        <h3>Add Task</h3>
        <div className="row"><input placeholder="Title" value={title} onChange={e => setTitle(e.target.value)} /><select value={priority} onChange={e => setPriority(e.target.value)}><option>Low</option><option>Medium</option><option>High</option></select><button className="btn" onClick={addTask}>Add</button></div>
        <input placeholder="Description" value={desc} onChange={e => setDesc(e.target.value)} />
      </div>
      <div className="kanban">
        {COLUMNS.map(col => (
          <div key={col} className="kanban-col">
            <h3>{col}</h3>
            {tasks.filter(t => t.status === col).map(task => (
              <div key={task.id}>
                <TaskCard task={task} onMove={move} onDelete={del} />
                <div className="comment-section">
                  <div className="row"><input placeholder="Comment..." value={ctext[task.id] || ""} onChange={e => setCtext(p => ({ ...p, [task.id]: e.target.value }))} /><button className="btn small" onClick={() => addComment(task.id)}>Post</button></div>
                  {(comments[task.id] || []).map(c => <p key={c.id} className="comment">{c.comment}</p>)}
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
