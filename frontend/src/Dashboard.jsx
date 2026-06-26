import { useState, useEffect } from "react";
import { useNavigate, Link } from "react-router-dom";

const API = "http://localhost:5000";

function Dashboard() {
  const [projects, setProjects] = useState([]);
  const [stats, setStats] = useState({});
  const [projectName, setProjectName] = useState("");
  const [projectDescription, setProjectDescription] = useState("");

  const navigate = useNavigate();
  const token = localStorage.getItem("token");
  const headers = { Authorization: `Bearer ${token}` };

  // Load data when the page opens
  useEffect(() => {
    fetchProjects();
    fetchStats();
  }, []);

  async function fetchProjects() {
    const response = await fetch(`${API}/projects`, { headers });
    const data = await response.json();
    setProjects(data);
  }

  async function fetchStats() {
    const response = await fetch(`${API}/stats`, { headers });
    const data = await response.json();
    setStats(data);
  }

  async function createProject() {
    await fetch(`${API}/projects`, {
      method: "POST",
      headers: { ...headers, "Content-Type": "application/json" },
      body: JSON.stringify({ name: projectName, description: projectDescription })
    });

    // Clear the form
    setProjectName("");
    setProjectDescription("");

    // Refresh the lists
    fetchProjects();
    fetchStats();
  }

  async function deleteProject(projectId) {
    if (!window.confirm("Delete this project?")) return;

    await fetch(`${API}/projects/${projectId}`, {
      method: "DELETE",
      headers
    });

    fetchProjects();
    fetchStats();
  }

  function logout() {
    localStorage.clear();
    navigate("/");
  }

  return (
    <div className="page">
      {/* Top Navigation */}
      <nav className="navbar">
        <h2>Dashboard</h2>
        <button className="btn" onClick={logout}>Logout</button>
      </nav>

      {/* Statistics Cards */}
      <div className="stats">
        <div className="card">
          <h3>{stats.total_projects || 0}</h3>
          <p>Projects</p>
        </div>
        <div className="card">
          <h3>{stats.total_tasks || 0}</h3>
          <p>Tasks</p>
        </div>
        <div className="card">
          <h3>{stats.completed_tasks || 0}</h3>
          <p>Completed</p>
        </div>
      </div>

      {/* Create Project Form */}
      <div className="card">
        <h3>Create New Project</h3>
        <input
          placeholder="Project Name"
          value={projectName}
          onChange={(e) => setProjectName(e.target.value)}
        />
        <input
          placeholder="Description"
          value={projectDescription}
          onChange={(e) => setProjectDescription(e.target.value)}
        />
        <button className="btn" onClick={createProject}>Create</button>
      </div>

      {/* Project List */}
      <h3>Your Projects</h3>
      {projects.map((project) => (
        <div key={project.id} className="project-item">
          <Link to={`/project/${project.id}`}>
            <h4>{project.name}</h4>
          </Link>
          <p>{project.description}</p>
          <p><small>{project.member_count || 1} member(s)</small></p>
          <button className="btn danger" onClick={() => deleteProject(project.id)}>
            Delete
          </button>
        </div>
      ))}

      {projects.length === 0 && <p>No projects yet. Create one above.</p>}
    </div>
  );
}

export default Dashboard;
