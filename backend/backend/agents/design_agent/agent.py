"""
✅ DesignAgent v13.4 — STRICT CATEGORY MODE (FINAL)
--------------------------------------------------
- image_context kommt NUR vom Master
- Ordnername = Kategorie (1:1)
- KEINE Eigenwahl
- KEIN Fallback
- Rotation pro Kategorie stabil
"""

from pathlib import Path
from PIL import Image, ImageOps

from backend.backend.core.logger import logger
from backend.backend.core.branding_loader import load_brand_context
from agents.design_agent.rotation import get_next_image

BASE_DIR = Path(__file__).resolve().parents[2]
CLIENTS_DIR = BASE_DIR / "clients"

ALLOWED_EXT = {".jpg", ".jpeg", ".png"}


def run(
    prompt: str = "",
    platform: str = "instagram",
    client: str | None = None,
    context: dict | None = None
):
    if not client:
        raise RuntimeError("❌ Client fehlt")

    context = context or {}
    image_context = context.get("image_context")

    if not image_context:
        raise RuntimeError("❌ image_context fehlt (Master muss Kategorie setzen)")

    assets_root = CLIENTS_DIR / client / "assets" / "approved"
    category_dir = assets_root / image_context

    if not category_dir.exists():
        raise RuntimeError(f"❌ Kategorie-Ordner fehlt: {image_context}")

    images = [
        p for p in category_dir.iterdir()
        if p.is_file() and p.suffix.lower() in ALLOWED_EXT
    ]

    if not images:
        raise RuntimeError(f"❌ Keine Bilder mehr in Kategorie '{image_context}'")

    chosen = get_next_image(
        client=client,
        category=image_context,
        images=images
    )

    if not chosen:
        raise RuntimeError(
            f"❌ Keine weiteren Bilder verfügbar für '{image_context}'"
        )

    # EXIF-Fix
    try:
        im = Image.open(chosen)
        im = ImageOps.exif_transpose(im)
        im.save(chosen)
    except Exception as e:
        logger.warning(f"[DesignAgent] EXIF-Fix fehlgeschlagen: {e}")

    brand_ctx = load_brand_context(client, prompt)

    logger.info(
        f"[DesignAgent] Bild gewählt: {chosen.name} | Kontext: {image_context}"
    )

    return {
        "status": "ok",
        "design": str(chosen),
        "image_context": image_context,
        "client": client,
        "platform": platform,
        "branding": {
            "logo": brand_ctx.get("logo"),
            "contact_overlay": brand_ctx.get("contact_overlay"),
            "image_category_rules": brand_ctx.get("image_category_rules"),
        }
    }