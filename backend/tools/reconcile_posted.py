from pathlib import Path
from core.post_store import get_posts
import shutil

CLIENT = "mtm_client"

BASE_DIR = Path(__file__).resolve().parents[1]  # backend/
CLIENT_DIR = BASE_DIR / "clients" / CLIENT / "output"

POSTING_QUEUE = CLIENT_DIR / "posting_queue"
POSTED_DIR = CLIENT_DIR / "posted"

POSTED_DIR.mkdir(exist_ok=True)

def reconcile():
    posts = get_posts(CLIENT)
    moved = []
    skipped = []

    for p in posts:
        if p.get("status") != "posted":
            continue

        post_id = p.get("id")
        if not post_id:
            continue

        for ext in [".png", ".jpg", ".jpeg", ".webp"]:
            fname = f"{post_id}{ext}"
            src = POSTING_QUEUE / fname
            dst = POSTED_DIR / fname

            if src.exists():
                shutil.move(str(src), str(dst))
                moved.append(fname)
                break
        else:
            skipped.append(post_id)

    print("✅ RECONCILE DONE")
    print(f"→ moved:   {len(moved)}")
    print(f"→ skipped (no file found): {len(skipped)}")

    if skipped:
        print("⚠️ Skipped IDs:")
        for s in skipped:
            print(" -", s)

if __name__ == "__main__":
    reconcile()
