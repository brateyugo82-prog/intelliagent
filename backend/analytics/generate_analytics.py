import json
from pathlib import Path
from datetime import datetime, timezone
from collections import Counter, defaultdict

from core.post_store import get_posts
from core.lead_store import list_leads

CLIENT = "mtm_client"

BASE_DIR = Path(__file__).resolve().parents[1]
OUT_PATH = (
    BASE_DIR
    / "static"
    / CLIENT
    / "state"
    / "analytics_summary.json"
)
OUT_PATH.parent.mkdir(parents=True, exist_ok=True)


def generate():
    posts = get_posts(CLIENT)
    leads = list_leads(client=CLIENT, limit=10_000)

    published_posts = [p for p in posts if p.get("status") == "published"]

    # ==============================
    # Aggregationen
    # ==============================

    leads_by_platform = Counter()
    leads_by_post = Counter()
    content_type_posts = Counter()
    content_type_leads = Counter()

    post_map = {p["id"]: p for p in published_posts}

    # Leads aggregieren
    for l in leads:
        if l.get("platform"):
            leads_by_platform[l["platform"]] += 1

        pid = l.get("post_id")
        if pid:
            leads_by_post[pid] += 1

            post = post_map.get(pid)
            if post:
                ct = post.get("content_category")
                if ct:
                    content_type_leads[ct] += 1

    # Content Types aus Posts
    for p in published_posts:
        ct = p.get("content_category")
        if ct:
            content_type_posts[ct] += 1

    # ==============================
    # Conversion pro Post
    # ==============================

    post_performance = []

    for pid, post in post_map.items():
        leads_count = leads_by_post.get(pid, 0)
        post_performance.append({
            "post_id": pid,
            "category": post.get("category"),
            "content_category": post.get("content_category"),
            "platforms": list((post.get("results") or {}).keys()),
            "leads": leads_count,
        })

    post_performance.sort(key=lambda x: x["leads"], reverse=True)

    # ==============================
    # Conversion pro Content-Type
    # ==============================

    content_type_performance = {}

    for ct, post_count in content_type_posts.items():
        lead_count = content_type_leads.get(ct, 0)
        content_type_performance[ct] = {
            "posts": post_count,
            "leads": lead_count,
            "conversion_rate": round(
                lead_count / post_count, 2
            ) if post_count else 0,
        }

    # ==============================
    # FINAL SUMMARY
    # ==============================

    summary = {
        "client": CLIENT,
        "generated_at": datetime.now(timezone.utc).isoformat(),

        "counts": {
            "published_posts": len(published_posts),
            "total_leads": len(leads),
        },

        "leads_by_platform": dict(leads_by_platform),

        "top_posts_by_leads": post_performance[:5],

        "content_type_performance": content_type_performance,

        "top_content_types": sorted(
            content_type_performance.keys(),
            key=lambda k: content_type_performance[k]["leads"],
            reverse=True
        )[:3],

        "beste_plattformen": [
            k for k, _ in leads_by_platform.most_common(3)
        ],
    }

    OUT_PATH.write_text(
        json.dumps(summary, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    print(f"✅ Analytics geschrieben → {OUT_PATH}")


if __name__ == "__main__":
    generate()