"""
Conversion Agent v1.0
---------------------
- Markiert Leads als gewonnen oder verloren
- Grundlage für Abrechnung & ROI
"""

from datetime import datetime
from pathlib import Path
import csv
from typing import Dict

from backend.backend.core.logger import logger

BASE_DIR = Path(__file__).resolve().parents[1]


def _get_conversions_path(client: str) -> Path:
    path = BASE_DIR / "clients" / client / "data" / "conversions.csv"
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def _ensure_csv_exists(path: Path):
    if not path.exists():
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                "date",
                "platform",
                "message",
                "conversion_status",  # won | lost
                "revenue_eur"
            ])


def run(
    client: str,
    platform: str,
    message: str,
    status: str,              # "won" oder "lost"
    revenue_eur: float = 0.0  # nur bei won relevant
) -> Dict:

    if status not in {"won", "lost"}:
        return {"error": "status must be 'won' or 'lost'"}

    path = _get_conversions_path(client)
    _ensure_csv_exists(path)

    with open(path, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            datetime.now().isoformat(),
            platform,
            message,
            status,
            revenue_eur if status == "won" else 0.0
        ])

    logger.info(f"[ConversionAgent] ✅ Lead '{status}' gespeichert")

    return {
        "status": "stored",
        "conversion": status,
        "revenue_eur": revenue_eur
    }