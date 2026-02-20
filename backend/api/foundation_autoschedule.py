from core.platform_times import build_platform_times
from fastapi import APIRouter, HTTPException
from pathlib import Path
from datetime import datetime, timezone
import json

from core.post_store import get_post_by_id, update_post
from core.fs_utils import move_variants

router = APIRouter(prefix="/api/foundation", tags=["foundation"])

# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve()
while BASE_DIR.name != "backend":
    BASE_DIR = BASE_DIR.parent

CLIENTS_DIR = BASE_DIR / "clients"

# 👉 MUSS hier definiert sein (nicht aus dashboard importieren!)
def _posting_queue_dir(client: str) -> Path:
    return CLIENTS_DIR / client / "output" / "posting_queue"


def _approved_dir(client: str) -> Path:
    return CLIENTS_DIR / client / "output" / "approved"


# ============================================================
# AUTOSCHEDULE FOUNDATION POSTS
# ============================================================

@router.post("/autoschedule/{client}")
def autoschedule_foundation(client: str):
    client_dir = CLIENTS_DIR / client
    schedule_path = client_dir / "content_rules" / "foundation_schedule.json"

    if not schedule_path.exists():
        raise HTTPException(
            status_code=404,
            detail=f"foundation_schedule.json fehlt unter {schedule_path}",
        )

    data = json.loads(schedule_path.read_text(encoding="utf-8"))
    posts = data.get("posts", [])

    if not posts:
        return {
            "status": "noop",
            "reason": "keine Posts im foundation_schedule.json",
        }

    approved_dir = _approved_dir(client)
    posting_queue_dir = _posting_queue_dir(client)
    posting_queue_dir.mkdir(parents=True, exist_ok=True)

    scheduled: list[str] = []

    for entry in posts:
        post_id = entry.get("id")
        publish_at = entry.get("publish_at")

        if not post_id or not publish_at:
            continue

        post = get_post_by_id(post_id)
        if not post:
            continue

        if post.get("status") != "approved":
            continue

        # 🔁 approved → posting_queue
        move_variants(
            base_id=post_id,
            src_dir=approved_dir,
            dst_dir=posting_queue_dir,
        )

        update_post(
            post_id,
            {
                "status": "scheduled",
                "platform_times": build_platform_times(),
                "publish_at": publish_at,
                "updated_at": datetime.now(timezone.utc).isoformat(),
            },
        )

        scheduled.append(post_id)

    return {
        "status": "ok",
        "scheduled": scheduled,
        "count": len(scheduled),
    }