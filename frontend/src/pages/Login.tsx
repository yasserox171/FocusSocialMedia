import { FormEvent, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../auth";

export default function Login() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  const submit = async (e: FormEvent) => {
    e.preventDefault();
    setBusy(true);
    setError("");
    try {
      await login(username, password);
      navigate("/");
    } catch {
      setError("بيانات الدخول غير صحيحة.");
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="auth-wrap">
      <form className="card auth-card" onSubmit={submit}>
        <h1>
          فوكس<span style={{ color: "var(--amber)" }}>.</span>سوشيال
        </h1>
        <p className="sub">المنصة الداخلية لأعضاء ومنخرطي جمعية فوكس — آسفي</p>
        {error && <div className="error-box">{error}</div>}
        <div className="field">
          <label>اسم المستخدم</label>
          <input
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            autoComplete="username"
            required
          />
        </div>
        <div className="field">
          <label>كلمة المرور</label>
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            autoComplete="current-password"
            required
          />
        </div>
        <button className="btn" style={{ width: "100%" }} disabled={busy}>
          {busy ? "جارٍ الدخول…" : "دخول"}
        </button>
        <p className="sub" style={{ marginTop: 16, marginBottom: 0 }}>
          الانضمام بدعوة من الإدارة فقط. توصلت بدعوة؟ افتح رابطها مباشرة.
        </p>
      </form>
    </div>
  );
}
