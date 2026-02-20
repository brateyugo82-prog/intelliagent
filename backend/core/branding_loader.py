import importlib
from core.client_config import load_client_config
from core.logger import logger


def load_brand_context(client: str, prompt: str = "") -> dict:
    """
    Lädt Branding- & CI-Kontext eines Clients.
    Reihenfolge:
    1️⃣ config.json (Hauptquelle)
    2️⃣ branding_utils_<client>.py (optional Override)
    """

    # --------------------------------------------------
    # 1️⃣ CONFIG.JSON LADEN (PRIMÄR)
    # --------------------------------------------------
    try:
        cfg = load_client_config(client)
        brand_cfg = cfg.get("brand_assets", {})
        image_rules = cfg.get("image_category_rules", {})
        platform_overrides = cfg.get("platform_overrides", {})

        base_ctx = {
            "mode": "generate",
            "prompt": prompt,

            # Branding
            "logo": brand_cfg.get("logo"),
            "contact_overlay": brand_cfg.get("contact_overlay"),
            "slogan_sets": brand_cfg.get("slogan_sets"),

            # Regeln
            "image_category_rules": image_rules,
            "platform_overrides": platform_overrides,

            # Defaults
            "tone": cfg.get("brand_identity", {}).get("style", "professionell"),
            "region": cfg.get("contact", {}).get("address"),
        }

        logger.info(f"[BrandingLoader] ✅ config.json geladen für {client}")

    except Exception as e:
        logger.warning(f"[BrandingLoader] ⚠️ Config-Ladefehler für {client}: {e}")
        base_ctx = {
            "mode": "generate",
            "prompt": prompt,
            "logo": None,
            "contact_overlay": None,
            "slogan_sets": {},
            "image_category_rules": {},
            "platform_overrides": {},
            "tone": "professionell",
            "region": None,
        }

    # --------------------------------------------------
    # 2️⃣ OPTIONAL: branding_utils_<client> OVERRIDE
    # --------------------------------------------------
    try:
        module_path = f"backend.clients.{client}.branding_utils_{client}"
        branding_utils = importlib.import_module(module_path)

        override_ctx = branding_utils.get_brand_context(client, prompt) or {}

        base_ctx.update(override_ctx)

        logger.info(f"[BrandingLoader] 🔁 branding_utils Override aktiv für {client}")

    except Exception:
        logger.info(f"[BrandingLoader] ℹ️ Kein branding_utils Override für {client}")

    return base_ctx