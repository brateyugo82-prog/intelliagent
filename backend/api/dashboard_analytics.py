from fastapi import APIRouter, HTTPException
from pathlib import Path
import json

router = APIRouter(prefix="/api/dashboard", tags=["dashboard-analytics"])

BASE_DIR = Path(__file__).resolve().parents[1]  # backend/
CLIENTS_DIR = BASE_DIR / "clients"


@router.get("/{client}/analytics")
def get_dashboard_analytics(client: str):
    """
    Liest Analytics ausschließlich aus:
    clients/{client}/state/analytics_summary.json
    """

    summary_path = CLIENTS_DIR / client / "state" / "analytics_summary.json"

    if not summary_path.exists():
        return {
            "status": "empty",
            "client": client,
            "analytics": None,
            "leads": {
                "total": 0,
                "by_status": {},
                "by_source": {},
            },
        }

    try:
        summary = json.loads(summary_path.read_text(encoding="utf-8"))
    except Exception as e:
        raise HTTPException(500, f"analytics_summary.json invalid: {e}")

    return {
        "status": "ok",
        "client": client,
        "analytics": {k: v for k, v in summary.items() if k != "leads"},
        "leads": summary.get(
            "leads",
            {
                "total": 0,
                "by_status": {},
                "by_source": {},
            },
        ),
    }
