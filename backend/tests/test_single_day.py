"""
🧪 IntelliAgent Test — Einzel-Workflow (z. B. Montag)
---------------------------------------------------
Führt den kompletten Agentenlauf für den MTM-Client aus,
um einen vollen Workflow (Content → Design → Communication → Publish → Analytics)
für einen einzigen Tag zu simulieren.
"""

import sys
from master_agent.master import run_workflow

if __name__ == "__main__":
    client = "mtm_client"
    platform = "instagram"
    prompt = "Erstelle einen realistischen Post für Social Media über Möbelmontage durch das MTM-Team."
    
    print("\n🚀 Starte Einzel-Workflow-Test für Montag (generate)...\n")
    results = run_workflow(client=client, prompt=prompt, platform=platform)
    print("\n✅ Test abgeschlossen.\nErgebnis:")
    for agent, output in results.items():
        print(f"🧩 {agent}: {output.get('status', 'no status')}")
