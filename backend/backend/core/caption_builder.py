
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
CLIENTS_DIR = BASE_DIR / "clients"

# ============================================================
# ✅ SINGLE SOURCE OF TRUTH: captions/foundation.json
# ============================================================
def build_caption(*, client: str, platform: str, post_id: str | None = None, **_) -> str:
    if not post_id:
        return ""

    path = CLIENTS_DIR / client / "captions" / "foundation.json"
    if not path.exists():
        return ""

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return ""

    entry = data.get(post_id)
    if not isinstance(entry, dict):
        return ""

    text = entry.get(platform)
    return text.strip() if isinstance(text, str) else ""
