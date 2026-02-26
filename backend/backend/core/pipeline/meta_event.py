"""
✅ FINAL — Meta Event Pipeline (IntelliAgent)
---------------------------------------------
- Nimmt rohe Meta Webhook Events entgegen
- Erkennt Lead-relevante Inhalte
- Normalisiert Daten
- Speichert Leads über core.lead_store
- KEINE Agenten
- KEINE Business-Logik
"""

from fastapi import APIRouter, Request
from typing import Dict, Any
from core.logger import logger
from core.leads_store import insert_lead

router = APIRouter(prefix="/pipeline", tags=["Pipeline"])


# ============================================================
# 🔍 Helper: Meta Payload Parsing
# ============================================================

def _extract_lead_from_entry(entry: Dict[str, Any], client: str):
    """
    Extrahiert Lead-Daten aus einem Meta Entry.
    Unterstützt:
    - Instagram / Facebook DMs
    - Kommentare
    """

    messaging = entry.get("messaging", [])
    changes = entry.get("changes", [])

    # --------------------------------------------------------
    # 1️⃣ Messenger / Instagram DM
    # --------------------------------------------------------
    for msg in messaging:
        message = msg.get("message", {}).get("text")

        if not message:
            continue

        logger.error(f"🔥 PIPELINE INSERT (DM) → client={client} message={message}")

        lead_id = insert_lead(
            client=client,
            source="meta_dm",
            platform="meta",
            name=None,
            email=None,
            phone=None,
            message=message,
            post_id=None,
            raw_payload=msg,
        )

        logger.error(f"✅ LEAD STORED (DM) → lead_id={lead_id}")

    # --------------------------------------------------------
    # 2️⃣ Kommentare / Feed Events
    # --------------------------------------------------------
    for change in changes:
        value = change.get("value", {})
        message = value.get("message") or value.get("comment")

        if not message:
            continue

        logger.error(f"🔥 PIPELINE INSERT (COMMENT) → client={client} message={message}")

        lead_id = insert_lead(
            client=client,
            source="meta_comment",
            platform="meta",
            name=None,
            email=None,
            phone=None,
            message=message,
            post_id=None,
            raw_payload=value,
        )

        logger.error(f"✅ LEAD STORED (COMMENT) → lead_id={lead_id}")


# ============================================================
# 🚀 Endpoint
# ============================================================

@router.post("/meta_event")
async def handle_meta_event(req: Request):
    payload = await req.json()

    logger.error(f"🔥 META_EVENT RECEIVED → keys={list(payload.keys())}")

    client = payload.get("client", "unknown")
    entries = payload.get("entry", [])

    if not entries:
        logger.warning("[MetaPipeline] ℹ️ Keine entry-Daten – übersprungen")
        return {"status": "ignored"}

    for entry in entries:
        try:
            _extract_lead_from_entry(entry, client)
        except Exception as e:
            logger.exception(f"[MetaPipeline] ❌ Fehler beim Verarbeiten eines Entries")

    return {"status": "ok"}