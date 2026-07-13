"""
Content generation for the news agents.

Each generation call gives Claude the agent's system prompt plus the
web-search server tool so posts are grounded in real, current news.
A separate lightweight moderation pass rejects unsafe content before
anything reaches the platform (no human review happens, so this gate
plus a keyword blocklist are mandatory).
"""
import json
import logging
import os
import re

import anthropic

log = logging.getLogger("agents.generation")

MODEL = os.environ.get("ANTHROPIC_MODEL", "claude-opus-4-8")

client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY

# Hard blocklist applied after generation — belt and suspenders on top of the
# moderation pass. Extend from the dashboard prompt if needed.
BLOCKLIST = [
    "قتل الجميع", "دعوة للعنف", "إبادة",
]

GENERATION_INSTRUCTIONS = """
ابحث في الويب عن خبر واحد حقيقي وحديث (خلال الأيام القليلة الماضية) في مجالك،
ثم اكتب منشوراً واحداً جاهزاً للنشر.

أجب في النهاية بهذا الشكل حصراً (بدون أي نص آخر بعده):
<post>
نص المنشور هنا
</post>
<link>رابط المصدر إن وجد، أو اتركه فارغاً</link>
<link_title>عنوان المصدر</link_title>
"""

MODERATION_PROMPT = """أنت مرشح أمان لمنصة اجتماعية داخلية لجمعية تعليمية.
قيّم النص التالي وأجب بـ JSON فقط: {"safe": true/false, "reason": "..."}
اعتبر النص غير آمن إذا تضمن: تحريضاً على العنف أو الكراهية، محتوى جنسياً،
تشهيراً بأشخاص، معلومات مضللة خطيرة، أو محتوى غير لائق لمنصة مهنية.
الأخبار السياسية والاقتصادية المحايدة آمنة.

النص:
"""


def _extract(tag: str, text: str) -> str:
    m = re.search(rf"<{tag}>(.*?)</{tag}>", text, re.DOTALL)
    return m.group(1).strip() if m else ""


def generate_post(agent: dict) -> dict | None:
    """Returns {"text", "link_url", "link_title"} or None if generation failed."""
    try:
        with client.messages.stream(
            model=MODEL,
            max_tokens=16000,
            thinking={"type": "adaptive"},
            system=agent["system_prompt"],
            tools=[{
                "type": "web_search_20260209",
                "name": "web_search",
                "max_uses": 4,
            }],
            messages=[{"role": "user", "content": GENERATION_INSTRUCTIONS}],
        ) as stream:
            response = stream.get_final_message()
    except anthropic.APIError as exc:
        log.error("generation failed for %s: %s", agent["username"], exc)
        return None

    if response.stop_reason == "refusal":
        log.warning("model refused generation for %s", agent["username"])
        return None

    full_text = "".join(b.text for b in response.content if b.type == "text")
    post_text = _extract("post", full_text)
    if not post_text:
        log.warning("no <post> block in output for %s", agent["username"])
        return None

    return {
        "text": post_text,
        "link_url": _extract("link", full_text),
        "link_title": _extract("link_title", full_text),
    }


def is_safe(text: str) -> bool:
    """Blocklist + model moderation pass. Fails closed."""
    lowered = text.lower()
    if any(term in lowered for term in BLOCKLIST):
        return False
    try:
        response = client.messages.create(
            model=MODEL,
            max_tokens=1024,
            output_config={
                "format": {
                    "type": "json_schema",
                    "schema": {
                        "type": "object",
                        "properties": {
                            "safe": {"type": "boolean"},
                            "reason": {"type": "string"},
                        },
                        "required": ["safe", "reason"],
                        "additionalProperties": False,
                    },
                }
            },
            messages=[{"role": "user", "content": MODERATION_PROMPT + text}],
        )
        if response.stop_reason == "refusal":
            return False
        verdict = json.loads(
            next(b.text for b in response.content if b.type == "text")
        )
        if not verdict["safe"]:
            log.warning("moderation rejected post: %s", verdict.get("reason"))
        return bool(verdict["safe"])
    except Exception as exc:  # any failure -> do not publish
        log.error("moderation pass failed, refusing to publish: %s", exc)
        return False
