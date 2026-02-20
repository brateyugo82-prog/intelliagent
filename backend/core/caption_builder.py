import json
import random
from pathlib import Path
from typing import Any, Dict, List, Optional

BASE_DIR = Path(__file__).resolve().parents[1]
CLIENTS_DIR = BASE_DIR / "clients"

PLATFORMS = {"instagram", "facebook", "linkedin"}


# -------------------------------------------------
# JSON HELPERS
# -------------------------------------------------

def _safe_load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


# -------------------------------------------------
# SLOGAN NORMALIZATION
# -------------------------------------------------

def _normalize_entries(data: Any, category: str) -> List[Dict[str, Any]]:
    """
    Unterstützt:
    1) [ {instagram:{...}, facebook:{...}, linkedin:{...}}, ... ]
    2) { "items": [ ... ] }
    3) { "<category>": [ ... ] }
    4) { "<category>": { ... } }   (single entry)
    5) { "id1": {...}, "id2": {...} }
    """
    if not data:
        return []

    if isinstance(data, list):
        return [x for x in data if isinstance(x, dict)]

    if isinstance(data, dict):
        if isinstance(data.get("items"), list):
            return [x for x in data["items"] if isinstance(x, dict)]

        if isinstance(data.get(category), list):
            return [x for x in data[category] if isinstance(x, dict)]

        if isinstance(data.get(category), dict):
            return [data[category]]

        values = list(data.values())
        if values and all(isinstance(v, dict) for v in values):
            return values

    return []


def _pick_platform_block(entry: Dict[str, Any], platform: str) -> Optional[Dict[str, Any]]:
    block = entry.get(platform)
    if isinstance(block, dict):
        return block
    return None


def _normalize_hashtags(hashtags: Any, platform: str) -> List[str]:
    if isinstance(hashtags, list):
        tags = [str(x).strip() for x in hashtags if str(x).strip()]
    else:
        tags = []

    if platform == "instagram":
        return tags[:12]
    if platform == "facebook":
        return tags[:6]
    if platform == "linkedin":
        return tags[:4]
    return tags[:8]


# -------------------------------------------------
# CTA
# -------------------------------------------------

def _pick_cta(client: str, platform: str, category: str) -> str:
    """
    Holt gezielt CTA aus clients/<client>/cta_library.json
    """
    cta_path = CLIENTS_DIR / client / "cta_library.json"
    if not cta_path.exists():
        return ""

    lib = _safe_load_json(cta_path)
    if not isinstance(lib, dict):
        return ""

    options = (
        lib
        .get(platform, {})
        .get(category, [])
    )

    if not options or not isinstance(options, list):
        return ""

    return random.choice(options).strip()


# -------------------------------------------------
# PUBLIC API
# -------------------------------------------------

def build_caption(*, client: str, category: str, platform: str) -> str:
    """
    Baut Caption aus:
    - Text + Hashtags aus slogans/<category>.json
    - CTA aus cta_library.json
    """
    platform = platform.strip().lower()
    category = category.strip().lower()

    if platform not in PLATFORMS:
        return ""

    slogan_path = CLIENTS_DIR / client / "slogans" / f"{category}.json"
    if not slogan_path.exists():
        return ""

    data = _safe_load_json(slogan_path)
    entries = _normalize_entries(data, category=category)
    if not entries:
        return ""

    entry = random.choice(entries)
    block = _pick_platform_block(entry, platform)
    if not block:
        return ""

    text = str(block.get("caption") or block.get("text") or "").strip()
    hashtags = _normalize_hashtags(block.get("hashtags", []), platform)
    cta = _pick_cta(client, platform, category)

    parts: List[str] = []
    if text:
        parts.append(text)
    if cta:
        parts.append(cta)
    if hashtags:
        parts.append(" ".join(hashtags))

    return "\n\n".join(parts).strip()