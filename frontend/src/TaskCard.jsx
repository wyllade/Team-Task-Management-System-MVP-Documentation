function TaskCard({ task, onStatusChange, onDelete }) {
  return (
    <div style={{ border: "1px solid #ccc", padding: "0.5rem", margin: "0.5rem 0", background: "#f9f9f9" }}>
      <h4>{task.title}</h4>
      <p>Priority: {task.priority}</p>
      <p>Status: {task.status}</p>
      {task.description && <p>{task.description}</p>}
      {onStatusChange && task.status === "Todo" && (
        <button onClick={() => onStatusChange(task.id, "In Progress")}>Start Task</button>
      )}
      {onStatusChange && task.status === "In Progress" && (
        <button onClick={() => onStatusChange(task.id, "Review")}>Send to Review</button>
      )}
      {onStatusChange && task.status === "Review" && (
        <button onClick={() => onStatusChange(task.id, "Done")}>Mark Done</button>
      )}
      {onDelete && (
        <button onClick={() => onDelete(task.id)} style={{ marginLeft: "0.5rem" }}>Delete</button>
      )}
    </div>
  );
}

export default TaskCard;
