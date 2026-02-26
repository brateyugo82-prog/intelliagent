from fastapi import APIRouter
from pathlib import Path

from backend.backend.core.post_store import get_posts, ensure_post_exists
from backend.backend.core.post_ids import base_post_id
from backend.backend.core.categories import safe_category

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])

CLIENT = "mtm_client"
BASE_DIR = Path(__file__).resolve().parents[1]
CLIENT_DIR = BASE_DIR / "clients" / CLIENT


@router.get("/mtm/posts")
def get_dashboard_posts():
    posts = get_posts(CLIENT)

    preview, approved, scheduled, posted = [], [], [], []

    for p in posts:
        base_id = base_post_id(p.get("id", ""))
        if base_id:
            try:
                ensure_post_exists(base_id, CLIENT)
            except Exception:
                pass

        status = (p.get("status") or "preview").lower()

        item = {
            "id": p.get("id"),
            "preview": p.get("preview"),
            "caption": p.get("caption"),
            "category": safe_category(p.get("category")),
            "status": status,
            "results": p.get("results"),
            "created_at": p.get("created_at"),
            "updated_at": p.get("updated_at"),
        }

        if status == "approved":
            approved.append(item)
        elif status == "scheduled":
            scheduled.append(item)
        elif status == "posted":
            posted.append(item)
        else:
            preview.append(item)

    return {
        "preview": preview,
        "approved": approved,
        "scheduled": scheduled,
        "posted": posted,
    }
