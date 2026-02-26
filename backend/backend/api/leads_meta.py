from fastapi import APIRouter, Request
from backend.backend.core.leads_store import add_lead
import json

router = APIRouter(prefix="/api/leads", tags=["leads-meta"])

@router.post("/meta")
async def ingest_meta_lead(req: Request):
    payload = await req.json()

    # Meta DM Text extrahieren (robust)
    text = ""
    try:
        entry = payload["entry"][0]
        messaging = entry["messaging"][0]
        text = messaging.get("message", {}).get("text", "")
    except Exception:
        text = json.dumps(payload)

    lead = add_lead(
        client="mtm_client",
        raw_text=text,
        parsed={
            "source": "meta_dm",
            "platform": "instagram_or_facebook",
            "raw": payload,
        },
    )

    return {"ok": True, "lead_id": lead["id"]}