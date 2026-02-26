"""
✅ FINAL + STABLE VERSION — Meta Webhook Endpoint (IntelliAgent)
"""

from fastapi import APIRouter, Request
from fastapi.responses import PlainTextResponse, JSONResponse
from datetime import datetime
from pathlib import Path
import os
import json
import requests

from core.logger import logger

router = APIRouter(prefix="/meta", tags=["Meta Webhook"])

VERIFY_TOKEN = os.getenv("META_VERIFY_TOKEN", "intelliagent_webhook")

BACKEND_WEBHOOK_TARGET = os.getenv(
    "BACKEND_WEBHOOK_TARGET",
    "http://localhost:8000/pipeline/meta_event"
)

LOG_FILE = Path("logs/meta_events.jsonl")


@router.get("/health")
async def health():
    return {"status": "ok"}


@router.get("/webhook")
async def verify_webhook(request: Request):
    mode = request.query_params.get("hub.mode")
    token = request.query_params.get("hub.verify_token")
    challenge = request.query_params.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        logger.info("✅ Meta Webhook verified")
        return PlainTextResponse(challenge)

    logger.warning("❌ Meta Webhook verification failed")
    return PlainTextResponse("Verification failed", status_code=403)


@router.post("/webhook")
async def receive_webhook(request: Request):
    data = await request.json()

    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with LOG_FILE.open("a", encoding="utf-8") as f:
        json.dump(
            {"timestamp": datetime.utcnow().isoformat(), "data": data},
            f,
            ensure_ascii=False,
        )
        f.write("\n")

    if data.get("entry"):
        try:
            requests.post(BACKEND_WEBHOOK_TARGET, json=data, timeout=5)
        except Exception as e:
            logger.error(f"Forward failed: {e}")

    return JSONResponse({"status": "received"})
