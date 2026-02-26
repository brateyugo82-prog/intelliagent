from __future__ import annotations
from core.platform_times import build_platform_times
"""
🗓️ IntelliAgent – Approval → Scheduling
--------------------------------------
- Liest approved Posts
- Nutzt weekly_plan.json (content_category-basiert)
- Unterstützt publish_time pro Regel
- Unterstützt fallback mapping (z.B. manual -> service)
- Setzt publish_at + status = scheduled
- KEIN Publish
- KEIN Meta
"""


from datetime import datetime, timezone, timedelta
from pathlib import Path
import json
from typing import Any, Dict, Optional, Tuple

from core.logger import logger
from core.post_store import get_posts, update_post

# =====================================================
# CONFIG
# =====================================================

CLIENT = "mtm_client"
DEFAULT_TIME = "09:00"  # fallback, falls rule kein publish_time hat

BASE_DIR = Path(__file__).resolve().parents[2]
WEEKLY_PLAN_PATH = (
    BASE_DIR
    / "backend"
    / "clients"
    / CLIENT
    / "content_rules"
    / "weekly_plan.json"
)

WEEKDAYS = {
    "monday": 0,
    "tuesday": 1,
    "wednesday": 2,
    "thursday": 3,
    "friday": 4,
    "saturday": 5,
    "sunday": 6,
}

# =====================================================
# HELPERS
# =====================================================


def load_weekly_plan() -> Dict[str, Any]:
    if not WEEKLY_PLAN_PATH.exists():
        raise FileNotFoundError(f"weekly_plan.json fehlt: {WEEKLY_PLAN_PATH}")
    return json.loads(WEEKLY_PLAN_PATH.read_text(encoding="utf-8"))


def _parse_time_hhmm(time_str: str) -> Tuple[int, int]:
    try:
        hour, minute = map(int, str(time_str).split(":"))
        if not (0 <= hour <= 23 and 0 <= minute <= 59):
            raise ValueError
        return hour, minute
    except Exception:
        logger.warning(f"[ApprovalScheduler] ⚠️ Ungültige publish_time '{time_str}', nutze DEFAULT_TIME {DEFAULT_TIME}")
        return _parse_time_hhmm(DEFAULT_TIME)


def next_datetime_for_day(day_name: str, time_str: str) -> datetime:
    """
    Berechnet den nächsten Zeitpunkt für einen Wochentag + Uhrzeit (UTC).
    - Wenn target_day == heute UND Uhrzeit noch in Zukunft => heute.
    - Sonst nächster passender Wochentag.
    """
    now = datetime.now(timezone.utc)
    day_key = day_name.lower().strip()
    target_weekday = WEEKDAYS[day_key]

    hour, minute = _parse_time_hhmm(time_str)

    # Baseline: heute mit Zielzeit
    candidate = now.replace(hour=hour, minute=minute, second=0, microsecond=0)

    days_ahead = (target_weekday - now.weekday()) % 7

    if days_ahead == 0:
        # Heute: nur heute nehmen, wenn candidate in Zukunft ist, sonst nächste Woche
        if candidate <= now:
            days_ahead = 7
    # falls nicht heute: candidate + days_ahead
    scheduled = candidate + timedelta(days=days_ahead)
    return scheduled


def _rule_matches_post(rule: Dict[str, Any], post: Dict[str, Any]) -> bool:
    """
    Match-Regeln:
    - content_category MUSS passen
    - Optional: service_type, image_context, category können als Constraint existieren
    """
    if rule.get("content_category") != post.get("content_category"):
        return False

    # optional constraints
    for key in ("service_type", "image_context", "category"):
        if key in rule and rule.get(key) is not None:
            if post.get(key) != rule.get(key):
                return False

    return True


def find_best_rule_for_post(weekly_plan: Dict[str, Any], post: Dict[str, Any]) -> Optional[Tuple[str, Dict[str, Any]]]:
    """
    Gibt (day, rule) zurück.
    1) Best match: content_category + alle optional constraints (service_type/image_context/category)
    2) Fallback match: nur content_category
    """
    week = weekly_plan.get("week", {}) or {}

    # 1) strict match
    for day, rules in week.items():
        for rule in rules or []:
            if _rule_matches_post(rule, post):
                return day, rule

    # 2) loose match (nur content_category)
    cc = post.get("content_category")
    for day, rules in week.items():
        for rule in rules or []:
            if rule.get("content_category") == cc:
                return day, rule

    return None


def apply_fallback_content_category(weekly_plan: Dict[str, Any], post: Dict[str, Any]) -> Optional[str]:
    """
    weekly_plan kann ein fallback dict enthalten:
      fallback: { "manual": "service", "finished_work": "service", ... }

    Wir versuchen:
    1) fallback[post.content_category]
    2) fallback[post.category]
    """
    fb = weekly_plan.get("fallback") or {}
    if not isinstance(fb, dict):
        return None

    cc = post.get("content_category")
    cat = post.get("category")

    if cc in fb:
        return fb[cc]
    if cat in fb:
        return fb[cat]
    return None


def _utcnow_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


# =====================================================
# MAIN LOGIC
# =====================================================

def run_approval_scheduler():
    logger.info("🗓️ Approval Scheduler gestartet")

    weekly_plan = load_weekly_plan()
    posts = get_posts(CLIENT)

    for post in posts:
        if post.get("status") != "approved":
            continue

        if not post.get("content_category"):
            logger.warning(f"[ApprovalScheduler] ❌ Post {post.get('id')} hat keine content_category")
            continue

        # Versuch 1: direktes Matching
        match = find_best_rule_for_post(weekly_plan, post)

        # Versuch 2: fallback mapping (manual/finished_work/etc.)
        if not match:
            fb_cc = apply_fallback_content_category(weekly_plan, post)
            if fb_cc:
                original = post.get("content_category")
                post = dict(post)  # nicht mutieren
                post["content_category"] = fb_cc
                logger.info(f"[ApprovalScheduler] ↪️ Fallback content_category: {original} → {fb_cc} (post {post.get('id')})")
                match = find_best_rule_for_post(weekly_plan, post)

        if not match:
            logger.warning(f"[ApprovalScheduler] ❌ Kein Slot für content_category {post.get('content_category')} (post {post.get('id')})")
            continue

        day, rule = match
        publish_time = rule.get("publish_time") or DEFAULT_TIME

        try:
            publish_at = next_datetime_for_day(day, publish_time)

            update_post(
                post["id"],
                {
                    "status": "scheduled",
                    "platform_times": build_platform_times(),
                    "publish_at": publish_at.isoformat(),
                    "updated_at": _utcnow_iso(),
                },
            )

            logger.info(
                f"[ApprovalScheduler] ✅ Scheduled {post['id']} → {day} {publish_at.isoformat()} (time={publish_time})"
            )

        except Exception as e:
            logger.error(f"[ApprovalScheduler] ❌ Fehler bei {post.get('id')}: {e}")


if __name__ == "__main__":
    run_approval_scheduler()