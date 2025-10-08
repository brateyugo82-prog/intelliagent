"""
Analytics Agent: analysiert Content und Design.
Verwendet den globalen OpenAI-Key (Mark) über get_openai_key()
und liefert eine prägnante qualitative Analyse des generierten Inhalts.
"""

from typing import Dict, Any
from backend.core.config import get_openai_key
from backend.core.logger import logger

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None
    logger.error("openai-Paket nicht installiert. Bitte 'pip install openai'.")


def run(prompt: str, task: str = None, platform: str = None, client: str = None) -> Dict[str, Any]:
    """
    Führt eine Content- oder Designanalyse durch.
    Bewertet Wirkung, Ton, Reichweite und Verbesserungsmöglichkeiten.
    """
    if not task:
        task = "Analysiere Content und Design"
    if not client:
        client = "unbekannt"

    # Analyse-Prompt
    analysis_prompt = f"""
Du bist AnalyticsAgent für den Kunden {client}.
Analysiere den gelieferten Content/Design kritisch:

- Wie wirkt der Content (Ton, Verständlichkeit, Nutzen)?
- Welche Reichweite könnte er auf der Plattform {platform} erzielen?
- Welche Verbesserungen sind möglich?

Antworte prägnant und in Stichpunkten.
Content-Eingabe:
{prompt}
"""

    logger.info(f"[AnalyticsAgent] Bearbeite Task für {client}: {task}")
    logger.info(f"[AnalyticsAgent] Prompt an OpenAI: {analysis_prompt}")

    # OpenAI-Key holen (immer globaler Key zuerst)
    openai_key = get_openai_key()

    if not openai_key or openai_key == "DUMMY_KEY":
        logger.error("[AnalyticsAgent] Kein gültiger OpenAI API-Key gefunden!")
        return {"error": "OpenAI API-Key fehlt oder ungültig."}

    if OpenAI is None:
        return {"error": "openai-Paket nicht installiert."}

    try:
        oai = OpenAI(api_key=openai_key)
        resp = oai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "system", "content": analysis_prompt}],
            max_tokens=400
        )

        if not resp or not resp.choices:
            logger.error("[AnalyticsAgent] Keine Antwort von OpenAI erhalten.")
            return {"error": "Keine Antwort von OpenAI erhalten."}

        answer = resp.choices[0].message.content.strip()
        logger.info(f"[AnalyticsAgent] Analyse abgeschlossen: {answer[:120]}...")

        return {
            "analytics": answer,
            "task": task,
            "platform": platform,
            "client": client
        }

    except Exception as e:
        logger.error(f"[AnalyticsAgent] Fehler: {e}")
        return {"error": str(e)}
