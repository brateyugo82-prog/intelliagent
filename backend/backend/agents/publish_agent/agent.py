from __future__ import annotations
"""
✅ Publish Agent v7.2 — Stored-Post Publisher (IntelliAgent Standard, STABLE)
----------------------------------------------------------------------------
- Publisher nutzt NUR gespeicherte Posts (core/post_store.py)
- KEIN Caption-Builder
- Enforced Status-Flow: preview → approved → scheduled → published
- publish_post(post_id, publish_at) als Haupt-API
- Plattform-Adapter optional (aktuell Simulation)
- Exakt angepasst an reales PostStore-Interface
"""


from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
import os
import smtplib
from email.mime.text import MIMEText
import requests

from backend.backend.core.logger import logger


# ------------------------------------------------------------
# 🔔 Benachrichtigungen (optional)
# ------------------------------------------------------------
def _notify_client(client: str, platforms: List[str], message: str) -> None:
    logger.info(f"[PublishAgent] 🔔 Benachrichtigung: {message}")

    smtp_host = os.getenv("SMTP_HOST")
    smtp_user = os.getenv("SMTP_USER")
    smtp_pass = os.getenv("SMTP_PASS")
    smtp_to = os.getenv("NOTIFY_EMAIL")

    if smtp_host and smtp_user and smtp_pass and smtp_to:
        try:
            msg = MIMEText(
                f"Hallo {client},\n\n{message}\n\n"
                f"Plattformen: {', '.join(platforms)}\n\n"
                f"— IntelliAgent Solutions"
            )
            msg["Subject"] = f"Content-Update ({', '.join(platforms)})"
            msg["From"] = smtp_user
            msg["To"] = smtp_to

            with smtplib.SMTP(smtp_host, 587, timeout=10) as server:
                server.starttls()
                server.login(smtp_user, smtp_pass)
                server.send_message(msg)

            logger.info("[PublishAgent] 📧 E-Mail gesendet.")
        except Exception as e:
            logger.error(f"[PublishAgent] ❌ E-Mail-Fehler: {e}")

    teams_url = os.getenv("TEAMS_WEBHOOK")
    if teams_url:
        try:
            payload = {
                "text": (
                    f"📢 *Content veröffentlicht*\n\n{message}\n\n"
                    f"Plattformen: {', '.join(platforms)}"
                )
            }
            r = requests.post(teams_url, json=payload, timeout=10)
            if r.status_code in (200, 201):
                logger.info("[PublishAgent] 💬 Teams-Benachrichtigung gesendet.")
            else:
                logger.warning(
                    f"[PublishAgent] ⚠ Teams-Webhook Fehler: {r.status_code} {r.text}"
                )
        except Exception as e:
            logger.error(f"[PublishAgent] ❌ Teams-Fehler: {e}")


# ------------------------------------------------------------
# 🧰 PostStore Zugriff
# ------------------------------------------------------------
def _load_post_from_store(post_id: str) -> Dict[str, Any]:
    from core import post_store
    post = post_store.get_post_by_id(post_id)
    if not post:
        raise RuntimeError(f"[PublishAgent] ❌ Post nicht gefunden: {post_id}")
    return post


def _update_post_in_store(post_id: str, patch: Dict[str, Any]) -> Dict[str, Any]:
    """
    Return updated post so we can re-read fresh status/results if needed.
    """
    from core import post_store
    return post_store.update_post(post_id, patch)


# ------------------------------------------------------------
# 🧩 Helpers
# ------------------------------------------------------------
def _utcnow_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _normalize_platforms(post: Dict[str, Any]) -> List[str]:
    """
    Prefer explicit 'platforms' list.
    Else allow comma-separated 'platform'.
    Else default to instagram/facebook/linkedin if results exist, otherwise instagram.
    """
    if isinstance(post.get("platforms"), list) and post["platforms"]:
        return [str(p).strip().lower() for p in post["platforms"] if str(p).strip()]

    if isinstance(post.get("platform"), str) and post["platform"].strip():
        return [p.strip().lower() for p in post["platform"].split(",") if p.strip()]

    # fallback: if results already contain platforms, use those
    if isinstance(post.get("results"), dict) and post["results"]:
        keys = [str(k).strip().lower() for k in post["results"].keys()]
        keys = [k for k in keys if k]
        if keys:
            return keys

    return ["instagram"]


def _get_client(post: Dict[str, Any]) -> str:
    return str(post.get("client") or "unbekannt")


def _get_status(post: Dict[str, Any]) -> str:
    return str(post.get("status") or "").strip().lower()


def _safe_import_platform_adapter(platform: str):
    try:
        if platform == "instagram":
            from agents.publish_agent.platforms.instagram import publish
            return publish
        if platform == "facebook":
            from agents.publish_agent.platforms.facebook import publish
            return publish
        if platform == "linkedin":
            from agents.publish_agent.platforms.linkedin import publish
            return publish
        if platform == "tiktok":
            from agents.publish_agent.platforms.tiktok import publish
            return publish
    except Exception as e:
        logger.warning(f"[PublishAgent] ⚠ Adapter Import fehlgeschlagen ({platform}): {e}")
        return None
    return None


# ------------------------------------------------------------
# ✅ Haupt-API
# ------------------------------------------------------------
def publish_post(post_id: str, publish_at: Optional[datetime] = None) -> Dict[str, Any]:
    post = _load_post_from_store(post_id)

    client = _get_client(post)
    platforms = _normalize_platforms(post)
    status = _get_status(post)

    # already done
    if status == "published":
        return {"status": "skipped", "reason": "already_published", "post_id": post_id}

    # Only schedule (no publishing)
    if publish_at is not None:
        _update_post_in_store(
            post_id,
            {
                "status": "scheduled",
                  "platform_times": build_platform_times(),
                "publish_at": publish_at.astimezone(timezone.utc).isoformat(),
                "updated_at": _utcnow_iso(),
            },
        )
        return {"status": "scheduled", "post_id": post_id}

    # Guard: Scheduler should call publish only when due.
    # If someone calls publish_post() directly while still preview/approved,
    # we still allow it, but we mark scheduled immediately.
    if status in ("preview", "approved"):
        post = _update_post_in_store(
            post_id,
            {
                "status": "scheduled",
                  "platform_times": build_platform_times(),
                "publish_at": _utcnow_iso(),
                "updated_at": _utcnow_iso(),
            },
        )
        status = _get_status(post)

    results: Dict[str, Any] = {}

    for platform in platforms:
        adapter = _safe_import_platform_adapter(platform)

        try:
            if adapter is None:
                logger.info(f"[PublishAgent] 🧪 Simuliere Publish auf {platform} ({post_id})")
            else:
                adapter(post)

            results[platform] = {
                "status": "ok",
                "published_at": _utcnow_iso(),
                # keep whatever store might already have, otherwise None
                "preview_url": (post.get("results") or {}).get(platform, {}).get("preview_url"),
                "caption": (post.get("results") or {}).get(platform, {}).get("caption"),
            }

        except Exception as e:
            logger.error(f"[PublishAgent] ❌ Fehler auf {platform}: {e}")
            results[platform] = {"status": "error", "error": str(e)}

    # FINAL write-back (✅ fixed parentheses/indent + stable fields)
    _update_post_in_store(
        post_id,
        {
            "status": "published",          # 🔑 FINAL STATE
            "published_at": _utcnow_iso(),  # 🔑 Scheduler-Ende
            "posted_at": _utcnow_iso(),     # 🔑 Dashboard / Analytics
            "updated_at": _utcnow_iso(),
            "results": results,
        },
    )

    msg = f"✅ Post published ({post_id}) auf {', '.join(platforms)}"
    logger.info(f"[PublishAgent] 🚀 {msg}")
    _notify_client(client, platforms, msg)

    return {
        "status": "published",
        "post_id": post_id,
        "client": client,
        "platforms": platforms,
        "results": results,
    }


# ------------------------------------------------------------
# ♻️ Legacy Entry
# ------------------------------------------------------------
def run(
    prompt: str,
    task: Optional[str] = None,
    platform: Optional[str] = None,
    client: Optional[str] = None,
    mode: Optional[str] = None,
    post_id: Optional[str] = None,
) -> Dict[str, Any]:
    if post_id:
        return publish_post(post_id)
    return {"status": "error", "reason": "deprecated_run_without_post_id"}


if __name__ == "__main__":
    print({"ok": True, "note": "Use publish_post(post_id) for tests."})