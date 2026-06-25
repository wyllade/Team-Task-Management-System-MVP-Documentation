import { useState, useEffect } from "react";
import { useParams, Link } from "react-router-dom";

const API_URL = "http://localhost:5000";

function TaskPage() {

    const { id } = useParams();

    const token = localStorage.getItem("token");

    const headers = {
        Authorization: `Bearer ${token}`
    };

    const [task, setTask] = useState(null);
    const [comments, setComments] = useState([]);
    const [commentText, setCommentText] = useState("");

    useEffect(() => {
        loadTask();
        loadComments();
    }, []);

    async function loadTask() {

        const response = await fetch(
            `${API_URL}/tasks/${id}`,
            { headers }
        );

        const data = await response.json();

        setTask(data);
    }

    async function loadComments() {

        const response = await fetch(
            `${API_URL}/comments?task_id=${id}`,
            { headers }
        );

        const data = await response.json();

        setComments(data);
    }

    function getNextStatus(currentStatus) {

        if (currentStatus === "Todo") {
            return "In Progress";
        }

        if (currentStatus === "In Progress") {
            return "Review";
        }

        if (currentStatus === "Review") {
            return "Done";
        }

        return null;
    }

    async function moveTask() {

        const nextStatus = getNextStatus(task.status);

        await fetch(
            `${API_URL}/tasks/${id}`,
            {
                method: "PUT",
                headers: {
                    ...headers,
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    status: nextStatus
                })
            }
        );

        loadTask();
    }

    async function addComment() {

        if (commentText === "") {
            return;
        }

        await fetch(
            `${API_URL}/comments`,
            {
                method: "POST",
                headers: {
                    ...headers,
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    task_id: Number(id),
                    comment: commentText
                })
            }
        );

        setCommentText("");

        loadComments();
    }

    if (task === null) {
        return (
            <div className="page">
                <p>Loading...</p>
            </div>
        );
    }

    return (
        <div className="page">

            <nav className="navbar">

                <Link to={`/project/${task.project_id}`}>
                    Back to Project
                </Link>

                <h2>{task.title}</h2>

            </nav>

            <div className="task-detail-card">

                <h3>Task Details</h3>

                <p>
                    <strong>Status:</strong>
                    {" "}
                    {task.status}
                </p>

                {task.status !== "Done" && (
                    <button
                        className="btn"
                        onClick={moveTask}
                    >
                        Move To {getNextStatus(task.status)}
                    </button>
                )}

                <p>
                    <strong>Priority:</strong>
                    {" "}
                    {task.priority}
                </p>

                <p>
                    <strong>Assigned To:</strong>
                    {" "}
                    {task.assignee_name || "Unassigned"}
                </p>

                <p>
                    <strong>Created By:</strong>
                    {" "}
                    {task.creator_name}
                </p>

                {task.description && (
                    <p>
                        <strong>Description:</strong>
                        {" "}
                        {task.description}
                    </p>
                )}

            </div>

            <div className="card">

                <h3>Comments</h3>

                <div className="row">

                    <input
                        type="text"
                        placeholder="Write a comment..."
                        value={commentText}
                        onChange={(e) =>
                            setCommentText(
                                e.target.value
                            )
                        }
                    />

                    <button
                        className="btn"
                        onClick={addComment}
                    >
                        Post
                    </button>

                </div>

                {comments.length > 0 ? (

                    comments.map(comment => (
                        <p
                            key={comment.id}
                            className="comment"
                        >
                            <strong>
                                {comment.username}
                            </strong>

                            : {comment.comment}
                        </p>
                    ))

                ) : (

                    <p>No comments yet.</p>

                )}

            </div>

        </div>
    );
}

export default TaskPage;