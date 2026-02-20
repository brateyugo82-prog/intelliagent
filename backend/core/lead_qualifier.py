from datetime import datetime, timedelta, timezone
from core.lead_parser import parse_lead_text
from core.lead_store import add_lead, is_duplicate, update_status
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]

def load_policy(client: str):
    with open(BASE_DIR / "clients" / client / "policies" / "lead_qualification.json") as f:
        return json.load(f)

def qualify_lead(client: str, text: str):
    policy = load_policy(client)

    if is_duplicate(text, policy["duplicate_window_days"]):
        return {"status": "duplicate"}

    parsed = parse_lead_text(text, client)
    lead = add_lead(client, text, parsed)

    # Pflichtfelder
    if not parsed["is_relevant_service"]:
        update_status(lead["id"], "invalid")
        return {"lead_id": lead["id"], "status": "invalid"}

    if not parsed["has_phone"]:
        update_status(lead["id"], "warm")
        return {"lead_id": lead["id"], "status": "warm"}

    update_status(lead["id"], "qualified")
    return {"lead_id": lead["id"], "status": "qualified"}
