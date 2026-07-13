"""
AI agents worker.

Every SCHEDULE_REFRESH_MINUTES it reloads agent configs from the backend and
(re)builds today's posting schedule: each enabled agent gets `posts_per_day`
random slots inside its active window. When a slot fires the worker generates
a post with Claude (web search included), runs the safety gate, and publishes
through the platform's normal posting API.

Run: python worker.py   (needs BACKEND_URL, AGENT_WORKER_SECRET, ANTHROPIC_API_KEY)
"""
import logging
import os
import random
import time
from datetime import datetime, timedelta

from apscheduler.schedulers.background import BackgroundScheduler
from dotenv import load_dotenv

load_dotenv()

import generation  # noqa: E402
import platform_api  # noqa: E402

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
log = logging.getLogger("agents.worker")

SCHEDULE_REFRESH_MINUTES = int(os.environ.get("SCHEDULE_REFRESH_MINUTES", "60"))
# Minimum spacing between two posts of the same agent (rate limiting).
MIN_GAP_MINUTES = int(os.environ.get("AGENT_MIN_GAP_MINUTES", "90"))

scheduler = BackgroundScheduler(timezone=os.environ.get("TIME_ZONE", "Africa/Casablanca"))
_last_post_at: dict[int, datetime] = {}


def run_agent(agent: dict):
    agent_id = agent["id"]
    now = datetime.now()
    last = _last_post_at.get(agent_id)
    if last and (now - last) < timedelta(minutes=MIN_GAP_MINUTES):
        log.info("skip %s: posted %.0f min ago", agent["username"],
                 (now - last).total_seconds() / 60)
        return

    log.info("generating post for %s (%s)", agent["username"], agent["topic"])
    result = generation.generate_post(agent)
    if not result:
        return
    if not generation.is_safe(result["text"]):
        log.warning("post for %s blocked by safety gate", agent["username"])
        return
    try:
        post = platform_api.publish_post(
            agent_id, result["text"], result["link_url"], result["link_title"]
        )
        _last_post_at[agent_id] = now
        log.info("published post #%s for %s", post["id"], agent["username"])
    except Exception as exc:
        log.error("publish failed for %s: %s", agent["username"], exc)


def build_schedule():
    """Clear agent jobs and schedule today's remaining slots for each agent."""
    for job in scheduler.get_jobs():
        if job.id.startswith("agent-"):
            job.remove()

    try:
        agents = platform_api.fetch_agents()
    except Exception as exc:
        log.error("cannot fetch agents from backend: %s", exc)
        return

    now = datetime.now()
    for agent in agents:
        start_h = agent["active_hour_start"]
        end_h = max(agent["active_hour_end"], start_h + 1)
        for i in range(agent["posts_per_day"]):
            hour = random.randint(start_h, end_h - 1)
            minute = random.randint(0, 59)
            run_at = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
            if run_at <= now:
                continue  # slot already passed today; tomorrow's refresh reschedules
            scheduler.add_job(
                run_agent,
                "date",
                run_date=run_at,
                args=[agent],
                id=f"agent-{agent['id']}-{i}-{run_at:%H%M}",
                replace_existing=True,
            )
            log.info("scheduled %s at %s", agent["username"], run_at.strftime("%H:%M"))


def main():
    log.info("agents worker starting (backend=%s, model=%s)",
             platform_api.BACKEND_URL, generation.MODEL)
    scheduler.add_job(build_schedule, "interval",
                      minutes=SCHEDULE_REFRESH_MINUTES, id="refresh-schedule")
    scheduler.start()
    build_schedule()

    # Optional: post immediately on boot so the feed is never empty on day one.
    if os.environ.get("AGENT_POST_ON_BOOT", "0") == "1":
        try:
            for agent in platform_api.fetch_agents():
                run_agent(agent)
        except Exception as exc:
            log.error("boot post failed: %s", exc)

    try:
        while True:
            time.sleep(60)
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()


if __name__ == "__main__":
    main()
