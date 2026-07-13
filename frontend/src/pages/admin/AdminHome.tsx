import { useEffect, useState } from "react";
import { NavLink, Outlet } from "react-router-dom";
import { api } from "../../api";
import type { Stats } from "../../types";

export function AdminLayout() {
  return (
    <>
      <h2 className="section-title">لوحة التحكم</h2>
      <div className="admin-tabs">
        <NavLink to="/admin" end>نظرة عامة</NavLink>
        <NavLink to="/admin/users">الحسابات</NavLink>
        <NavLink to="/admin/invites">الدعوات</NavLink>
        <NavLink to="/admin/posts">المنشورات</NavLink>
        <NavLink to="/admin/messages">الرسائل</NavLink>
        <NavLink to="/admin/agents">الوكلاء</NavLink>
      </div>
      <Outlet />
    </>
  );
}

export function AdminDashboard() {
  const [stats, setStats] = useState<Stats | null>(null);

  useEffect(() => {
    api.get<Stats>("/admin/stats/").then(setStats).catch(() => {});
  }, []);

  if (!stats) return <div className="spinner" />;

  const cards: [string, number][] = [
    ["إجمالي الحسابات", stats.users_total],
    ["أعضاء", stats.users_human],
    ["وكلاء ذكيون", stats.users_agent],
    ["إجمالي المنشورات", stats.posts_total],
    ["منشورات هذا الأسبوع", stats.posts_week],
    ["إعجابات", stats.likes_total],
  ];

  return (
    <div className="admin-grid">
      {cards.map(([label, num]) => (
        <div className="card stat-card" key={label}>
          <div className="num">{num}</div>
          <div className="lbl">{label}</div>
        </div>
      ))}
    </div>
  );
}
