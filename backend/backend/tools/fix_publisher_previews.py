from pathlib import Path
from core.post_store import get_posts, update_post

CLIENT = "mtm_client"
BASE = Path(__file__).resolve().parents[1]
OUT = BASE / "clients" / CLIENT / "output" / "posting_queue"

PLATFORMS = {
    "instagram": "",
    "facebook": "_facebook",
    "linkedin": "_linkedin",
}

EXTS = [".png", ".jpg", ".jpeg", ".webp"]

def run():
    posts = get_posts(CLIENT)
    fixed = 0

    for p in posts:
        if p.get("status") != "scheduled":
            continue

        pid = p["id"]
        results = {}

        for platform, suffix in PLATFORMS.items():
            for ext in EXTS:
                f = OUT / f"{pid}{suffix}{ext}"
                if f.exists():
                    results[platform] = {
                        "preview_url": f"/static/{CLIENT}/output/posting_queue/{f.name}"
                    }
                    break

        if results:
            update_post(pid, {
                "results": results
            })
            fixed += 1

    print("✅ PUBLISHER PREVIEWS FIXED")
    print("→ scheduled posts updated:", fixed)

if __name__ == "__main__":
    run()
