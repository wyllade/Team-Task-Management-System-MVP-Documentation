import { useState } from "react";
import { useNavigate } from "react-router-dom";

function Login() {

    const [isRegister, setIsRegister] = useState(false);

    const [username, setUsername] = useState("");
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");

    const navigate = useNavigate();

    async function handleSubmit() {

        // Choose the correct API endpoint
        let url;

        if (isRegister) {
            url = "http://localhost:5000/register";
        } else {
            url = "http://localhost:5000/login";
        }

        // Create request body
        let userData;

        if (isRegister) {
            userData = {
                username,
                email,
                password
            };
        } else {
            userData = {
                email,
                password
            };
        }

        // Send request to backend
        const response = await fetch(url, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(userData)
        });

        const data = await response.json();

        // Login successful
        if (data.token) {

            localStorage.setItem("token", data.token);

            localStorage.setItem(
                "user",
                JSON.stringify(data.user)
            );

            navigate("/dashboard");

        } else {

            alert(data.message);

        }
    }

    return (
        <div className="auth-page">

            <div className="auth-card">

                <h1>
                    {isRegister ? "Register" : "Login"}
                </h1>

                {isRegister && (
                    <input
                        type="text"
                        placeholder="Username"
                        value={username}
                        onChange={(e) =>
                            setUsername(e.target.value)
                        }
                    />
                )}

                <input
                    type="email"
                    placeholder="Email"
                    value={email}
                    onChange={(e) =>
                        setEmail(e.target.value)
                    }
                />

                <input
                    type="password"
                    placeholder="Password"
                    value={password}
                    onChange={(e) =>
                        setPassword(e.target.value)
                    }
                />

                <button
                    className="btn"
                    onClick={handleSubmit}
                >
                    {isRegister ? "Register" : "Login"}
                </button>

                <p
                    className="toggle"
                    onClick={() =>
                        setIsRegister(!isRegister)
                    }
                >
                    {isRegister
                        ? "Already have an account? Login"
                        : "Create an account"}
                </p>

            </div>

        </div>
    );
}

export default Login;