from pathlib import Path
from datetime import datetime, timezone
import json

BASE = Path(__file__).resolve().parents[1]
CLIENTS = BASE / "clients"
STORE = BASE / "runtime" / "posts.json"

def _collect_ids(dir: Path):
    if not dir.exists():
        return set()
    ids = set()
    for f in dir.iterdir():
        if f.is_file():
            parts = f.stem.split("_")
            if len(parts) >= 2:
                ids.add(f"{parts[0]}_{parts[1]}")
    return ids

def sync_client(client: str):
    cbase = CLIENTS / client / "output"

    preview = _collect_ids(cbase / "preview")
    approved = _collect_ids(cbase / "approved")
    queue = _collect_ids(cbase / "posting_queue")
    posted = _collect_ids(cbase / "posted")

    all_ids = preview | approved | queue | posted
    now = datetime.now(timezone.utc).isoformat()

    posts = []
    for pid in sorted(all_ids):
        if pid in posted:
            status = "posted"
        elif pid in queue:
            status = "scheduled"
        elif pid in approved:
            status = "approved"
        else:
            status = "preview"

        posts.append({
            "id": pid,
            "type": (
                "foundation" if pid.startswith("fp_")
                else "trust" if pid.startswith("tr_")
                else "service"
            ),
            "status": status,
            "updated_at": now,
        })

    STORE.parent.mkdir(exist_ok=True)
    STORE.write_text(json.dumps(posts, indent=2, ensure_ascii=False), encoding="utf-8")
    return posts
