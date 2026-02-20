from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from pathlib import Path
import json
import shutil
from datetime import datetime

from agents.publish_agent import run as publish_run
from core.posting_guard import posting_allowed
from core.client_config import load_client_config

router = APIRouter(prefix="/api/publisher", tags=["publisher"])

# -------------------------------------------------
# 📦 Models
# -------------------------------------------------
class PublishPayload(BaseModel):
    client: str
    platform: str | None = None   # "instagram,facebook"
    mode: str | None = None


# -------------------------------------------------
# 📂 Helpers (pfad-agnostisch)
# -------------------------------------------------
ALLOWED_EXTS = {".jpg", ".jpeg", ".png"}


def client_dirs(client: str):
    base = Path(__file__).resolve().parents[1] / "clients" / client
    output = base / "output"
    state = base / "state"

    preview = output / "preview"
    approved = output / "approved"
    posted = output / "posted"

    meta_file = state / "image_meta.json"

    for d in [preview, approved, posted, state]:
        d.mkdir(parents=True, exist_ok=True)

    return preview, approved, posted, meta_file


def load_meta(meta_file: Path) -> dict:
    if meta_file.exists():
        try:
            return json.loads(meta_file.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}


def save_meta(meta_file: Path, meta: dict):
    meta_file.write_text(
        json.dumps(meta, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def find_file(folder: Path, post_id: str) -> Path | None:
    for f in folder.glob(f"{post_id}.*"):
        if f.suffix.lower() in ALLOWED_EXTS:
            return f
    return None


# -------------------------------------------------
# 🌐 Queue (Publisher Tab)
# -------------------------------------------------
@router.get("/queue")
def queue(client: str):
    preview, approved, posted, meta_file = client_dirs(client)
    meta = load_meta(meta_file)

    def list_folder(folder: Path, status: str):
        items = []
        for f in folder.iterdir():
            if not f.is_file() or f.suffix.lower() not in ALLOWED_EXTS:
                continue

            entry = meta.get(f.name, {})
            items.append({
                "id": f.stem,
                "status": status,
                "category": entry.get("category", "uncategorized"),
                "caption": entry.get("caption", ""),
                "preview": f"/static/{client}/output/{status}/{f.name}",
            })
        return items

    return {
        "approved": list_folder(approved, "approved"),
        "posted": list_folder(posted, "posted"),
    }


# -------------------------------------------------
# 🚀 POST (Approved → Posted)
# -------------------------------------------------
@router.post("/post/{post_id}")
def post_now(post_id: str, payload: PublishPayload):
    client = payload.client
    platform = payload.platform or "instagram,facebook"
    mode = payload.mode

    cfg = load_client_config(client)

    allowed, reason = posting_allowed(cfg, platform)
    if not allowed:
        return {
            "status": "blocked",
            "reason": reason,
        }

    preview, approved, posted, meta_file = client_dirs(client)
    meta = load_meta(meta_file)

    src = find_file(approved, post_id)
    if not src:
        raise HTTPException(status_code=404, detail="Approved-Datei nicht gefunden")

    entry = meta.get(src.name, {})
    caption = entry.get("caption", "")
    category = entry.get("category", "uncategorized")

    # 1️⃣ Publish Agent
    result = publish_run(
        prompt=caption or f"Post ({category})",
        client=client,
        platform=platform,
        mode=mode,
    )

    # 2️⃣ Move File
    dst = posted / src.name
    shutil.move(str(src), str(dst))

    # 3️⃣ Meta Update
    meta.setdefault(src.name, {})
    meta[src.name]["last_posted_at"] = datetime.utcnow().isoformat()
    meta[src.name]["last_posted_platform"] = platform
    save_meta(meta_file, meta)

    return {
        "status": "ok",
        "id": post_id,
        "client": client,
        "platform": platform,
        "file": src.name,
        "publish_result": result,
    }
# =================================================
# MANUAL / CLI FINALIZE (LinkedIn etc.)
# =================================================

def publish_single_post(client: str, post_id: str, platform: str, manual: bool = False):
    """
    Finalisiert einen Post genau wie der Auto-Publisher:
    - verschiebt Dateien nach output/posted
    - setzt posted_at
    - setzt platform_status
    """

    from core.post_store import get_post_by_id, update_post
    from datetime import datetime
    from pathlib import Path
    import shutil

    base_dir = Path(__file__).resolve().parents[1]
    client_dir = base_dir / "clients" / client / "output"

    posting_queue = client_dir / "posting_queue"
    posted_dir = client_dir / "posted"

    posted_dir.mkdir(parents=True, exist_ok=True)

    post = get_post_by_id(post_id)
    if not post:
        raise RuntimeError(f"Post {post_id} nicht gefunden")

    # ---- Datei verschieben (wenn vorhanden) ----
    image_file = post.get("image_file")
    if image_file:
        src = posting_queue / image_file
        if src.exists():
            dst = posted_dir / image_file
            shutil.move(str(src), str(dst))

    # ---- Status setzen ----
    post.setdefault("platform_status", {})
    post["platform_status"][platform] = "posted"

    # Wenn alle Plattformen posted → Gesamtstatus
    if all(v == "posted" for v in post["platform_status"].values()):
        post["status"] = "posted"
        post["posted_at"] = datetime.utcnow().isoformat()

    update_post(post_id, post)

    return {
        "post_id": post_id,
        "platform": platform,
        "status": post["status"],
        "posted_at": post.get("posted_at"),
        "manual": manual,
    }
