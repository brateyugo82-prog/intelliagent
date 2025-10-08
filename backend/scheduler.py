"""
Scheduler: Führt den MasterAgent für ausgewählte Clients automatisch aus.
Nur MTM ist aktiv.
"""

import time
from datetime import datetime
from backend.master_agent.master import run_workflow
from backend.core.logger import logger

# ------------------------------------------------------------
# 🧠 Konfiguration
# ------------------------------------------------------------
ACTIVE_CLIENTS = ["mtm_client"]  # 🚀 nur dieser Client läuft
INTERVAL_MINUTES = 30  # alle 30 Minuten (oder wie du willst)

# ------------------------------------------------------------
# 🚀 Hauptloop
# ------------------------------------------------------------
if __name__ == "__main__":
    while True:
        start_time = datetime.now()
        print(f"\n🕐 {start_time} – Starte Agentenlauf ...")

        for client in ACTIVE_CLIENTS:
            try:
                print(f"🚀 Starte Workflow für {client}")
                result = run_workflow(client)
                logger.info(f"[Scheduler] Workflow abgeschlossen für {client}")
            except Exception as e:
                logger.error(f"[Scheduler] Fehler bei {client}: {e}")

        print(f"🏁 Alle aktiven Clients abgeschlossen. Warte bis zum nächsten Lauf ...")
        time.sleep(INTERVAL_MINUTES * 60)
