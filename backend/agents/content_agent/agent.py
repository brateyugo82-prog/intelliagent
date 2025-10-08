"""
Content Agent: Generiert hochwertigen Social Media oder Blog-Content mit ChatGPT.
Verwendet das Memory-System, um doppelte Themen zu vermeiden.
"""

from typing import Dict, Any
from backend.core.config import get_openai_key
from backend.core.logger import logger
from backend.core import memory

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None
    logger.error("openai-Paket nicht installiert. Bitte 'pip install openai'.")


def run(prompt: str, task: str = None, platform: str = None, client: str = None) -> Dict[str, Any]:
    """
    Erstellt hochwertigen Content (SEO, Blog, Social Media) für einen Kunden.
    Nutzt globalen OpenAI-Key (Mark) und verhindert doppelte Themen über memory.py.
    """
    if not task:
        task = "Erstelle hochwertigen Content für Social Media oder Blog"
    if not client:
        client = "unbekannt"

    # 🧠 Gedächtnisprüfung
    if memory.already_seen(client, prompt):
        logger.info(f"[ContentAgent] Überspringe doppelten Prompt für {client}")
        return {"status": "skipped", "reason": "duplicate"}

    full_prompt = f"""
Du bist ContentAgent für den Kunden {client}.
Aufgabe: {task}
Plattform: {platform}
Thema: {prompt}

Erstelle hochwertigen, suchmaschinenoptimierten Content.
Der Text soll informativ, sympathisch und professionell wirken.
"""
    logger.info(f"[ContentAgent] Bearbeite Task für {client}: {task}")
    logger.info(f"[ContentAgent] Prompt an OpenAI: {full_prompt}")

    # 🔑 Globalen Key holen
    openai_key = get_openai_key()

    if not openai_key or openai_key == "DUMMY_KEY":
        logger.error("[ContentAgent] Kein gültiger OpenAI API-Key vorhanden!")
        return {"error": "OpenAI API-Key fehlt oder ungültig."}

    if OpenAI is None:
        return {"error": "openai-Paket nicht installiert."}

    try:
        client_openai = OpenAI(api_key=openai_key)
        response = client_openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "system", "content": full_prompt}],
            max_tokens=600
        )

        if not response or not response.choices:
            logger.error("[ContentAgent] Keine Antwort von OpenAI erhalten.")
            return {"error": "Keine Antwort von OpenAI erhalten."}

        gpt_answer = response.choices[0].message.content.strip()
        logger.info(f"[ContentAgent] Antwort erhalten: {gpt_answer[:120]}...")

        # 🧠 Erinnerung speichern (zur Duplicate-Erkennung)
        memory.remember(client, prompt, {"agent": "content_agent", "output": gpt_answer[:150]})

        return {
            "status": "ok",
            "content": gpt_answer,
            "client": client,
            "task": task
        }

    except Exception as e:
        logger.error(f"[ContentAgent] Fehler: {e}")
        return {"error": str(e)}
