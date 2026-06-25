import { useState, useEffect } from "react";
import { useParams, Link } from "react-router-dom";

const API_URL = "http://localhost:5000";
const COLUMNS = ["Todo", "In Progress", "Review", "Done"];

// Maps out the natural workflow sequence
const NEXT_STATUS_MAP = {
  "Todo": "In Progress",
  "In Progress": "Review",
  "Review": "Done"
};

function ProjectPage() {
  const { id } = useParams();
  
  // Auth state data
  const token = localStorage.getItem("token");
  const user = JSON.parse(localStorage.getItem("user") || "{}");
  const headers = { 
    "Authorization": `Bearer ${token}`,
    "Content-Type": "application/json"
  };

  // List data states
  const [tasks, setTasks] = useState([]);
  const [members, setMembers] = useState([]);
  const [users, setUsers] = useState([]);

  // Form input states
  const [taskTitle, setTaskTitle] = useState("");
  const [taskDescription, setTaskDescription] = useState("");
  const [priority, setPriority] = useState("Medium");
  const [assigneeId, setAssigneeId] = useState("");
  const [newMemberId, setNewMemberId] = useState("");

  const [isAdmin, setIsAdmin] = useState(false);

  // Load everything when the component mounts
  useEffect(() => {
    loadProjectData();
  }, [id]);

  const loadProjectData = async () => {
    try {
      await Promise.all([loadMembers(), loadUsers(), loadTasks()]);
    } catch (err) {
      console.error("Error loading board data:", err);
    }
  };

  const loadMembers = async () => {
    const res = await fetch(`${API_URL}/projects/${id}/members`, { headers });
    const data = await res.json();
    setMembers(data);

    // Check if the current logged-in user is an admin of this project
    const currentMember = data.find(m => m.user_id === user.id);
    if (currentMember?.role === "admin") {
      setIsAdmin(true);
    }
  };

  const loadUsers = async () => {
    const res = await fetch(`${API_URL}/users`, { headers });
    const data = await res.json();
    setUsers(data);
  };

  const loadTasks = async () => {
    const res = await fetch(`${API_URL}/tasks?project_id=${id}`, { headers });
    const data = await res.json();
    setTasks(data);
  };

  const handleAddTask = async (e) => {
    e.preventDefault(); // Stop page refresh
    
    const newTask = {
      title: taskTitle,
      description: taskDescription,
      priority,
      project_id: Number(id),
      ...(assigneeId && { assignee_id: Number(assigneeId) })
    };

    await fetch(`${API_URL}/tasks`, {
      method: "POST",
      headers,
      body: JSON.stringify(newTask)
    });

    // Reset fields
    setTaskTitle("");
    setTaskDescription("");
    setPriority("Medium");
    setAssigneeId("");
    
    loadTasks();
  };

  const handleUpdateTaskStatus = async (taskId, currentStatus) => {
    const nextStatus = NEXT_STATUS_MAP[currentStatus];
    if (!nextStatus) return;

    await fetch(`${API_URL}/tasks/${taskId}`, {
      method: "PUT",
      headers,
      body: JSON.stringify({ status: nextStatus })
    });

    loadTasks();
  };

  const handleDeleteTask = async (taskId) => {
    if (!window.confirm("Are you sure you want to delete this task?")) return;
    
    await fetch(`${API_URL}/tasks/${taskId}`, { method: "DELETE", headers });
    loadTasks();
  };

  const handleAddMember = async (e) => {
    e.preventDefault();
    if (!newMemberId) return;

    await fetch(`${API_URL}/projects/${id}/members`, {
      method: "POST",
      headers,
      body: JSON.stringify({ user_id: Number(newMemberId) })
    });

    setNewMemberId("");
    loadMembers();
  };

  const handleRemoveMember = async (memberUserId) => {
    if (!window.confirm("Remove this member from the project?")) return;

    await fetch(`${API_URL}/projects/${id}/members/${memberUserId}`, { 
      method: "DELETE", 
      headers 
    });
    loadMembers();
  };

  // Filter out users who are already part of this project
  const memberIds = members.map(m => m.user_id);
  const availableUsers = users.filter(u => !memberIds.includes(u.id));

  return (
    <div className="page">
      <nav className="navbar">
        <Link to="/dashboard">← Back to Dashboard</Link>
        <h2>Project #{id}</h2>
      </nav>

      {/* Admin Panel: Add/Remove Members */}
      {isAdmin && (
        <div className="card">
          <h3>Project Members</h3>
          <div className="members-list">
            {members.map(member => (
              <div key={member.user_id} className="member-item">
                <span>{member.username} ({member.role})</span>
                {member.role !== "admin" && (
                  <button className="btn danger" onClick={() => handleRemoveMember(member.user_id)}>
                    Remove
                  </button>
                )}
              </div>
            ))}
          </div>

          <form onSubmit={handleAddMember} className="inline-form">
            <select value={newMemberId} onChange={(e) => setNewMemberId(e.target.value)}>
              <option value="">Select user to add...</option>
              {availableUsers.map(u => (
                <option key={u.id} value={u.id}>{u.username}</option>
              ))}
            </select>
            <button type="submit" className="btn">Add Member</button>
          </form>
        </div>
      )}

      {/* Creation Panel: Create Tasks */}
      <div className="card">
        <h3>Create New Task</h3>
        <form onSubmit={handleAddTask} className="task-form">
          <input 
            placeholder="Task Title" 
            value={taskTitle} 
            onChange={(e) => setTaskTitle(e.target.value)} 
            required 
          />
          <input 
            placeholder="Description" 
            value={taskDescription} 
            onChange={(e) => setTaskDescription(e.target.value)} 
          />
          
          <select value={priority} onChange={(e) => setPriority(e.target.value)}>
            <option>Low</option>
            <option>Medium</option>
            <option>High</option>
            <option>Critical</option>
          </select>

          <select value={assigneeId} onChange={(e) => setAssigneeId(e.target.value)}>
            <option value="">Assign User (Optional)</option>
            {members.map(m => (
              <option key={m.user_id} value={m.user_id}>{m.username}</option>
            ))}
          </select>

          <button type="submit" className="btn">Create Task</button>
        </form>
      </div>

      {/* Kanban Board Layout */}
      <div className="kanban">
        {COLUMNS.map(status => (
          <div key={status} className="column">
            <h3>{status}</h3>
            
            <div className="task-list">
              {tasks
                .filter(task => task.status === status)
                .map(task => (
                  <div key={task.id} className="task">
                    <h4>{task.title}</h4>
                    {task.description && <p>{task.description}</p>}
                    <p><small>Priority:</small> <strong>{task.priority}</strong></p>
                    {task.assignee_name && <p><small>Assigned to:</small> {task.assignee_name}</p>}

                    <div className="task-actions">
                      {status !== "Done" && (
                        <button className="btn" onClick={() => handleUpdateTaskStatus(task.id, task.status)}>
                          Move →
                        </button>
                      )}
                      {isAdmin && (
                        <button className="btn danger" onClick={() => handleDeleteTask(task.id)}>
                          Delete
                        </button>
                      )}
                    </div>
                  </div>
                ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default ProjectPage;