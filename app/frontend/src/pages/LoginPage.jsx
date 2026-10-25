import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../auth.jsx";

export default function LoginPage() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  async function submit(e) {
    e.preventDefault();
    setError("");
    setBusy(true);
    try {
      const me = await login(username, password);
      navigate(me.role === "admin" ? "/admin/products" : "/shop");
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <section className="card narrow">
      <h1 id="page-title">Log in</h1>
      <form id="login-form" onSubmit={submit}>
        <label htmlFor="username">Username</label>
        <input id="username" name="username" autoComplete="username"
               value={username} onChange={(e) => setUsername(e.target.value)} />
        <label htmlFor="password">Password</label>
        <input id="password" name="password" type="password" autoComplete="current-password"
               value={password} onChange={(e) => setPassword(e.target.value)} />
        {error && <p id="login-error" className="error" role="alert">{error}</p>}
        <button id="login-button" type="submit" disabled={busy}>Log in</button>
      </form>
      <p className="hint" id="demo-accounts">
        Demo accounts: <code>admin / admin123</code>, <code>user / user123</code>, <code>user2 / user123</code>
      </p>
    </section>
  );
}
