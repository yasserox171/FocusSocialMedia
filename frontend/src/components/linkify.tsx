import type { ReactNode } from "react";

const URL_RE = /(https?:\/\/[^\s<]+)/g;
// Trailing characters that are almost always punctuation, not part of the URL.
const TRAILING_PUNCT_RE = /[).,!?;:'"\]]+$/;

/** Extracts the YouTube embed URL from a watch/share/shorts link, or null. */
export function youtubeEmbedUrl(url: string): string | null {
  let parsed: URL;
  try {
    parsed = new URL(url);
  } catch {
    return null;
  }
  const host = parsed.hostname.replace(/^www\.|^m\./, "");
  let videoId: string | null = null;

  if (host === "youtu.be") {
    videoId = parsed.pathname.slice(1).split("/")[0];
  } else if (host === "youtube.com") {
    if (parsed.pathname === "/watch") {
      videoId = parsed.searchParams.get("v");
    } else if (parsed.pathname.startsWith("/shorts/")) {
      videoId = parsed.pathname.split("/")[2];
    } else if (parsed.pathname.startsWith("/embed/")) {
      videoId = parsed.pathname.split("/")[2];
    }
  }

  return videoId ? `https://www.youtube.com/embed/${videoId}` : null;
}

/** Renders text with any http(s) URLs turned into links that open in a new tab. */
export function Linkified({ text }: { text: string }) {
  const nodes: ReactNode[] = [];
  let lastIndex = 0;
  let key = 0;

  for (const match of text.matchAll(URL_RE)) {
    const start = match.index ?? 0;
    if (start > lastIndex) nodes.push(text.slice(lastIndex, start));

    let raw = match[0];
    let trail = "";
    const trailMatch = raw.match(TRAILING_PUNCT_RE);
    if (trailMatch) {
      trail = trailMatch[0];
      raw = raw.slice(0, -trail.length);
    }

    nodes.push(
      <a
        key={key++}
        href={raw}
        target="_blank"
        rel="noreferrer"
        className="inline-link"
      >
        {raw}
      </a>
    );
    if (trail) nodes.push(trail);
    lastIndex = start + match[0].length;
  }

  if (lastIndex < text.length) nodes.push(text.slice(lastIndex));
  return <>{nodes}</>;
}
