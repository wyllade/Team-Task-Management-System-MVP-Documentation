import { useState, useEffect } from "react";
import { useNavigate, Link } from "react-router-dom";

function Dashboard() {
  const [projects, setProjects] = useState([]);
  const [stats, setStats] = useState({ total_projects: 0, total_tasks: 0, completed_tasks: 0 });
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const navigate = useNavigate();

  const token = localStorage.getItem("token");

  useEffect(() => {
    fetchProjects();
    fetchStats();
  }, []);

  async function fetchProjects() {
    const response = await fetch("http://localhost:5000/projects", {
      headers: { Authorization: `Bearer ${token}` },
    });
    const data = await response.json();
    setProjects(data);
  }

  async function fetchStats() {
    const response = await fetch("http://localhost:5000/stats", {
      headers: { Authorization: `Bearer ${token}` },
    });
    const data = await response.json();
    setStats(data);
  }

  async function createProject() {
    await fetch("http://localhost:5000/projects", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({ name, description }),
    });
    setName("");
    setDescription("");
    fetchProjects();
  }

  async function deleteProject(id) {
    await fetch(`http://localhost:5000/projects/${id}`, {
      method: "DELETE",
      headers: { Authorization: `Bearer ${token}` },
    });
    fetchProjects();
  }

  function logout() {
    localStorage.removeItem("token");
    localStorage.removeItem("user");
    navigate("/");
  }

  return (
    <div style={{ padding: "2rem" }}>
      <h1>Dashboard</h1>
      <button onClick={logout}>Logout</button>

      <div style={{ border: "1px solid #ccc", padding: "1rem", margin: "1rem 0" }}>
        <h3>Stats</h3>
        <p>Total Projects: {stats.total_projects}</p>
        <p>Total Tasks: {stats.total_tasks}</p>
        <p>Completed Tasks: {stats.completed_tasks}</p>
      </div>

      <div style={{ border: "1px solid #ccc", padding: "1rem", margin: "1rem 0" }}>
        <h3>Create Project</h3>
        <input placeholder="Project Name" value={name} onChange={(e) => setName(e.target.value)} />
        <br />
        <input placeholder="Description" value={description} onChange={(e) => setDescription(e.target.value)} />
        <br />
        <button onClick={createProject}>Create</button>
      </div>

      <h3>My Projects</h3>
      {projects.map((project) => (
        <div key={project.id} style={{ border: "1px solid #ccc", padding: "0.5rem", margin: "0.5rem 0" }}>
          <Link to={`/project/${project.id}`}>
            <h4>{project.name}</h4>
          </Link>
          <p>{project.description}</p>
          <button onClick={() => deleteProject(project.id)}>Delete</button>
        </div>
      ))}
    </div>
  );
}

export default Dashboard;
