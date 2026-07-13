import { useRef, useState } from "react";
import { api } from "../api";
import type { Post } from "../types";

export default function Composer({ onCreated }: { onCreated: (p: Post) => void }) {
  const [text, setText] = useState("");
  const [linkUrl, setLinkUrl] = useState("");
  const [showLink, setShowLink] = useState(false);
  const [file, setFile] = useState<File | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const fileInput = useRef<HTMLInputElement>(null);

  const canPost = !busy && (text.trim() || file || linkUrl.trim());

  const submit = async () => {
    if (!canPost) return;
    setBusy(true);
    setError("");
    const form = new FormData();
    if (text.trim()) form.append("text", text.trim());
    if (linkUrl.trim()) form.append("link_url", linkUrl.trim());
    if (file) {
      form.append(file.type.startsWith("video/") ? "video" : "image", file);
    }
    try {
      const post = await api.post<Post>("/posts/", form);
      setText("");
      setLinkUrl("");
      setShowLink(false);
      setFile(null);
      if (fileInput.current) fileInput.current.value = "";
      onCreated(post);
    } catch (e) {
      setError(e instanceof Error ? e.message : "تعذر النشر");
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="card composer">
      <textarea
        placeholder="شارك خبراً أو فكرة مع أعضاء فوكس…"
        value={text}
        onChange={(e) => setText(e.target.value)}
      />
      {showLink && (
        <input
          dir="ltr"
          placeholder="https://example.com/article"
          value={linkUrl}
          onChange={(e) => setLinkUrl(e.target.value)}
          style={{ marginTop: 8 }}
        />
      )}
      {error && <div className="error-box" style={{ marginTop: 8 }}>{error}</div>}
      <div className="composer-bar">
        <label className="attach-label">
          {file ? `📎 ${file.name.slice(0, 22)}` : "📷 صورة / فيديو"}
          <input
            ref={fileInput}
            type="file"
            accept="image/*,video/*"
            hidden
            onChange={(e) => setFile(e.target.files?.[0] ?? null)}
          />
        </label>
        <button className="attach-label" onClick={() => setShowLink(!showLink)}>
          🔗 رابط
        </button>
        <div className="spacer" />
        <button className="btn" disabled={!canPost} onClick={submit}>
          {busy ? "جارٍ النشر…" : "انشر"}
        </button>
      </div>
    </div>
  );
}
