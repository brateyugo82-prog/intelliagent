"""
✅ FINAL — Analytics Agent v2.4 (LEADS SAFE)
-------------------------------------------
- Aggregiert Leads IMMER
- Analysiert veröffentlichte Posts
- OpenAI optional
- Dashboard-kompatibel
"""

from typing import Dict, Any, List
from pathlib import Path
from datetime import datetime, timedelta, timezone
import json

from backend.backend.core.logger import logger
from backend.backend.core.config import get_openai_key
from core import post_store, memory
from backend.backend.core.leads_store import list_leads

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None


# ============================================================
# LEADS
# ============================================================

def build_lead_stats(client: str) -> dict:
    leads = list_leads(client)

    by_status: dict[str, int] = {}
    by_source: dict[str, int] = {}

    for l in leads:
        status = l.get("status", "unknown")
        source = l.get("source", "unknown")

        by_status[status] = by_status.get(status, 0) + 1
        by_source[source] = by_source.get(source, 0) + 1

    return {
        "total": len(leads),
        "by_status": by_status,
        "by_source": by_source,
    }


# ============================================================
# POSTS
# ============================================================

def get_published_posts(client: str, platform: str, period_days: int) -> List[dict]:
    since = datetime.now(timezone.utc) - timedelta(days=period_days)
    posts: List[dict] = []

    for p in post_store.get_posts(client):
        if p.get("status") != "published":
            continue

        published_at = p.get("published_at")
        if not published_at:
            continue

        try:
            dt = datetime.fromisoformat(published_at)
        except Exception:
            continue

        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        else:
            dt = dt.astimezone(timezone.utc)

        if dt < since:
            continue

        if platform != "multi":
            if platform not in (p.get("platforms") or []):
                continue

        posts.append(p)

    return posts


# ============================================================
# WRITE SUMMARY
# ============================================================

def write_summary(client: str, platform: str, period: str, data: dict):
    base = Path(__file__).resolve().parents[2]  # backend/
    state_dir = base / "clients" / client / "state"
    state_dir.mkdir(parents=True, exist_ok=True)

    out = {
        "client": client,
        "platform": platform,
        "period": period,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        **data,
    }

    path = state_dir / "analytics_summary.json"
    path.write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")

    logger.info(f"[AnalyticsAgent] analytics_summary.json geschrieben → {path}")


# ============================================================
# MAIN
# ============================================================

def run(
    client: str,
    platform: str = "multi",
    period: str = "30d",
    prompt: str | None = None,
    task: str | None = None,
) -> Dict[str, Any]:

    period_days = int(period.replace("d", ""))
    lead_stats = build_lead_stats(client)
    posts = get_published_posts(client, platform, period_days)

    # --------------------------------------------------------
    # FALLBACK: KEINE POSTS
    # --------------------------------------------------------
    if not posts:
        result = {
            "status": "ok",
            "posts_analyzed": 0,
            "top_content_types": [],
            "schwache_content_types": [],
            "beste_plattformen": [],
            "optimale_post_frequenz": "unbekannt",
            "konkrete_empfehlung_naechster_zyklus": "Noch keine veröffentlichen Posts.",
            "leads": lead_stats,
        }
        write_summary(client, platform, period, result)
        return result

    # --------------------------------------------------------
    # COMPACT POSTS
    # --------------------------------------------------------
    compact = [
        {
            "id": p.get("id"),
            "content_category": p.get("content_category"),
            "platforms": p.get("platforms"),
            "published_at": p.get("published_at"),
            "metrics": p.get("platform_results", {}),
        }
        for p in posts
    ]

    # --------------------------------------------------------
    # NO OPENAI → SAFE RESULT
    # --------------------------------------------------------
    openai_key = get_openai_key()
    if not openai_key or OpenAI is None:
        result = {
            "status": "ok",
            "posts_analyzed": len(posts),
            "top_content_types": [],
            "schwache_content_types": [],
            "beste_plattformen": [],
            "optimale_post_frequenz": "täglich",
            "konkrete_empfehlung_naechster_zyklus": "Mehr Daten sammeln.",
            "leads": lead_stats,
        }
        write_summary(client, platform, period, result)
        return result

    # --------------------------------------------------------
    # OPENAI PATH
    # --------------------------------------------------------
    try:
        oai = OpenAI(api_key=openai_key)

        analysis_prompt = f"""
Analysiere die Performance dieser Posts.

Antworte ausschließlich im JSON-Format.

POSTS:
{json.dumps(compact, indent=2, ensure_ascii=False)}
"""

        resp = oai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Antworte strikt im JSON-Format."},
                {"role": "user", "content": analysis_prompt},
            ],
            max_tokens=700,
        )

        parsed = json.loads(resp.choices[0].message.content)

        parsed["status"] = "ok"
        parsed["posts_analyzed"] = len(posts)
        parsed["leads"] = lead_stats

        write_summary(client, platform, period, parsed)

        memory.remember(
            client,
            f"analytics:{client}:{platform}:{period}",
            parsed,
        )

        return parsed

    except Exception as e:
        logger.error(f"[AnalyticsAgent] Fehler: {e}")

        result = {
            "status": "error",
            "error": str(e),
            "posts_analyzed": len(posts),
            "leads": lead_stats,
        }
        write_summary(client, platform, period, result)
        return result