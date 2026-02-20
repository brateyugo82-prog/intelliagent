import json
from pathlib import Path
from datetime import datetime, timedelta, timezone
from hashlib import sha256

BASE_DIR = Path(__file__).resolve().parents[1]
DB_DIR = BASE_DIR / "db"
DB_DIR.mkdir(exist_ok=True)
LEADS_FILE = DB_DIR / "leads.json"

def _now():
    return datetime.now(timezone.utc)

def _load():
    if not LEADS_FILE.exists():
        return []
    return json.loads(LEADS_FILE.read_text())

def _save(leads):
    LEADS_FILE.write_text(json.dumps(leads, indent=2, ensure_ascii=False))

def _fingerprint(text: str):
    return sha256(text.strip().lower().encode()).hexdigest()

def is_duplicate(text: str, days: int):
    fp = _fingerprint(text)
    since = _now() - timedelta(days=days)
    for l in _load():
        if l["fingerprint"] == fp and datetime.fromisoformat(l["created_at"]) >= since:
            return True
    return False

def add_lead(client: str, raw_text: str, parsed: dict):
    leads = _load()
    lead = {
        "id": f"lead_{len(leads)+1}",
        "client": client,
        "raw_text": raw_text,
        "parsed": parsed,
        "status": "raw",
        "created_at": _now().isoformat(),
        "updated_at": _now().isoformat(),
        "fingerprint": _fingerprint(raw_text),
    }
    leads.append(lead)
    _save(leads)
    return lead

def update_status(lead_id: str, status: str):
    leads = _load()
    for l in leads:
        if l["id"] == lead_id:
            l["status"] = status
            l["updated_at"] = _now().isoformat()
            _save(leads)
            return l
    return None

def list_leads():
    return _load()

# =================================================
# 🧲 Public API (used by api.leads_meta)
# =================================================
def insert_lead(lead: dict) -> dict:
    """
    Standard entry point for inserting a lead.
    This keeps api/* decoupled from internal store logic.
    """
    return save_lead(lead)

# =================================================
# 🗄️ Public DB Access (used by api.stats)
# =================================================
