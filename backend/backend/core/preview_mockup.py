from PIL import Image, ImageDraw, ImageFont
import textwrap
from pathlib import Path


# ------------------------------------------------------------
# 📐 Plattform-Presets
# ------------------------------------------------------------
PLATFORM_PRESETS = {
    "instagram": {
        "size": (1080, 1350),
        "image_height": 900,
        "text_width": 45,
    },
    "facebook": {
        "size": (1080, 1350),
        "image_height": 900,
        "text_width": 55,
    },
    "linkedin": {
        "size": (1200, 1350),
        "image_height": 850,
        "text_width": 60,
    },
}


# ------------------------------------------------------------
# 🖼 Plattform-Mockup Generator (NO CROP – CONTAIN)
# ------------------------------------------------------------
def create_platform_mockup(
    image_path: str,
    text: str,
    output_path: str,
    platform: str = "instagram",
):
    """
    Erstellt ein Plattform-Mockup aus einem ORIGINALBILD.
    ❗ KEIN Cropping – Bild wird IMMER vollständig angezeigt (Contain).
    """

    if platform not in PLATFORM_PRESETS:
        raise ValueError(f"Unbekannte Plattform: {platform}")

    preset = PLATFORM_PRESETS[platform]
    canvas_width, canvas_height = preset["size"]
    image_area_height = preset["image_height"]
    text_width = preset["text_width"]

    padding = 40
    background_color = "white"
    text_color = (0, 0, 0)

    # ------------------------------------------------------------
    # 📷 Originalbild laden
    # ------------------------------------------------------------
    img = Image.open(image_path).convert("RGB")

    # ------------------------------------------------------------
    # ✅ CONTAIN-SCALING (kein Crop)
    # ------------------------------------------------------------
    max_w = canvas_width
    max_h = image_area_height

    scale = min(max_w / img.width, max_h / img.height)
    new_w = int(img.width * scale)
    new_h = int(img.height * scale)

    img = img.resize((new_w, new_h), Image.LANCZOS)

    # ------------------------------------------------------------
    # 🧱 Canvas erstellen
    # ------------------------------------------------------------
    canvas = Image.new("RGB", (canvas_width, canvas_height), background_color)
    draw = ImageDraw.Draw(canvas)

    # Bild zentriert in der oberen Image-Area
    x_img = (canvas_width - new_w) // 2
    y_img = (image_area_height - new_h) // 2
    canvas.paste(img, (x_img, y_img))

    # ------------------------------------------------------------
    # ✍️ Font laden (fallback safe)
    # ------------------------------------------------------------
    try:
        font_path = Path(__file__).parent / "fonts" / "Inter-Regular.ttf"
        font = ImageFont.truetype(str(font_path), size=32)
    except Exception:
        font = ImageFont.load_default()

    # ------------------------------------------------------------
    # 📝 Text vorbereiten
    # ------------------------------------------------------------
    text = text or ""
    wrapped = []

    for line in text.split("\n"):
        wrapped.extend(
            textwrap.wrap(
                line,
                width=text_width,
                replace_whitespace=False,
                drop_whitespace=False,
            )
        )
        wrapped.append("")

    wrapped_text = "\n".join(wrapped).strip()

    # ------------------------------------------------------------
    # 📝 Text unter Bild rendern
    # ------------------------------------------------------------
    text_x = padding
    text_y = image_area_height + padding

    draw.multiline_text(
        (text_x, text_y),
        wrapped_text,
        fill=text_color,
        font=font,
        spacing=10,
        align="left",
    )

    # ------------------------------------------------------------
    # 💾 Speichern
    # ------------------------------------------------------------
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(output_path, quality=95)

    print(f"✅ RENDERED: {output_path}")