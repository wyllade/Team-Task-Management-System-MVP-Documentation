import { useState, useEffect } from "react";
import { useParams, Link } from "react-router-dom";
import TaskCard from "./TaskCard";

function ProjectPage() {
  const { id } = useParams();
  const token = localStorage.getItem("token");

  const [tasks, setTasks] = useState([]);
  const [comments, setComments] = useState({});
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [priority, setPriority] = useState("Medium");
  const [commentText, setCommentText] = useState({});

  useEffect(() => {
    fetchTasks();
  }, []);

  async function fetchTasks() {
    const response = await fetch(`http://localhost:5000/tasks?project_id=${id}`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    const data = await response.json();
    setTasks(data);
    data.forEach((task) => fetchComments(task.id));
  }

  async function fetchComments(taskId) {
    const response = await fetch(`http://localhost:5000/comments?task_id=${taskId}`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    const data = await response.json();
    setComments((prev) => ({ ...prev, [taskId]: data }));
  }

  async function createTask() {
    await fetch("http://localhost:5000/tasks", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({ title, description, priority, project_id: parseInt(id) }),
    });
    setTitle("");
    setDescription("");
    setPriority("Medium");
    fetchTasks();
  }

  async function updateStatus(taskId, status) {
    await fetch(`http://localhost:5000/tasks/${taskId}`, {
      method: "PUT",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({ status }),
    });
    fetchTasks();
  }

  async function deleteTask(taskId) {
    await fetch(`http://localhost:5000/tasks/${taskId}`, {
      method: "DELETE",
      headers: { Authorization: `Bearer ${token}` },
    });
    fetchTasks();
  }

  async function addComment(taskId) {
    const text = commentText[taskId];
    if (!text) return;
    await fetch("http://localhost:5000/comments", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({ task_id: taskId, comment: text }),
    });
    setCommentText((prev) => ({ ...prev, [taskId]: "" }));
    fetchComments(taskId);
  }

  const columns = ["Todo", "In Progress", "Review", "Done"];

  return (
    <div style={{ padding: "2rem" }}>
      <Link to="/dashboard">&larr; Back to Dashboard</Link>
      <h1>Project #{id}</h1>

      <div style={{ border: "1px solid #ccc", padding: "1rem", margin: "1rem 0" }}>
        <h3>Add Task</h3>
        <input placeholder="Title" value={title} onChange={(e) => setTitle(e.target.value)} />
        <br />
        <input placeholder="Description" value={description} onChange={(e) => setDescription(e.target.value)} />
        <br />
        <select value={priority} onChange={(e) => setPriority(e.target.value)}>
          <option>Low</option>
          <option>Medium</option>
          <option>High</option>
        </select>
        <br />
        <button onClick={createTask}>Add Task</button>
      </div>

      <div style={{ display: "flex", gap: "1rem" }}>
        {columns.map((column) => (
          <div key={column} style={{ flex: 1, border: "1px solid #ccc", padding: "0.5rem" }}>
            <h3>{column}</h3>
            {tasks
              .filter((task) => task.status === column)
              .map((task) => (
                <div key={task.id}>
                  <TaskCard task={task} onStatusChange={updateStatus} onDelete={deleteTask} />
                  <div style={{ margin: "0.5rem 0" }}>
                    <input
                      placeholder="Add comment..."
                      value={commentText[task.id] || ""}
                      onChange={(e) =>
                        setCommentText((prev) => ({ ...prev, [task.id]: e.target.value }))
                      }
                    />
                    <button onClick={() => addComment(task.id)}>Comment</button>
                    {comments[task.id] &&
                      comments[task.id].map((c) => (
                        <p key={c.id} style={{ fontSize: "0.9rem", margin: "0.2rem 0" }}>
                          - {c.comment}
                        </p>
                      ))}
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
