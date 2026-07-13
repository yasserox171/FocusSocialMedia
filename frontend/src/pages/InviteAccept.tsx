import { FormEvent, useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { api } from "../api";

export default function InviteAccept() {
  const { token } = useParams();
  const navigate = useNavigate();
  const [inviteName, setInviteName] = useState<string | null>(null);
  const [invalid, setInvalid] = useState(false);
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    api
      .get<{ display_name: string }>(`/auth/invite/${token}/`)
      .then((r) => setInviteName(r.display_name))
      .catch(() => setInvalid(true));
  }, [token]);

  const submit = async (e: FormEvent) => {
    e.preventDefault();
    setBusy(true);
    setError("");
    try {
      await api.post("/auth/invite/accept/", { token, username, password });
      navigate("/login");
    } catch (err) {
      setError(err instanceof Error ? err.message : "تعذر إنشاء الحساب.");
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="auth-wrap">
      <form className="card auth-card" onSubmit={submit}>
        <h1>مرحباً بك 👋</h1>
        {invalid ? (
          <div className="error-box">هذه الدعوة غير صالحة أو استُعملت من قبل.</div>
        ) : (
          <>
            <p className="sub">
              دعوة باسم: <strong>{inviteName ?? "…"}</strong> — أكمل إنشاء حسابك.
            </p>
            {error && <div className="error-box">{error}</div>}
            <div className="field">
              <label>اسم المستخدم</label>
              <input
                dir="ltr"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                required
              />
            </div>
            <div className="field">
              <label>كلمة المرور (8 أحرف على الأقل)</label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                minLength={8}
                required
              />
            </div>
            <button className="btn" style={{ width: "100%" }} disabled={busy}>
              أنشئ الحساب
            </button>
          </>
        )}
      </form>
    </div>
  );
}
