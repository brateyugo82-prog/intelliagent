from backend.backend.core.post_store import get_posts, update_post

CLIENT = "mtm_client"

posts = get_posts(CLIENT)
fixed = 0

for p in posts:
    if p.get("status") != "scheduled":
        continue

    if p.get("results"):
        continue

    preview = p.get("preview")
    if not preview:
        continue

    results = {
        "instagram": {"preview_url": preview, "caption": p.get("caption", "")},
        "facebook": {"preview_url": preview, "caption": p.get("caption", "")},
        "linkedin": {"preview_url": preview, "caption": p.get("caption", "")},
    }

    update_post(p["id"], {"results": results})
    fixed += 1

print("✅ results rebuilt:", fixed)
