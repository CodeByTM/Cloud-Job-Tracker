import { useState } from "react";
import { confirmSignUp, signIn, signUp } from "../services/auth";

function AuthForm({ onAuthSuccess }) {
  const [mode, setMode] = useState("signin");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [code, setCode] = useState("");
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  async function handleSubmit(event) {
    event.preventDefault();
    setError("");
    setMessage("");

    try {
      if (mode === "signup") {
        await signUp(email, password);
        setMessage("Account created. Enter the code sent to your email.");
        setMode("confirm");
        return;
      }

      if (mode === "confirm") {
        await confirmSignUp(email, code);
        setMessage("Account confirmed. You can now sign in.");
        setMode("signin");
        return;
      }

      await signIn(email, password);
      onAuthSuccess();
    } catch (err) {
      setError(err.message || "Authentication failed");
    }
  }

  return (
    <div className="auth-wrapper">
      <form className="job-form" onSubmit={handleSubmit}>
        <h2>
          {mode === "signup"
            ? "Sign Up"
            : mode === "confirm"
            ? "Confirm Account"
            : "Sign In"}
        </h2>

        <input
          type="email"
          placeholder="Email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
        />

        {mode !== "confirm" && (
          <input
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
        )}

        {mode === "confirm" && (
          <input
            type="text"
            placeholder="Confirmation Code"
            value={code}
            onChange={(e) => setCode(e.target.value)}
            required
          />
        )}

        <button type="submit">
          {mode === "signup"
            ? "Create Account"
            : mode === "confirm"
            ? "Confirm Account"
            : "Sign In"}
        </button>

        {mode === "signin" && (
  <>
    <button type="button" onClick={() => setMode("signup")}>
      Switch to Sign Up
    </button>
    <button type="button" onClick={() => setMode("confirm")}>
      Enter Confirmation Code
    </button>
  </>
)}

        {mode === "signup" && (
          <button type="button" onClick={() => setMode("signin")}>
            Switch to Sign In
          </button>
        )}

        {mode === "confirm" && (
          <button type="button" onClick={() => setMode("signin")}>
            Back to Sign In
          </button>
        )}

        {message && <p>{message}</p>}
        {error && <p className="error">{error}</p>}
      </form>
    </div>
  );
}

export default AuthForm;