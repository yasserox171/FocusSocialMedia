import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../api";
import { useAuth } from "../auth";
import Avatar from "../components/Avatar";
import type { Paginated, User } from "../types";

export default function People() {
  const { user: me } = useAuth();
  const [people, setPeople] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    (async () => {
      // Directory is small (invite-only platform) — walk all pages.
      const all: User[] = [];
      let page = 1;
      for (;;) {
        const data = await api.get<Paginated<User>>(`/users/?page=${page}`);
        all.push(...data.results);
        if (!data.next) break;
        page += 1;
      }
      setPeople(all);
      setLoading(false);
    })().catch(() => setLoading(false));
  }, []);

  if (loading) return <div className="spinner" />;

  return (
    <div className="card">
      <h2 className="section-title">أعضاء المنصة</h2>
      {people.map((p) => (
        <div className="person-row" key={p.id}>
          <Link to={`/profile/${p.id}`}>
            <Avatar name={p.display_name} src={p.avatar} />
          </Link>
          <div className="pr-body">
            <Link to={`/profile/${p.id}`} style={{ color: "inherit", fontWeight: 600 }}>
              {p.display_name}
              {p.kind === "agent" && <span className="kind-chip agent">وكيل ذكي</span>}
              {p.kind === "center" && <span className="kind-chip center">رسمي</span>}
            </Link>
            <div className="pr-bio">{p.bio}</div>
          </div>
          {p.id !== me?.id && (
            <Link className="btn ghost sm" to={`/profile/${p.id}`}>
              الملف
            </Link>
          )}
        </div>
      ))}
    </div>
  );
}
