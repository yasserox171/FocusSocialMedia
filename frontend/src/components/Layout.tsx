import { useEffect, useRef, useState } from "react";
import { NavLink, Outlet, useLocation } from "react-router-dom";
import { api, wsUrl } from "../api";
import { useAuth } from "../auth";
import { useTheme } from "../theme";
import type { Notification } from "../types";

function NavItems({ unread }: { unread: number }) {
  const { user, logout } = useAuth();
  return (
    <>
      <NavLink to="/" end className="nav-item">
        <span>🏠</span> الرئيسية
      </NavLink>
      <NavLink to="/people" className="nav-item">
        <span>👥</span> الأعضاء
      </NavLink>
      <NavLink to="/messages" className="nav-item">
        <span>💬</span> الرسائل
      </NavLink>
      <NavLink to="/notifications" className="nav-item">
        <span>🔔</span> الإشعارات
        {unread > 0 && <span className="nav-badge">{unread > 99 ? "99+" : unread}</span>}
      </NavLink>
      <NavLink to={`/profile/${user?.id}`} className="nav-item">
        <span>👤</span> حسابي
      </NavLink>
      {user?.is_staff && (
        <NavLink to="/admin" className="nav-item">
          <span>🛠️</span> الإدارة
        </NavLink>
      )}
      <button className="nav-item" onClick={logout}>
        <span>🚪</span> خروج
      </button>
    </>
  );
}

export default function Layout() {
  const { theme, toggle } = useTheme();
  const [unread, setUnread] = useState(0);
  const [toast, setToast] = useState<string | null>(null);
  const location = useLocation();
  const wsRef = useRef<WebSocket | null>(null);

  // Unread counter + live notifications socket.
  useEffect(() => {
    api
      .get<{ count: number }>("/notifications/unread-count/")
      .then((r) => setUnread(r.count))
      .catch(() => {});

    let closed = false;
    let socket: WebSocket;
    const connect = () => {
      socket = new WebSocket(wsUrl("/ws/notifications/"));
      wsRef.current = socket;
      socket.onmessage = (ev) => {
        const msg = JSON.parse(ev.data);
        if (msg.type === "notification") {
          const n: Notification = msg.data;
          setUnread((c) => c + 1);
          setToast(n.text);
          setTimeout(() => setToast(null), 4000);
        }
      };
      socket.onclose = () => {
        if (!closed) setTimeout(connect, 5000); // auto-reconnect
      };
    };
    connect();
    return () => {
      closed = true;
      socket.close();
    };
  }, []);

  // Reset badge when the notifications page is opened.
  useEffect(() => {
    if (location.pathname === "/notifications") setUnread(0);
  }, [location.pathname]);

  return (
    <div className="app-shell">
      <nav className="sidenav">
        <div className="brand">
          فوكس<span className="dot">.</span>سوشيال
        </div>
        <NavItems unread={unread} />
        <div style={{ flex: 1 }} />
        <button className="nav-item" onClick={toggle}>
          <span>{theme === "dark" ? "☀️" : "🌙"}</span>
          {theme === "dark" ? "وضع نهاري" : "وضع ليلي"}
        </button>
      </nav>

      <main className="main-col">
        <Outlet />
      </main>

      <nav className="bottomnav">
        <NavItems unread={unread} />
      </nav>

      {toast && <div className="toast">🔔 {toast}</div>}
    </div>
  );
}
