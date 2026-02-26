"""
✅ IntelliAgent Analytics Worker (STABLE, Minimal)
-------------------------------------------------
- Triggert AnalyticsAgent periodisch
- KEIN Dashboard-Code
- KEIN Master-Agent
- Ergebnisse werden persistent gespeichert
- Loop-fähig für Render Worker
- RUN_ONCE=1 für lokalen Test
"""

from __future__ import annotations

import os
import time
from datetime import datetime
from pathlib import Path
from typing import List

from backend.backend.core.logger import logger
from agents.analytics_agent.agent import run as analytics_run


BASE_DIR = Path(__file__).resolve().parents[2]  # backend/
CLIENTS_DIR = BASE_DIR / "clients"


def _list_clients() -> List[str]:
    if not CLIENTS_DIR.exists():
        return []

    return [
        p.name
        for p in CLIENTS_DIR.iterdir()
        if p.is_dir() and not p.name.startswith("--")
    ]


def run_once():
    logger.info("[AnalyticsWorker] 🚀 Analytics-Lauf gestartet")

    clients = _list_clients()
    period = os.getenv("ANALYTICS_PERIOD", "30d")

    for client in clients:
        try:
            logger.info(f"[AnalyticsWorker] 📊 Analysiere client={client}")
            analytics_run(
                prompt="Automatischer Performance-Zyklus",
                client=client,
                platform="multi",
                period=period,
            )
        except Exception as e:
            logger.error(f"[AnalyticsWorker] ❌ Fehler bei client={client}: {e}")

    logger.info("[AnalyticsWorker] ✅ Analytics-Lauf abgeschlossen")


def loop(poll_seconds: int = 3600):
    logger.info(f"[AnalyticsWorker] 🔁 Worker gestartet | poll_seconds={poll_seconds}")

    while True:
        run_once()

        if os.getenv("RUN_ONCE", "") == "1":
            logger.info("[AnalyticsWorker] 🧪 RUN_ONCE=1 -> exit")
            return

        time.sleep(poll_seconds)


if __name__ == "__main__":
    poll = int(os.getenv("ANALYTICS_POLL_SECONDS", "3600"))  # default: 1h
    loop(poll_seconds=poll)