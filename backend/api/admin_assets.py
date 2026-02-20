from fastapi import APIRouter
from pathlib import Path
import shutil
import subprocess

router = APIRouter(prefix="/api/admin", tags=["admin"])

BASE_DIR = Path(__file__).resolve().parents[1]  # backend/
CLIENT = "mtm_client"

CLIENT_DIR = BASE_DIR / "clients" / CLIENT
PREVIEW_DIR = CLIENT_DIR / "output" / "preview"

SCRIPT = BASE_DIR / "scripts" / "sync_assets_to_preview.py"


@router.post("/resync-preview")
def resync_preview():
    # 1. Preview leeren
    if PREVIEW_DIR.exists():
        for f in PREVIEW_DIR.iterdir():
            if f.is_file():
                f.unlink()

    # 2. Sync-Script ausführen
    subprocess.run(
        ["python", str(SCRIPT)],
        cwd=str(BASE_DIR),
        check=True
    )

    return {"status": "ok", "message": "Preview neu aufgebaut"}