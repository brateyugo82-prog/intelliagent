from pathlib import Path
from datetime import datetime, timezone
import shutil

# =================================================
# GLOBAL
# =================================================
CLIENT = "mtm_client"

BASE_DIR = Path(__file__).resolve().parents[2]
CLIENT_DIR = BASE_DIR / "clients" / CLIENT
OUTPUT_DIR = CLIENT_DIR / "output"

PREVIEW_DIR = OUTPUT_DIR / "preview"
APPROVED_DIR = OUTPUT_DIR / "approved"
POSTING_QUEUE_DIR = OUTPUT_DIR / "posting_queue"
POSTED_DIR = OUTPUT_DIR / "posted"

for d in (PREVIEW_DIR, APPROVED_DIR, POSTING_QUEUE_DIR, POSTED_DIR):
    d.mkdir(parents=True, exist_ok=True)

ALLOWED_EXTS = {".png", ".jpg", ".jpeg", ".webp"}
PLATFORM_SUFFIXES = ("", "_facebook", "_linkedin")

# =================================================
# HELPERS
# =================================================
def utcnow_iso():
    return datetime.now(timezone.utc).isoformat()

def base_post_id(post_id: str) -> str:
    if post_id.endswith("_facebook"):
        return post_id[:-9]
    if post_id.endswith("_linkedin"):
        return post_id[:-9]
    return post_id

def any_variants_exist(base_id: str, folder: Path) -> bool:
    for ext in ALLOWED_EXTS:
        for suf in PLATFORM_SUFFIXES:
            if (folder / f"{base_id}{suf}{ext}").exists():
                return True
    return False

def move_variants(base_id: str, src: Path, dst: Path) -> bool:
    moved = False
    for ext in ALLOWED_EXTS:
        for suf in PLATFORM_SUFFIXES:
            f = src / f"{base_id}{suf}{ext}"
            if f.exists():
                shutil.move(str(f), str(dst / f.name))
                moved = True
    return moved
