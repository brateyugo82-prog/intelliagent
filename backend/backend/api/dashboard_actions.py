from fastapi import APIRouter, HTTPException
from datetime import datetime

from backend.backend.core.post_store import get_post_by_id, update_post, ensure_post_exists

from backend.backend.api.helpers.dashboard_helpers import (
    CLIENT,
    PREVIEW_DIR,
    APPROVED_DIR,
    POSTING_QUEUE_DIR,
    POSTED_DIR,
    base_post_id,
    any_variants_exist,
    move_variants,
    utcnow_iso,
)

router = APIRouter(prefix="/api/dashboard", tags=["dashboard-actions"])

# =================================================
# APPROVE
# =================================================

@router.post("/approve/{post_id}")
def approve_post(post_id: str):
    base_id = base_post_id(post_id)
    ensure_post_exists(base_id, client=CLIENT)

    # 🔁 preview → posting_queue
    if any_variants_exist(base_id, PREVIEW_DIR):
        move_variants(base_id, PREVIEW_DIR, POSTING_QUEUE_DIR)
    elif any_variants_exist(base_id, APPROVED_DIR):
        move_variants(base_id, APPROVED_DIR, POSTING_QUEUE_DIR)

    update_post(
        base_id,
        {
            "status": "scheduled",
            "publish_at": utcnow_iso(),
            "updated_at": utcnow_iso(),
        },
    )

    return {"status": "scheduled", "post_id": base_id}



# =================================================
# SCHEDULE
# =================================================
@router.post("/schedule/{post_id}")
def schedule_post(post_id: str, payload: dict):
    base_id = base_post_id(post_id)
    ensure_post_exists(base_id, client=CLIENT)

    if any_variants_exist(base_id, APPROVED_DIR):
        move_variants(base_id, APPROVED_DIR, POSTING_QUEUE_DIR)
    elif any_variants_exist(base_id, PREVIEW_DIR):
        move_variants(base_id, PREVIEW_DIR, POSTING_QUEUE_DIR)
    else:
        raise HTTPException(400, "No files to schedule")

    update_post(
        base_id,
        {
            "status": "scheduled",
            "publish_at": payload.get("publish_at"),
            "updated_at": utcnow_iso(),
        },
    )

    return {"status": "scheduled", "post_id": base_id}


# =================================================
# POST
# =================================================
@router.post("/post/{post_id}")
def post_post(post_id: str):
    base_id = base_post_id(post_id)
    ensure_post_exists(base_id, client=CLIENT)

    moved = False

    if any_variants_exist(base_id, POSTING_QUEUE_DIR):
        moved = move_variants(base_id, POSTING_QUEUE_DIR, POSTED_DIR)
    elif any_variants_exist(base_id, APPROVED_DIR):
        moved = move_variants(base_id, APPROVED_DIR, POSTED_DIR)

    if not moved:
        raise HTTPException(400, "No files to post")

    update_post(
        base_id,
        {
            "status": "posted",
            "posted_at": utcnow_iso(),
            "updated_at": utcnow_iso(),
        },
    )

    return {"status": "posted", "post_id": base_id}


# =================================================
# REVERT
# =================================================
@router.post("/revert/{post_id}")
def revert_post(post_id: str):
    base_id = base_post_id(post_id)
    ensure_post_exists(base_id, client=CLIENT)

    move_variants(base_id, APPROVED_DIR, PREVIEW_DIR)
    move_variants(base_id, POSTING_QUEUE_DIR, PREVIEW_DIR)
    move_variants(base_id, POSTED_DIR, PREVIEW_DIR)

    update_post(
        base_id,
        {
            "status": "preview",
            "updated_at": utcnow_iso(),
        },
    )

    return {"status": "reverted", "post_id": base_id}
