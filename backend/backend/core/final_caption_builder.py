import json
import random
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
CLIENTS_DIR = BASE_DIR / "clients"


def _pick_random(path: Path, platform: str) -> str:
    if not path.exists():
        return ""

    data = json.loads(path.read_text(encoding="utf-8"))
    items = data.get(platform, [])
    if not items:
        return ""

    return random.choice(items)


def build_final_caption(
    *,
    client: str,
    platform: str,
    base_text: str,
    category: str
) -> str:
    """
    Baut die finale Caption für die Plattform:
    - base_text (aus Dashboard / captions)
    - + CTA (bereits im Text oder extra)
    - + Emojis
    - + Hashtags
    """

    platform = platform.lower()

    client_dir = CLIENTS_DIR / client

    emoji = _pick_random(
        client_dir / "emojis" / f"{category}.json",
        platform
    )

    hashtags = _pick_random(
        client_dir / "hashtags" / f"{category}.json",
        platform
    )

    parts = [base_text.strip()]

    if emoji:
        parts.append(emoji)

    if hashtags:
        parts.append(hashtags)

    return "\n\n".join(parts).strip()
