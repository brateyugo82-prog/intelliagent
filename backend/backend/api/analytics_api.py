from fastapi import APIRouter

router = APIRouter(prefix="/api/dashboard", tags=["analytics"])

@router.get("/{client}/analytics")
def get_analytics(client: str):
    return {
        "client": client,
        "posts": {"preview": 0, "approved": 0, "scheduled": 0, "posted": 0},
        "leads": {"total": 0, "qualified": 0},
        "note": "stub"
    }
