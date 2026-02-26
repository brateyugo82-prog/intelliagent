from pathlib import Path
import shutil

def move_post_to_posted(client: str, post_id: str):
    from core.paths import posting_queue_dir
    base = posting_queue_dir(client).parent
    src_dirs = ["posting_queue", "scheduled", "approved"]
    dst_dir = base / "posted"
    dst_dir.mkdir(parents=True, exist_ok=True)

    moved = False

    for d in src_dirs:
        src = base / d
        if not src.exists():
            continue

        for f in src.glob(f"{post_id}*"):
            shutil.move(str(f), dst_dir / f.name)
            moved = True

    return moved
