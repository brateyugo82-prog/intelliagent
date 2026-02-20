"""
🧪 IntelliAgent DesignAgent Test — MTM Client
---------------------------------------------
Automatischer Test für den DesignAgent:
✅ Prüft config.json & Logo-Datei
✅ Generiert Bild über OpenAI (falls aktiviert)
✅ Führt lokales Branding durch (Logo + Text)
✅ Zeigt Ausgabe- und Fehlerpfade klar an
"""

import sys, json, os, time
from pathlib import Path
from core.logger import logger

# 🔧 Projekt-Root hinzufügen
ROOT_DIR = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT_DIR))

from agents.design_agent.agent import run, _add_logo

def main():
    client = "mtm_client"
    platform = "instagram"
    task = "Erzeuge ein Markenbild mit MTM-Logo"
    prompt = "Ein realistisches Foto eines MTM-Umzugs-LKWs mit zwei Handwerkern beim Tragen einer Couch."

    # === Pfade prüfen ===
    from core.paths import CLIENTS_DIR
    client_dir = CLIENTS_DIR / client
    logo_path = client_dir / "assets/logo.png"
    base_image = client_dir / "assets/flotte.png"
    config_path = client_dir / "config.json"
    out_dir = client_dir / "output/images"
    out_dir.mkdir(parents=True, exist_ok=True)

    print("\n🚀 Starte DesignAgent-Test für:", client)
    print("📂 Root:", client_dir)

    if not config_path.exists():
        print(f"❌ config.json fehlt unter: {config_path}")
        return
    if not logo_path.exists():
        print(f"⚠️  Kein Logo gefunden unter: {logo_path}")
    else:
        print(f"✅ Logo gefunden: {logo_path}")

    # === Modus prüfen ===
    mode = os.getenv("DESIGN_AGENT_MODE", "prod").lower()
    print(f"⚙️  Modus: {mode}")

    # === Test 1: Online / OpenAI-Modus ===
    if mode == "prod":
        print("\n🧠 Generiere neues Markenbild über OpenAI ...\n")
        result = run(prompt=prompt, client=client, platform=platform, task=task)
        print("\n=== RESULT (OpenAI) ===")
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print("\n⏩ Überspringe OpenAI-Test (Modus != PROD)")

    # === Test 2: Lokales Branding auf vorhandenes Fahrzeugbild ===
    if base_image.exists() and logo_path.exists():
        print("\n🧩 Lokaler Branding-Test — füge echtes Logo hinzu ...")
        try:
            temp_copy = out_dir / f"{client}_{int(time.time())}_local.png"
            from shutil import copyfile
            copyfile(base_image, temp_copy)
            _add_logo(temp_copy, logo_path)
            print("✅ Fertig! →", temp_copy.with_name(temp_copy.stem + "_with_logo.png"))
        except Exception as e:
            print("❌ Fehler beim lokalen Branding-Test:", e)
    else:
        print("⚠️ Kein Basisbild gefunden, lokales Branding übersprungen.")

    print("\n✅ Test abgeschlossen.")
    print(f"📁 Ergebnisse unter: {out_dir}")


if __name__ == "__main__":
    main()
