import json
import random
from pathlib import Path
from typing import List


def _rotation_file(client: str, category: str) -> Path:
    return (
        Path(__file__).resolve().parents[3]
        / "clients"
        / client
        / "output"
        / "rotation"
        / f"slogans_{category}.json"
    )


def get_next_slogan(
    *,
    client: str,
    category: str,
    slogans: List[str]
) -> str:
    """
    Gibt garantiert einen Slogan aus der AKTUELLEN Whitelist zurück.
    - Keine historischen / verbotenen Slogans
    - Rotation bleibt stabil
    - Reset, wenn Whitelist geändert wurde
    """

    if not slogans:
        raise RuntimeError("❌ Leere Slogan-Liste")

    path = _rotation_file(client, category)
    path.parent.mkdir(parents=True, exist_ok=True)

    slogans_set = set(slogans)

    # -------------------------------------------------
    # 🆕 ERSTE NUTZUNG ODER RESET
    # -------------------------------------------------
    if not path.exists():
        shuffled = slogans[:]
        random.shuffle(shuffled)

        data = {
            "remaining": shuffled,
            "used": []
        }

    else:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # -------------------------------------------------
        # 🔒 HARTE BEREINIGUNG GEGEN WHITELIST
        # -------------------------------------------------
        data["remaining"] = [
            s for s in data.get("remaining", [])
            if s in slogans_set
        ]
        data["used"] = [
            s for s in data.get("used", [])
            if s in slogans_set
        ]

        # -------------------------------------------------
        # 🔁 ALLES VERBRAUCHT ODER ALLES RAUSGEFILTERT
        # -------------------------------------------------
        if not data["remaining"]:
            shuffled = slogans[:]
            random.shuffle(shuffled)

            data = {
                "remaining": shuffled,
                "used": []
            }

    # -------------------------------------------------
    # 🎯 NÄCHSTER SLOGAN (GARANTIERT VALIDE)
    # -------------------------------------------------
    slogan = data["remaining"].pop(0)

    if slogan not in slogans_set:
        raise RuntimeError(
            f"❌ Rotation-Fehler: Slogan nicht in Whitelist ({category}): {slogan}"
        )

    data["used"].append(slogan)

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    return slogan