import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import Login from "./Login";
import Dashboard from "./Dashboard";
import ProjectPage from "./ProjectPage";
import TaskPage from "./TaskPage";
import "./App.css";

function App() {
  const token = localStorage.getItem("token");
  const isLoggedIn = token !== null;

  if (!isLoggedIn) {
    return <Login />;
  }

  return (
    <Routes>
      <Route path="/" element={<Navigate to="/dashboard" />} />
      <Route path="/dashboard" element={<Dashboard />} />
      <Route path="/project/:id" element={<ProjectPage />} />
      <Route path="/task/:id" element={<TaskPage />} />
    </Routes>
  );
}

ReactDOM.createRoot(document.getElementById("root")).render(
  <BrowserRouter>
    <App />
  </BrowserRouter>
);