from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from pathlib import Path
import shutil
from datetime import datetime, timezone

from core.post_store import (
    get_posts,
    update_post,
    get_post_by_id,
    ensure_post_exists,
)

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])

# =================================================
# CONFIG
# =================================================
CLIENT = "mtm_client"

BASE_DIR = Path(__file__).resolve().parents[1]  # backend/
CLIENTS_DIR = BASE_DIR / "clients"
CLIENT_DIR = CLIENTS_DIR / CLIENT
OUTPUT_DIR = CLIENT_DIR / "output"

PREVIEW_DIR = OUTPUT_DIR / "preview"
APPROVED_DIR = OUTPUT_DIR / "approved"
POSTING_QUEUE_DIR = OUTPUT_DIR / "posting_queue"  # ✅ FEHLTE
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
# MODELS
# =================================================
class UpdateMetaPayload(BaseModel):
    category: str | None = None
    caption: str | None = None
    platform: str | None = None  # instagram | facebook | linkedin


class SchedulePayload(BaseModel):
    publish_at: datetime
    platforms: list[str] | None = None  # default: all


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
    """
    Foundation + weekly posts use base IDs (fp_01, tr_02, uuid).
    Only strip known suffixes.
    """
    if not isinstance(post_id, str):
        return ""
    if post_id.endswith("_facebook"):
        return post_id[:-9]
    if post_id.endswith("_linkedin"):
        return post_id[:-9]
    return post_id


def _static_to_fs(url: str) -> Path:
n
def _fs_exists_from_static(url: str) -> bool:n
    try:n
        return _static_to_fs(url).exists()n
    except Exception:n
        return Falsen
    """
    /static/<client>/... -> backend/clients/<client>/...
    """
    if not isinstance(url, str) or not url.startswith("/static/"):
        raise HTTPException(400, f"Invalid static url: {url}")
    rel = url.replace("/static/", "", 1)
    return CLIENTS_DIR / rel



def _pick_existing_preview(post: dict) -> str | None:
    """
    Liefert IMMER ein valides Preview-Asset zurück, egal ob
    preview / approved / scheduled / posted.
    """

    # 1️⃣ explizit gesetztes preview prüfen
    prev = post.get("preview")
    if isinstance(prev, str) and prev.startswith("/static/") and _fs_exists_from_static(prev):
        return prev

    # 2️⃣ platform previews prüfen (instagram/facebook/linkedin)
    results = post.get("results") or {}
    for r in results.values():
        url = (r or {}).get("preview_url")
        if isinstance(url, str) and url.startswith("/static/") and _fs_exists_from_static(url):
            return url

    # 3️⃣ fallback: anhand Status aus Ordnern suchen
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
                return f"/static/{CLIENT}/output/{folder}/{base_id}{ext}"

    # 4️⃣ letzter Fallback: irgendwas zurückgeben, damit UI nicht stirbt
    if isinstance(prev, str) and prev.startswith("/static/"):
        return prev

    for r in results.values():
        url = (r or {}).get("preview_url")
        if isinstance(url, str) and url.startswith("/static/"):
            return url

    return None


def _best_caption(post: dict) -> str:
    c = post.get("caption")
    if isinstance(c, str) and c.strip():
        return c.strip()

    ig = (post.get("results") or {}).get("instagram") or {}
    igc = ig.get("caption")
    return igc.strip() if isinstance(igc, str) else ""


def _move_variants(base_id: str, src_dir: Path, dst_dir: Path) -> bool:
    """
    Verschiebt alle Varianten:
    - base.png/jpg/...
    - base_facebook.png/jpg/...
    - base_linkedin.png/jpg/...
    """
    moved = False
    dst_dir.mkdir(parents=True, exist_ok=True)

    for ext in ALLOWED_EXTS:
        for suffix in PLATFORM_SUFFIXES:
            src = src_dir / f"{base_id}{suffix}{ext}"
                shutil.move(str(src), str(dst_dir / src.name))
                moved = True

    return moved


def _any_variants_exist(base_id: str, folder: Path) -> bool:
    for ext in ALLOWED_EXTS:
        for suffix in PLATFORM_SUFFIXES:
                return True
    return False


def _copy_source_to_folder(post: dict, base_id: str, dst_dir: Path) -> str:
    """
    Fallback for foundation posts:
    Copy source_image_path file to dst_dir/base_id.<ext>
    Returns the file name created.
    """
    source_url = post.get("source_image_path") or post.get("preview")
    if not isinstance(source_url, str) or not source_url.startswith("/static/"):
        raise HTTPException(400, "No valid source_image_path for fallback copy")

    src_fs = _static_to_fs(source_url)
        raise HTTPException(404, f"Source image missing: {src_fs}")

    dst_dir.mkdir(parents=True, exist_ok=True)
    ext = src_fs.suffix.lower()
    if ext not in ALLOWED_EXTS:
        ext = ".png"

    out_name = f"{base_id}{ext}"
    dst_fs = dst_dir / out_name

    shutil.copy2(str(src_fs), str(dst_fs))
    return out_name


def _update_preview_urls_for_status(base_id: str, post: dict, status: str):
    """
    Updates preview + results.*.preview_url
    based on status folder:
    preview | approved | scheduled | posted
    """
    folder_map = {
        "preview": "preview",
        "approved": "approved",
        "scheduled": "posting_queue",
        "posted": "posted",
    }

    folder = folder_map.get(status)
    if not folder:
        return

    new_url = None

    for ext in ALLOWED_EXTS:
        path = CLIENT_DIR / "output" / folder / f"{base_id}{ext}"
            new_url = f"/static/{CLIENT}/output/{folder}/{base_id}{ext}"
            break

    if not new_url:
        return  # kein Asset gefunden → nichts anfassen

    results = post.get("results") or {}

    for pf in ("instagram", "facebook", "linkedin"):
        if pf in results and isinstance(results[pf], dict):
            results[pf]["preview_url"] = new_url

    update_post(
        base_id,
        {
            "preview": new_url,
            "results": results,
            "updated_at": _utcnow_iso(),
        },
    )


# =================================================
# READ DASHBOARD
# =================================================
@router.get("/mtm/posts")
def get_dashboard_posts():
    posts = get_posts(CLIENT)

    preview, approved, scheduled, posted = [], [], [], []

    for p in sorted(posts, key=lambda x: x.get("created_at", ""), reverse=True):
        base_id = _base_post_id(p.get("id", ""))
        if base_id:
            try:
                ensure_post_exists(base_id, client=CLIENT)
            except Exception:
                pass


        # --- normalize status ---
        # --- filesystem is source of truth ---
            status = "posted"

        item = {
            "id": p.get("id"),
            "preview": _pick_existing_preview(p) or (p.get("preview") or ""),
            "caption": _best_caption(p),
            "category": _safe_category(p.get("category")),
            "status": status,
            "content_category": p.get("content_category"),
            "results": p.get("results") or {},
            "publish_at": p.get("publish_at"),
            "posted_at": p.get("posted_at"),
            "platform_times": p.get("platform_times"),
            "platform_times": p.get("platform_times"),
            "platform_status": p.get("platform_status"),
            "platform_times": p.get("platform_times"),
            "created_at": p.get("created_at"),
            "updated_at": p.get("updated_at"),
        }

        if status == "approved":
            approved.append(item)
        elif status == "scheduled":
        elif status == "posted":
            posted.append(item)
            scheduled.append(item)
            posted.append(item)
        else:
            preview.append(item)
    return {
        "preview": preview,
        "approved": approved,
        "scheduled": scheduled,
        "posted": posted,
    }


# =================================================
# UPDATE META
# =================================================
@router.post("/update-meta/{post_id}")
def update_meta(post_id: str, payload: UpdateMetaPayload):
    base_id = _base_post_id(post_id)
    post = get_post_by_id(base_id)
    if not post:
        raise HTTPException(404, "Post not found")

    patch = {"updated_at": _utcnow_iso()}
    results = post.get("results") or {}

    # platform caption update
    if payload.platform and payload.caption is not None:
        if payload.platform not in results:
            raise HTTPException(400, "Unknown platform")

        results[payload.platform]["caption"] = payload.caption
        patch["results"] = results

        if payload.platform == "instagram":
            patch["caption"] = payload.caption

        update_post(base_id, patch)
        return {"status": "ok"}

    # global updates
    if payload.caption is not None:
        patch["caption"] = payload.caption

    if payload.category is not None:
        patch["category"] = _safe_category(payload.category)

    update_post(base_id, patch)
    return {"status": "ok"}


# =================================================
# APPROVE / SCHEDULE / POST / REVERT
# =================================================
@router.post("/approve/{post_id}")
def approve_post(post_id: str):
    """
    preview -> approved
    - Weekly posts: move preview variants preview/ -> approved/
    - Foundation posts: if no preview variants exist, copy from source_image_path/assets
    """
    base_id = _base_post_id(post_id)
    post = get_post_by_id(base_id)
    if not post:
        raise HTTPException(404, "Post not found")

    moved = _move_variants(base_id, PREVIEW_DIR, APPROVED_DIR)

    if not moved:
        pass
        # Fallback for foundation assets (or any post whose previews are not files)

    update_post(
        base_id,
        {
            "status": "approved",
            "updated_at": _utcnow_iso(),
        },
    )

    return {"status": "approved", "post_id": base_id}


@router.post("/schedule/{post_id}")
def schedule_post(post_id: str, payload: SchedulePayload):
    base_id = _base_post_id(post_id)

    if _any_variants_exist(base_id, APPROVED_DIR):
        _move_variants(base_id, APPROVED_DIR, POSTING_QUEUE_DIR)
    elif _any_variants_exist(base_id, PREVIEW_DIR):
        _move_variants(base_id, PREVIEW_DIR, POSTING_QUEUE_DIR)
    else:
        raise HTTPException(400, "No files to schedule")

    update_post(
        base_id,
        {
            "status": "scheduled",
            "publish_at": payload.publish_at.isoformat(),
            "updated_at": _utcnow_iso(),
        },
    )

    # 🔥 DAS IST DER ENTSCHEIDENDE SCHRITT
    _update_preview_urls_for_status(base_id, "scheduled")

    return {
        "status": "scheduled",
        "post_id": base_id,
        "publish_at": payload.publish_at,
    }


@router.post("/post/{post_id}")
def post_post(post_id: str):
    """
    approved/scheduled -> posted
    - move approved -> posted
    - fallback: copy from source -> posted
    """
    base_id = _base_post_id(post_id)
    post = get_post_by_id(base_id)
    if not post:
        raise HTTPException(404, "Post not found")

    moved = False

    if _any_variants_exist(base_id, APPROVED_DIR):
    elif _any_variants_exist(base_id, PREVIEW_DIR):

    if not moved:
        pass

    update_post(
        base_id,
        {
            "status": "posted",
            "posted_at": _utcnow_iso(),
            "updated_at": _utcnow_iso(),
        },
    )

    return {"status": "posted", "post_id": base_id}


@router.post("/revert/{post_id}")
def revert_post(post_id: str):
    """
    approved | scheduled | posted -> preview
    (Moves files back if they exist; does not delete assets.)
    """
    base_id = _base_post_id(post_id)
    post = get_post_by_id(base_id)
    if not post:
        raise HTTPException(404, "Post not found")

    if _any_variants_exist(base_id, APPROVED_DIR):
        _move_variants(base_id, APPROVED_DIR, PREVIEW_DIR)

    update_post(
        base_id,
        {
            "status": "preview",
            "publish_at": None,
            "updated_at": _utcnow_iso(),
        },
    )

    return {"status": "reverted_to_preview", "post_id": base_id}
# ============================================================
# 📊 ANALYTICS (Dashboard)
# ============================================================

# ============================================================
# 📊 DASHBOARD ANALYTICS (STABLE, FILE-BASED)
# ============================================================

@router.get("/{client}/analytics")
def get_dashboard_analytics(client: str):
    """
    Liest Analytics ausschließlich aus:
    clients/{client}/state/analytics_summary.json
    """

    from pathlib import Path
    import json
    from fastapi import HTTPException

    base = Path(__file__).resolve().parents[1]  # backend/
    summary_path = base / "clients" / client / "state" / "analytics_summary.json"

        return {
            "status": "empty",
            "client": client,
            "analytics": None,
            "leads": {
                "total": 0,
                "by_status": {},
                "by_source": {},
            },
        }

    try:
        summary = json.loads(summary_path.read_text(encoding="utf-8"))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"analytics_summary.json invalid: {e}",
        )

    return {
        "status": "ok",
        "client": client,
        "analytics": {k: v for k, v in summary.items() if k != "leads"},
        "leads": summary.get(
            "leads",
            {
                "total": 0,
                "by_status": {},
                "by_source": {},
            },
        ),
    }

