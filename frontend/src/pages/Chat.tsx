import { FormEvent, useEffect, useRef, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { api, wsUrl } from "../api";
import { useAuth } from "../auth";
import Avatar from "../components/Avatar";
import type { Conversation, Message, Paginated } from "../types";

export default function Chat() {
  const { id } = useParams();
  const { user: me } = useAuth();
  const [conversation, setConversation] = useState<Conversation | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [text, setText] = useState("");
  const [typing, setTyping] = useState(false);
  const wsRef = useRef<WebSocket | null>(null);
  const bodyRef = useRef<HTMLDivElement>(null);
  const typingTimeout = useRef<number>();
  const lastTypingSent = useRef(0);

  // Load conversation info + history, mark as read.
  useEffect(() => {
    api.get<Conversation[]>("/conversations/").then((all) => {
      setConversation(all.find((c) => c.id === Number(id)) ?? null);
    });
    api
      .get<Paginated<Message>>(`/conversations/${id}/messages/`)
      .then((data) => setMessages(data.results));
    api.post(`/conversations/${id}/read/`).catch(() => {});
  }, [id]);

  // Live socket.
  useEffect(() => {
    let closed = false;
    let socket: WebSocket;
    const connect = () => {
      socket = new WebSocket(wsUrl(`/ws/chat/${id}/`));
      wsRef.current = socket;
      socket.onmessage = (ev) => {
        const msg = JSON.parse(ev.data);
        if (msg.type === "message") {
          setTyping(false);
          setMessages((prev) =>
            prev.some((m) => m.id === msg.data.id) ? prev : [...prev, msg.data]
          );
          api.post(`/conversations/${id}/read/`).catch(() => {});
        } else if (msg.type === "typing") {
          setTyping(true);
          window.clearTimeout(typingTimeout.current);
          typingTimeout.current = window.setTimeout(() => setTyping(false), 2500);
        }
      };
      socket.onclose = () => {
        if (!closed) setTimeout(connect, 4000);
      };
    };
    connect();
    return () => {
      closed = true;
      socket.close();
    };
  }, [id]);

  // Autoscroll on new messages.
  useEffect(() => {
    bodyRef.current?.scrollTo({ top: bodyRef.current.scrollHeight });
  }, [messages, typing]);

  const send = async (e: FormEvent) => {
    e.preventDefault();
    const trimmed = text.trim();
    if (!trimmed) return;
    setText("");
    const ws = wsRef.current;
    if (ws && ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify({ type: "message", text: trimmed }));
    } else {
      // REST fallback if the socket is reconnecting.
      const m = await api.post<Message>(`/conversations/${id}/messages/`, {
        text: trimmed,
      });
      setMessages((prev) => [...prev, m]);
    }
  };

  const onTyping = (value: string) => {
    setText(value);
    const now = Date.now();
    const ws = wsRef.current;
    if (ws && ws.readyState === WebSocket.OPEN && now - lastTypingSent.current > 1500) {
      ws.send(JSON.stringify({ type: "typing" }));
      lastTypingSent.current = now;
    }
  };

  return (
    <div className="chat-shell">
      <div className="chat-head">
        <Link to="/messages" className="icon-btn">→</Link>
        {conversation && (
          <>
            <Avatar
              name={conversation.other_user.display_name}
              src={conversation.other_user.avatar}
              size="sm"
            />
            <strong>{conversation.other_user.display_name}</strong>
          </>
        )}
      </div>

      <div className="chat-body" ref={bodyRef}>
        {messages.map((m) => (
          <div key={m.id} className={`bubble ${m.sender === me?.id ? "mine" : "theirs"}`}>
            {m.text}
            <time>
              {new Date(m.created_at).toLocaleTimeString("ar-MA", {
                hour: "2-digit",
                minute: "2-digit",
              })}
            </time>
          </div>
        ))}
        {typing && (
          <div className="typing">
            يكتب <span className="d" /> <span className="d" /> <span className="d" />
          </div>
        )}
      </div>

      <form className="chat-input" onSubmit={send}>
        <input
          placeholder="اكتب رسالة…"
          value={text}
          onChange={(e) => onTyping(e.target.value)}
        />
        <button className="btn">إرسال</button>
      </form>
    </div>
  );
}
