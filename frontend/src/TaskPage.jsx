import { useState, useEffect } from "react";
import { useParams, Link } from "react-router-dom";

const API_URL = "http://localhost:5000";

// Simple status progression dictionary
const NEXT_STATUS_MAP = {
  "Todo": "In Progress",
  "In Progress": "Review",
  "Review": "Done"
};

function TaskPage() {
  const { id } = useParams();
  
  const token = localStorage.getItem("token");
  const headers = {
    "Authorization": `Bearer ${token}`,
    "Content-Type": "application/json"
  };

  const [task, setTask] = useState(null);
  const [comments, setComments] = useState([]);
  const [commentText, setCommentText] = useState("");

  // Load task and comments when page opens
  useEffect(() => {
    const loadPageData = async () => {
      try {
        const [taskRes, commentsRes] = await Promise.all([
          fetch(`${API_URL}/tasks/${id}`, { headers }),
          fetch(`${API_URL}/comments?task_id=${id}`, { headers })
        ]);

        const taskData = await taskRes.json();
        const commentsData = await commentsRes.json();

        setTask(taskData);
        setComments(commentsData);
      } catch (error) {
        console.error("Failed to fetch task details:", error);
      }
    };

    loadPageData();
  }, [id]);

  // Moves task to the next step in the workflow
  const handleMoveTask = async () => {
    const nextStatus = NEXT_STATUS_MAP[task.status];
    if (!nextStatus) return; // If it's already "Done", stop here

    try {
      const response = await fetch(`${API_URL}/tasks/${id}`, {
        method: "PUT",
        headers,
        body: JSON.stringify({ status: nextStatus })
      });

      if (response.ok) {
        // Update local state directly instead of doing another API fetch
        setTask({ ...task, status: nextStatus });
      }
    } catch (error) {
      alert("Could not update task status");
    }
  };

  // Submits a new comment
  const handleAddComment = async (e) => {
    e.preventDefault(); // Prevents page reload
    if (!commentText.trim()) return;

    try {
      const response = await fetch(`${API_URL}/comments`, {
        method: "POST",
        headers,
        body: JSON.stringify({
          task_id: Number(id),
          comment: commentText
        })
      });

      if (response.ok) {
        const newComment = await response.json();
        // Append new comment to list and clear input field
        setComments([...comments, newComment]);
        setCommentText("");
      }
    } catch (error) {
      alert("Failed to post comment");
    }
  };

  // Show loading screen until task data arrives
  if (!task) {
    return (
      <div className="page">
        <p>Loading task details...</p>
      </div>
    );
  }

  const nextStatus = NEXT_STATUS_MAP[task.status];

  return (
    <div className="page">
      <nav className="navbar">
        <Link to={`/project/${task.project_id}`}>← Back to Project</Link>
        <h2>{task.title}</h2>
      </nav>

      <div className="task-detail-card">
        <h3>Task Details</h3>
        <p><strong>Status:</strong> {task.status}</p>
        
        {nextStatus && (
          <button className="btn" onClick={handleMoveTask}>
            Move To {nextStatus}
          </button>
        )}

        <p><strong>Priority:</strong> {task.priority}</p>
        <p><strong>Assigned To:</strong> {task.assignee_name || "Unassigned"}</p>
        <p><strong>Created By:</strong> {task.creator_name}</p>
        
        {task.description && (
          <p><strong>Description:</strong> {task.description}</p>
        )}
      </div>

      <div className="card">
        <h3>Comments</h3>

        {/* Form allows hitting 'Enter' to submit comment */}
        <form onSubmit={handleAddComment} className="row">
          <input
            type="text"
            placeholder="Write a comment..."
            value={commentText}
            onChange={(e) => setCommentText(e.target.value)}
            required
          />
          <button type="submit" className="btn">Post</button>
        </form>

        <div className="comments-list">
          {comments.length > 0 ? (
            comments.map((c) => (
              <p key={c.id} className="comment">
                <strong>{c.username}</strong>: {c.comment}
              </p>
            ))
          ) : (
            <p>No comments yet.</p>
          )}
        </div>
      </div>
    </div>
  );
}

export default TaskPage;