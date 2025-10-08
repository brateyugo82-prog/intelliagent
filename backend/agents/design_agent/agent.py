"""
Design Agent: erweitert für IntelliAgent.
Erzeugt hochwertige Bilder mit OpenAI Image API (gpt-image-1),
liest Branding-Daten (Farben, Slogans) aus assets/
und berechnet geschätzte Kosten pro Generierung.
"""

from typing import Dict, Any
import base64
import time
import os
import json
import random
from pathlib import Path

from backend.core.config import get_openai_key
from backend.core.logger import logger

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None
    logger.error("openai-Paket nicht installiert. Bitte 'pip install openai'.")


# ------------------------------------------------------------
# 📁 Basisverzeichnis
# ------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parents[2]  # backend/
CLIENTS_DIR = BASE_DIR / "clients"


def _load_brand_assets(client: str) -> Dict[str, Any]:
    """
    Lädt farben.json und slogans.txt aus dem Client-Asset-Ordner.
    """
    assets_dir = CLIENTS_DIR / client / "assets"
    colors_path = assets_dir / "farben.json"
    slogans_path = assets_dir / "slogans.txt"

    colors = {}
    slogans = []

    if colors_path.exists():
        try:
            with open(colors_path, "r", encoding="utf-8") as f:
                colors = json.load(f)
        except Exception as e:
            logger.warning(f"[DesignAgent] Farben konnten nicht geladen werden: {e}")

    if slogans_path.exists():
        try:
            with open(slogans_path, "r", encoding="utf-8") as f:
                slogans = [line.strip() for line in f if line.strip()]
        except Exception as e:
            logger.warning(f"[DesignAgent] Slogans konnten nicht geladen werden: {e}")

    return {"colors": colors, "slogans": slogans}


def _estimate_cost(quality: str) -> float:
    """
    Schätzt Kosten in USD je nach Qualitätsstufe.
    """
    quality = quality.lower()
    if quality == "low":
        return 0.02
    elif quality == "medium":
        return 0.05
    else:
        return 0.10  # high


def run(prompt: str, task: str = None, platform: str = None, client: str = None) -> Dict[str, Any]:
    """
    Hauptfunktion: erzeugt Bilder, berücksichtigt Branding & Kosten.
    """
    if not task:
        task = "Erzeuge ein Markenbild"
    if not client:
        client = "unbekannt"

    mode = os.getenv("DESIGN_AGENT_MODE", "prod").lower()
    quality = os.getenv("IMAGE_QUALITY", "high").lower()

    logger.info(f"[DesignAgent] Starte im Modus: {mode.upper()} (Qualität: {quality})")

    # Branding laden
    brand_data = _load_brand_assets(client)
    colors = brand_data.get("colors", {})
    slogans = brand_data.get("slogans", [])

    slogan_sample = ""
    if slogans:
        selected = random.sample(slogans, min(2, len(slogans)))
        slogan_sample = " | ".join(selected)

    color_desc = colors.get("description", "")
    primary_color = colors.get("primary", "#FF0000")

    # Prompt erweitern
    full_prompt = (
        f"{task}\nClient: {client}\nPlatform: {platform}\n"
        f"Branding-Farben: {color_desc} (Primärfarbe: {primary_color}).\n"
        f"Berücksichtige folgende Slogans oder deren Stil: {slogan_sample}\n"
        f"Prompt: {prompt}"
    )

    image_size = "2048x1536" if mode == "prod" else "1024x1024"
    cost_estimate = _estimate_cost(quality)
    logger.info(f"[DesignAgent] Geschätzte Kosten pro Bild: ~${cost_estimate:.2f} USD")
    logger.info(f"[DesignAgent] Prompt an OpenAI Image API: {full_prompt}")
    logger.info(f"[DesignAgent] Bildgröße: {image_size}")

    # 🔑 Key holen
    openai_key = get_openai_key()
    if not openai_key or openai_key == "DUMMY_KEY":
        logger.error("[DesignAgent] Kein gültiger OpenAI API-Key vorhanden.")
        return {"error": "OpenAI API-Key fehlt oder ungültig."}
    if OpenAI is None:
        return {"error": "openai-Paket nicht installiert."}

    try:
        # 🗂️ Zielordner vorbereiten
        out_dir = CLIENTS_DIR / client / "output" / "images"
        out_dir.mkdir(parents=True, exist_ok=True)
        filename = f"{client}_{int(time.time())}.png"
        file_path = out_dir / filename

        # 🚀 API-Aufruf
        oai = OpenAI(api_key=openai_key)
        response = oai.images.generate(
            model="gpt-image-1",
            prompt=full_prompt,
            size=image_size
        )

        logger.info("[DesignAgent] Antwort von OpenAI empfangen.")

        # 🔍 Bild speichern
        image_url = None
        try:
            item = response.data[0]
            if getattr(item, "b64_json", None):
                img_bytes = base64.b64decode(item.b64_json)
                file_path.write_bytes(img_bytes)
                image_url = str(file_path)
                logger.info(f"[DesignAgent] Bild gespeichert: {image_url}")
            elif getattr(item, "url", None):
                image_url = item.url
                logger.info(f"[DesignAgent] Bild-URL empfangen: {image_url}")
        except Exception as parse_err:
            logger.error(f"[DesignAgent] Fehler beim Auslesen der Bilddaten: {parse_err}")

        if image_url:
            return {
                "status": "ok",
                "design": image_url,
                "task": task,
                "platform": platform,
                "client": client,
                "cost_estimate_usd": cost_estimate
            }

        logger.error("[DesignAgent] Keine Bilddaten erhalten.")
        return {"error": "Keine Bilddaten erhalten."}

    except Exception as e:
        logger.error(f"[DesignAgent] Fehler: {e}")
        return {"error": str(e)}
