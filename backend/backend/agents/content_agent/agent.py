"""
✅ ContentAgent v11.1 — Unified IntelliAgent Standard (CLEAN)
------------------------------------------------------------
- Generiert Content-Ideen, Hooks, Skripte & Konzepte
- KEIN kundenspezifischer Content im Agent
- Branding & Stil über branding_loader
- Duplicate-Schutz über Memory (nur Ideen, keine Posts)
- Plattform-agnostisch, aber kontextbewusst
"""

from typing import Dict, Any
from core.config import get_openai_key
from core.logger import logger
from core import memory
from core.branding_loader import load_brand_context

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None
    logger.error("❌ openai-Paket nicht installiert. Bitte `pip install openai`.")


# ------------------------------------------------------------
# 🚀 Hauptfunktion (EINHEITLICHE AGENTEN-SIGNATUR)
# ------------------------------------------------------------
def run(
    prompt: str,
    task: str | None = None,
    platform: str | None = None,
    client: str | None = None,
    context: dict | None = None
) -> Dict[str, Any]:
    """
    Generiert Content-Ideen, Hooks, Skripte oder Konzepte.
    KEIN fertiger Posting-Text.
    """

    # --------------------------------------------------------
    # Defaults
    # --------------------------------------------------------
    task = task or "Erstelle Content-Ideen"
    platform = platform or "multi"
    client = client or "unknown"
    context = context or {}

    # --------------------------------------------------------
    # Branding laden (NUR Stil & Tonalität)
    # --------------------------------------------------------
    brand_ctx = load_brand_context(client, prompt)
    brand_prompt = brand_ctx.get("prompt", "")
    slogan = brand_ctx.get("slogan")

    # --------------------------------------------------------
    # Duplicate Check (nur für IDEEN)
    # --------------------------------------------------------
    memory_key = f"{task}:{prompt}:{platform}"

    if memory.already_seen(client, memory_key):
        logger.info(f"[ContentAgent] Duplicate-Idee erkannt für {client}, übersprungen.")
        return {
            "status": "skipped",
            "reason": "duplicate",
            "client": client,
            "platform": platform
        }

    # --------------------------------------------------------
    # Plattform-Kontext (leicht, nicht zwingend)
    # --------------------------------------------------------
    platform_context = {
        "tiktok": "Kurz, direkt, Hook in den ersten Sekunden",
        "instagram": "Emotional, visuell, Storytelling",
        "facebook": "Lokal, erklärend, vertrauensvoll",
        "linkedin": "Sachlich, fachlich, Mehrwert-orientiert"
    }

    platform_hint = platform_context.get(platform, "plattformneutral")

    # --------------------------------------------------------
    # GPT Prompt (IDEEN-LEVEL)
    # --------------------------------------------------------
    gpt_prompt = f"""
Du bist ein erfahrener Content-Stratege.

Markenstil:
- professionell
- zuverlässig
- nahbar
{slogan and f"- Slogan: {slogan}"}

Aufgabe:
{task}

Thema:
"{prompt}"

Plattform:
{platform}

Plattform-Hinweis:
{platform_hint}

WICHTIG:
- KEIN finaler Social-Media-Post
- KEINE Bildbeschreibung
- KEINE Werbeversprechen
- Fokus auf IDEEN & STRUKTUR

ANTWORTFORMAT (JSON):
{{
  "hook": "...",
  "kernaussage": "...",
  "content_idee": "...",
  "cta_idee": "..."
}}
"""

    logger.info(
        f"[ContentAgent] Generiere Content-Idee | Client={client} | Plattform={platform}"
    )

    # --------------------------------------------------------
    # OpenAI Setup
    # --------------------------------------------------------
    openai_key = get_openai_key()
    if not openai_key or openai_key == "DUMMY_KEY":
        logger.error("[ContentAgent] ❌ OpenAI API-Key fehlt oder ungültig.")
        return {"error": "OpenAI API-Key fehlt"}

    if OpenAI is None:
        return {"error": "openai-Paket nicht installiert"}

    # --------------------------------------------------------
    # OpenAI Call
    # --------------------------------------------------------
    try:
        oai = OpenAI(api_key=openai_key)
        response = oai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "Du denkst strategisch, strukturiert und praxisnah."
                },
                {
                    "role": "user",
                    "content": gpt_prompt
                }
            ],
            max_tokens=600
        )

        if not response or not response.choices:
            raise RuntimeError("Leere Antwort von OpenAI")

        raw_output = response.choices[0].message.content.strip()

        # ----------------------------------------------------
        # Memory speichern (nur IDEE, kein Post)
        # ----------------------------------------------------
        memory.remember(
            client,
            memory_key,
            {
                "agent": "content_agent",
                "platform": platform,
                "task": task,
                "prompt": prompt,
                "output": raw_output
            }
        )

        return {
            "status": "ok",
            "client": client,
            "platform": platform,
            "output": raw_output
        }

    except Exception as e:
        logger.error(f"[ContentAgent] ❌ Fehler: {e}")
        return {"error": str(e)}


# ------------------------------------------------------------
# 🧪 Lokaler Test
# ------------------------------------------------------------
if __name__ == "__main__":
    test = run(
        prompt="10 Tipps für einen stressfreien Umzug",
        task="Ideen für Social & Blog",
        client="mtm_client",
        platform="instagram"
    )
    print(test)