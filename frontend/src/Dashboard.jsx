import { useState, useEffect } from "react";
import { useNavigate, Link } from "react-router-dom";

const API = "http://localhost:5000";

function Dashboard() {
  const [projects, setProjects] = useState([]);
  const [stats, setStats] = useState({});
  const [name, setName] = useState("");
  const [desc, setDesc] = useState("");
  const navigate = useNavigate();
  const token = localStorage.getItem("token");
  const headers = { Authorization: `Bearer ${token}` };

  useEffect(() => { fetch(`${API}/projects`, { headers }).then(r => r.json()).then(setProjects); }, []);
  useEffect(() => { fetch(`${API}/stats`, { headers }).then(r => r.json()).then(setStats); }, []);

  async function create() {
    await fetch(`${API}/projects`, { method: "POST", headers: { ...headers, "Content-Type": "application/json" }, body: JSON.stringify({ name, description: desc }) });
    setName(""); setDesc("");
    fetch(`${API}/projects`, { headers }).then(r => r.json()).then(setProjects);
  }

  async function del(id) {
    await fetch(`${API}/projects/${id}`, { method: "DELETE", headers });
    fetch(`${API}/projects`, { headers }).then(r => r.json()).then(setProjects);
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
            <Link to={`/project/${p.id}`}><h4>{p.name}</h4></Link>
            <p>{p.description}</p>
            <button className="btn small" onClick={() => del(p.id)}>Delete</button>
          </div>
        ))}
      </div>
    </div>
  );
}

export default Dashboard;
