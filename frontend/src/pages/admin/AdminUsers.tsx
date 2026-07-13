import { FormEvent, useEffect, useState } from "react";
import { api } from "../../api";
import type { Paginated, User } from "../../types";

interface AdminUser extends User {
  is_staff: boolean;
}

export default function AdminUsers() {
  const [users, setUsers] = useState<AdminUser[]>([]);
  const [editing, setEditing] = useState<AdminUser | "new" | null>(null);
  const [loading, setLoading] = useState(true);

  const load = () => {
    api
      .get<Paginated<AdminUser>>("/admin/users/?page=1")
      .then(async (first) => {
        const all = [...first.results];
        let page = 2;
        let next = first.next;
        while (next) {
          const d = await api.get<Paginated<AdminUser>>(`/admin/users/?page=${page}`);
          all.push(...d.results);
          next = d.next;
          page += 1;
        }
        setUsers(all);
      })
      .finally(() => setLoading(false));
  };

  useEffect(load, []);

  const toggleActive = async (u: AdminUser) => {
    await api.patch(`/admin/users/${u.id}/`, { is_active: !u.is_active });
    setUsers((prev) =>
      prev.map((x) => (x.id === u.id ? { ...x, is_active: !u.is_active } : x))
    );
  };

  const remove = async (u: AdminUser) => {
    if (!confirm(`حذف حساب ${u.display_name} نهائياً؟ ستُحذف كل منشوراته ورسائله.`)) return;
    await api.delete(`/admin/users/${u.id}/`);
    setUsers((prev) => prev.filter((x) => x.id !== u.id));
  };

  if (loading) return <div className="spinner" />;

  return (
    <div className="card">
      <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 12 }}>
        <h3 style={{ margin: 0 }}>الحسابات ({users.length})</h3>
        <button className="btn sm" onClick={() => setEditing("new")}>
          + حساب جديد
        </button>
      </div>
      <div style={{ overflowX: "auto" }}>
        <table className="data">
          <thead>
            <tr>
              <th>الاسم</th>
              <th>المستخدم</th>
              <th>النوع</th>
              <th>الحالة</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            {users.map((u) => (
              <tr key={u.id}>
                <td>{u.display_name}</td>
                <td dir="ltr">{u.username}</td>
                <td>
                  {u.kind === "human" ? "عضو" : u.kind === "agent" ? "وكيل" : "المركز"}
                  {u.is_staff ? " · مشرف" : ""}
                </td>
                <td>
                  <span className={`pill ${u.is_active ? "on" : "off"}`}>
                    {u.is_active ? "نشط" : "معطل"}
                  </span>
                </td>
                <td style={{ whiteSpace: "nowrap" }}>
                  <button className="icon-btn" onClick={() => setEditing(u)}>تعديل</button>
                  <button className="icon-btn" onClick={() => toggleActive(u)}>
                    {u.is_active ? "تعطيل" : "تفعيل"}
                  </button>
                  <button className="icon-btn danger" onClick={() => remove(u)}>حذف</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {editing && (
        <UserModal
          user={editing === "new" ? null : editing}
          onClose={() => setEditing(null)}
          onSaved={() => {
            setEditing(null);
            load();
          }}
        />
      )}
    </div>
  );
}

function UserModal({
  user,
  onClose,
  onSaved,
}: {
  user: AdminUser | null;
  onClose: () => void;
  onSaved: () => void;
}) {
  const [username, setUsername] = useState(user?.username ?? "");
  const [displayName, setDisplayName] = useState(user?.display_name ?? "");
  const [bio, setBio] = useState(user?.bio ?? "");
  const [password, setPassword] = useState("");
  const [isStaff, setIsStaff] = useState(user?.is_staff ?? false);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  const submit = async (e: FormEvent) => {
    e.preventDefault();
    setBusy(true);
    setError("");
    const body: Record<string, unknown> = {
      username,
      display_name: displayName,
      bio,
      is_staff: isStaff,
    };
    if (password) body.password = password;
    try {
      if (user) await api.patch(`/admin/users/${user.id}/`, body);
      else await api.post("/admin/users/", body);
      onSaved();
    } catch (err) {
      setError(err instanceof Error ? err.message : "خطأ");
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <form className="card modal" onClick={(e) => e.stopPropagation()} onSubmit={submit}>
        <h3 style={{ marginTop: 0 }}>{user ? "تعديل حساب" : "حساب جديد"}</h3>
        {error && <div className="error-box">{error}</div>}
        <div className="field">
          <label>اسم المستخدم</label>
          <input dir="ltr" value={username} onChange={(e) => setUsername(e.target.value)} required />
        </div>
        <div className="field">
          <label>الاسم الكامل</label>
          <input value={displayName} onChange={(e) => setDisplayName(e.target.value)} required />
        </div>
        <div className="field">
          <label>الوصف / المنصب</label>
          <input value={bio} onChange={(e) => setBio(e.target.value)} />
        </div>
        <div className="field">
          <label>{user ? "كلمة مرور جديدة (اختياري)" : "كلمة المرور"}</label>
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required={!user}
          />
        </div>
        <label style={{ display: "flex", gap: 8, alignItems: "center", marginBottom: 14 }}>
          <input
            type="checkbox"
            style={{ width: "auto" }}
            checked={isStaff}
            onChange={(e) => setIsStaff(e.target.checked)}
          />
          صلاحيات مشرف
        </label>
        <div style={{ display: "flex", gap: 8, justifyContent: "flex-end" }}>
          <button type="button" className="btn ghost" onClick={onClose}>إلغاء</button>
          <button className="btn" disabled={busy}>حفظ</button>
        </div>
      </form>
    </div>
  );
}
