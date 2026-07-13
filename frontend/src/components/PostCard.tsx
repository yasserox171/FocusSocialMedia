import { useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../api";
import { useAuth } from "../auth";
import type { Post } from "../types";
import Avatar from "./Avatar";
import Lightbox from "./Lightbox";
import { Linkified, youtubeEmbedUrl } from "./linkify";
import PostVideo from "./PostVideo";
import { timeAgo } from "./timeago";

const KIND_LABEL: Record<string, string> = {
  agent: "وكيل ذكي",
  center: "رسمي",
};

export default function PostCard({
  post,
  onDeleted,
}: {
  post: Post;
  onDeleted?: (id: number) => void;
}) {
  const { user } = useAuth();
  const [liked, setLiked] = useState(post.liked_by_me);
  const [likes, setLikes] = useState(post.likes_count);
  const [justLiked, setJustLiked] = useState(false);
  const [lightboxOpen, setLightboxOpen] = useState(false);

  const toggleLike = async () => {
    // Optimistic update; server response corrects the count.
    setLiked(!liked);
    setLikes((n) => n + (liked ? -1 : 1));
    if (!liked) {
      setJustLiked(true);
      setTimeout(() => setJustLiked(false), 400);
    }
    try {
      const res = await api.post<{ liked: boolean; likes_count: number }>(
        `/posts/${post.id}/like/`
      );
      setLiked(res.liked);
      setLikes(res.likes_count);
    } catch {
      setLiked(liked);
      setLikes(post.likes_count);
    }
  };

  const remove = async () => {
    if (!confirm("حذف هذا المنشور؟")) return;
    await api.delete(`/posts/${post.id}/`);
    onDeleted?.(post.id);
  };

  const canDelete = user && (user.id === post.author.id || user.is_staff);
  const kindChip = KIND_LABEL[post.author.kind];
  const ytEmbed = post.link_url ? youtubeEmbedUrl(post.link_url) : null;

  return (
    <article className="card post-card">
      <div className="post-head">
        <Link to={`/profile/${post.author.id}`}>
          <Avatar name={post.author.display_name} src={post.author.avatar} />
        </Link>
        <div>
          <div className="post-author">
            <Link to={`/profile/${post.author.id}`} style={{ color: "inherit" }}>
              {post.author.display_name}
            </Link>
            {kindChip && (
              <span className={`kind-chip ${post.author.kind}`}>{kindChip}</span>
            )}
          </div>
          <div className="post-meta">{timeAgo(post.created_at)}</div>
        </div>
      </div>

      {post.text && (
        <p className="post-text">
          <Linkified text={post.text} />
        </p>
      )}
      {post.image && (
        <img
          className="post-media clickable"
          src={post.image}
          alt=""
          onClick={() => setLightboxOpen(true)}
        />
      )}
      {post.video && <PostVideo src={post.video} />}
      {post.link_url && (
        ytEmbed ? (
          <div className="yt-embed">
            <iframe
              src={ytEmbed}
              title={post.link_title || "فيديو يوتيوب"}
              allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
              allowFullScreen
            />
          </div>
        ) : (
          <a
            className="link-preview"
            href={post.link_url}
            target="_blank"
            rel="noreferrer"
          >
            <span className="lp-title">{post.link_title || "رابط خارجي"}</span>
            <span className="lp-url">{post.link_url}</span>
          </a>
        )
      )}

      <div className="post-actions">
        <button
          className={`like-btn ${liked ? "liked" : ""} ${justLiked ? "just-liked" : ""}`}
          onClick={toggleLike}
          aria-pressed={liked}
        >
          <span className="heart">{liked ? "♥" : "♡"}</span>
          {likes > 0 ? likes : "إعجاب"}
        </button>
        {canDelete && (
          <button className="icon-btn danger" onClick={remove}>
            حذف
          </button>
        )}
      </div>

      {lightboxOpen && post.image && (
        <Lightbox src={post.image} onClose={() => setLightboxOpen(false)} />
      )}
    </article>
  );
}
