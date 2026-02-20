"""
🧪 IntelliAgent Weekly Cycle Test — MTM Client
------------------------------------------------
Simuliert den vollständigen Wochenablauf mit Posting-Plan.
Erzeugt realistische Posts (Bilder + Texte) für 5 Tage:
Montag–Freitag → generate / flotte_text / mix
"""

import sys
from master_agent.master import run_workflow
from agents.publish_agent.agent import _get_posting_mode
from datetime import datetime, timedelta

def simulate_day(client: str, date: datetime):
    day_name = date.strftime("%A")
    print(f"\n📅 Simuliere {day_name} — {date.strftime('%d.%m.%Y')}")
    mode = _get_posting_mode(client)
    print(f"🔧 Ermittelter Modus: {mode}")

    prompt = f"Automatischer Testpost ({mode}) für {day_name}."
    platform = "instagram,facebook"

    results = run_workflow(client=client, prompt=prompt, platform=platform)
    print(f"✅ {day_name} abgeschlossen.\n")
    return results

if __name__ == "__main__":
    client = "mtm_client"
    start_date = datetime.now()

    print("\n🚀 Starte Wochen-Test (MTM Postingplan: Mo–Fr)\n")

    for i in range(5):  # Montag bis Freitag
        test_date = start_date + timedelta(days=i)
        simulate_day(client, test_date)

    print("\n🏁 Wochen-Test abgeschlossen. Ergebnisse siehe clients/mtm_client/output/")
