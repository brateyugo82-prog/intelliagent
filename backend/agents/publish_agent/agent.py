"""
Publish Agent: Veröffentlicht Content auf verschiedenen Kanälen (Mock)
und benachrichtigt den Kunden (Log, optional E-Mail oder Teams-Webhook).
Speichert Veröffentlichungen im Memory, um doppelte Posts zu vermeiden.
"""

from typing import Dict, Any, List
from backend.core.logger import logger
from backend.core import memory
from backend.core.config import get_openai_key
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
import os
import requests


# ------------------------------------------------------------
# 🔔 Benachrichtigungssystem
# ------------------------------------------------------------
def _notify_client(client: str, platforms: List[str], message: str):
    """
    Benachrichtigt den Kunden:
    - immer per Log
    - optional per E-Mail (SMTP_* Variablen im .env)
    - optional per Teams-Webhook (TEAMS_WEBHOOK im .env)
    """
    # 1️⃣ Log
    logger.info(f"[PublishAgent] Benachrichtigung an {client}: {message}")

    # 2️⃣ E-Mail-Benachrichtigung
    smtp_host = os.getenv("SMTP_HOST")
    smtp_user = os.getenv("SMTP_USER")
    smtp_pass = os.getenv("SMTP_PASS")
    smtp_to = os.getenv("NOTIFY_EMAIL")

    if smtp_host and smtp_user and smtp_pass and smtp_to:
        try:
            msg = MIMEText(
                f"Hallo {client},\n\n{message}\n\nPlattformen: {', '.join(platforms)}\n\nViele Grüße,\nDein IntelliAgent-System"
            )
            msg["Subject"] = f"Agenten-Benachrichtigung: Veröffentlichung auf {', '.join(platforms)}"
            msg["From"] = smtp_user
            msg["To"] = smtp_to

            with smtplib.SMTP(smtp_host, 587) as server:
                server.starttls()
                server.login(smtp_user, smtp_pass)
                server.send_message(msg)

            logger.info(f"[PublishAgent] E-Mail-Benachrichtigung an {smtp_to} gesendet.")
        except Exception as e:
            logger.error(f"[PublishAgent] Fehler beim Senden der Benachrichtigung: {e}")

    # 3️⃣ Teams-Webhook (optional)
    teams_url = os.getenv("TEAMS_WEBHOOK")
    if teams_url:
        try:
            payload = {
                "text": f"📢 Hallo {client},\n\n{message}\nPlattformen: {', '.join(platforms)}"
            }
            resp = requests.post(teams_url, json=payload)
            if resp.status_code == 200:
                logger.info("[PublishAgent] Teams-Benachrichtigung erfolgreich gesendet.")
            else:
                logger.error(f"[PublishAgent] Teams-Webhook-Fehler: {resp.status_code} {resp.text}")
        except Exception as e:
            logger.error(f"[PublishAgent] Fehler beim Senden an Teams: {e}")


# ------------------------------------------------------------
# 🚀 Hauptfunktion
# ------------------------------------------------------------
def run(prompt: str, task: str = None, platform: str = None, client: str = None) -> Dict[str, Any]:
    """
    Führt die Veröffentlichung aus (Mock).
    Später hier: echte API-Calls zu WordPress, LinkedIn, Facebook, Instagram.
    """
    if not task:
        task = "Veröffentliche Content"
    if not client:
        client = "unbekannt"

    # Plattformen splitten, z. B. "facebook, instagram"
    platforms = [p.strip() for p in platform.split(",")] if platform else ["website"]

    # 🧠 Doppelte Veröffentlichungen verhindern
    memory_key = f"publish:{client}:{','.join(platforms)}:{prompt[:100]}"
    if memory.already_seen(client, memory_key):
        logger.info(f"[PublishAgent] Veröffentlichung bereits durchgeführt → Übersprungen für {client}")
        return {"status": "skipped", "reason": "duplicate"}

    logger.info(f"[PublishAgent] Starte Veröffentlichung für {client} auf {platforms}")

    # 🧩 Globale OpenAI-Konfiguration laden (z. B. für spätere Auto-Textergänzung)
    openai_key = get_openai_key()
    if not openai_key or openai_key == "DUMMY_KEY":
        logger.warning("[PublishAgent] Kein gültiger OpenAI-Key gefunden. Fortsetzung im Mock-Modus.")

    # 🚀 Veröffentlichung (Mock)
    messages = []
    for p in platforms:
        msg = f"Content wurde auf {p} für {client} veröffentlicht (Mock)."
        logger.info(f"[PublishAgent] {msg}")
        messages.append(msg)

    final_message = " | ".join(messages)

    # 🧠 Speicherung im Memory-System
    memory.remember(client, memory_key, {
        "agent": "publish_agent",
        "timestamp": datetime.now().isoformat(),
        "platforms": platforms,
        "message": final_message
    })

    # 🔔 Benachrichtigung an den Kunden (Log, Mail, Teams)
    _notify_client(client, platforms, final_message)

    return {
        "status": "ok",
        "publish": final_message,
        "task": task,
        "platforms": platforms,
        "client": client
    }
