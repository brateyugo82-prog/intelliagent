from core.platform_times import build_platform_times
"""
📅 IntelliAgent – Foundation Post Scheduler (CREATE ONLY)
--------------------------------------------------------
- Erzeugt Foundation Posts EINMALIG
- Reihenfolge aus foundation_posts.json
- KEIN Publishing
- KEIN Master-Aufruf
- Speichert Posts im core.post_store
- Danach: foundation.done = true
"""

import os
import json
import time
from datetime import datetime, timezone
from pathlib import Path

from core.logger import logger
from core import post_store


BASE_DIR = Path(__file__).resolve().parents[1]  # backend/
CLIENTS_DIR = BASE_DIR / "clients"
POLL_INTERVAL_SECONDS = 60


# -------------------------------------------------
# HELPERS
# -------------------------------------------------

def load_foundation(client: str) -> dict | None:
    path = CLIENTS_DIR / client / "foundation_posts.json"
    if not path.exists():
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_foundation(client: str, data: dict) -> None:
    path = CLIENTS_DIR / client / "foundation_posts.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def get_next_foundation_post(data: dict) -> dict | None:
    for post in data.get("foundation_posts", []):
        if not post.get("posted", False):
            return post
    return None


def create_scheduled_post(client: str, foundation_post: dict) -> None:
    """
    Erzeugt einen scheduled Post im PostStore.
    KEIN Publishing.
    """
    post_id = foundation_post.get("id")
    if not post_id:
        raise ValueError("Foundation-Post ohne ID")

    post = {
        "id": post_id,
        "client": client,
        "source": "foundation",
        "status": "scheduled",
            "platform_times": build_platform_times(),
        "platforms": foundation_post.get("platforms", ["instagram"]),
        "content_category": foundation_post.get("content_category"),
        "image_context": foundation_post.get("image_context"),
        "text": foundation_post.get("text"),
        "publish_at": datetime.now(timezone.utc).isoformat(),
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    post_store.save_post(post)
    logger.info(f"[FoundationScheduler] 🧱 Post gespeichert: {post_id}")


# -------------------------------------------------
# FOUNDATION RUN
# -------------------------------------------------

def run_foundation_for_client(client: str) -> bool:
    foundation = load_foundation(client)
    if not foundation:
        return False

    if foundation.get("done") is True:
        return False

    post = get_next_foundation_post(foundation)
    if not post:
        foundation["done"] = True
        save_foundation(client, foundation)
        logger.info(f"[FoundationScheduler] ✅ Foundation abgeschlossen für {client}")
        return False

    logger.info(f"[FoundationScheduler] 🚀 Foundation-Post → {client} | {post['id']}")

    try:
        create_scheduled_post(client, post)
    except Exception as e:
        logger.error(f"[FoundationScheduler] ❌ Fehler ({client}): {e}")
        return True

    post["posted"] = True
    save_foundation(client, foundation)
    return True


# -------------------------------------------------
# MAIN LOOP
# -------------------------------------------------

def scheduler_loop():
    logger.info("🕓 IntelliAgent Foundation Scheduler gestartet")

    while True:
        for client in os.listdir(CLIENTS_DIR):
            client_dir = CLIENTS_DIR / client
            if not client_dir.is_dir():
                continue

            did_run = run_foundation_for_client(client)

            # 🔒 Sobald ein Foundation-Post erzeugt wurde:
            # KEIN weiterer Client in diesem Zyklus
            if did_run:
                logger.info("⏸ Foundation aktiv – weiterer Durchlauf pausiert")
                break

        time.sleep(POLL_INTERVAL_SECONDS)


if __name__ == "__main__":
    scheduler_loop()