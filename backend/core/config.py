"""
Globale Konfiguration für IntelliAgent Backend.
Lädt alle wichtigen ENV-Variablen (OpenAI, Microsoft, etc.)
und stellt eine Utility-Funktion bereit, um pro Kunde oder global den richtigen API-Key zu verwenden.
"""

import os
from dotenv import load_dotenv
from backend.core.logger import logger

# 🔧 Lade globale .env aus dem Backend-Root
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENV_PATH = os.path.join(BASE_DIR, ".env")
if os.path.exists(ENV_PATH):
    load_dotenv(ENV_PATH)
    logger.info(f"[Config] Globale .env geladen: {ENV_PATH}")
else:
    logger.warning("[Config] Keine globale .env im Backend-Verzeichnis gefunden!")

# 🔑 Globale Keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "DUMMY_KEY")
AZURE_CLIENT_ID = os.getenv("AZURE_CLIENT_ID", "")
AZURE_TENANT_ID = os.getenv("AZURE_TENANT_ID", "")
AZURE_CLIENT_SECRET = os.getenv("AZURE_CLIENT_SECRET", "")
MICROSOFT_GRAPH_SCOPE = os.getenv("MICROSOFT_GRAPH_SCOPE", "https://graph.microsoft.com/.default")


# 🧠 Neue Funktion: den richtigen OpenAI-Key bestimmen
def get_openai_key(client_env_path: str = None) -> str:
    """
    Gibt den passenden OpenAI API Key zurück.
    1️⃣ Priorität: Globaler Key (Mark)
    2️⃣ Fallback: Kunden-Key aus client/.env
    """
    if OPENAI_API_KEY and OPENAI_API_KEY != "DUMMY_KEY":
        logger.info("🔐 [Config] Verwende globalen OpenAI-Key (Mark).")
        return OPENAI_API_KEY

    if client_env_path and os.path.exists(client_env_path):
        try:
            with open(client_env_path, "r") as f:
                for line in f:
                    if line.strip().startswith("CUSTOMER_OPENAI_KEY="):
                        key = line.strip().split("=", 1)[1]
                        if key:
                            logger.info(f"🔑 [Config] Verwende Kunden-Key aus {client_env_path}")
                            return key
        except Exception as e:
            logger.error(f"[Config] Fehler beim Lesen der Kunden-.env: {e}")

    logger.warning("[Config] Kein gültiger OpenAI-Key gefunden! Verwende Dummy.")
    return "DUMMY_KEY"


# Optional: andere globale Variablen
LINKEDIN_API_KEY = os.getenv("LINKEDIN_API_KEY", "DUMMY_KEY")
INSTAGRAM_API_KEY = os.getenv("INSTAGRAM_API_KEY", "DUMMY_KEY")
FACEBOOK_API_KEY = os.getenv("FACEBOOK_API_KEY", "DUMMY_KEY")
