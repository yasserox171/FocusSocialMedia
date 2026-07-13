import { useEffect, useState } from "react";
import { api } from "../../api";
import { timeAgo } from "../../components/timeago";
import type { AgentProfile, Paginated } from "../../types";

export default function AdminAgents() {
  const [agents, setAgents] = useState<AgentProfile[]>([]);
  const [loading, setLoading] = useState(true);
  const [savedId, setSavedId] = useState<number | null>(null);

  useEffect(() => {
    api
      .get<Paginated<AgentProfile>>("/admin/agents/")
      .then((d) => setAgents(d.results))
      .finally(() => setLoading(false));
  }, []);

  const update = (id: number, patch: Partial<AgentProfile>) =>
    setAgents((prev) => prev.map((a) => (a.id === id ? { ...a, ...patch } : a)));

  const save = async (agent: AgentProfile) => {
    await api.patch(`/admin/agents/${agent.id}/`, {
      system_prompt: agent.system_prompt,
      enabled: agent.enabled,
      posts_per_day: agent.posts_per_day,
      active_hour_start: agent.active_hour_start,
      active_hour_end: agent.active_hour_end,
    });
    setSavedId(agent.id);
    setTimeout(() => setSavedId(null), 1500);
  };

  if (loading) return <div className="spinner" />;

  return (
    <>
      {agents.map((agent) => (
        <div className="card" key={agent.id}>
          <div style={{ display: "flex", alignItems: "center", gap: 12, marginBottom: 10 }}>
            <h3 style={{ margin: 0, flex: 1 }}>{agent.display_name}</h3>
            <span className={`pill ${agent.enabled ? "on" : "off"}`}>
              {agent.enabled ? "مفعّل" : "متوقف"}
            </span>
            <label className="switch">
              <input
                type="checkbox"
                checked={agent.enabled}
                onChange={(e) => update(agent.id, { enabled: e.target.checked })}
              />
              <span className="track" />
            </label>
          </div>

          <div className="field">
            <label>البرومبت (تعليمات الوكيل)</label>
            <textarea
              rows={5}
              value={agent.system_prompt}
              onChange={(e) => update(agent.id, { system_prompt: e.target.value })}
            />
          </div>

          <div style={{ display: "flex", gap: 12, flexWrap: "wrap" }}>
            <div className="field" style={{ flex: 1, minWidth: 120 }}>
              <label>منشورات/اليوم</label>
              <input
                type="number"
                min={1}
                max={10}
                value={agent.posts_per_day}
                onChange={(e) => update(agent.id, { posts_per_day: +e.target.value })}
              />
            </div>
            <div className="field" style={{ flex: 1, minWidth: 120 }}>
              <label>من الساعة</label>
              <input
                type="number"
                min={0}
                max={23}
                value={agent.active_hour_start}
                onChange={(e) => update(agent.id, { active_hour_start: +e.target.value })}
              />
            </div>
            <div className="field" style={{ flex: 1, minWidth: 120 }}>
              <label>إلى الساعة</label>
              <input
                type="number"
                min={1}
                max={24}
                value={agent.active_hour_end}
                onChange={(e) => update(agent.id, { active_hour_end: +e.target.value })}
              />
            </div>
          </div>

          <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
            <button className="btn sm" onClick={() => save(agent)}>
              {savedId === agent.id ? "✓ حُفظ" : "حفظ"}
            </button>
            <span style={{ color: "var(--muted)", fontSize: 13 }}>
              {agent.posts_count} منشوراً ·{" "}
              {agent.last_posted_at
                ? `آخر نشر ${timeAgo(agent.last_posted_at)}`
                : "لم ينشر بعد"}
            </span>
          </div>
        </div>
      ))}
    </>
  );
}
