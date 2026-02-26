from fastapi import APIRouter, HTTPException
from backend.backend.core.leads_store import (
    list_leads,
    add_lead,
    update_status,
)

router = APIRouter(prefix="/api/dashboard/mtm", tags=["leads"])


# ===============================
# 📥 GET ALL LEADS
# ===============================
@router.get("/leads")
def get_leads():
    return list_leads()


# ===============================
# 📥 INGEST LEAD (Website / Meta / etc.)
# ===============================
@router.post("/ingest")
def ingest_lead(payload: dict):
    text = payload.get("message") or payload.get("text") or ""

    return add_lead(
        client=payload.get("client", "mtm_client"),
        raw_text=text,
        parsed={
            "source": payload.get("source"),
            "platform": payload.get("platform"),
            "name": payload.get("name"),
            "email": payload.get("email"),
            "phone": payload.get("phone"),
            "message": payload.get("message"),
            "post_id": payload.get("post_id"),
        },
    )


# ===============================
# 🔁 UPDATE LEAD STATUS  ← DAS FEHLTE
# ===============================
@router.patch("/leads/{lead_id}")
def set_lead_status(lead_id: str, status: str):
    updated = update_status(lead_id, status)
    if not updated:
        raise HTTPException(status_code=404, detail="Lead not found")
    return {"ok": True, "lead": updated}
from collections import Counter

@router.get("/leads/status")
def lead_status_stats(client: str | None = None):
    leads = list_leads()

    if client:
        leads = [l for l in leads if l.get("client") == client]

    total = len(leads)
    by_status = Counter(l.get("status", "raw") for l in leads)
    by_source = Counter(l.get("parsed", {}).get("source", "unknown") for l in leads)

    return {
        "stats": {
            "total": total,
            "by_status": dict(by_status),
            "by_source": dict(by_source),
        }
    }

from backend.backend.core.leads_store import update_status

@router.patch("/leads/{lead_id}")
def set_lead_status(lead_id: str, status: str):
    lead = update_status(lead_id, status)
    if not lead:
        return {"error": "not found"}
    return lead
