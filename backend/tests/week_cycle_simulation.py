"""
🧪 IntelliAgent Week Simulation Test
------------------------------------
Simuliert eine komplette Woche (Mo–Fr) für MTM.
Dienstag & Donnerstag → flotte.png (Overlay)
Andere Tage → reguläre KI-Bildgenerierung.
"""

from datetime import datetime, timedelta
from master_agent.master import run_workflow
import agents.publish_agent.agent as publish_agent
import importlib

CLIENT = "mtm_client"
PLATFORM = "instagram,facebook"

def simulate_day(fake_day: str):
    """Simuliert einen einzelnen Tag (setzt Fake-Day in _get_posting_mode)."""
    print(f"\n📅 Simuliere {fake_day}")

    # Monkeypatch _get_posting_mode → gibt gewünschten Wochentag zurück
    original_get_posting_mode = publish_agent._get_posting_mode

    def fake_mode(client: str):
        # Kunde-Config laden
        from pathlib import Path
        import json
        cfg_path = Path(__file__).resolve().parents[1] / "clients" / client / "config.json"
        with open(cfg_path, "r", encoding="utf-8") as f:
            cfg = json.load(f)
        plan = cfg.get("posting_plan", {})
        if fake_day in plan.get("days_flottetext", []):
            return "flotte_text"
        elif fake_day in plan.get("days_new_images", []):
            return "generate"
        return "none"

    publish_agent._get_posting_mode = fake_mode

    # Workflow starten
    result = run_workflow(client=CLIENT, prompt=f"Simulierter Tag: {fake_day}", platform=PLATFORM)

    # Modus wiederherstellen
    publish_agent._get_posting_mode = original_get_posting_mode

    return result


if __name__ == "__main__":
    # Montag–Freitag simulieren
    week_days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    for day in week_days:
        simulate_day(day)

    print("\n🏁 Wochen-Simulation abgeschlossen – Ergebnisse unter:")
    print("→ clients/mtm_client/output/images/")
