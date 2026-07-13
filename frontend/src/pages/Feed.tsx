import { useCallback, useEffect, useRef, useState } from "react";
import { api } from "../api";
import Composer from "../components/Composer";
import PostCard from "../components/PostCard";
import type { Paginated, Post } from "../types";

export default function Feed() {
  const [posts, setPosts] = useState<Post[]>([]);
  const [nextPage, setNextPage] = useState<number | null>(1);
  const [loading, setLoading] = useState(false);
  const composerRef = useRef<HTMLDivElement>(null);

  const loadMore = useCallback(async () => {
    if (nextPage === null || loading) return;
    setLoading(true);
    try {
      const data = await api.get<Paginated<Post>>(`/posts/?page=${nextPage}`);
      setPosts((prev) => {
        const known = new Set(prev.map((p) => p.id));
        return [...prev, ...data.results.filter((p) => !known.has(p.id))];
      });
      setNextPage(data.next ? nextPage + 1 : null);
    } finally {
      setLoading(false);
    }
  }, [nextPage, loading]);

  useEffect(() => {
    loadMore();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Infinite scroll.
  useEffect(() => {
    const onScroll = () => {
      if (
        window.innerHeight + window.scrollY >
        document.body.offsetHeight - 600
      ) {
        loadMore();
      }
    };
    window.addEventListener("scroll", onScroll);
    return () => window.removeEventListener("scroll", onScroll);
  }, [loadMore]);

  return (
    <>
      <div ref={composerRef}>
        <Composer onCreated={(p) => setPosts((prev) => [p, ...prev])} />
      </div>

      {posts.map((post) => (
        <PostCard
          key={post.id}
          post={post}
          onDeleted={(id) => setPosts((prev) => prev.filter((p) => p.id !== id))}
        />
      ))}

      {loading && <div className="spinner" />}
      {!loading && posts.length === 0 && (
        <div className="empty">
          <span className="icon">📭</span>
          لا منشورات بعد — كن أول من ينشر!
        </div>
      )}

      <button
        className="fab"
        aria-label="منشور جديد"
        onClick={() => {
          composerRef.current?.scrollIntoView({ behavior: "smooth" });
          composerRef.current?.querySelector("textarea")?.focus();
        }}
      >
        ✏️
      </button>
    </>
  );
}
