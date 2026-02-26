import json
from pathlib import Path
from datetime import datetime, timedelta, timezone
from hashlib import sha256

# =================================================
# 📁 PATHS
# =================================================

BASE_DIR = Path(__file__).resolve().parents[1]
DB_DIR = BASE_DIR / "db"
DB_DIR.mkdir(exist_ok=True)

LEADS_FILE = DB_DIR / "leads.json"

# =================================================
# ⏱️ TIME
# =================================================

def _now():
    return datetime.now(timezone.utc)

# =================================================
# 💾 IO
# =================================================

def _load():
    if not LEADS_FILE.exists():
        return []
    return json.loads(LEADS_FILE.read_text(encoding="utf-8"))

def _save(leads):
    LEADS_FILE.write_text(
        json.dumps(leads, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

# =================================================
# 🔑 HELPERS
# =================================================

def _fingerprint(text: str) -> str:
    return sha256(text.strip().lower().encode()).hexdigest()

def is_duplicate(text: str, days: int = 3) -> bool:
    """
    Prevent duplicate leads within X days based on text fingerprint.
    """
    fp = _fingerprint(text)
    since = _now() - timedelta(days=days)

    for l in _load():
        if (
            l.get("fingerprint") == fp
            and datetime.fromisoformat(l["created_at"]) >= since
        ):
            return True
    return False

# =================================================
# 🧠 AUTO QUALIFY
# =================================================

QUALIFY_KEYWORDS = [
    "umzug",
    "montage",
    "transport",
    "entrümpelung",
    "moebel",
    "möbel",
]

def _auto_status(raw_text: str) -> str:
    text = raw_text.lower()
    if any(k in text for k in QUALIFY_KEYWORDS):
        return "qualified"
    return "raw"

# =================================================
# ➕ ADD LEAD (SINGLE SOURCE OF TRUTH)
# =================================================

def add_lead(client: str, raw_text: str, parsed: dict) -> dict:
    leads = _load()

    # optional: Duplikate blocken
    # if is_duplicate(raw_text):
    #     return None

    status = _auto_status(raw_text)

    lead = {
        "id": f"lead_{len(leads) + 1}",
        "client": client,
        "raw_text": raw_text,
        "parsed": parsed,
        "status": status,
        "created_at": _now().isoformat(),
        "updated_at": _now().isoformat(),
        "fingerprint": _fingerprint(raw_text),
    }

    leads.append(lead)
    _save(leads)
    return lead

# =================================================
# 🔁 UPDATE STATUS
# =================================================

def update_status(lead_id: str, status: str):
    leads = _load()

    for l in leads:
        if l["id"] == lead_id:
            l["status"] = status
            l["updated_at"] = _now().isoformat()
            _save(leads)
            return l

    return None

# =================================================
# 📋 READ
# =================================================

def list_leads():
    return _load()