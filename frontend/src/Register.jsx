import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";

function Register() {
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const navigate = useNavigate();

  async function register() {
    const response = await fetch("http://localhost:5000/register", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, email, password }),
    });
    const data = await response.json();
    alert(data.message);
    navigate("/");
  }

  return (
    <div style={{ padding: "2rem" }}>
      <h1>Register</h1>
      <input placeholder="Username" value={username} onChange={(e) => setUsername(e.target.value)} />
      <br />
      <input placeholder="Email" value={email} onChange={(e) => setEmail(e.target.value)} />
      <br />
      <input placeholder="Password" type="password" value={password} onChange={(e) => setPassword(e.target.value)} />
      <br />
      <button onClick={register}>Register</button>
      <p>
        <Link to="/">Already have an account? Login</Link>
      </p>
    </div>
  );
}

export default Register;
