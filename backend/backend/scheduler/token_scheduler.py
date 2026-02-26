"""
🤖 IntelliAgent – Multi-Platform Token & Analytics Scheduler (FINAL)
------------------------------------------------------------------
Einmaliger Lauf (Render Cron oder manuell).

Aktiv:
✅ Meta (Facebook / Instagram)
✅ LinkedIn
✅ TikTok
✅ Analytics (periodisch)
"""

import os
import json
import logging
import requests
from pathlib import Path
from datetime import datetime, timedelta

from agents.analytics_agent.agent import run as run_analytics


# =====================================================
# CONFIG
# =====================================================
TOKENS_DIR = Path("state/tokens")
TOKENS_DIR.mkdir(parents=True, exist_ok=True)

from core.paths import CLIENTS_DIR

ANALYTICS_PERIOD = "30d"   # leicht änderbar
ANALYTICS_PLATFORM = "multi"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

# =====================================================
# HELPER
# =====================================================
def save_token(platform: str, token: str, expires_in: int):
    data = {
        "access_token": token,
        "expires_at": (datetime.utcnow() + timedelta(seconds=expires_in)).isoformat()
    }

    with open(TOKENS_DIR / f"{platform}.json", "w") as f:
        json.dump(data, f)

    logging.info(f"💾 {platform} Token gespeichert")


# =====================================================
# META
# =====================================================
def refresh_meta():
    app_id = os.getenv("META_APP_ID")
    app_secret = os.getenv("META_APP_SECRET")
    token = os.getenv("META_ACCESS_TOKEN")

    if not all([app_id, app_secret, token]):
        logging.warning("Meta: ENV fehlt – übersprungen")
        return

    r = requests.get(
        "https://graph.facebook.com/v21.0/oauth/access_token",
        params={
            "grant_type": "fb_exchange_token",
            "client_id": app_id,
            "client_secret": app_secret,
            "fb_exchange_token": token,
        },
        timeout=10
    )

    data = r.json()
    if "access_token" not in data:
        logging.error(f"Meta Fehler: {data}")
        return

    save_token(
        "meta",
        data["access_token"],
        data.get("expires_in", 60 * 60 * 24 * 60)
    )


# =====================================================
# LINKEDIN
# =====================================================
def refresh_linkedin():
    refresh_token = os.getenv("LINKEDIN_REFRESH_TOKEN")
    client_id = os.getenv("LINKEDIN_CLIENT_ID")
    client_secret = os.getenv("LINKEDIN_CLIENT_SECRET")

    if not all([refresh_token, client_id, client_secret]):
        logging.warning("LinkedIn: ENV fehlt – übersprungen")
        return

    r = requests.post(
        "https://www.linkedin.com/oauth/v2/accessToken",
        data={
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
            "client_id": client_id,
            "client_secret": client_secret,
        },
        timeout=10
    )

    data = r.json()
    if "access_token" not in data:
        logging.error(f"LinkedIn Fehler: {data}")
        return

    save_token(
        "linkedin",
        data["access_token"],
        data.get("expires_in", 60 * 60 * 24 * 60)
    )


# =====================================================
# TIKTOK
# =====================================================
def refresh_tiktok():
    refresh_token = os.getenv("TIKTOK_REFRESH_TOKEN")
    client_key = os.getenv("TIKTOK_CLIENT_KEY")
    client_secret = os.getenv("TIKTOK_CLIENT_SECRET")

    if not all([refresh_token, client_key, client_secret]):
        logging.warning("TikTok: ENV fehlt – übersprungen")
        return

    r = requests.post(
        "https://open-api.tiktok.com/oauth/refresh_token/",
        data={
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
            "client_key": client_key,
            "client_secret": client_secret,
        },
        timeout=10
    )

    data = r.json()
    token = data.get("data", {}).get("access_token")

    if not token:
        logging.error(f"TikTok Fehler: {data}")
        return

    save_token(
        "tiktok",
        token,
        data.get("data", {}).get("expires_in", 60 * 60 * 24 * 60)
    )


# =====================================================
# ANALYTICS
# =====================================================
def run_analytics_for_all_clients():
    if not CLIENTS_DIR.exists():
        logging.warning("Clients-Verzeichnis fehlt – Analytics übersprungen")
        return

    for client_dir in CLIENTS_DIR.iterdir():
        if not client_dir.is_dir():
            continue

        client = client_dir.name
        logging.info(f"📊 Analytics gestartet für Client: {client}")

        try:
            result = run_analytics(
                client=client,
                platform=ANALYTICS_PLATFORM,
                period=ANALYTICS_PERIOD,
            )

            if result.get("status") == "skipped":
                logging.info(f"ℹ️ Keine Daten für Analytics ({client})")
            elif result.get("status") == "ok":
                logging.info(f"✅ Analytics abgeschlossen ({client})")
            else:
                logging.warning(f"⚠️ Analytics Ergebnis ({client}): {result}")

        except Exception as e:
            logging.error(f"❌ Analytics Fehler ({client}): {e}")


# =====================================================
# RUN
# =====================================================
def run():
    logging.info("🚀 Token & Analytics Scheduler gestartet")

    refresh_meta()
    refresh_linkedin()
    refresh_tiktok()

    run_analytics_for_all_clients()

    logging.info("🏁 Token & Analytics Scheduler abgeschlossen")


if __name__ == "__main__":
    run()