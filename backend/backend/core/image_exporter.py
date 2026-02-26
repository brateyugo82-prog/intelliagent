from pathlib import Path
from PIL import Image


# ------------------------------------------------------------
# 📐 Ziel-Formate (plattform-spezifisch, bewusst redundant)
# ------------------------------------------------------------
FORMATS = {
    # Instagram
    "instagram_feed": (1080, 1350),   # 4:5
    "instagram_reel": (1080, 1920),   # 9:16

    # Facebook
    "facebook_feed": (1080, 1350),    # 4:5

    # LinkedIn
    "linkedin_feed": (1080, 1080),    # 1:1

    # TikTok
    "tiktok_video": (1080, 1920),     # 9:16
}


def export_social_formats(
    image_path: str,
    output_dir: str
) -> dict:
    """
    Erstellt Social-Media-Formate aus EINEM gebrandeten Bild.
    - Untere 25% sind Safe-Zone (Logo / Tel / Website)
    - Crop immer von OBEN
    """

    img = Image.open(image_path).convert("RGB")
    w, h = img.size

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    results = {}

    SAFE_ZONE_RATIO = 0.25
    safe_height = int(h * SAFE_ZONE_RATIO)

    for name, (target_w, target_h) in FORMATS.items():

        target_ratio = target_w / target_h
        current_ratio = w / h

        # --------------------------------------------
        # ✂️ Crop-Logik (branding-sicher)
        # --------------------------------------------
        if current_ratio > target_ratio:
            # zu breit → links/rechts
            new_w = int(h * target_ratio)
            left = (w - new_w) // 2
            box = (left, 0, left + new_w, h)
        else:
            # zu hoch → NUR oben
            new_h = int(w / target_ratio)
            top = max(0, h - new_h - safe_height)
            box = (0, top, w, top + new_h)

        cropped = img.crop(box)
        resized = cropped.resize((target_w, target_h), Image.LANCZOS)

        out_path = output_dir / f"{Path(image_path).stem}_{name}.png"
        resized.save(out_path, quality=95)

        results[name] = str(out_path)

    return results