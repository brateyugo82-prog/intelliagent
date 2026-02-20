"""
Lead Agent v1.1 (FINAL)
----------------------
- Erkennt qualifizierte Leads aus Social Media Nachrichten
- Speichert Leads mandantenfähig in clients/<client>/data/leads.csv
"""

from typing import Dict
from datetime import datetime
import csv
from pathlib import Path

from core.logger import logger
from core.config import get_openai_key

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None


# ------------------------------------------------------------
# 📁 Basisverzeichnisse
# ------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parents[1]
CLIENTS_DIR = BASE_DIR / "clients"


# ------------------------------------------------------------
# 📄 Lead-Dateipfad
# ------------------------------------------------------------
def _get_leads_path(client: str) -> Path:
    """
    clients/<client>/data/leads.csv
    """
    path = CLIENTS_DIR / client / "data" / "leads.csv"
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def _ensure_csv_exists(path: Path):
    if not path.exists():
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                "date",
                "platform",
                "type",
                "message",
                "status",
                "source"
            ])


# ------------------------------------------------------------
# 🧠 KI-Lead-Erkennung
# ------------------------------------------------------------
def _is_lead_via_ai(message: str) -> bool:
    if not OpenAI:
        logger.error("[LeadAgent] OpenAI nicht verfügbar")
        return False

    key = get_openai_key()
    if not key or key == "DUMMY_KEY":
        logger.error("[LeadAgent] Kein gültiger OpenAI-Key")
        return False

    prompt = f"""
Du bist ein Lead-Filter für ein Umzugsunternehmen.

Antworte NUR mit:
- YES → wenn es eine konkrete Anfrage ist
- NO → wenn es KEIN Lead ist

Nachricht:
"{message}"
"""

    client = OpenAI(api_key=key)
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "system", "content": prompt}],
        max_tokens=5
    )

    answer = resp.choices[0].message.content.strip().upper()
    return answer.startswith("YES")


# ------------------------------------------------------------
# 🚀 Hauptfunktion
# ------------------------------------------------------------
def run(
    message: str,
    platform: str,
    source: str,
    client: str
) -> Dict:

    logger.info(f"[LeadAgent] Prüfe Nachricht ({platform}): {message}")

    is_lead = _is_lead_via_ai(message)

    if not is_lead:
        logger.info("[LeadAgent] ❌ Kein Lead erkannt")
        return {"status": "ignored"}

    leads_path = _get_leads_path(client)
    _ensure_csv_exists(leads_path)

    with open(leads_path, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            datetime.now().isoformat(),
            platform,
            "service_request",
            message,
            "new",
            source
        ])

    logger.info(f"[LeadAgent] ✅ Lead gespeichert → {leads_path}")
    return {"status": "stored", "path": str(leads_path)}