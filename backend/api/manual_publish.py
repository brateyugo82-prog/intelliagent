from fastapi import APIRouter
from tools.finalize_post import finalize_manual_post

router = APIRouter(prefix="/api/manual", tags=["manual"])

@router.post("/posted/{client}/{post_id}/{platform}")
def mark_manual_posted(client: str, post_id: str, platform: str):
    return finalize_manual_post(client, post_id, platform)
