from pathlib import Path
from core.post_store import get_posts, update_post

CLIENT = "mtm_client"

BASE_DIR = Path(__file__).resolve().parents[1]
OUT = BASE_DIR / "clients" / CLIENT / "output"

POSTED = OUT / "posted"
QUEUE = OUT / "posting_queue"

def base_post_id(pid: str) -> str:
    """
    fp_03_instagram -> fp_03
    fp_03 -> fp_03
    """
    if not pid:
        return ""
    return pid.split("_")[0] + "_" + pid.split("_")[1] if pid.startswith(("fp_", "tr_", "sv_")) else pid

def exists_any(base_id: str, folder: Path) -> bool:
    if not folder.exists():
        return False
    for f in folder.iterdir():
        if f.is_file() and f.name.startswith(base_id):
            return True
    return False

def reconcile():
    posts = get_posts(CLIENT)
    fixed = []

    for p in posts:
        pid = p.get("id")
        if not pid:
            continue

        base_id = base_post_id(pid)

        if exists_any(base_id, POSTED):
            new_status = "posted"
        elif exists_any(base_id, QUEUE):
            new_status = "scheduled"
        else:
            new_status = "preview"

        old_status = p.get("status")
        if old_status != new_status:
            update_post(pid, {"status": new_status})
            fixed.append((pid, old_status, new_status))

    print("✅ STATUS RECONCILE DONE")
    for pid, old, new in fixed:
        print(f" - {pid}: {old} → {new}")

if __name__ == "__main__":
    reconcile()
