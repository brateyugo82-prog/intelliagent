"""
✅ FINAL + STABLE VERSION – Meta Webhook Endpoint (Render Ready)
--------------------------------------------------------------------
Verifiziert den Meta Callback-Token (GET),
empfängt Echtzeit-Events (POST),
und speichert sie lokal oder leitet sie intern weiter.
"""

from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse, JSONResponse
import os
import requests
import json
from datetime import datetime
from pathlib import Path

app = FastAPI(title="Meta Webhook API", version="2.0")

# ===== Konfiguration aus .env =====
VERIFY_TOKEN = os.getenv("META_VERIFY_TOKEN", "intelliagent_webhook")
BACKEND_WEBHOOK_TARGET = os.getenv(
    "BACKEND_WEBHOOK_TARGET",
    "https://intelliagent-backend.onrender.com/meta_events"
)
LOG_FILE = Path("backend/logs/meta_events.json")

# ===== Root Endpoint (Render Health) =====
@app.api_route("/", methods=["GET", "HEAD"])
async def root():
    return {
        "status": "ok",
        "service": "IntelliAgent Backend running",
        "version": "2.0"
    }

# ===== Meta Verification =====
@app.get("/meta/webhook")
async def verify_webhook(request: Request):
    mode = request.query_params.get("hub.mode")
    token = request.query_params.get("hub.verify_token")
    challenge = request.query_params.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        print("✅ Webhook-Verification erfolgreich!")
        return PlainTextResponse(challenge)
    else:
        print("❌ Webhook-Verification fehlgeschlagen.")
        return PlainTextResponse("Verification failed", status_code=403)

# ===== Haupt-WebHook Endpoint =====
@app.post("/meta/webhook")
async def receive_webhook(request: Request):
    """
    Empfängt Events von Meta (z. B. neue Kommentare, Nachrichten, Posts)
    und leitet sie intern weiter oder speichert sie.
    """
    try:
        data = await request.json()
        print("📩 Meta Event empfangen:")
        print(json.dumps(data, indent=2, ensure_ascii=False))

        # 🔹 Event-Logging speichern
        try:
            LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
            with open(LOG_FILE, "a", encoding="utf-8") as f:
                json.dump(
                    {"timestamp": datetime.now().isoformat(), "data": data},
                    f,
                    ensure_ascii=False,
                )
                f.write("\n")
            print("🧾 Event gespeichert in logs/meta_events.json")
        except Exception as log_err:
            print(f"⚠️ Fehler beim Speichern der Logs: {log_err}")

        # 🔹 Weiterleitung ans Backend
        try:
            response = requests.post(BACKEND_WEBHOOK_TARGET, json=data, timeout=5)
            print(f"📤 Weitergeleitet an Backend (Status {response.status_code})")
        except Exception as forward_err:
            print(f"⚠️ Fehler beim Weiterleiten: {forward_err}")

        return JSONResponse({"status": "received"}, status_code=200)

    except Exception as e:
        print(f"❌ Fehler beim Empfangen: {e}")
        return JSONResponse({"error": str(e)}, status_code=400)


# ===== Interner Event-Handler =====
@app.post("/meta_events")
async def handle_meta_events(request: Request):
    """
    Dieser Endpoint verarbeitet interne Events,
    wenn BACKEND_WEBHOOK_TARGET auf dieselbe App zeigt.
    """
    try:
        data = await request.json()
        print("🧩 /meta_events aufgerufen – Daten empfangen:")
        print(json.dumps(data, indent=2, ensure_ascii=False))
        return JSONResponse({"status": "meta_event_stored"}, status_code=200)
    except Exception as e:
        print(f"❌ Fehler beim internen Event-Handler: {e}")
        return JSONResponse({"error": str(e)}, status_code=400)


# ===== Health Endpoint =====
@app.get("/health")
async def health_check():
    return {"status": "ok", "verify_token": VERIFY_TOKEN}
