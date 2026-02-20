"""
✅ FINAL + STABLE VERSION — Meta Webhook Endpoint (IntelliAgent, Render Ready)
----------------------------------------------------------------------------
- Verifiziert den Meta Callback-Token (GET)
- Empfängt Echtzeit-Events (POST)
- Speichert Events als JSON-Lines
- Leitet Events optional in die interne Pipeline weiter
- Import- & Struktur-konsistent mit dem bestehenden Backend
"""

from fastapi import APIRouter, Request
from fastapi.responses import PlainTextResponse, JSONResponse
from datetime import datetime
from pathlib import Path
import os
import json
import requests

from core.logger import logger

# ============================================================
# 🔧 Router
# ============================================================
router = APIRouter(prefix="/meta", tags=["Meta Webhook"])

# ============================================================
# ⚙️ Konfiguration
# ============================================================
VERIFY_TOKEN = os.getenv("META_VERIFY_TOKEN", "intelliagent_webhook")

BACKEND_WEBHOOK_TARGET = os.getenv(
    "BACKEND_WEBHOOK_TARGET",
    "http://localhost:8000/pipeline/meta_event"
)

LOG_FILE = Path("logs/meta_events.jsonl")

# ============================================================
# 🌐 Root / Health
# ============================================================
@router.get("/")
async def root():
    return {
        "status": "ok",
        "service": "Meta Webhook",
        "version": "2.0",
    }


@router.get("/health")
async def health_check():
    return {
        "status": "ok",
        "verify_token": VERIFY_TOKEN,
    }

# ============================================================
# ✅ Meta Verification (GET)
# ============================================================
@router.get("/webhook")
async def verify_webhook(request: Request):
    mode = request.query_params.get("hub.mode")
    token = request.query_params.get("hub.verify_token")
    challenge = request.query_params.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        logger.info("✅ [MetaWebhook] Verifikation erfolgreich")
        return PlainTextResponse(challenge)

    logger.warning("❌ [MetaWebhook] Verifikation fehlgeschlagen")
    return PlainTextResponse("Verification failed", status_code=403)

# ============================================================
# 📩 Meta Event Empfang (POST)
# ============================================================
@router.post("/webhook")
async def receive_webhook(request: Request):
    try:
        data = await request.json()

        logger.info("📩 [MetaWebhook] Event empfangen")
        logger.debug(json.dumps(data, indent=2, ensure_ascii=False))

        # --------------------------------------------------------
        # 🧾 Event lokal loggen (JSON Lines)
        # --------------------------------------------------------
        try:
            LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
            with LOG_FILE.open("a", encoding="utf-8") as f:
                json.dump(
                    {
                        "timestamp": datetime.utcnow().isoformat(),
                        "data": data,
                    },
                    f,
                    ensure_ascii=False,
                )
                f.write("\n")
            logger.info("🧾 [MetaWebhook] Event geloggt")
        except Exception as log_err:
            logger.error(f"⚠️ [MetaWebhook] Log-Fehler: {log_err}")

        # --------------------------------------------------------
        # 🔁 Weiterleitung an interne Pipeline (NUR echte Events)
        # --------------------------------------------------------
        if BACKEND_WEBHOOK_TARGET and data.get("entry"):
            try:
                r = requests.post(
                    BACKEND_WEBHOOK_TARGET,
                    json=data,
                    timeout=5,
                )
                logger.info(
                    f"📤 [MetaWebhook] Weitergeleitet → {BACKEND_WEBHOOK_TARGET} "
                    f"(Status {r.status_code})"
                )
            except Exception as forward_err:
                logger.error(f"⚠️ [MetaWebhook] Weiterleitungsfehler: {forward_err}")

        return JSONResponse({"status": "received"}, status_code=200)

    except Exception as e:
        logger.error(f"❌ [MetaWebhook] Fehler beim Empfangen: {e}")
        return JSONResponse({"error": str(e)}, status_code=400)