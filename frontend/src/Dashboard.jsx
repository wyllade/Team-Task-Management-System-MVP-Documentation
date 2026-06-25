const API = "http://localhost:5000";

function Dashboard() {

  const [projects, setProjects] = useState([]);
  const [stats, setStats] = useState({});

  const [projectName, setProjectName] = useState("");
  const [projectDescription, setProjectDescription] = useState("");

  const navigate = useNavigate();

  const token = localStorage.getItem("token");

  const headers = {
    Authorization: `Bearer ${token}`
  };

  useEffect(() => {
    fetchProjects();
    fetchStats();
  }, []);

  async function fetchProjects() {

    const response = await fetch(`${API}/projects`, {
      headers
    });

    const data = await response.json();

    setProjects(data);
  }

  async function fetchStats() {

    const response = await fetch(`${API}/stats`, {
      headers
    });

    const data = await response.json();

    setStats(data);
  }

  async function createProject() {

    const newProject = {
      name: projectName,
      description: projectDescription
    };

    await fetch(`${API}/projects`, {
      method: "POST",
      headers: {
        ...headers,
        "Content-Type": "application/json"
      },
      body: JSON.stringify(newProject)
    });

    setProjectName("");
    setProjectDescription("");

    fetchProjects();
    fetchStats();
  }

  function logout() {
    localStorage.clear();
    navigate("/");
  }
}