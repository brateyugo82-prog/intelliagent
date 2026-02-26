"""
🕓 IntelliAgent – Global Post Scheduler (PUBLISH ONLY)
----------------------------------------------------
- Ruft KEINEN Master
- Erzeugt KEINEN Content
- Published NUR gespeicherte Posts
- Status-Flow:
    scheduled → published
"""

import time
from datetime import datetime, timezone

from core.logger import logger
from core.post_store import get_posts
from agents.publish_agent.agent import publish_post

POLL_INTERVAL_SECONDS = 30
CLIENT = "mtm_client"


def get_due_posts():
    """
    Liefert alle Posts, die:
    - status == scheduled
    - publish_at <= now
    """
    now = datetime.now(timezone.utc)
    due = []

    posts = get_posts(CLIENT)

    for post in posts:
        if post.get("status") != "scheduled":
            continue

        publish_at = post.get("publish_at")
        if not publish_at:
            continue

        try:
            publish_time = datetime.fromisoformat(publish_at)
        except Exception:
            logger.warning(f"[Scheduler] ❌ Ungültiges publish_at: {publish_at}")
            continue

        if publish_time <= now:
            due.append(post)

    return due


def scheduler_loop():
    logger.info("🕓 IntelliAgent Post Scheduler gestartet")

    while True:
        try:
            due_posts = get_due_posts()

            if due_posts:
                logger.info(f"[Scheduler] 🔔 {len(due_posts)} Posts fällig")

            for post in due_posts:
                post_id = post["id"]

                try:
                    # 🔑 EINZIGER CALL
                    publish_post(post_id)

                    logger.info(f"[Scheduler] ✅ Published: {post_id}")

                except Exception as e:
                    logger.error(f"[Scheduler] ❌ Publish-Fehler ({post_id}): {e}")

        except Exception as loop_error:
            logger.error(f"[Scheduler] ❌ Loop-Fehler: {loop_error}")

        time.sleep(POLL_INTERVAL_SECONDS)


if __name__ == "__main__":
    scheduler_loop()