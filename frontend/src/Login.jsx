import { useState } from "react";
import { useNavigate } from "react-router-dom";

function Login() {
  const [isRegister, setIsRegister] = useState(false);
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const navigate = useNavigate();

  // Handles form submission for both login and register
  const handleSubmit = async (e) => {
    e.preventDefault(); // prevents page refresh

    // Change endpoint based on mode
    const url = isRegister 
      ? "http://localhost:5000/register" 
      : "http://localhost:5000/login";

    // Set up the body data (backend will just ignore username if it's login)
    const userData = { username, email, password };

    try {
      const response = await fetch(url, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(userData),
      });

      const data = await response.json();

      if (data.token) {
        // Save user data to local storage and go to dashboard
        localStorage.setItem("token", data.token);
        localStorage.setItem("user", JSON.stringify(data.user));
        navigate("/dashboard");
      } else {
        alert(data.message || "Something went wrong");
      }
    } catch (error) {
      console.error("Auth error:", error);
      alert("Failed to connect to server");
    }
  };

  return (
    <div className="auth-page">
      <form className="auth-card" onSubmit={handleSubmit}>
        <h1>{isRegister ? "Register" : "Login"}</h1>

        {isRegister && (
          <input
            type="text"
            placeholder="Username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            required
          />
        )}

        <input
          type="email"
          placeholder="Email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
        />

        <input
          type="password"
          placeholder="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
        />

        <button type="submit" className="btn">
          {isRegister ? "Register" : "Login"}
        </button>

        <p className="toggle" onClick={() => setIsRegister(!isRegister)} style={{ cursor: "pointer" }}>
          {isRegister ? "Already have an account? Login" : "Create an account"}
        </p>
      </form>
    </div>
  );
}

export default Login;