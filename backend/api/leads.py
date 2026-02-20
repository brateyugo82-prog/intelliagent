from fastapi import APIRouter, Query
from core.lead_store import list_leads
from core.lead_qualifier import qualify_lead

router = APIRouter(prefix="/api/leads", tags=["leads"])


@router.get("/")
def get_leads(
    client: str | None = Query(default=None),
    status: str | None = Query(default=None),
):
    leads = list_leads()

    if client:
        leads = [l for l in leads if l.get("client") == client]

    if status:
        leads = [l for l in leads if l.get("status") == status]

    return leads


@router.post("/ingest")
def ingest_lead(payload: dict):
    text = payload.get("text", "")
    client = payload.get("client", "mtm_client")
    return qualify_lead(client, text)
