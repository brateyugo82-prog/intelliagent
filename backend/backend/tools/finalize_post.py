import sys
from core.post_store import get_post_by_id, update_post
from core.post_files import move_post_to_posted
from datetime import datetime

if len(sys.argv) != 3:
    print("Usage: python -m tools.finalize_post <post_id> <platform>")
    sys.exit(1)

post_id = sys.argv[1]
platform = sys.argv[2]

# �� HARDCODED für jetzt – später dynamisch
client = "mtm_client"

post = get_post_by_id(post_id)
post.setdefault("platform_status", {})
post["platform_status"][platform] = "posted"

# Wenn alle Plattformen posted → finalisieren
if all(v == "posted" for v in post["platform_status"].values()):
    post["status"] = "posted"
    post["posted_at"] = datetime.utcnow().isoformat()

    update_post(post_id, post)

    moved = move_post_to_posted(client, post_id)

    print("✅ FINALIZED:", {
        "post_id": post_id,
        "platform": platform,
        "status": post["status"],
        "posted_at": post["posted_at"],
        "files_moved": moved,
    })
else:
    update_post(post_id, post)
    print("ℹ️ Platform marked posted, waiting for others")
