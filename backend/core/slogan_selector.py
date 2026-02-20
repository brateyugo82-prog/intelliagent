import json
from pathlib import Path
from datetime import date
from typing import List

def pick_rotated_entry(
    *,
    items: List[str],
    client_dir: Path,
    key: str,
) -> str:
    """
    items = bereits geladene Liste (z.B. slogans aus JSON)
    key   = z.B. "slogan_work_action" oder "cta_team_vehicle"
    """

    if not items:
        return ""

    rotation_path = client_dir / "state" / "rotation.json"
    today = str(date.today())

    rotation = {}
    if rotation_path.exists():
        try:
            rotation = json.loads(rotation_path.read_text(encoding="utf-8"))
        except Exception:
            rotation = {}

    used_today = rotation.get(today, {}).get(key, [])

    for item in items:
        if item not in used_today:
            used_today.append(item)
            rotation.setdefault(today, {})[key] = used_today
            rotation_path.parent.mkdir(parents=True, exist_ok=True)
            rotation_path.write_text(
                json.dumps(rotation, indent=2, ensure_ascii=False),
                encoding="utf-8"
            )
            return item

    # alles durch → reset
    rotation.setdefault(today, {})[key] = [items[0]]
    rotation_path.write_text(
        json.dumps(rotation, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )
    return items[0]