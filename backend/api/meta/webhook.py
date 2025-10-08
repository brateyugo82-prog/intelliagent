# backend/api/meta/webhook.py

from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse

app = FastAPI()

@app.get("/api/meta/webhook")
async def verify_webhook(request: Request):
    """
    Validierung für Meta / Instagram Webhook.
    Meta ruft diesen Endpoint mit ?hub.mode, ?hub.verify_token und ?hub.challenge auf.
    Wenn Token korrekt, dann gib den hub.challenge-Wert im Klartext zurück.
    """
    mode = request.query_params.get("hub.mode")
    token = request.query_params.get("hub.verify_token")
    challenge = request.query_params.get("hub.challenge")

    VERIFY_TOKEN = "intelliagent_webhook"  # <- das muss mit dem Token im Meta-Dashboard übereinstimmen

    if mode == "subscribe" and token == VERIFY_TOKEN:
        return PlainTextResponse(challenge, status_code=200)
    return PlainTextResponse("verification failed", status_code=403)
