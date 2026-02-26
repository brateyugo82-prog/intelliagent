from pathlib import Path
from core.client_config import load_client_config
from core.logger import logger

# ------------------------------------------------------------
# ⚙️ KONSTANTEN
# ------------------------------------------------------------
ALLOWED_CATEGORIES = {
    "team_vehicle",
    "work_action",
    "finished_work",
    "process_detail",
    "empty_space",
}

IMAGE_EXTS = {".jpg", ".jpeg", ".png"}

# clients/<client>/assets/approved/<category>/*
BASE_DIR = Path(__file__).resolve().parents[2]
CLIENTS_DIR = BASE_DIR / "clients"


# ------------------------------------------------------------
# 📸 HELPER
# ------------------------------------------------------------
def _count_available_images(client: str, category: str) -> int:
    """
    Zählt verfügbare ORIGINAL-Bilder pro Kategorie
    (used/ wird NICHT berücksichtigt)
    """
    path = CLIENTS_DIR / client / "assets" / "approved" / category

    if not path.exists():
        logger.debug(f"[CategorySelector] Ordner fehlt: {path}")
        return 0

    count = sum(
        1
        for f in path.iterdir()
        if f.is_file() and f.suffix.lower() in IMAGE_EXTS
    )

    logger.debug(f"[CategorySelector] {client}/{category}: {count} Bilder")
    return count


def _pick_best_available(available: dict, weights: dict | None = None) -> str | None:
    """
    Pickt beste verfügbare Kategorie.
    Optional nach category_weights sortiert.
    """
    if weights:
        for cat, _ in sorted(weights.items(), key=lambda x: -x[1]):
            if available.get(cat, 0) > 0:
                return cat

    for cat, cnt in available.items():
        if cnt > 0:
            return cat

    return None


# ------------------------------------------------------------
# 🧠 HAUPTFUNKTION
# ------------------------------------------------------------
def pick_category(client: str, preferred: str | None = None) -> str:
    """
    Kategorie-Resolver (DUMM & STABIL)

    - preferred kommt vom Master (Prelaunch / Weekly / Dashboard)
    - prüft NUR, ob Bilder existieren
    - kein Rolling Plan
    """

    cfg = load_client_config(client)

    weights = cfg.get("category_weights", {})

    # ---------------- VERFÜGBARKEIT ----------------
    available = {
        cat: _count_available_images(client, cat)
        for cat in ALLOWED_CATEGORIES
    }

    logger.info(f"[CategorySelector] Verfügbare Bilder: {available}")

    # ---------------- 1️⃣ Preferred vom Master ----------------
    if preferred:
        if preferred not in ALLOWED_CATEGORIES:
            logger.warning(f"[CategorySelector] Ungültige Kategorie: {preferred}")
        elif available.get(preferred, 0) > 0:
            logger.info(f"[CategorySelector] Preferred OK → {preferred}")
            return preferred
        else:
            logger.warning(f"[CategorySelector] Preferred leer → {preferred}")

    # ---------------- 2️⃣ Gewichteter Fallback ----------------
    fallback = _pick_best_available(available, weights)
    if fallback:
        logger.warning(f"[CategorySelector] Fallback → {fallback}")
        return fallback

    # ---------------- TOTAL FAIL ----------------
    raise RuntimeError("❌ Keine Bilder in irgendeiner Kategorie verfügbar")