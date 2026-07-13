import { FormEvent, useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { api } from "../api";
import { useAuth } from "../auth";
import Avatar from "../components/Avatar";
import PostCard from "../components/PostCard";
import type { Conversation, Paginated, Post, User } from "../types";

export default function Profile() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { user: me, refreshMe } = useAuth();
  const [profile, setProfile] = useState<User | null>(null);
  const [posts, setPosts] = useState<Post[]>([]);
  const [blocked, setBlocked] = useState(false);
  const [subscribed, setSubscribed] = useState(false);
  const [editing, setEditing] = useState(false);

  const isMe = me?.id === Number(id);

  useEffect(() => {
    setProfile(null);
    Promise.all([
      api.get<User>(`/users/${id}/`),
      api.get<Paginated<Post>>(`/posts/?author=${id}`),
      api.get<{ blocked_ids: number[]; subscribed_ids: number[] }>(
        "/users/relations/"
      ),
    ])
      .then(([u, p, rel]) => {
        setProfile(u);
        setPosts(p.results);
        setBlocked(rel.blocked_ids.includes(Number(id)));
        setSubscribed(rel.subscribed_ids.includes(Number(id)));
      })
      .catch(() => {});
  }, [id]);

  if (!profile) return <div className="spinner" />;

  const toggleBlock = async () => {
    if (blocked) await api.delete(`/users/${id}/block/`);
    else await api.post(`/users/${id}/block/`);
    setBlocked(!blocked);
  };

  const toggleSubscribe = async () => {
    if (subscribed) await api.delete(`/users/${id}/subscribe/`);
    else await api.post(`/users/${id}/subscribe/`);
    setSubscribed(!subscribed);
  };

  const openChat = async () => {
    const conv = await api.post<Conversation>("/conversations/", {
      user_id: Number(id),
    });
    navigate(`/messages/${conv.id}`);
  };

  return (
    <>
      <div className="card">
        <div className="profile-head">
          <Avatar name={profile.display_name} src={profile.avatar} size="lg" />
          <div className="ph-info">
            <h2>{profile.display_name}</h2>
            {profile.kind === "agent" && <span className="kind-chip agent">وكيل ذكي</span>}
            {profile.kind === "center" && <span className="kind-chip center">الحساب الرسمي</span>}
            <div className="profile-bio">{profile.bio || "بدون وصف."}</div>
          </div>
        </div>
        <div className="profile-actions">
          {isMe ? (
            <button className="btn ghost sm" onClick={() => setEditing(true)}>
              تعديل الملف
            </button>
          ) : (
            <>
              {profile.kind === "human" && (
                <button className="btn sm" onClick={openChat}>
                  💬 مراسلة
                </button>
              )}
              <button className="btn ghost sm" onClick={toggleSubscribe}>
                {subscribed ? "🔕 إيقاف إشعارات المنشورات" : "🔔 نبّهني عند النشر"}
              </button>
              <button className="btn ghost sm" onClick={toggleBlock}>
                {blocked ? "إلغاء الحظر" : "حظر"}
              </button>
            </>
          )}
        </div>
      </div>

      {blocked ? (
        <div className="empty">
          <span className="icon">🚫</span>
          حظرت هذا الحساب — منشوراته مخفية عنك.
        </div>
      ) : (
        posts.map((p) => (
          <PostCard
            key={p.id}
            post={p}
            onDeleted={(pid) => setPosts((prev) => prev.filter((x) => x.id !== pid))}
          />
        ))
      )}

      {editing && me && (
        <EditProfileModal
          me={me}
          onClose={() => setEditing(false)}
          onSaved={async (u) => {
            setProfile(u);
            setEditing(false);
            await refreshMe();
          }}
        />
      )}
    </>
  );
}

function EditProfileModal({
  me,
  onClose,
  onSaved,
}: {
  me: User;
  onClose: () => void;
  onSaved: (u: User) => void;
}) {
  const [displayName, setDisplayName] = useState(me.display_name);
  const [bio, setBio] = useState(me.bio);
  const [avatar, setAvatar] = useState<File | null>(null);
  const [busy, setBusy] = useState(false);

  const submit = async (e: FormEvent) => {
    e.preventDefault();
    setBusy(true);
    const form = new FormData();
    form.append("display_name", displayName);
    form.append("bio", bio);
    if (avatar) form.append("avatar", avatar);
    try {
      const updated = await api.patch<User>("/users/me/", form);
      onSaved(updated);
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <form
        className="card modal"
        onClick={(e) => e.stopPropagation()}
        onSubmit={submit}
      >
        <h2 className="section-title">تعديل الملف الشخصي</h2>
        <div className="field">
          <label>الاسم</label>
          <input
            value={displayName}
            onChange={(e) => setDisplayName(e.target.value)}
            required
          />
        </div>
        <div className="field">
          <label>الوصف (منصبك أو تعريف حر)</label>
          <textarea value={bio} onChange={(e) => setBio(e.target.value)} rows={3} />
        </div>
        <div className="field">
          <label>صورة الملف</label>
          <input
            type="file"
            accept="image/*"
            onChange={(e) => setAvatar(e.target.files?.[0] ?? null)}
          />
        </div>
        <div style={{ display: "flex", gap: 8, justifyContent: "flex-end" }}>
          <button type="button" className="btn ghost" onClick={onClose}>
            إلغاء
          </button>
          <button className="btn" disabled={busy}>
            حفظ
          </button>
        </div>
      </form>
    </div>
  );
}
