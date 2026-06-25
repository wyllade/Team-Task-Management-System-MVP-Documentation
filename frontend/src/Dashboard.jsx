import { useState, useEffect } from "react";
import { useNavigate, Link } from "react-router-dom";

const API = "http://localhost:5000";

function Dashboard() {
  const [projects, setProjects] = useState([]);
  const [stats, setStats] = useState({});
  const [name, setName] = useState("");
  const [desc, setDesc] = useState("");
  const [editId, setEditId] = useState(null);
  const [editName, setEditName] = useState("");
  const [editDesc, setEditDesc] = useState("");
  const navigate = useNavigate();
  const token = localStorage.getItem("token");
  const headers = { Authorization: `Bearer ${token}` };

  useEffect(() => { load(); }, []);

  function load() {
    fetch(`${API}/projects`, { headers }).then(r => r.json()).then(setProjects);
    fetch(`${API}/stats`, { headers }).then(r => r.json()).then(setStats);
  }

  async function create() {
    await fetch(`${API}/projects`, { method: "POST", headers: { ...headers, "Content-Type": "application/json" }, body: JSON.stringify({ name, description: desc }) });
    setName(""); setDesc(""); load();
  }

  async function del(id) {
    await fetch(`${API}/projects/${id}`, { method: "DELETE", headers });
    load();
  }

  function startEdit(p) {
    setEditId(p.id);
    setEditName(p.name);
    setEditDesc(p.description || "");
  }

  async function saveEdit(id) {
    await fetch(`${API}/projects/${id}`, { method: "PUT", headers: { ...headers, "Content-Type": "application/json" }, body: JSON.stringify({ name: editName, description: editDesc }) });
    setEditId(null); load();
  }

  function logout() { localStorage.clear(); navigate("/"); }

  return (
    <div className="page">
      <nav className="navbar"><h2>Dashboard</h2><button className="btn" onClick={logout}>Logout</button></nav>
      <div className="stats">
        <div className="card"><h3>{stats.total_projects || 0}</h3><p>Projects</p></div>
        <div className="card"><h3>{stats.total_tasks || 0}</h3><p>Tasks</p></div>
        <div className="card"><h3>{stats.completed_tasks || 0}</h3><p>Done</p></div>
      </div>
      <div className="card create-form">
        <h3>New Project</h3>
        <input placeholder="Name" value={name} onChange={e => setName(e.target.value)} />
        <input placeholder="Description" value={desc} onChange={e => setDesc(e.target.value)} />
        <button className="btn" onClick={create}>Create</button>
      </div>
      <div className="project-list">
        {projects.map(p => (
          <div key={p.id} className="card project-item">
            {editId === p.id ? (
              <div>
                <input value={editName} onChange={e => setEditName(e.target.value)} />
                <input value={editDesc} onChange={e => setEditDesc(e.target.value)} />
                <button className="btn small" onClick={() => saveEdit(p.id)}>Save</button>
                <button className="btn small danger" onClick={() => setEditId(null)}>Cancel</button>
              </div>
            ) : (
              <div>
                <Link to={`/project/${p.id}`}><h4>{p.name}</h4></Link>
                <p>{p.description}</p>
                <span className="pill">{p.member_count || 1} member{(p.member_count || 1) > 1 ? "s" : ""}</span>
                <div className="project-actions">
                  <button className="btn small" onClick={() => startEdit(p)}>Edit</button>
                  <button className="btn small danger" onClick={() => del(p.id)}>Delete</button>
                </div>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}

export default Dashboard;
