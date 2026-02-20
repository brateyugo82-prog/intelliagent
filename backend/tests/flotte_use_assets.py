"""
🧪 MTM Flotten-Overlay Test v1.3
-------------------------------
Nutzt das flotte.png aus assets/
und erstellt CI-konforme Varianten (rote Box, weißer Text).
- Automatische Schriftgrößenanpassung bei langen Slogans
- Vier vordefinierte Kurzslogans im Wechsel
- Kompatibel mit Pillow >= 10 (textbbox)
Speichert Ergebnisse in /output/images/ mit Datum im Namen.
→ Simulation: Dienstag & Donnerstag.
"""

from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
import random, json, datetime

CLIENT = "mtm_client"
BASE_DIR = Path(__file__).resolve().parents[1]
CLIENT_DIR = BASE_DIR / "clients" / CLIENT
ASSETS_DIR = CLIENT_DIR / "assets"
OUTPUT_DIR = CLIENT_DIR / "output" / "images"
CONFIG_PATH = CLIENT_DIR / "config.json"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# === Config laden ===
with open(CONFIG_PATH, "r", encoding="utf-8") as f:
    cfg = json.load(f)

brand = cfg.get("brand_identity", {})
contact = cfg.get("contact", {})

primary_color = brand.get("primary_color", "#E30613")
phone = contact.get("phone", "")
website = contact.get("website", "")
if website:
    website = website.replace("https://", "").replace("http://", "")
    if not website.startswith("www."):
        website = f"www.{website}"

# === Quelle: flotte.png aus assets ===
src = ASSETS_DIR / "flotte.png"
if not src.exists():
    raise FileNotFoundError("❌ assets/flotte.png nicht gefunden!")

# === Vier Kurzslogans im Wechsel ===
ROTATION_SLOGANS = [
    "IHR UMZUG – UNSER HANDWERK.",
    "MIT MTM LÄUFT’S STRESSFREI.",
    "VON HANNOVER IN DIE WELT.",
    "MÖBEL. TRANSPORT. MONTAGE."
]

def create_overlay(day_name: str, slogan: str):
    """Erstellt CI-Bild mit Text-Overlay und Datum"""
    image = Image.open(src).convert("RGB")
    w, h = image.size
    draw = ImageDraw.Draw(image)

    # Rote Box unten
    box_height = int(h * 0.22)
    draw.rectangle([(0, h - box_height), (w, h)], fill=primary_color)

    # Fonts laden (Arial → Helvetica → Default)
    def get_font(size):
        try:
            return ImageFont.truetype("Arial Bold.ttf", size)
        except:
            try:
                return ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", size)
            except:
                return ImageFont.load_default()

    # Dynamische Schriftgröße je nach Textlänge
    slogan_font_size = int(box_height * 0.28)
    font_slogan = get_font(slogan_font_size)
    bbox = draw.textbbox((0, 0), slogan, font=font_slogan)
    while bbox[2] - bbox[0] > w * 0.9 and slogan_font_size > 20:
        slogan_font_size -= 2
        font_slogan = get_font(slogan_font_size)
        bbox = draw.textbbox((0, 0), slogan, font=font_slogan)

    font_small = get_font(int(box_height * 0.18))

    # Textinhalte
    text_slogan = slogan.upper()
    text_contact = f"{phone}   {website}"

    # Textgrößen
    bbox_slogan = draw.textbbox((0, 0), text_slogan, font=font_slogan)
    bbox_contact = draw.textbbox((0, 0), text_contact, font=font_small)
    tw_slogan = bbox_slogan[2] - bbox_slogan[0]
    tw_contact = bbox_contact[2] - bbox_contact[0]

    # Zentrierung
    x_slogan = (w - tw_slogan) / 2
    y_slogan = h - box_height + (box_height * 0.20)
    x_contact = (w - tw_contact) / 2
    y_contact = h - box_height + (box_height * 0.60)

    # Zeichnen
    draw.text((x_slogan, y_slogan), text_slogan, fill="white", font=font_slogan)
    draw.text((x_contact, y_contact), text_contact, fill="white", font=font_small)

    # Dateiname mit Datum
    date_str = datetime.datetime.now().strftime("%Y-%m-%d")
    slogan_slug = slogan.split("–")[0].strip().replace(" ", "_").replace(".", "")
    filename = f"{CLIENT}_flotte_{day_name.lower()}_{slogan_slug}_{date_str}.png"
    out_path = OUTPUT_DIR / filename
    image.save(out_path, "PNG")

    print(f"✅ {day_name}-Post gespeichert: {out_path}")
    print(f"🧠 Slogan: {slogan}")
    print(f"☎️  {text_contact}\n")

# === Simulation: Dienstag & Donnerstag ===
for i, day in enumerate(["Tuesday", "Thursday"]):
    slogan = ROTATION_SLOGANS[i % len(ROTATION_SLOGANS)]
    create_overlay(day, slogan)
