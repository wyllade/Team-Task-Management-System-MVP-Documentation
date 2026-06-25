import { useState, useEffect } from "react";
import { useParams, Link } from "react-router-dom";

const API = "http://localhost:5000";
const COLUMNS = ["Todo", "In Progress", "Review", "Done"];
const NEXT = { "Todo": "In Progress", "In Progress": "Review", "Review": "Done" };

function TaskPage() {
  const { id } = useParams();
  const token = localStorage.getItem("token");
  const headers = { Authorization: `Bearer ${token}` };

  const [task, setTask] = useState(null);
  const [comments, setComments] = useState([]);
  const [ctext, setCtext] = useState("");

  useEffect(() => { load(); }, []);

  async function load() {
    const t = await fetch(`${API}/tasks/${id}`, { headers }).then(r => r.json());
    setTask(t);
    const c = await fetch(`${API}/comments?task_id=${id}`, { headers }).then(r => r.json());
    setComments(c);
  }

  async function move(status) {
    await fetch(`${API}/tasks/${id}`, { method: "PUT", headers: { ...headers, "Content-Type": "application/json" }, body: JSON.stringify({ status }) });
    load();
  }

  async function addComment() {
    if (!ctext) return;
    await fetch(`${API}/comments`, { method: "POST", headers: { ...headers, "Content-Type": "application/json" }, body: JSON.stringify({ task_id: +id, comment: ctext }) });
    setCtext("");
    const c = await fetch(`${API}/comments?task_id=${id}`, { headers }).then(r => r.json());
    setComments(c);
  }

  if (!task) return <div className="page"><p>Loading...</p></div>;

  return (
    <div className="page">
      <nav className="navbar">
        <Link to={`/project/${task.project_id}`}>&larr; Back to Project</Link>
        <h2>{task.title}</h2>
      </nav>

      <div className="task-detail-card">
        <div className="task-detail-row">
          <span className="label">Status</span>
          <span className={`pill status-${task.status.toLowerCase().replace(/\s+/g, "-")}`}>{task.status}</span>
          {task.status !== "Done" && (
            <button className="btn small" onClick={() => move(NEXT[task.status])}>
              Move to {NEXT[task.status]}
            </button>
          )}
        </div>

        <div className="task-detail-row">
          <span className="label">Priority</span>
          <span className="pill">{task.priority}</span>
        </div>

        <div className="task-detail-row">
          <span className="label">Assigned To</span>
          <span>{task.assignee_name || "Unassigned"}</span>
        </div>

        <div className="task-detail-row">
          <span className="label">Created By</span>
          <span>{task.creator_name}</span>
        </div>

        {task.description && (
          <div className="task-detail-row">
            <span className="label">Description</span>
            <p>{task.description}</p>
          </div>
        )}
      </div>

      <div className="card comment-section-full">
        <h3>Comments</h3>
        <div className="row">
          <input placeholder="Write a comment..." value={ctext} onChange={e => setCtext(e.target.value)} />
          <button className="btn small" onClick={addComment}>Post</button>
        </div>
        {comments.map(c => (
          <p key={c.id} className="comment"><strong>{c.username}:</strong> {c.comment}</p>
        ))}
        {comments.length === 0 && <p className="empty">No comments yet.</p>}
      </div>
    </div>
  );
}

export default TaskPage;
