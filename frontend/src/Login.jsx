import { useState } from "react";
import { useNavigate } from "react-router-dom";

function Login() {
  const [isRegister, setIsRegister] = useState(false);
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const navigate = useNavigate();

  async function submit() {
    const url = isRegister ? "http://localhost:5000/register" : "http://localhost:5000/login";
    const body = isRegister ? { username, email, password } : { email, password };
    const res = await fetch(url, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) });
    const data = await res.json();
    if (data.token) {
      localStorage.setItem("token", data.token);
      localStorage.setItem("user", JSON.stringify(data.user));
      navigate("/dashboard");
    } else {
      alert(data.message);
      if (isRegister) navigate("/");
    }
  }

  return (
    <div className="auth-page">
      <div className="auth-card">
        <h1>{isRegister ? "Register" : "Login"}</h1>
        {isRegister && <input placeholder="Username" value={username} onChange={e => setUsername(e.target.value)} />}
        <input placeholder="Email" value={email} onChange={e => setEmail(e.target.value)} />
        <input placeholder="Password" type="password" value={password} onChange={e => setPassword(e.target.value)} />
        <button className="btn" onClick={submit}>{isRegister ? "Register" : "Login"}</button>
        <p className="toggle" onClick={() => setIsRegister(!isRegister)}>
          {isRegister ? "Already have an account? Login" : "Create an account"}
        </p>
      </div>
    </div>
  );
}

export default Login;
