from fastapi import HTTPException
from pathlib import Path
import shutil
from datetime import datetime, timezone

# =================================================
# CONFIG
# =================================================
CLIENT = "mtm_client"

BASE_DIR = Path(__file__).resolve().parents[1]
CLIENTS_DIR = BASE_DIR / "clients"
CLIENT_DIR = CLIENTS_DIR / CLIENT
OUTPUT_DIR = CLIENT_DIR / "output"

PREVIEW_DIR = OUTPUT_DIR / "preview"
APPROVED_DIR = OUTPUT_DIR / "approved"
POSTING_QUEUE_DIR = OUTPUT_DIR / "posting_queue"

for d in (PREVIEW_DIR, APPROVED_DIR, POSTING_QUEUE_DIR):
    d.mkdir(parents=True, exist_ok=True)

VALID_IMAGE_CATEGORIES = {
    "finished_work",
    "work_action",
    "process_detail",
    "team_vehicle",
    "empty_space",
}

ALLOWED_EXTS = {".jpg", ".jpeg", ".png", ".webp"}
PLATFORM_SUFFIXES = ("", "_facebook", "_linkedin")

# =================================================
# HELPERS
# =================================================
def _utcnow_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

def _safe_category(cat: str | None) -> str:
    if not isinstance(cat, str):
        return "finished_work"
    c = cat.strip().lower()
    return c if c in VALID_IMAGE_CATEGORIES else "finished_work"

def _base_post_id(post_id: str) -> str:
    if not isinstance(post_id, str):
        return ""
    if post_id.endswith("_facebook"):
        return post_id[:-9]
    if post_id.endswith("_linkedin"):
        return post_id[:-9]
    return post_id

def _static_to_fs(url: str) -> Path:
    if not isinstance(url, str) or not url.startswith("/static/"):
        raise HTTPException(400, f"Invalid static url: {url}")
    rel = url.replace("/static/", "", 1)
    return CLIENTS_DIR / rel

def _fs_exists_from_static(url: str) -> bool:
    try:
        return _static_to_fs(url).exists()
    except Exception:
        return False

def _pick_existing_preview(post: dict) -> str | None:
    prev = post.get("preview")
    if isinstance(prev, str) and prev.startswith("/static/") and _fs_exists_from_static(prev):
        return prev

    results = post.get("results") or {}
    for r in results.values():
        url = (r or {}).get("preview_url")
        if isinstance(url, str) and url.startswith("/static/") and _fs_exists_from_static(url):
            return url

    status = (post.get("status") or "preview").lower()
    folder_map = {
        "preview": "preview",
        "approved": "approved",
        "scheduled": "posting_queue",
        "posted": "posted",
    }

    folder = folder_map.get(status)
    if folder:
        base_id = _base_post_id(post.get("id", ""))
        for ext in ALLOWED_EXTS:
            path = CLIENT_DIR / "output" / folder / f"{base_id}{ext}"
            if path.exists():
                return f"/static/{CLIENT}/output/{folder}/{base_id}{ext}"

    return prev if isinstance(prev, str) else None

def _best_caption(post: dict) -> str:
    c = post.get("caption")
    if isinstance(c, str) and c.strip():
        return c.strip()
    ig = (post.get("results") or {}).get("instagram") or {}
    return ig.get("caption", "") or ""

def _move_variants(base_id: str, src_dir: Path, dst_dir: Path) -> bool:
    moved = False
    dst_dir.mkdir(parents=True, exist_ok=True)
    for ext in ALLOWED_EXTS:
        for suffix in PLATFORM_SUFFIXES:
            src = src_dir / f"{base_id}{suffix}{ext}"
            if src.exists():
                shutil.move(str(src), str(dst_dir / src.name))
                moved = True
    return moved

def _any_variants_exist(base_id: str, folder: Path) -> bool:
    for ext in ALLOWED_EXTS:
        for suffix in PLATFORM_SUFFIXES:
            if (folder / f"{base_id}{suffix}{ext}").exists():
                return True
    return False

def _update_preview_urls_for_status(base_id: str, post: dict, status: str):
    folder_map = {
        "preview": "preview",
        "approved": "approved",
        "scheduled": "posting_queue",
        "posted": "posted",
    }
    folder = folder_map.get(status)
    if not folder:
        return

    for ext in ALLOWED_EXTS:
        path = CLIENT_DIR / "output" / folder / f"{base_id}{ext}"
        if path.exists():
            url = f"/static/{CLIENT}/output/{folder}/{base_id}{ext}"
            results = post.get("results") or {}
            for pf in results:
                results[pf]["preview_url"] = url
            return
