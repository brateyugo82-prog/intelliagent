from datetime import datetime, timedelta, timezone
from core.leads_store import list_leads, update_status
from pathlib import Path
import json

BASE_DIR = Path(__file__).resolve().parents[1]

def load_policy(client):
    with open(BASE_DIR / "clients" / client / "policies" / "lead_qualification.json") as f:
        return json.load(f)

def run(client: str):
    policy = load_policy(client)
    hours = policy["silence_equals_approval_hours"]
    now = datetime.now(timezone.utc)

    for l in list_leads():
        if l["client"] != client:
            continue
        if l["status"] != "warm":
            continue

        updated = datetime.fromisoformat(l["updated_at"])
        if now - updated >= timedelta(hours=hours):
            update_status(l["id"], "qualified")
            print(f"✅ Silence-Approved: {l['id']}")
