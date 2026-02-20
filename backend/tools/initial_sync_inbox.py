from pathlib import Path
import shutil
import time

# =====================================================
# 🔹 PROJECT ROOT (FIX – DAMIT PYTHON NICHT IRGENDWOHIN SCHREIBT)
# =====================================================
PROJECT_ROOT = Path.home() / "IntelliAgent"
BACKEND_ROOT = PROJECT_ROOT / "backend"

# =====================================================
# 🔹 GOOGLE DRIVE INBOX (lokaler Spiegel – macOS)
# =====================================================
BASE = (
    Path.home()
    / "Library"
    / "CloudStorage"
    / "GoogleDrive-brateyugo82@gmail.com"
    / "Meine Ablage"
    / "MTM_Social_Media"
    / "Inbox"
)

INBOX_IMAGES = BASE / "bilder"
INBOX_VIDEOS = BASE / "videos"

# =====================================================
# 🔹 BACKEND ZIEL (DEINE VS-CODE-STRUKTUR)
# =====================================================
CLIENT_ROOT = BACKEND_ROOT / "clients" / "mtm_client"

TARGET_BASE = CLIENT_ROOT / "assets" / "approved" / "inbox"
TARGET_IMAGES = TARGET_BASE / "bilder"
TARGET_VIDEOS = TARGET_BASE / "videos"

# =====================================================
# 🔹 DATEITYPEN
# =====================================================
IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".heic"}
VIDEO_EXTS = {".mp4", ".mov"}

# =====================================================
# 🔹 ZIELORDNER SICHERSTELLEN
# =====================================================
TARGET_IMAGES.mkdir(parents=True, exist_ok=True)
TARGET_VIDEOS.mkdir(parents=True, exist_ok=True)

# =====================================================
# 🔹 HELPER: WARTET BIS DRIVE DATEI FERTIG IST
# =====================================================
def is_file_stable(path: Path, wait=1):
    size1 = path.stat().st_size
    time.sleep(wait)
    size2 = path.stat().st_size
    return size1 == size2 and size1 > 0

# =====================================================
# 🔹 SYNC-FUNKTION (DIE EINZIGE, DIE WIR NUTZEN)
# =====================================================
def sync_folder(src: Path, dst: Path, allowed_exts: set):
    if not src.exists():
        print(f"⚠️ Ordner fehlt: {src}")
        return

    for file in src.iterdir():
        if not file.is_file():
            continue

        if file.suffix.lower() not in allowed_exts:
            continue

        try:
            if not is_file_stable(file):
                print(f"⏳ noch im Drive-Sync: {file.name}")
                continue

            target = dst / file.name
            if target.exists():
                continue

            shutil.copy2(file, target)
            print(f"✅ übernommen: {file.name}")

        except Exception as e:
            print(f"❌ Fehler bei {file.name}: {e}")

# =====================================================
# 🔹 START
# =====================================================
print("🚀 Initial-Sync Bilder")
sync_folder(INBOX_IMAGES, TARGET_IMAGES, IMAGE_EXTS)

print("🚀 Initial-Sync Videos")
sync_folder(INBOX_VIDEOS, TARGET_VIDEOS, VIDEO_EXTS)

print("🎉 Initial-Sync abgeschlossen")