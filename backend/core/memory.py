"""
Memory-Subsystem für IntelliAgent.
Speichert pro Kunde alle erzeugten Texte, Prompts und Metadaten,
um doppelte Inhalte zu vermeiden.
"""

import os, json, hashlib
from datetime import datetime, timedelta
from typing import Dict, Any
from backend.core.logger import logger  # 👈 Logging-Integration

# --------------------------------------------------
# 🔧 Grundfunktionen
# --------------------------------------------------

def _memory_path(client: str) -> str:
    return os.path.join("backend", "clients", client, "memory.json")


def _ensure_file(path: str):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    if not os.path.exists(path):
        with open(path, "w", encoding="utf-8") as f:
            json.dump({"entries": []}, f, indent=2, ensure_ascii=False)


def load_memory(client: str) -> Dict[str, Any]:
    path = _memory_path(client)
    _ensure_file(path)
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        logger.warning(f"[Memory] Defekte memory.json bei {client} → neu erstellt")
        _ensure_file(path)
        return {"entries": []}


def save_memory(client: str, data: Dict[str, Any]):
    path = _memory_path(client)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


# --------------------------------------------------
# 🧠 Logik
# --------------------------------------------------

def _hash(text: str) -> str:
    return hashlib.sha256(text.strip().encode("utf-8")).hexdigest()


def already_seen(client: str, text: str) -> bool:
    """Prüft, ob ein Text/Prompt bereits bekannt ist."""
    if not text:
        return False
    memory = load_memory(client)
    h = _hash(text)
    seen = any(entry["hash"] == h for entry in memory["entries"])
    if seen:
        logger.info(f"[Memory] Duplicate erkannt für {client}")
    return seen


def remember(client: str, text: str, meta: Dict[str, Any] = None):
    """Speichert neuen Text/Prompt im Memory."""
    if not text:
        return
    memory = load_memory(client)
    h = _hash(text)
    if any(entry["hash"] == h for entry in memory["entries"]):
        return  # schon bekannt

    entry = {
        "hash": h,
        "text_preview": text[:150],
        "timestamp": datetime.now().isoformat(),
        "meta": meta or {}
    }
    memory["entries"].append(entry)
    save_memory(client, memory)
    logger.info(f"[Memory] Neuer Eintrag gespeichert für {client}: {entry['text_preview'][:60]}...")


def cleanup(client: str, days: int = 30):
    """Löscht alte Einträge (älter als X Tage)."""
    memory = load_memory(client)
    cutoff = datetime.now() - timedelta(days=days)
    memory["entries"] = [
        e for e in memory["entries"]
        if datetime.fromisoformat(e["timestamp"]) > cutoff
    ]
    save_memory(client, memory)
    logger.info(f"[Memory] Alte Einträge für {client} bereinigt (älter als {days} Tage).")
