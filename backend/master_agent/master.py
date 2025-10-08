"""
Dynamischer Master Agent: Orchestriert alle Agenten in einer sichtbaren Kette.
Verarbeitet Content-, Design-, Communication-, Publish- und Analytics-Agenten
in definierter Reihenfolge und sorgt für Logging, Memory-Cleanup & Config-Handling.
"""

import importlib
import os
import sys
import json
from typing import Dict, Any
from datetime import datetime
from dotenv import load_dotenv
from backend.core.logger import logger
from backend.core.config import get_openai_key
from backend.core import memory

# ------------------------------------------------------------
# 🧭 Basisverzeichnisse (wichtig gegen doppelte "clients"-Ordner)
# ------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLIENTS_DIR = os.path.join(BASE_DIR, "clients")

# ------------------------------------------------------------
# 🎨 Farben für Konsole
# ------------------------------------------------------------
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
RESET = "\033[0m"


# ------------------------------------------------------------
# 📁 Client Config laden
# ------------------------------------------------------------
def load_client_config(client: str) -> Dict[str, Any]:
    path = os.path.join(CLIENTS_DIR, client, "config.json")
    if not os.path.exists(path):
        logger.warning(f"[MasterAgent] Keine config.json für Client {client}")
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


# ------------------------------------------------------------
# ✂️ Hilfsfunktion zur Textkürzung
# ------------------------------------------------------------
def _shorten(value: str, length: int = 80) -> str:
    if not value:
        return ""
    return (value[:length] + "...") if len(value) > length else value


# ------------------------------------------------------------
# 🧠 Hauptworkflow
# ------------------------------------------------------------
def run_workflow(client: str, prompt: str = "", platform: str = "") -> dict:
    results = {}

    client_dir = os.path.join(CLIENTS_DIR, client)
    dotenv_path = os.path.join(client_dir, ".env")
    output_dir = os.path.join(client_dir, "output")
    os.makedirs(output_dir, exist_ok=True)

    # 🔑 API-Key vorbereiten (globaler Key aus .env oder Umgebung)
    openai_key = get_openai_key()
    if not openai_key or openai_key == "DUMMY_KEY":
        logger.warning(f"[MasterAgent] Kein gültiger OpenAI-Key gefunden. Workflow läuft im Mock-Modus.")

    # 🌍 Client-spezifische .env laden
    if os.path.exists(dotenv_path):
        load_dotenv(dotenv_path, override=True)
        logger.info(f"[MasterAgent] .env geladen für {client}")
    else:
        logger.warning(f"[MasterAgent] Keine .env für {client}")

    # ⚙️ Client-Config laden
    config = load_client_config(client)
    config["client"] = client
    config["assets_path"] = os.path.join(client_dir, "assets")
    agents_cfg = config.get("agents", {})

    # 🔁 Reihenfolge der Agenten
    agent_order = [
        ("content_agent", "ContentAgent"),
        ("design_agent", "DesignAgent"),
        ("communication_agent", "CommunicationAgent"),
        ("publish_agent", "PublishAgent"),
        ("analytics_agent", "AnalyticsAgent"),
    ]

    print(f"\n{CYAN}🚀 Starte Workflow für Client: {client} | Platform: {platform or '-'}{RESET}\n")

    for agent_key, agent_log in agent_order:
        try:
            module_path = f"backend.agents.{agent_key}.agent"
            agent_module = importlib.import_module(module_path)

            # 🧩 Task aus config.json oder Default
            task = agents_cfg.get(agent_key, {}).get("task")
            if not task:
                defaults = {
                    "content_agent": "Erstelle Content",
                    "design_agent": "Erzeuge ein Bild",
                    "communication_agent": "Formuliere Kundenkommunikation",
                    "publish_agent": "Veröffentliche Content",
                    "analytics_agent": "Analysiere Content",
                }
                task = defaults.get(agent_key, "Task ausführen")

            print(f"{YELLOW}➡️  {agent_log}: {task}{RESET}")

            # 🧠 Agenten-Aufruf
            result = agent_module.run(prompt=prompt, task=task, platform=platform, client=client)

            if not isinstance(result, dict):
                raise ValueError("Agent gibt kein Dict zurück!")

            results[agent_key] = result

            # 💬 Vorschau / Kurz-Ausgabe
            preview = None
            if "content" in result:
                preview = _shorten(result["content"])
            elif "design" in result:
                preview = result["design"]
            elif "output" in result:
                preview = _shorten(str(result["output"]))
            elif "publish" in result:
                preview = _shorten(result["publish"])
            elif "analytics" in result:
                preview = _shorten(result["analytics"])

            if preview:
                print(f"{GREEN}✅ {agent_log} abgeschlossen | Output: {preview}{RESET}\n")
            else:
                print(f"{GREEN}✅ {agent_log} abgeschlossen{RESET}\n")

        except Exception as e:
            logger.error(f"[MasterAgent] Fehler bei {agent_key}: {e}")
            results[agent_key] = {"error": str(e)}
            print(f"{RED}❌ {agent_log} Fehler: {e}{RESET}\n")

    # 💾 Ergebnisse speichern
    result_path = os.path.join(output_dir, "workflow_result.json")
    with open(result_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    # 🧹 Memory-Cleanup (alte Einträge löschen)
    try:
        memory.cleanup(client, days=30)
        logger.info(f"[MasterAgent] Memory-Cleanup für {client} durchgeführt.")
    except Exception as mem_err:
        logger.warning(f"[MasterAgent] Memory-Cleanup übersprungen: {mem_err}")

    print(f"{CYAN}🏁 Workflow abgeschlossen. Ergebnisse gespeichert in {result_path}{RESET}\n")
    return results


# ------------------------------------------------------------
# 🧩 Direkter Start (CLI)
# ------------------------------------------------------------
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python backend/master_agent/master.py <client_name> [prompt] [platform]")
        sys.exit(1)

    client_name = sys.argv[1]
    prompt = sys.argv[2] if len(sys.argv) > 2 else ""
    platform = sys.argv[3] if len(sys.argv) > 3 else ""

    start_time = datetime.now()
    print(f"\n🕐 {start_time} – Starte Agentenlauf ...")
    try:
        run_workflow(client_name, prompt, platform)
    except KeyboardInterrupt:
        print("\n🚫 Workflow manuell abgebrochen.")
    except Exception as e:
        logger.error(f"[MasterAgent] Unerwarteter Fehler: {e}")
        print(f"{RED}❌ Unerwarteter Fehler: {e}{RESET}")
