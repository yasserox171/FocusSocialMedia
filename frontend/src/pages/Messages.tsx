import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../api";
import Avatar from "../components/Avatar";
import { timeAgo } from "../components/timeago";
import type { Conversation } from "../types";

export default function Messages() {
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api
      .get<Conversation[]>("/conversations/")
      .then(setConversations)
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="spinner" />;

  return (
    <div className="card">
      <h2 className="section-title">الرسائل</h2>
      {conversations.length === 0 && (
        <div className="empty">
          <span className="icon">💬</span>
          لا محادثات بعد — افتح ملف أي عضو وابدأ المراسلة.
        </div>
      )}
      {conversations.map((c) => (
        <Link className="conv-item" to={`/messages/${c.id}`} key={c.id}>
          <Avatar name={c.other_user.display_name} src={c.other_user.avatar} />
          <div className="cv-body">
            <div className="cv-name">{c.other_user.display_name}</div>
            <div className="cv-last">
              {c.last_message ? c.last_message.text : "ابدأ المحادثة…"}
            </div>
          </div>
          <div style={{ textAlign: "center" }}>
            <div className="notif-time">{timeAgo(c.updated_at)}</div>
            {c.unread_count > 0 && (
              <div className="unread-dot">{c.unread_count}</div>
            )}
          </div>
        </Link>
      ))}
    </div>
  );
}
