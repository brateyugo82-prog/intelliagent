import json
import random
from pathlib import Path
from typing import Dict, List, Optional, Tuple

BASE_DIR = Path(__file__).resolve().parents[1]
CLIENTS_DIR = BASE_DIR / "clients"

PLATFORMS = {"instagram", "facebook", "linkedin"}

def _safe_load_json(path: Path) -> Optional[Dict]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None

def pick_cta(*, client: str, platform: str, category: str) -> Tuple[str, str]:
    """
    Returns (cta_id, cta_text)

    Expected structure in clients/<client>/cta_library.json:
    {
      "instagram": { "lead": ["...", ...], "service": [...], ... },
      "facebook":  { ... },
      "linkedin":  { ... }
    }
    """
    platform = platform.strip().lower()
    category = category.strip().lower()

    if platform not in PLATFORMS:
        return ("", "")

    path = CLIENTS_DIR / client / "cta_library.json"
    if not path.exists():
        return ("", "")

    data = _safe_load_json(path)
    if not isinstance(data, dict):
        return ("", "")

    pool = None
    plat_block = data.get(platform)
    if isinstance(plat_block, dict):
        pool = plat_block.get(category)

    if not isinstance(pool, list) or not pool:
        return ("", "")

    idx = random.randrange(0, len(pool))
    text = str(pool[idx]).strip()
    cta_id = f"{platform}_{category}_{idx+1:02d}"
    return (cta_id, text)