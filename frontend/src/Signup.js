import React, { useState } from "react";

function Signup({ onSignupSuccess }) {
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [message, setMessage] = useState("");

  const handleSignup = async (e) => {
    e.preventDefault();
    setMessage("");

    // --- Client-side validation ---
    if (!name || !email || !password) {
      setMessage("Name, Email & Password are required");
      return;
    }
    if (password.length < 6) {
      setMessage("Password must be at least 6 characters long");
      return;
    }

    try {
      const res = await fetch("http://127.0.0.1:8000/auth/signup", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name, email, password }),
      });

      const data = await res.json();

      if (!res.ok) {
        // Handle FastAPI / Pydantic validation errors
        if (Array.isArray(data.detail)) {
          const errors = data.detail
            .map((err) => {
              const field = err.loc ? err.loc[err.loc.length - 1] : "input";
              return `${field}: ${err.msg || "Invalid input"}`;
            })
            .join(", ");
          throw new Error(errors);
        } else if (data.detail) {
          throw new Error(
            typeof data.detail === "string"
              ? data.detail
              : JSON.stringify(data.detail)
          );
        } else {
          throw new Error("Signup failed");
        }
      }

      // Success ðŸŽ‰
      localStorage.setItem("token", data.access_token);
      setMessage("Signup successful âœ…");
      setName("");
      setEmail("");
      setPassword("");
      if (onSignupSuccess) onSignupSuccess();
    } catch (err) {
      setMessage(err.message);
    }
  };

  return (
    <div
      className="signup-container"
      style={{ padding: "20px", maxWidth: "400px", margin: "auto" }}
    >
      <h2>Signup</h2>
      <form onSubmit={handleSignup}>
        <div style={{ marginBottom: "10px" }}>
          <label>Name: </label>
          <input
            type="text"
            value={name}
            onChange={(e) => setName(e.target.value)}
            required
            style={{ width: "100%" }}
          />
        </div>
        <div style={{ marginBottom: "10px" }}>
          <label>Email: </label>
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            style={{ width: "100%" }}
          />
        </div>
        <div style={{ marginBottom: "10px" }}>
          <label>Password: </label>
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            style={{ width: "100%" }}
          />
        </div>
        <button type="submit">Signup</button>
      </form>

      {message && (
        <p style={{ color: message.includes("successful") ? "green" : "red" }}>
          {message}
        </p>
      )}
    </div>
  );
}

export default Signup;

