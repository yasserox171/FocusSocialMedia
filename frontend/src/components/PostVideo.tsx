import { useRef, useState } from "react";

/** Video with a custom framed player: big centered play button until started,
 * then native controls — reads as a modern app player rather than a raw
 * browser <video> tag. */
export default function PostVideo({ src }: { src: string }) {
  const videoRef = useRef<HTMLVideoElement>(null);
  const [playing, setPlaying] = useState(false);

  return (
    <div className="video-frame">
      <video
        ref={videoRef}
        className="video-el"
        src={src}
        controls={playing}
        playsInline
        preload="metadata"
        controlsList="nodownload"
        onPlay={() => setPlaying(true)}
        onPause={() => setPlaying(false)}
        onClick={() => {
          if (!playing) videoRef.current?.play();
        }}
      />
      {!playing && (
        <button
          className="video-play-overlay"
          onClick={() => videoRef.current?.play()}
          aria-label="تشغيل الفيديو"
        >
          <span className="video-play-btn">▶</span>
        </button>
      )}
    </div>
  );
}
