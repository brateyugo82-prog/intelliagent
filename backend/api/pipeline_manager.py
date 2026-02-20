"""
✅ FINAL + STABLE VERSION — IntelliAgent Pipeline Manager
------------------------------------------------------------
Zentrale Steuerung der Multi-Agenten-Pipeline:

✅ NEU (STABIL):
- /pipeline/meta_lead  -> speichert Leads SOFORT (keine Agenten)

Bestehend:
- /pipeline/meta_event -> Agenten-Workflow (kann lange dauern)
"""

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from datetime import datetime
from typing import Dict, Any

from core.logger import logger
from core import memory
from core.lead_store import insert_lead

from agents import communication_agent, publish_agent, analytics_agent

router = APIRouter(prefix="/pipeline", tags=["Pipeline"])


# ============================================================
# ✅ A) FAST LEAD PIPELINE (NO AGENTS) — hängt NICHT
# ============================================================

def _extract_leads_from_entry(entry: Dict[str, Any], client: str) -> int:
    """
    Minimaler Lead-Extractor für Meta Payloads.
    Speichert nur, wenn Text vorhanden ist.
    """
    saved = 0

    # 1) Messaging (IG DM / Messenger)
    for msg in entry.get("messaging", []):
        text = (msg.get("message") or {}).get("text")
        if not text:
            continue

        insert_lead(
            source="meta_dm",
            platform="meta",
            client=client,
            name=None,
            email=None,
            phone=None,
            message=text,
            raw_payload=msg,
        )
        saved += 1

    # 2) Changes (Kommentare / Feed)
    for change in entry.get("changes", []):
        value = change.get("value") or {}
        text = value.get("message") or value.get("comment")
        if not text:
            continue

        insert_lead(
            source="meta_comment",
            platform="meta",
            client=client,
            name=None,
            email=None,
            phone=None,
            message=text,
            raw_payload=value,
        )
        saved += 1

    return saved


@router.post("/meta_lead")
async def process_meta_lead(request: Request):
    """
    ✅ Speichert Leads sofort.
    ❌ Keine Agenten.
    ❌ Keine Business-Logik.
    """
    try:
        event = await request.json()
        client = event.get("client", "unknown")
        entries = event.get("entry", [])

        if not entries:
            return JSONResponse({"status": "ignored", "reason": "no_entries"}, status_code=200)

        saved_total = 0
        for entry in entries:
            saved_total += _extract_leads_from_entry(entry, client)

        logger.info(f"✅ [PipelineLead] saved={saved_total} client={client}")
        return JSONResponse({"status": "ok", "saved": saved_total, "client": client}, status_code=200)

    except Exception as e:
        logger.error(f"❌ [PipelineLead] Fehler: {e}")
        return JSONResponse({"status": "error", "error": str(e)}, status_code=400)


# ============================================================
# ✅ B) AGENT PIPELINE (kann lange dauern)
# ============================================================

@router.post("/meta_event")
async def process_meta_event(request: Request):
    """
    Wird aufgerufen, wenn Meta ein Event (z. B. Kommentar, Nachricht) sendet.
    Führt automatisch den kompletten Agenten-Workflow aus.
    """
    try:
        event = await request.json()

        logger.info("📩 [Pipeline] Neues Meta-Event empfangen")
        logger.info(event)

        # --------------------------------------------------
        # 🧠 Basisdaten extrahieren (Meta-kompatibel + Fallback)
        # --------------------------------------------------
        entry = event.get("entry", [{}])[0]
        changes = entry.get("changes", [{}])[0]
        value = changes.get("value", {})

        client_name = value.get("client") or "MTM"
        prompt_text = (
            value.get("message")
            or value.get("text")
            or "Neuer Social-Media-Input erkannt."
        )

        # --------------------------------------------------
        # 💬 1️⃣ Communication-Agent
        # --------------------------------------------------
        logger.info("💬 [Pipeline] Communication-Agent startet")

        comm_result = communication_agent.run(
            prompt=prompt_text,
            client=client_name,
            platform="social"
        )

        if not comm_result or "output" not in comm_result:
            raise RuntimeError("Communication-Agent lieferte kein gültiges Ergebnis")

        # --------------------------------------------------
        # 🚀 2️⃣ Publishing-Agent (PREVIEW / AUTO)
        # --------------------------------------------------
        logger.info("🚀 [Pipeline] Publishing-Agent startet")

        pub_result = publish_agent.run(
            prompt=comm_result["output"],
            client=client_name,
            platform="facebook,instagram",
            mode="auto"
        )

        # --------------------------------------------------
        # 📊 3️⃣ Analytics-Agent
        # --------------------------------------------------
        logger.info("📊 [Pipeline] Analytics-Agent startet")

        ana_result = analytics_agent.run(
            prompt=comm_result["output"],
            client=client_name,
            platform="social"
        )

        # --------------------------------------------------
        # 🧠 4️⃣ Memory Persistenz
        # --------------------------------------------------
        pipeline_key = f"pipeline:{client_name}:{datetime.now().isoformat()}"

        memory.remember(
            client_name,
            pipeline_key,
            {
                "input": prompt_text,
                "communication": comm_result,
                "publishing": pub_result,
                "analytics": ana_result,
                "timestamp": datetime.now().isoformat(),
            },
        )

        logger.info("✅ [Pipeline] Verarbeitung abgeschlossen")

        return JSONResponse(
            {
                "status": "ok",
                "pipeline": {
                    "input": prompt_text,
                    "communication": comm_result,
                    "publishing": pub_result,
                    "analytics": ana_result,
                },
            },
            status_code=200,
        )

    except Exception as e:
        logger.error(f"❌ [Pipeline] Fehler: {e}")
        return JSONResponse(
            {"status": "error", "error": str(e)},
            status_code=400,
        )