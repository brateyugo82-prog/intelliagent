import sys
from backend.backend.core.post_store import get_post_by_id, update_post, finalize_post_if_done

post_id = sys.argv[1]
platform = sys.argv[2]

post = get_post_by_id(post_id)
post.setdefault("platform_status", {})
post["platform_status"][platform] = "posted"

update_post(post_id, post)
finalize_post_if_done(post_id)

print(f"✅ {post_id} auf {platform} als gepostet markiert")
