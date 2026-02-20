"""
🔄 Sync Assets → Output Preview (FINAL)
--------------------------------------
- liest Kategorien aus assets/approved/<category>/
- kopiert Bilder nach output/preview
- pflegt state/image_meta.json als EINZIGE Wahrheitsquelle
"""

from pathlib import Path
import json
import shutil

# -------------------------------------------------
# 📂 Basis
# -------------------------------------------------
BASE_DIR = Path(__file__).resolve().parents[1]   # backend/
CLIENT = "mtm_client"

CLIENT_DIR = BASE_DIR / "clients" / CLIENT
ASSETS_DIR = CLIENT_DIR / "assets" / "approved"
PREVIEW_DIR = CLIENT_DIR / "output" / "preview"
STATE_DIR = CLIENT_DIR / "state"
META_FILE = STATE_DIR / "image_meta.json"

PREVIEW_DIR.mkdir(parents=True, exist_ok=True)
STATE_DIR.mkdir(parents=True, exist_ok=True)

# -------------------------------------------------
# 📦 Bestehende Meta laden
# -------------------------------------------------
if META_FILE.exists():
    try:
        meta = json.loads(META_FILE.read_text(encoding="utf-8"))
    except Exception:
        meta = {}
else:
    meta = {}

print("🔄 Sync assets → preview inkl. Kategorien")

# -------------------------------------------------
# 🔄 Sync
# -------------------------------------------------
for category_dir in ASSETS_DIR.iterdir():
    if not category_dir.is_dir():
        continue

    category = category_dir.name

    for img in category_dir.iterdir():
        if img.suffix.lower() not in {".jpg", ".jpeg", ".png"}:
            continue

        # Zielbild
        target = PREVIEW_DIR / img.name

        # Bild kopieren (nur wenn nicht vorhanden)
        if not target.exists():
            shutil.copy2(img, target)

        # Meta pflegen
        meta.setdefault(img.name, {})
        meta[img.name]["category"] = category
        meta[img.name].setdefault("caption", "")
        meta[img.name]["source"] = "assets"

# -------------------------------------------------
# 💾 Meta speichern
# -------------------------------------------------
META_FILE.write_text(
    json.dumps(meta, indent=2, ensure_ascii=False),
    encoding="utf-8"
)

print("✅ Sync abgeschlossen")
print(f"📄 Meta-Datei aktualisiert: {META_FILE}")