from fastapi import APIRouter, Request
from core.lead_store import insert_lead

router = APIRouter(prefix="/api/leads/meta", tags=["Leads"])


def normalize_meta_payload(payload: dict) -> dict:
    """
    Vereinheitlicht:
    - Meta Lead Ads
    - Instagram / Facebook DMs
    - Custom Meta Payloads (falls später nötig)
    """

    client = payload.get("client", "mtm_client")
    platform = payload.get("platform", "meta")
    source = payload.get("source", "meta")

    name = payload.get("name")
    email = payload.get("email")
    phone = payload.get("phone")
    message = payload.get("message")
    post_id = payload.get("post_id")

    # ----------------------------
    # 🔹 Meta DM Payload
    # ----------------------------
    entry = payload.get("entry", [])
    if entry:
        messaging = entry[0].get("messaging", [])
        if messaging:
            msg = messaging[0].get("message", {})
            message = msg.get("text", message)

    # ----------------------------
    # 🔹 Meta Lead Ads Payload
    # ----------------------------
    changes = entry[0].get("changes", []) if entry else []
    if changes:
        value = changes[0].get("value", {})
        for field in value.get("field_data", []):
            if field["name"] == "full_name":
                name = field["values"][0]
            elif field["name"] == "email":
                email = field["values"][0]
            elif field["name"] == "phone_number":
                phone = field["values"][0]

    return {
        "client": client,
        "source": source,
        "platform": platform,
        "name": name,
        "email": email,
        "phone": phone,
        "message": message or "Meta Lead",
        "post_id": post_id,
        "raw_payload": payload,
    }


@router.post("")
async def receive_meta_lead(request: Request):
    payload = await request.json()

    lead = normalize_meta_payload(payload)

    lead_id = insert_lead(
        client=lead["client"],
        source=lead["source"],
        platform=lead["platform"],
        name=lead["name"],
        email=lead["email"],
        phone=lead["phone"],
        message=lead["message"],
        post_id=lead["post_id"],
        raw_payload=lead["raw_payload"],
    )

    return {
        "status": "ok",
        "id": lead_id,
    }