from fastapi import APIRouter, HTTPException
from core.post_store import get_post_by_id, update_post
from api.dashboard_helpers import (
    PREVIEW_DIR,
    APPROVED_DIR,
    POSTING_QUEUE_DIR,
    _base_post_id,
    _utcnow_iso,
    _move_variants,
    _any_variants_exist,
)

router = APIRouter(prefix="/api/dashboard", tags=["dashboard-actions"])

@router.post("/approve/{post_id}")
def approve_post(post_id: str):
    base_id = _base_post_id(post_id)
    if not get_post_by_id(base_id):
        raise HTTPException(404)

    _move_variants(base_id, PREVIEW_DIR, APPROVED_DIR)
    update_post(base_id, {"status": "approved", "updated_at": _utcnow_iso()})
    return {"status": "approved"}

@router.post("/schedule/{post_id}")
def schedule_post(post_id: str):
    base_id = _base_post_id(post_id)

    if _any_variants_exist(base_id, APPROVED_DIR):
        _move_variants(base_id, APPROVED_DIR, POSTING_QUEUE_DIR)
    elif _any_variants_exist(base_id, PREVIEW_DIR):
        _move_variants(base_id, PREVIEW_DIR, POSTING_QUEUE_DIR)
    else:
        raise HTTPException(400, "No files")

    update_post(base_id, {"status": "scheduled", "updated_at": _utcnow_iso()})
    return {"status": "scheduled"}

@router.post("/post/{post_id}")
def post_post(post_id: str):
    base_id = _base_post_id(post_id)
    update_post(base_id, {"status": "posted", "posted_at": _utcnow_iso()})
    return {"status": "posted"}

# =================================================
# 🔵 LINKEDIN MANUAL POST CONFIRM
# =================================================
@router.post("/{client}/linkedin/mark-posted/{post_id}")
def mark_linkedin_posted(client: str, post_id: str):
    base_id = _base_post_id(post_id)

    post = get_post_by_id(base_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    update_post(
        base_id,
        {
            "status": "posted",
            "posted_at": _utcnow_iso(),
            "updated_at": _utcnow_iso(),
            "platform_status": {
                **(post.get("platform_status") or {}),
                "linkedin": "posted",
            },
        },
    )

    return {
        "status": "ok",
        "post_id": base_id,
        "platform": "linkedin",
    }
