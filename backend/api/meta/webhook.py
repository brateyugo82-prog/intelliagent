"""
✅ FINAL VERSION – Meta Webhook Endpoint
---------------------------------------------------
Verifiziert den Meta Callback-Token (GET)
und empfängt Echtzeit-Events (POST).
"""

from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse, JSONResponse
import os
import requests
import json

app = FastAPI(title="Meta Webhook API", version="1.0")

# ===== Konfiguration aus .env =====
VERIFY_TOKEN = os.getenv("META_VERIFY_TOKEN", "intelliagent_webhook")
BACKEND_WEBHOOK_TARGET = os.getenv("BACKEND_WEBHOOK_TARGET", "http://localhost:8000/meta_events")

# ===== Root Endpoint für Render Health-Check =====
@app.api_route("/", methods=["GET", "HEAD"])
async def root():
    """
    Root-Endpoint, damit Render und andere Health-Checks 200 OK erhalten.
    Akzeptiert GET und HEAD, um 405 zu vermeiden.
    """
    return {
        "status": "ok",
        "service": "IntelliAgent Backend running",
        "version": "1.0"
    }

@app.get("/meta/webhook")
async def verify_webhook(request: Request):
    """
    Wird von Meta beim Einrichten des Webhooks aufgerufen.
    Prüft den Token und gibt den Challenge-Code zurück.
    """
    mode = request.query_params.get("hub.mode")
    token = request.query_params.get("hub.verify_token")
    challenge = request.query_params.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        print("✅ Webhook-Verification erfolgreich!")
        return PlainTextResponse(challenge)
    else:
        print("❌ Webhook-Verification fehlgeschlagen.")
        return PlainTextResponse("Verification failed", status_code=403)

@app.post("/meta/webhook")
async def receive_webhook(request: Request):
    """
    Empfängt Events von Meta (z. B. neue Kommentare, Nachrichten, Posts)
    und leitet sie an dein internes Backend weiter.
    """
    try:
        data = await request.json()
        print("📩 Meta Event empfangen:")
        print(json.dumps(data, indent=2, ensure_ascii=False))

        # Optional: Weiterleiten ans interne Backend (z. B. Logging oder DB)
        try:
            response = requests.post(BACKEND_WEBHOOK_TARGET, json=data, timeout=5)
            print(f"📤 Weitergeleitet an Backend (Status {response.status_code})")
        except Exception as forward_err:
            print(f"⚠️ Fehler beim Weiterleiten: {forward_err}")

        return JSONResponse({"status": "received"}, status_code=200)

    except Exception as e:
        print(f"❌ Fehler beim Empfangen: {e}")
        return JSONResponse({"error": str(e)}, status_code=400)

@app.get("/health")
async def health_check():
    """
    Health-Check-Endpunkt für Meta oder Render/Vercel
    """
    return {"status": "ok", "verify_token": VERIFY_TOKEN}
