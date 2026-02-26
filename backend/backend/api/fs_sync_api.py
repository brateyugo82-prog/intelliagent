from fastapi import APIRouter
from core.fs_sync import sync_client

router = APIRouter(prefix="/api/fs", tags=["fs-sync"])

@router.post("/resync/{client}")
def resync(client: str):
    posts = sync_client(client)
    return {
        "status": "ok",
        "posts": len(posts),
    }
