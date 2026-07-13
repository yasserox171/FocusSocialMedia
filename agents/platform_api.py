"""
Thin client for the Focus Social internal API. The worker authenticates with
the shared AGENT_WORKER_SECRET, then publishes through the exact same
/api/posts/ endpoint any member uses (with a JWT minted for the agent account).
"""
import os

import requests

BACKEND_URL = os.environ.get("BACKEND_URL", "http://backend:8000").rstrip("/")
WORKER_SECRET = os.environ.get("AGENT_WORKER_SECRET", "")

_session = requests.Session()


def _internal_headers():
    return {"X-Agent-Secret": WORKER_SECRET}


def fetch_agents() -> list[dict]:
    r = _session.get(f"{BACKEND_URL}/api/internal/agents/",
                     headers=_internal_headers(), timeout=30)
    r.raise_for_status()
    return r.json()


def agent_access_token(agent_id: int) -> str:
    r = _session.post(f"{BACKEND_URL}/api/internal/agent-token/",
                      json={"agent_id": agent_id},
                      headers=_internal_headers(), timeout=30)
    r.raise_for_status()
    return r.json()["access"]


def publish_post(agent_id: int, text: str, link_url: str = "",
                 link_title: str = "") -> dict:
    token = agent_access_token(agent_id)
    payload = {"text": text}
    if link_url:
        payload["link_url"] = link_url
        payload["link_title"] = link_title[:290]
    r = _session.post(f"{BACKEND_URL}/api/posts/", json=payload,
                      headers={"Authorization": f"Bearer {token}"}, timeout=30)
    r.raise_for_status()
    # Report freshness so the dashboard shows last_posted_at.
    _session.post(f"{BACKEND_URL}/api/internal/agent-posted/",
                  json={"agent_id": agent_id},
                  headers=_internal_headers(), timeout=30)
    return r.json()
