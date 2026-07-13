import { FormEvent, useEffect, useState } from "react";
import { api } from "../../api";
import type { Invite, Paginated } from "../../types";
import { timeAgo } from "../../components/timeago";

export default function AdminInvites() {
  const [invites, setInvites] = useState<Invite[]>([]);
  const [name, setName] = useState("");
  const [note, setNote] = useState("");
  const [copied, setCopied] = useState<number | null>(null);

  const load = () =>
    api.get<Paginated<Invite>>("/admin/invites/").then((d) => setInvites(d.results));

  useEffect(() => {
    load();
  }, []);

  const create = async (e: FormEvent) => {
    e.preventDefault();
    if (!name.trim()) return;
    await api.post("/admin/invites/", { display_name: name.trim(), note });
    setName("");
    setNote("");
    load();
  };

  const copyLink = (invite: Invite) => {
    navigator.clipboard.writeText(`${location.origin}/invite/${invite.token}`);
    setCopied(invite.id);
    setTimeout(() => setCopied(null), 1500);
  };

  const remove = async (invite: Invite) => {
    await api.delete(`/admin/invites/${invite.id}/`);
    load();
  };

  return (
    <>
      <form className="card" onSubmit={create}>
        <h3 style={{ marginTop: 0 }}>دعوة عضو جديد</h3>
        <div className="field">
          <label>اسم العضو الكامل</label>
          <input value={name} onChange={(e) => setName(e.target.value)} required />
        </div>
        <div className="field">
          <label>ملاحظة (اختياري)</label>
          <input value={note} onChange={(e) => setNote(e.target.value)} />
        </div>
        <button className="btn">أنشئ الدعوة</button>
      </form>

      <div className="card">
        <h3 style={{ marginTop: 0 }}>الدعوات</h3>
        <table className="data">
          <thead>
            <tr><th>الاسم</th><th>الحالة</th><th>التاريخ</th><th></th></tr>
          </thead>
          <tbody>
            {invites.map((inv) => (
              <tr key={inv.id}>
                <td>{inv.display_name}</td>
                <td>
                  <span className={`pill ${inv.used ? "on" : "off"}`}>
                    {inv.used ? "استُعملت" : "معلقة"}
                  </span>
                </td>
                <td>{timeAgo(inv.created_at)}</td>
                <td style={{ whiteSpace: "nowrap" }}>
                  {!inv.used && (
                    <>
                      <button className="icon-btn" onClick={() => copyLink(inv)}>
                        {copied === inv.id ? "✓ نُسخ" : "نسخ الرابط"}
                      </button>
                      <button className="icon-btn danger" onClick={() => remove(inv)}>
                        حذف
                      </button>
                    </>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </>
  );
}
