from fastapi import APIRouter
from core.post_store import get_posts, ensure_post_exists
from api.dashboard_helpers import (
    CLIENT,
    _base_post_id,
    _pick_existing_preview,
    _best_caption,
    _safe_category,
)

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])

@router.get("/{client}/posts")
def get_dashboard_posts(client: str):
    posts = get_posts(client)
    preview, approved, scheduled, posted = [], [], [], []

    for p in posts:
        base_id = _base_post_id(p.get("id", ""))
        if base_id:
            try:
                ensure_post_exists(base_id, client=client)
            except Exception:
                pass

        status = (p.get("status") or "preview").lower()

        item = {
            "id": p.get("id"),
            "preview": _pick_existing_preview(p),
            "caption": _best_caption(p),
            "category": _safe_category(p.get("category")),
            "status": status,
            "results": p.get("results") or {},
            "publish_at": p.get("publish_at"),
            "posted_at": p.get("posted_at"),
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
