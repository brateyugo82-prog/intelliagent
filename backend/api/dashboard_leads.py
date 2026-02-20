from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from collections import Counter

from core.lead_store import list_leads, update_status

router = APIRouter(prefix="/api/dashboard", tags=["dashboard-leads"])


class LeadStatusPayload(BaseModel):
    status: str


@router.get("/{client}/leads")
def get_dashboard_leads(client: str):
    return [l for l in list_leads() if l.get("client") == client]


@router.get("/{client}/leads/stats")
def get_dashboard_lead_stats(client: str):
    leads = [l for l in list_leads() if l.get("client") == client]

    by_status = Counter()
    by_source = Counter()

    for l in leads:
        if l.get("status"):
            by_status[l["status"]] += 1
        if l.get("source"):
            by_source[l["source"]] += 1

    return {
        "total": len(leads),
        "by_status": dict(by_status),
        "by_source": dict(by_source),
    }


@router.patch("/{client}/leads/{lead_id}")
def update_dashboard_lead_status(
    client: str,
    lead_id: str,
    payload: LeadStatusPayload,
):
    lead = update_status(lead_id, payload.status)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    return {
        "status": "ok",
        "lead_id": lead_id,
        "new_status": payload.status,
    }
