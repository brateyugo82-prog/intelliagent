from pathlib import Path
import json
from typing import List

ROTATION_DIR = Path("backend/state/image_rotation")
ROTATION_DIR.mkdir(parents=True, exist_ok=True)


def _get_state_file(client: str, category: str) -> Path:
    return ROTATION_DIR / f"{client}__{category}.json"


def get_next_image(
    client: str,
    category: str,
    images: List[Path]
) -> Path:
    """
    Gibt das nächste Bild zurück, ohne Wiederholung,
    rotiert durch alle Bilder.
    """

    if not images:
        raise RuntimeError("❌ Keine Bilder zur Rotation übergeben")

    state_file = _get_state_file(client, category)

    # -----------------------------------
    # State laden
    # -----------------------------------
    if state_file.exists():
        state = json.loads(state_file.read_text())
        last_index = state.get("last_index", -1)
    else:
        last_index = -1

    # -----------------------------------
    # Rotation
    # -----------------------------------
    next_index = (last_index + 1) % len(images)
    chosen = images[next_index]

    # -----------------------------------
    # State speichern
    # -----------------------------------
    state_file.write_text(
        json.dumps(
            {
                "last_index": next_index,
                "last_image": chosen.name
            },
            indent=2
        )
    )

    return chosen