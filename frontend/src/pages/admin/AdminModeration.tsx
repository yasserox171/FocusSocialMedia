import { useEffect, useState } from "react";
import { api } from "../../api";
import PostCard from "../../components/PostCard";
import { timeAgo } from "../../components/timeago";
import type { Message, Paginated, Post } from "../../types";

export function AdminPosts() {
  const [posts, setPosts] = useState<Post[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api
      .get<Paginated<Post>>("/admin/posts/")
      .then((d) => setPosts(d.results))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="spinner" />;

  return (
    <>
      <p style={{ color: "var(--muted)", fontSize: 14 }}>
        كل المنشورات (بما فيها المحجوبة عنك بالبلوك). احذف أي محتوى مخالف.
      </p>
      {posts.map((p) => (
        <PostCard
          key={p.id}
          post={p}
          onDeleted={(id) => setPosts((prev) => prev.filter((x) => x.id !== id))}
        />
      ))}
    </>
  );
}

interface AdminMessage extends Message {
  sender_name: string;
}

export function AdminMessages() {
  const [messages, setMessages] = useState<AdminMessage[]>([]);
  const [loading, setLoading] = useState(true);

  const load = () =>
    api
      .get<Paginated<AdminMessage>>("/admin/messages/")
      .then((d) => setMessages(d.results))
      .finally(() => setLoading(false));

  useEffect(() => {
    load();
  }, []);

  const remove = async (id: number) => {
    if (!confirm("حذف هذه الرسالة؟")) return;
    await api.delete(`/admin/messages/${id}/`);
    setMessages((prev) => prev.filter((m) => m.id !== id));
  };

  if (loading) return <div className="spinner" />;

  return (
    <div className="card">
      <p style={{ color: "var(--muted)", fontSize: 14, marginTop: 0 }}>
        آخر الرسائل على المنصة — للمراقبة وحذف المحتوى المخالف فقط.
      </p>
      <table className="data">
        <thead>
          <tr><th>المرسل</th><th>النص</th><th>الوقت</th><th></th></tr>
        </thead>
        <tbody>
          {messages.map((m) => (
            <tr key={m.id}>
              <td>{m.sender_name}</td>
              <td>{m.text.slice(0, 80)}</td>
              <td>{timeAgo(m.created_at)}</td>
              <td>
                <button className="icon-btn danger" onClick={() => remove(m.id)}>
                  حذف
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
