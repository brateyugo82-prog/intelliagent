"""
Communication Agent: Formuliert kurze, plattformgerechte Texte
für Social Media oder Kundenkommunikation.
Verwendet globalen OpenAI-Key (Mark) und nutzt memory.py, um doppelte Prompts zu vermeiden.
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
    Generiert kurze, plattformgerechte Social-Media-Texte (TikTok, Instagram, Facebook, LinkedIn)
    und vermeidet doppelte Themen durch Kunden-spezifisches Memory.
    """
    if not task:
        task = "Formuliere Kundenkommunikation"
    if not client:
        client = "unbekannt"

    # 🧠 Prüfen, ob das Thema schon existiert
    if memory.already_seen(client, prompt):
        logger.info(f"[CommunicationAgent] Duplicate Prompt für {client}, übersprungen.")
        return {"status": "skipped", "reason": "duplicate"}

    # Prompt für GPT
    full_prompt = f"""
Du bist CommunicationAgent für den Kunden {client}.
Erstelle jeweils kurze Texte für diese Plattformen:
- TikTok: locker, mit Emojis, max. 2 Sätze + 2 Hashtags
- Instagram: freundlich, ästhetisch, max. 3 Sätze + 3 Hashtags
- Facebook: informativ, vertrauenswürdig, max. 4 Sätze + 2 Hashtags
- LinkedIn: professionell, seriös, max. 4 Sätze + 2 Hashtags

Thema: {prompt}

Antworte im JSON-Format mit den Feldern:
{{
  "tiktok": "...",
  "instagram": "...",
  "facebook": "...",
  "linkedin": "..."
}}
"""

    logger.info(f"[CommunicationAgent] Prompt an OpenAI: {full_prompt}")

    # 🔑 Globalen Key abrufen
    openai_key = get_openai_key()

    if not openai_key or openai_key == "DUMMY_KEY":
        logger.error("[CommunicationAgent] Kein gültiger OpenAI API-Key gefunden!")
        return {"error": "OpenAI API-Key fehlt oder ungültig."}

    if OpenAI is None:
        return {"error": "openai-Paket nicht installiert."}

    # 🚀 Anfrage an GPT
    try:
        client_openai = OpenAI(api_key=openai_key)
        resp = client_openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "system", "content": full_prompt}],
            max_tokens=600
        )

        if not resp or not resp.choices:
            logger.error("[CommunicationAgent] Keine Antwort von OpenAI erhalten.")
            return {"error": "Keine Antwort von OpenAI erhalten."}

        answer = resp.choices[0].message.content.strip()
        logger.info(f"[CommunicationAgent] Antwort erhalten: {answer[:120]}...")

        # 🧠 Speichern im Gedächtnis
        memory.remember(client, prompt, {"agent": "communication_agent", "output": answer})

        return {
            "status": "ok",
            "output": answer,
            "task": task,
            "client": client
        }

    except Exception as e:
        logger.error(f"[CommunicationAgent] Fehler: {e}")
        return {"error": str(e)}
