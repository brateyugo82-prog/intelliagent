from pathlib import Path
from core.post_store import update_post
from core.time_utils import utcnow_iso
from core.filesystem import ALLOWED_EXTS

def update_preview_urls_for_status(
    client: str,
    client_dir: Path,
    base_id: str,
    post: dict,
    status: str,
):
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
        p = client_dir / "output" / folder / f"{base_id}{ext}"
        if p.exists():
            new_url = f"/static/{client}/output/{folder}/{base_id}{ext}"
            break

    if not new_url:
        return

    results = post.get("results") or {}
    for pf in results:
        results[pf]["preview_url"] = new_url

    update_post(
        base_id,
        {
            "preview": new_url,
            "results": results,
            "updated_at": utcnow_iso(),
        },
    )
