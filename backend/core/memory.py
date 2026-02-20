"""
🧠 Memory-Subsystem für IntelliAgent (FINAL & STABLE)
-----------------------------------------------------
Speichert pro Kunde:
- Texte
- Prompts
- Agenten-Metadaten

Ziel:
- Doppelte Inhalte verhindern
- Agenten-Entscheidungen absichern
- Langfristige Lernbasis pro Kunde

✔ Import-sicher
✔ JSON-robust
✔ Multi-Tenant-fähig
"""

import os
import json
import hashlib
from datetime import datetime, timedelta
from typing import Dict, Any

from core.logger import logger


# --------------------------------------------------
# 📁 Pfade & Setup
# --------------------------------------------------

def _memory_path(client: str) -> str:
    """
    Gibt den Pfad zur memory.json eines Clients zurück.
    """
    return os.path.join("clients", client, "memory.json")


def _ensure_file(path: str):
    """
    Stellt sicher, dass memory.json existiert und gültig ist.
    """
    os.makedirs(os.path.dirname(path), exist_ok=True)

    if not os.path.exists(path):
        with open(path, "w", encoding="utf-8") as f:
            json.dump({"entries": []}, f, indent=2, ensure_ascii=False)


# --------------------------------------------------
# 📖 Laden & Speichern
# --------------------------------------------------

def load_memory(client: str) -> Dict[str, Any]:
    path = _memory_path(client)
    _ensure_file(path)

    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            if "entries" not in data:
                raise ValueError("Ungültige Memory-Struktur")
            return data
    except Exception:
        logger.warning(
            f"[Memory] ⚠ Defekte memory.json bei {client} → Datei neu initialisiert"
        )
        _ensure_file(path)
        return {"entries": []}


def save_memory(client: str, data: Dict[str, Any]):
    path = _memory_path(client)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


# --------------------------------------------------
# 🔐 Hashing
# --------------------------------------------------

def _hash(text: str) -> str:
    return hashlib.sha256(text.strip().encode("utf-8")).hexdigest()


# --------------------------------------------------
# 🧠 Memory-Logik
# --------------------------------------------------

def already_seen(client: str, text: str) -> bool:
    """
    Prüft, ob ein Text/Prompt bereits im Memory existiert.
    """
    if not text:
        return False

    memory = load_memory(client)
    h = _hash(text)

    seen = any(entry.get("hash") == h for entry in memory["entries"])
    if seen:
        logger.info(f"[Memory] 🔁 Duplicate erkannt für {client}")

    return seen


def remember(client: str, text: str, meta: Dict[str, Any] | None = None):
    """
    Speichert neuen Text/Prompt inkl. Metadaten im Memory.
    """
    if not text:
        return

    memory = load_memory(client)
    h = _hash(text)

    if any(entry.get("hash") == h for entry in memory["entries"]):
        return  # bereits bekannt

    entry = {
        "hash": h,
        "text_preview": text[:150],
        "timestamp": datetime.now().isoformat(),
        "meta": meta or {},
    }

    memory["entries"].append(entry)
    save_memory(client, memory)

    logger.info(
        f"[Memory] 💾 Neuer Eintrag für {client}: {entry['text_preview'][:60]}..."
    )


def cleanup(client: str, days: int = 30):
    """
    Löscht alte Memory-Einträge (älter als X Tage).
    """
    memory = load_memory(client)
    cutoff = datetime.now() - timedelta(days=days)

    before = len(memory["entries"])
    memory["entries"] = [
        e
        for e in memory["entries"]
        if datetime.fromisoformat(e["timestamp"]) > cutoff
    ]
    after = len(memory["entries"])

    save_memory(client, memory)

    logger.info(
        f"[Memory] 🧹 Cleanup für {client}: {before - after} Einträge entfernt "
        f"(älter als {days} Tage)"
    )
