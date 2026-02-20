from PIL import Image
from pathlib import Path
from datetime import date
import shutil
from core.logger import logger


def trim_transparency(img: Image.Image) -> Image.Image:
    """
    Entfernt transparente Ränder vom Logo
    """
    bbox = img.getbbox()
    if bbox:
        return img.crop(bbox)
    return img


def apply_branding(
    image_path: str,
    brand_ctx: dict,
    image_context: str,
    platform: str,
    run_date: date,
) -> str:
    """
    Branding-Pipeline (FOUNDATION + WEEKLY, FINAL)

    WEEKLY:
    - Quelle: output/approved/
    - Original → used/
    - Kein Reuse

    FOUNDATION:
    - Quelle: assets/foundation/
    - Original BLEIBT UNVERÄNDERT
    - Kein used/, kein Rotate, kein Reuse
    """

    image_path = Path(image_path)
    image_path_str = str(image_path)

    # ------------------------------------------------
    # 🔒 MODE ERKENNEN
    # ------------------------------------------------
    is_weekly = "/approved/" in image_path_str
    is_foundation = "/assets/foundation/" in image_path_str

    if not (is_weekly or is_foundation):
        raise ValueError(
            "[BrandingRenderer] ❌ Quelle nicht erlaubt "
            "(nur approved/ oder assets/foundation/)"
        )

    if is_weekly and "/used/" in image_path_str:
        raise ValueError(
            "[BrandingRenderer] ❌ USED-Bilder dürfen NICHT erneut gebrandet werden"
        )

    mode = "FOUNDATION" if is_foundation else "WEEKLY"
    logger.info(f"[BrandingRenderer] 🔍 Mode erkannt: {mode}")

    # ------------------------------------------------
    # 🖼 BASISBILD LADEN
    # ------------------------------------------------
    img = Image.open(image_path).convert("RGBA")
    width, height = img.size

    BACKEND_ROOT = Path(__file__).resolve().parents[1]

    # ------------------------------------------------
    # 🎨 LOGO-PFAD
    # ------------------------------------------------
    logo_path = (
        BACKEND_ROOT
        / "clients"
        / brand_ctx["client_name"]
        / "assets"
        / "mtm_logo.png"
    )

    if not logo_path.exists():
        logger.error(f"[BrandingRenderer] ❌ Logo fehlt: {logo_path}")
        raise FileNotFoundError(logo_path)

    # ------------------------------------------------
    # 🧼 LOGO LADEN & TRIMMEN
    # ------------------------------------------------
    logo = Image.open(logo_path).convert("RGBA")
    logo = trim_transparency(logo)

    # ------------------------------------------------
    # 📐 LOGO-GRÖSSE
    # ------------------------------------------------
    logo_width = int(width * 1.10)
    ratio = logo_width / logo.width
    logo = logo.resize(
        (logo_width, int(logo.height * ratio)),
        Image.LANCZOS,
    )

    # ------------------------------------------------
    # 📍 POSITION
    # ------------------------------------------------
    BOTTOM_PADDING = 48
    x = (width - logo.width) // 2
    y = height - logo.height - BOTTOM_PADDING

    img.alpha_composite(logo, (x, y))

    # ------------------------------------------------
    # ✂️ TRIM
    # ------------------------------------------------
    new_height = y + logo.height
    img = img.crop((0, 0, width, new_height))

    # ------------------------------------------------
    # 💾 OUTPUT
    # ------------------------------------------------
    output_dir = (
        BACKEND_ROOT
        / "clients"
        / brand_ctx["client_name"]
        / "output"
        / "branded"
        / run_date.isoformat()
        / platform
    )
    output_dir.mkdir(parents=True, exist_ok=True)

    branded_path = output_dir / image_path.name

    img.convert("RGB").save(branded_path, quality=95, optimize=True)

    logger.info(f"[BrandingRenderer] ✅ Branding gespeichert → {branded_path}")

    # ------------------------------------------------
    # 📦 NUR WEEKLY → ORIGINAL NACH used/
    # ------------------------------------------------
    if is_weekly:
        used_dir = image_path.parent / "used"
        used_dir.mkdir(exist_ok=True)

        target_used_path = used_dir / image_path.name
        shutil.move(str(image_path), target_used_path)

        logger.info(
            f"[BrandingRenderer] 📦 WEEKLY Original verschoben → {target_used_path}"
        )
    else:
        logger.info(
            "[BrandingRenderer] 🔒 FOUNDATION Bild bleibt unverändert (kein used/)"
        )

    return str(branded_path)