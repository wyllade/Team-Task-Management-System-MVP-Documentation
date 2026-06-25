import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter, Routes, Route, Navigate, useLocation } from "react-router-dom";
import Login from "./Login";
import Dashboard from "./Dashboard";
import ProjectPage from "./ProjectPage";
import TaskPage from "./TaskPage";
import "./App.css";

function App() {
  useLocation();
  const token = localStorage.getItem("token");
  return (
    <Routes>
      <Route path="/" element={token ? <Navigate to="/dashboard" /> : <Login />} />
      <Route path="/dashboard" element={token ? <Dashboard /> : <Navigate to="/" />} />
      <Route path="/project/:id" element={token ? <ProjectPage /> : <Navigate to="/" />} />
      <Route path="/task/:id" element={token ? <TaskPage /> : <Navigate to="/" />} />
    </Routes>
  );
}

ReactDOM.createRoot(document.getElementById("root")).render(
  <BrowserRouter><App /></BrowserRouter>
);
