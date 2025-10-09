"""
🤖 IntelliAgent – Multi-Platform Token Scheduler
------------------------------------------------
Automatisiert die Verlängerung von API-Tokens für:
- Meta (Facebook/Instagram)
- LinkedIn
- TikTok

💡 Läuft auf Render als "worker"-Service
   oder lokal über: python scheduler.py
"""

import os
import time
import json
import requests
import logging
from datetime import datetime

# ================================================
# 🔧 Grundkonfiguration
# ================================================
REFRESH_INTERVAL_DAYS = 60   # alle 60 Tage
LOG_FILE = "scheduler.log"

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

# ================================================
# 🌍 META – Facebook / Instagram
# ================================================
def refresh_meta_token():
    META_APP_ID = os.getenv("META_APP_ID")
    META_APP_SECRET = os.getenv("META_APP_SECRET")
    META_ACCESS_TOKEN = os.getenv("META_ACCESS_TOKEN")

    if not (META_APP_ID and META_APP_SECRET and META_ACCESS_TOKEN):
        logging.warning("Meta: Kein vollständiges Token-Setup gefunden – übersprungen.")
        return

    try:
        url = (
            f"https://graph.facebook.com/v21.0/oauth/access_token?"
            f"grant_type=fb_exchange_token&client_id={META_APP_ID}"
            f"&client_secret={META_APP_SECRET}"
            f"&fb_exchange_token={META_ACCESS_TOKEN}"
        )
        r = requests.get(url)
        data = r.json()

        if "access_token" in data:
            new_token = data["access_token"]
            with open("meta_token.txt", "w") as f:
                f.write(new_token)
            logging.info("✅ Meta-Token erfolgreich erneuert.")
        else:
            logging.error(f"⚠️ Meta-Token-Fehler: {data}")
    except Exception as e:
        logging.exception(f"❌ Meta-Token-Exception: {e}")

# ================================================
# 💼 LINKEDIN
# ================================================
def refresh_linkedin_token():
    LINKEDIN_REFRESH_TOKEN = os.getenv("LINKEDIN_REFRESH_TOKEN")
    LINKEDIN_CLIENT_ID = os.getenv("LINKEDIN_CLIENT_ID")
    LINKEDIN_CLIENT_SECRET = os.getenv("LINKEDIN_CLIENT_SECRET")

    if not (LINKEDIN_REFRESH_TOKEN and LINKEDIN_CLIENT_ID and LINKEDIN_CLIENT_SECRET):
        logging.warning("LinkedIn: Kein vollständiges Token-Setup gefunden – übersprungen.")
        return

    try:
        url = "https://www.linkedin.com/oauth/v2/accessToken"
        payload = {
            "grant_type": "refresh_token",
            "refresh_token": LINKEDIN_REFRESH_TOKEN,
            "client_id": LINKEDIN_CLIENT_ID,
            "client_secret": LINKEDIN_CLIENT_SECRET
        }
        r = requests.post(url, data=payload)
        data = r.json()

        if "access_token" in data:
            new_token = data["access_token"]
            with open("linkedin_token.txt", "w") as f:
                f.write(new_token)
            logging.info("✅ LinkedIn-Token erfolgreich erneuert.")
        else:
            logging.error(f"⚠️ LinkedIn-Fehler: {data}")
    except Exception as e:
        logging.exception(f"❌ LinkedIn-Exception: {e}")

# ================================================
# 🎵 TIKTOK
# ================================================
def refresh_tiktok_token():
    TIKTOK_REFRESH_TOKEN = os.getenv("TIKTOK_REFRESH_TOKEN")
    TIKTOK_CLIENT_KEY = os.getenv("TIKTOK_CLIENT_KEY")
    TIKTOK_CLIENT_SECRET = os.getenv("TIKTOK_CLIENT_SECRET")

    if not (TIKTOK_REFRESH_TOKEN and TIKTOK_CLIENT_KEY and TIKTOK_CLIENT_SECRET):
        logging.warning("TikTok: Kein vollständiges Token-Setup gefunden – übersprungen.")
        return

    try:
        url = "https://open-api.tiktok.com/oauth/refresh_token/"
        payload = {
            "client_key": TIKTOK_CLIENT_KEY,
            "client_secret": TIKTOK_CLIENT_SECRET,
            "grant_type": "refresh_token",
            "refresh_token": TIKTOK_REFRESH_TOKEN
        }
        r = requests.post(url, data=payload)
        data = r.json()

        if "data" in data and "access_token" in data["data"]:
            new_token = data["data"]["access_token"]
            with open("tiktok_token.txt", "w") as f:
                f.write(new_token)
            logging.info("✅ TikTok-Token erfolgreich erneuert.")
        else:
            logging.error(f"⚠️ TikTok-Fehler: {data}")
    except Exception as e:
        logging.exception(f"❌ TikTok-Exception: {e}")

# ================================================
# 🧠 MASTER-FUNKTION
# ================================================
def run_refresh_cycle():
    logging.info("🚀 Starte Token-Refresh-Zyklus...")
    refresh_meta_token()
    refresh_linkedin_token()
    refresh_tiktok_token()
    logging.info("✅ Zyklus abgeschlossen.\n")

# ================================================
# ⏰ HAUPTSCHLEIFE
# ================================================
if __name__ == "__main__":
    logging.info("🕒 Multi-Platform Scheduler gestartet")
    while True:
        run_refresh_cycle()
        logging.info(f"⏰ Warte {REFRESH_INTERVAL_DAYS} Tage bis zum nächsten Lauf.\n")
        time.sleep(REFRESH_INTERVAL_DAYS * 24 * 60 * 60)
