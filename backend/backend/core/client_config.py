import json
from pathlib import Path
from backend.backend.core.logger import logger

# ------------------------------------------------------------
# 📁 Basisverzeichnis
# ------------------------------------------------------------
# __file__ = backend/core/client_config.py
# parents[1] = backend/
BASE_DIR = Path(__file__).resolve().parents[1]
CLIENTS_DIR = BASE_DIR / "clients"


def load_client_config(client: str) -> dict:
    """
    Lädt die config.json eines Kunden.

    Zentrale Quelle für:
    - Texte
    - Weekly Plan
    - Branding
    - Plattform-Regeln
    """
    if not client:
        raise RuntimeError("❌ Client fehlt beim Laden der config")

    cfg_path = CLIENTS_DIR / client / "config.json"

    if not cfg_path.exists():
        raise RuntimeError(
            f"❌ config.json nicht gefunden für Client: {client}\n"
            f"Erwarteter Pfad: {cfg_path}"
        )

    try:
        cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
        logger.info(f"[ClientConfig] ✅ Config geladen für {client}")
        return cfg

    except Exception as e:
        raise RuntimeError(
            f"❌ Fehler beim Laden der config für {client}: {e}"
        )