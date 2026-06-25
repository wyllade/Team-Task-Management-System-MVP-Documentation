import { useState, useEffect } from "react";
import { useParams, Link } from "react-router-dom";

const API_URL = "http://localhost:5000";

function ProjectPage() {

    const { id } = useParams();

    const token = localStorage.getItem("token");

    const user = JSON.parse(
        localStorage.getItem("user") || "{}"
    );

    const headers = {
        Authorization: `Bearer ${token}`
    };

    const [tasks, setTasks] = useState([]);
    const [members, setMembers] = useState([]);
    const [users, setUsers] = useState([]);

    const [taskTitle, setTaskTitle] = useState("");
    const [taskDescription, setTaskDescription] = useState("");
    const [priority, setPriority] = useState("Medium");
    const [assigneeId, setAssigneeId] = useState("");

    const [newMemberId, setNewMemberId] = useState("");

    const [isAdmin, setIsAdmin] = useState(false);

    useEffect(() => {
        loadProjectData();
    }, []);

    async function loadProjectData() {
        await loadMembers();
        await loadUsers();
        await loadTasks();
    }

    async function loadMembers() {

        const response = await fetch(
            `${API_URL}/projects/${id}/members`,
            { headers }
        );

        const data = await response.json();

        setMembers(data);

        const currentMember = data.find(
            member => member.user_id === user.id
        );

        if (
            currentMember &&
            currentMember.role === "admin"
        ) {
            setIsAdmin(true);
        }
    }

    async function loadUsers() {

        const response = await fetch(
            `${API_URL}/users`,
            { headers }
        );

        const data = await response.json();

        setUsers(data);
    }

    async function loadTasks() {

        const response = await fetch(
            `${API_URL}/tasks?project_id=${id}`,
            { headers }
        );

        const data = await response.json();

        setTasks(data);
    }

    async function addTask() {

        const newTask = {
            title: taskTitle,
            description: taskDescription,
            priority: priority,
            project_id: Number(id)
        };

        if (assigneeId) {
            newTask.assignee_id = Number(assigneeId);
        }

        await fetch(`${API_URL}/tasks`, {
            method: "POST",
            headers: {
                ...headers,
                "Content-Type": "application/json"
            },
            body: JSON.stringify(newTask)
        });

        setTaskTitle("");
        setTaskDescription("");
        setPriority("Medium");
        setAssigneeId("");

        loadTasks();
    }

    async function updateTaskStatus(taskId, newStatus) {

        await fetch(
            `${API_URL}/tasks/${taskId}`,
            {
                method: "PUT",
                headers: {
                    ...headers,
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    status: newStatus
                })
            }
        );

        loadTasks();
    }

    async function deleteTask(taskId) {

        await fetch(
            `${API_URL}/tasks/${taskId}`,
            {
                method: "DELETE",
                headers
            }
        );

        loadTasks();
    }

    async function addMember() {

        if (!newMemberId) {
            return;
        }

        await fetch(
            `${API_URL}/projects/${id}/members`,
            {
                method: "POST",
                headers: {
                    ...headers,
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    user_id: Number(newMemberId)
                })
            }
        );

        setNewMemberId("");

        loadMembers();
    }

    async function removeMember(memberId) {

        await fetch(
            `${API_URL}/projects/${id}/members/${memberId}`,
            {
                method: "DELETE",
                headers
            }
        );

        loadMembers();
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

    const memberIds = members.map(member => member.user_id);

    const availableUsers = users.filter(user => {
        return !memberIds.includes(user.id);
    });

    const columns = [
        "Todo",
        "In Progress",
        "Review",
        "Done"
    ];

    return (
        <div className="page">

            <nav className="navbar">
                <Link to="/dashboard">
                    ← Back
                </Link>

                <h2>
                    Project #{id}
                </h2>
            </nav>

            {isAdmin && (
                <div className="card">

                    <h3>Members</h3>

                    {members.map(member => (
                        <div
                            key={member.user_id}
                        >
                            {member.username}
                            ({member.role})

                            {member.role !== "admin" && (
                                <button
                                    className="btn danger"
                                    onClick={() =>
                                        removeMember(
                                            member.user_id
                                        )
                                    }
                                >
                                    Remove
                                </button>
                            )}
                        </div>
                    ))}

                    <br />

                    <select
                        value={newMemberId}
                        onChange={(e) =>
                            setNewMemberId(
                                e.target.value
                            )
                        }
                    >
                        <option value="">
                            Add Member
                        </option>

                        {availableUsers.map(user => (
                            <option
                                key={user.id}
                                value={user.id}
                            >
                                {user.username}
                            </option>
                        ))}
                    </select>

                    <button
                        className="btn"
                        onClick={addMember}
                    >
                        Add
                    </button>

                </div>
            )}

            <div className="card">

                <h3>Create Task</h3>

                <input
                    placeholder="Task Title"
                    value={taskTitle}
                    onChange={(e) =>
                        setTaskTitle(
                            e.target.value
                        )
                    }
                />

                <input
                    placeholder="Description"
                    value={taskDescription}
                    onChange={(e) =>
                        setTaskDescription(
                            e.target.value
                        )
                    }
                />

                <select
                    value={priority}
                    onChange={(e) =>
                        setPriority(
                            e.target.value
                        )
                    }
                >
                    <option>Low</option>
                    <option>Medium</option>
                    <option>High</option>
                    <option>Critical</option>
                </select>

                <select
                    value={assigneeId}
                    onChange={(e) =>
                        setAssigneeId(
                            e.target.value
                        )
                    }
                >
                    <option value="">
                        Assign User
                    </option>

                    {members.map(member => (
                        <option
                            key={member.user_id}
                            value={member.user_id}
                        >
                            {member.username}
                        </option>
                    ))}
                </select>

                <button
                    className="btn"
                    onClick={addTask}
                >
                    Create Task
                </button>

            </div>

            <div className="kanban">

                {columns.map(status => (

                    <div
                        key={status}
                        className="column"
                    >

                        <h3>{status}</h3>

                        {tasks
                            .filter(
                                task =>
                                    task.status === status
                            )
                            .map(task => (

                                <div
                                    key={task.id}
                                    className="task"
                                >

                                    <h4>
                                        {task.title}
                                    </h4>

                                    <p>
                                        {task.description}
                                    </p>

                                    <p>
                                        Priority:
                                        {task.priority}
                                    </p>

                                    {task.assignee_name && (
                                        <p>
                                            Assigned:
                                            {
                                                task.assignee_name
                                            }
                                        </p>
                                    )}

                                    {status !== "Done" && (
                                        <button
                                            className="btn"
                                            onClick={() =>
                                                updateTaskStatus(
                                                    task.id,
                                                    getNextStatus(
                                                        task.status
                                                    )
                                                )
                                            }
                                        >
                                            Move
                                        </button>
                                    )}

                                    {isAdmin && (
                                        <button
                                            className="btn danger"
                                            onClick={() =>
                                                deleteTask(
                                                    task.id
                                                )
                                            }
                                        >
                                            Delete
                                        </button>
                                    )}

                                </div>

                            ))}
                    </div>

                ))}

            </div>

        </div>
    );
}

export default ProjectPage;