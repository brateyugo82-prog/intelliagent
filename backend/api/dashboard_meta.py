from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from core.post_store import get_post_by_id, update_post
from api.dashboard_helpers import _base_post_id, _utcnow_iso, _safe_category

router = APIRouter(prefix="/api/dashboard", tags=["dashboard-meta"])

class UpdateMetaPayload(BaseModel):
    category: str | None = None
    caption: str | None = None
    platform: str | None = None

@router.post("/update-meta/{post_id}")
def update_meta(post_id: str, payload: UpdateMetaPayload):
    base_id = _base_post_id(post_id)
    post = get_post_by_id(base_id)
    if not post:
        raise HTTPException(404)

    patch = {"updated_at": _utcnow_iso()}
    if payload.caption:
        patch["caption"] = payload.caption
    if payload.category:
        patch["category"] = _safe_category(payload.category)

    update_post(base_id, patch)
    return {"status": "ok"}
