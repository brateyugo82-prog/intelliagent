from PIL import Image, ImageOps
from pathlib import Path
from datetime import date
import shutil
from backend.backend.core.logger import logger


def apply_branding(
    image_path: str,
    brand_ctx: dict,
    image_context: str,
    platform: str,
    run_date: date,
) -> str:

    image_path = Path(image_path)
    image_path_str = str(image_path)

    is_weekly = "/approved/" in image_path_str
    is_foundation = "/assets/foundation/" in image_path_str

    if is_weekly and "/used/" in image_path_str:
        raise ValueError("USED-Bilder dürfen nicht erneut gebrandet werden")

    mode = "FOUNDATION" if is_foundation else "WEEKLY"
    logger.info(f"[BrandingRenderer] Mode erkannt: {mode}")

    # ------------------------------------------------
    # BASISBILD
    # ------------------------------------------------
    img = ImageOps.exif_transpose(Image.open(image_path))
    if img.mode != "RGBA":
        img = img.convert("RGBA")

    width, height = img.size

    BACKEND_ROOT = Path(__file__).resolve().parents[1]

    # ------------------------------------------------
    # LOGO
    # ------------------------------------------------
    logo_path = (
        BACKEND_ROOT
        / "clients"
        / brand_ctx["client_name"]
        / "branding"
        / "logo.png"
    )

    if not logo_path.exists():
        raise FileNotFoundError(logo_path)

    logo = Image.open(logo_path).convert("RGBA")

    # ------------------------------------------------
    # LOGO SIZE (STABIL WIE FRÜHER)
    # ------------------------------------------------
    LOGO_HEIGHT = int(height * 0.12)
    ratio = LOGO_HEIGHT / logo.height
    logo = logo.resize(
        (int(logo.width * ratio), LOGO_HEIGHT),
        Image.LANCZOS
    )

    # ------------------------------------------------
    # POSITION (UNTEN, ZENTRIERT)
    # ------------------------------------------------
    x = (width - logo.width) // 2
    y = height - logo.height

    img.alpha_composite(logo, (x, y))

    # ------------------------------------------------
    # OUTPUT
    # ------------------------------------------------
    if "/images/" in image_path_str:
        output_dir = (
            BACKEND_ROOT
            / "clients"
            / brand_ctx["client_name"]
            / "output"
            / "preview"
        )
    else:
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
    out_path = output_dir / image_path.name

    img.convert("RGB").save(out_path, "JPEG", quality=95, subsampling=0)

    logger.info(f"[BrandingRenderer] Branding gespeichert → {out_path}")

    if is_weekly:
        used_dir = image_path.parent / "used"
        used_dir.mkdir(exist_ok=True)
        shutil.move(str(image_path), used_dir / image_path.name)

    return str(out_path)
