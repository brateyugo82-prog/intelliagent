import json
import random
from pathlib import Path
from typing import Dict, Any

from backend.backend.core.logger import logger


# -------------------------------------------------
# 📁 Pfade
# -------------------------------------------------
BASE_DIR = Path(__file__).resolve().parents[2]  # backend/
CLIENTS_DIR = BASE_DIR / "clients"


# -------------------------------------------------
# 🔧 Helper
# -------------------------------------------------
def _load_json(path: Path) -> dict | list:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as e:
        logger.warning(f"[CommunicationAgent] JSON fehlerhaft: {path} – {e}")
        return {}


def _pick_random(value):
    if isinstance(value, list):
        return random.choice(value) if value else ""
    return value or ""


# -------------------------------------------------
# 🧠 MAIN
# -------------------------------------------------
def run(
    prompt: str = "",
    platform: str = "",
    client: str = "",
    context: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    """
    🔒 HARD RULES:
    - KEINE Text-Generierung
    - NUR slogans.json + ctas.json
    """

    context = context or {}
    category = context.get("image_context")

    if not client or not category:
        logger.warning("[CommunicationAgent] client oder category fehlt")
        return {"output": {"text": "", "cta": "", "hashtags": []}}

    base_path = CLIENTS_DIR / client / "slogans" / category

    slogans_path = base_path / "slogans.json"
    ctas_path = base_path / "ctas.json"

    slogans_data = _load_json(slogans_path)
    ctas_data = _load_json(ctas_path)

    # -------------------------------------------------
    # 🧩 TEXT
    # -------------------------------------------------
    text = ""
    if isinstance(slogans_data, dict):
        text = _pick_random(slogans_data.get("slogans", []))
    elif isinstance(slogans_data, list):
        text = _pick_random(slogans_data)

    # -------------------------------------------------
    # 🧩 CTA
    # -------------------------------------------------
    cta = ""
    if isinstance(ctas_data, dict):
        cta = _pick_random(ctas_data.get("ctas", []))
    elif isinstance(ctas_data, list):
        cta = _pick_random(ctas_data)

    # -------------------------------------------------
    # ❌ KEINE HASHTAGS (optional später)
    # -------------------------------------------------
    hashtags = []

    logger.info(
        f"[CommunicationAgent] OK | client={client} | category={category} | platform={platform}"
    )

    return {
        "output": {
            "text": text,
            "cta": cta,
            "hashtags": hashtags,
        }
    }