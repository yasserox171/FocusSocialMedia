import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../api";
import Avatar from "../components/Avatar";
import { timeAgo } from "../components/timeago";
import type { Notification, Paginated } from "../types";

function targetOf(n: Notification): string {
  if (n.kind === "message" && n.conversation_id) return `/messages/${n.conversation_id}`;
  return "/";
}

export default function Notifications() {
  const [items, setItems] = useState<Notification[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api
      .get<Paginated<Notification>>("/notifications/")
      .then((d) => setItems(d.results))
      .finally(() => setLoading(false));
    api.post("/notifications/read-all/").catch(() => {});
  }, []);

  if (loading) return <div className="spinner" />;

  return (
    <div className="card">
      <h2 className="section-title">الإشعارات</h2>
      {items.length === 0 && (
        <div className="empty">
          <span className="icon">🔔</span>
          لا إشعارات بعد.
        </div>
      )}
      {items.map((n) => (
        <Link className={`notif-item ${n.is_read ? "" : "unread"}`} to={targetOf(n)} key={n.id}>
          <Avatar name={n.actor.display_name} src={n.actor.avatar} size="sm" />
          <div style={{ flex: 1 }}>
            <div>{n.text}</div>
            <div className="notif-time">{timeAgo(n.created_at)}</div>
          </div>
          <span>
            {n.kind === "like" ? "❤️" : n.kind === "message" ? "💬" : "📰"}
          </span>
        </Link>
      ))}
    </div>
  );
}
