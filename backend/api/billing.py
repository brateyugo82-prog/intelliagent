from fastapi import APIRouter, Query
from datetime import datetime, timedelta, timezone
from core.lead_store import list_leads

router = APIRouter(prefix="/api/billing", tags=["billing"])

PRICE_PER_LEAD = 15  # EUR


def week_range_utc(now=None):
    if not now:
        now = datetime.now(timezone.utc)
    start = now - timedelta(days=now.weekday())
    start = start.replace(hour=0, minute=0, second=0, microsecond=0)
    end = start + timedelta(days=7)
    return start, end


@router.get("/weekly")
def billing_weekly(client: str = Query(...)):
    start, end = week_range_utc()

    leads = [
        l for l in list_leads()
        if l.get("client") == client
        and l.get("status") == "converted"
        and start <= datetime.fromisoformat(l["updated_at"]) < end
    ]

    return {
        "status": "ok",
        "client": client,
        "period": {
            "from": start.isoformat(),
            "to": end.isoformat(),
        },
        "price_per_lead": PRICE_PER_LEAD,
        "converted_leads": len(leads),
        "amount_eur": len(leads) * PRICE_PER_LEAD,
        "lead_ids": [l["id"] for l in leads],
    }
