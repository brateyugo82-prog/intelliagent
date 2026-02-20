"""
✅ IntelliAgent Scheduler Worker (STABLE, Minimal)
-------------------------------------------------
- RUFT NICHT master_agent/master.py
- Holt Posts aus core.post_store (pro Client)
- Filter: status == "scheduled" und publish_at <= now
- Ruft publish_post(post_id)
- Loop-fähig für Render Worker
- Optional: RUN_ONCE=1 für lokalen Test
"""

from __future__ import annotations

import os
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Dict, Any, List

from core.logger import logger
from core import post_store
from agents.publish_agent.agent import publish_post


BASE_DIR = Path(__file__).resolve().parents[2]  # -> backend/
CLIENTS_DIR = BASE_DIR / "clients"


def _parse_iso_datetime(value: Optional[str]) -> Optional[datetime]:
    """
    Robust ISO parse:
    - akzeptiert "...Z" oder "+00:00"
    - liefert timezone-aware datetime in UTC zurück
    """
    if not value or not isinstance(value, str):
        return None

    v = value.strip()
    try:
        if v.endswith("Z"):
            v = v[:-1] + "+00:00"
        dt = datetime.fromisoformat(v)
        if dt.tzinfo is None:
            # defensiv: treat as UTC
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc)
    except Exception:
        return None


def _list_clients() -> List[str]:
    if not CLIENTS_DIR.exists():
        logger.warning(f"[Scheduler] CLIENTS_DIR fehlt: {CLIENTS_DIR}")
        return []

    out: List[str] = []
    for p in CLIENTS_DIR.iterdir():
        if p.is_dir() and not p.name.startswith("--"):
            out.append(p.name)
    return out


def _due_scheduled_posts_for_client(client: str, now_utc: datetime) -> List[Dict[str, Any]]:
    posts = post_store.get_posts(client)

    due: List[Dict[str, Any]] = []
    for p in posts:
        status = str(p.get("status") or "").lower().strip()
        if status != "scheduled":
            continue

        publish_at = _parse_iso_datetime(p.get("publish_at"))
        if publish_at is None:
            # scheduled ohne publish_at -> konservativ NICHT posten
            continue

        if publish_at <= now_utc:
            due.append(p)

    # deterministisch: älteste zuerst
    due.sort(key=lambda x: str(x.get("publish_at") or ""))
    return due


def run_once() -> Dict[str, Any]:
    now_utc = datetime.now(timezone.utc)
    clients = _list_clients()

    total_due = 0
    total_published = 0
    total_errors = 0

    for client in clients:
        try:
            due = _due_scheduled_posts_for_client(client, now_utc)
        except Exception as e:
            logger.error(f"[Scheduler] ❌ Fehler beim Laden der Posts für client={client}: {e}")
            total_errors += 1
            continue

        if not due:
            continue

        logger.info(f"[Scheduler] 🕒 Due Posts: client={client} count={len(due)}")
        total_due += len(due)

        for p in due:
            post_id = str(p.get("id") or "")
            if not post_id:
                continue

            try:
                res = publish_post(post_id)
                if res.get("status") == "published":
                    total_published += 1
                elif res.get("status") == "skipped":
                    # z.B. already_published – ok
                    pass
                else:
                    # error oder anderes
                    total_errors += 1
                logger.info(f"[Scheduler] ✅ publish_post result post_id={post_id} -> {res.get('status')}")
            except Exception as e:
                total_errors += 1
                logger.error(f"[Scheduler] ❌ publish_post crashed post_id={post_id}: {e}")

    return {
        "now_utc": now_utc.isoformat(),
        "clients": len(clients),
        "due": total_due,
        "published": total_published,
        "errors": total_errors,
    }


def loop(poll_seconds: int = 30) -> None:
    logger.info(f"[Scheduler] 🚀 Worker gestartet | poll_seconds={poll_seconds}")

    while True:
        summary = run_once()
        logger.info(
            f"[Scheduler] 📊 tick done due={summary['due']} published={summary['published']} errors={summary['errors']}"
        )

        # RUN_ONCE=1 -> nach einem Lauf beenden (lokal/test)
        if os.getenv("RUN_ONCE", "").strip() == "1":
            logger.info("[Scheduler] 🧪 RUN_ONCE=1 -> exit")
            return

        time.sleep(poll_seconds)


if __name__ == "__main__":
    poll = int(os.getenv("SCHEDULER_POLL_SECONDS", "30"))
    loop(poll_seconds=poll)
from scheduler.publish_guard import should_auto_publish, is_manual
from core.post_store import mark_manual_required

def handle_platform_publish(post, platform):
    if should_auto_publish(platform):
        publish(platform, post)
    elif is_manual(platform):
        mark_manual_required(post["id"], platform)
