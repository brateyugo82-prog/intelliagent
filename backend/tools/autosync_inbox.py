import shutil
import time
from pathlib import Path

# ----------------------------
# GOOGLE DRIVE (lokaler Spiegel)
# ----------------------------
GOOGLE_DRIVE = (
    Path.home()
    / "Library"
    / "CloudStorage"
    / "GoogleDrive-brateyugo82@gmail.com"
    / "Meine Ablage"
    / "MTM_Social_Media"
    / "Inbox"
)

INBOX_IMAGES = GOOGLE_DRIVE / "bilder"
INBOX_VIDEOS = GOOGLE_DRIVE / "videos"

# ----------------------------
# BACKEND ZIEL (DEINE echte Struktur)
# ----------------------------
PROJECT_ROOT = Path.home() / "IntelliAgent"
CLIENT_ROOT = PROJECT_ROOT / "backend" / "clients" / "mtm_client"

TARGET_IMAGES = CLIENT_ROOT / "assets" / "approved" / "inbox" / "bilder"
TARGET_VIDEOS = CLIENT_ROOT / "assets" / "approved" / "inbox" / "videos"

IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".heic"}
VIDEO_EXTS = {".mp4", ".mov", ".mkv"}

SCAN_INTERVAL = 5

TARGET_IMAGES.mkdir(parents=True, exist_ok=True)
TARGET_VIDEOS.mkdir(parents=True, exist_ok=True)

def sync_folder(src: Path, dst: Path, allowed_exts: set):
    if not src.exists():
        print(f"⚠️ Quelle fehlt: {src}")
        return

    for file in src.iterdir():
        if not file.is_file():
            continue
        if file.suffix.lower() not in allowed_exts:
            continue

        target = dst / file.name
        if target.exists():
            continue

        shutil.copy2(file, target)
        print(f"✅ übernommen → {dst.name}: {file.name}")

print("🔁 AutoSync läuft … CTRL+C zum Beenden")

while True:
    sync_folder(INBOX_IMAGES, TARGET_IMAGES, IMAGE_EXTS)
    sync_folder(INBOX_VIDEOS, TARGET_VIDEOS, VIDEO_EXTS)
    time.sleep(SCAN_INTERVAL)