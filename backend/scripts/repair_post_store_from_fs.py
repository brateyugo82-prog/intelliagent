import sys
from pathlib import Path
from datetime import datetime
from collections import defaultdict

# =================================================
# 🔧 PYTHONPATH FIX (DAMIT core/ GEFUNDEN WIRD)
# =================================================
BASE_DIR = Path(__file__).resolve().parents[1]  # backend/
sys.path.insert(0, str(BASE_DIR))

from core.post_store import ensure_post_exists, update_post

# =================================================
# CONFIG
# =================================================
CLIENT = "mtm_client"

CLIENT_DIR = BASE_DIR / "clients" / CLIENT / "output"

PREVIEW_DIR = CLIENT_DIR / "preview"
APPROVED_DIR = CLIENT_DIR / "approved"
POSTED_DIR = CLIENT_DIR / "posted"

ALLOWED_EXTS = {".jpg", ".jpeg", ".png", ".webp"}
PLATFORM_SUFFIXES = ("", "_facebook", "_linkedin")


# =================================================
# HELPERS
# =================================================
def base_id_from_filename(name: str) -> str:
    for suf in PLATFORM_SUFFIXES:
        if name.endswith(suf):
            return name[: -len(suf)]
    return name


def collect_posts():
    mapping = defaultdict(set)

    for folder, status in [
        (PREVIEW_DIR, "preview"),
        (APPROVED_DIR, "approved"),
        (POSTED_DIR, "posted"),
    ]:
        if not folder.exists():
            continue

        for f in folder.iterdir():
            if f.suffix.lower() not in ALLOWED_EXTS:
                continue

            base_id = f.stem.split("_", 1)[0]
            mapping[base_id].add(status)

    return mapping


def resolve_status(statuses: set[str]) -> str:
    if "posted" in statuses:
        return "posted"
    if "approved" in statuses:
        return "approved"
    return "preview"


# =================================================
# MAIN
# =================================================
def main():
    posts = collect_posts()

    print(f"🔧 Repairing {len(posts)} posts from filesystem…")

    for post_id, statuses in posts.items():
        final_status = resolve_status(statuses)

        ensure_post_exists(post_id, client=CLIENT)

        patch = {"status": final_status}

        if final_status == "posted":
            patch["posted_at"] = datetime.utcnow().isoformat()

        update_post(post_id, patch)

        print(f"✔ {post_id} → {final_status}")

    print("✅ Repair finished. Dashboard is sane again.")


if __name__ == "__main__":
    main()