from fastapi import APIRouter
from datetime import datetime, timedelta
from pathlib import Path

router = APIRouter(prefix="/api/stats", tags=["Stats"])

# ============================================================
# 🔐 TOKEN FILES (relativ zum backend/)
# ============================================================

BACKEND_DIR = Path(__file__).resolve()
while BACKEND_DIR.name != "backend":
    BACKEND_DIR = BACKEND_DIR.parent

TOKEN_FILES = {
    "meta": BACKEND_DIR / "scheduler" / "meta_token.txt",
    "linkedin": BACKEND_DIR / "scheduler" / "linkedin_token.txt",
    "tiktok": BACKEND_DIR / "scheduler" / "tiktok_token.txt",
}

REFRESH_INTERVAL_DAYS = 60


def token_status(platform: str, file_path: Path):
    if not file_path.exists():
        return {
            "platform": platform,
            "status": "missing",
            "last_refresh": None,
            "next_refresh": None,
        }

    mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
    next_refresh = mtime + timedelta(days=REFRESH_INTERVAL_DAYS)

    return {
        "platform": platform,
        "status": "ok" if datetime.now() < next_refresh else "expired",
        "last_refresh": mtime.isoformat(),
        "next_refresh": next_refresh.isoformat(),
    }


@router.get("/tokens")
async def get_token_status():
    return {
        "tokens": [
            token_status(platform, path)
            for platform, path in TOKEN_FILES.items()
        ]
    }

# ============================================================
# 📊 LEAD STATS
# ============================================================

from core.lead_store import list_leads

@router.get("/leads/summary")
async def lead_summary(period: str = "30d"):
    """
    Lead Analytics Summary
    period: 1d | 7d | 30d
    """

    days_map = {
        "1d": 1,
        "7d": 7,
        "30d": 30,
    }
    days = days_map.get(period, 30)
    since = datetime.utcnow() - timedelta(days=days)

    leads = list_leads()
    
    filtered = [
        l for l in leads
        if datetime.fromisoformat(l["created_at"]) >= since
    ]
    
    total = len(filtered)
    
    by_status = {}
    for l in filtered:
        status = l.get("status", "unknown")
        by_status[status] = by_status.get(status, 0) + 1
    
    by_source = {}
    for l in filtered:
        source = l.get("parsed", {}).get("source", "unknown")
        by_source[source] = by_source.get(source, 0) + 1

    return {
        "period": period,
        "since": since.isoformat(),
        "total": total,
        "by_status": by_status,
        "by_source": by_source,
    }