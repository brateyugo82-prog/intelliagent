import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
CLIENTS_DIR = BASE_DIR / "clients"

def _inject_foundation_caption(post, client):
    if post.get("type") != "foundation":
        return

    post_id = post.get("id")
    if not post_id:
        return

    posts_path = CLIENTS_DIR / client / "posts" / "foundation_posts.json"
    if not posts_path.exists():
        return

    try:
        data = json.loads(posts_path.read_text(encoding="utf-8"))
    except Exception:
        return

    entry = data.get(post_id)
    if not isinstance(entry, dict):
        return

    post.setdefault("results", {})
    for platform, text in entry.items():
        if not text:
            continue
        post["results"].setdefault(platform, {})
        # 🔥 NUR überschreiben wenn leer
        if not post["results"][platform].get("caption"):
            post["results"][platform]["caption"] = text.strip()

from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

# ============================================================
# 🔒 STORE PATH
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[2]  # IntelliAgent/backend
STORE_PATH = BASE_DIR / "backend" / "runtime" / "posts.json"
STORE_PATH.parent.mkdir(parents=True, exist_ok=True)

# Deine Ordner-Namen sind ohne underscore → wir normalisieren auf snake_case
VALID_IMAGE_CATEGORIES = {
    "finished_work",
    "work_action",
    "process_detail",
    "team_vehicle",
    "empty_space",
}

# ============================================================
# 🧠 INIT
# ============================================================

if not STORE_PATH.exists():
    STORE_PATH.write_text(
        json.dumps({"posts": []}, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

# ============================================================
# 📦 LOW LEVEL IO
# ============================================================

def _load() -> Dict[str, Any]:
    try:
        data = json.loads(STORE_PATH.read_text(encoding="utf-8"))
        if isinstance(data, dict) and isinstance(data.get("posts"), list):
            return data
    except Exception:
        pass
    return {"posts": []}


def _save(data: Dict[str, Any]):
    STORE_PATH.write_text(
        json.dumps(data, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def _normalize_category(cat: str) -> str:
    if not cat:
        return "finished_work"

    # akzeptiere auch deine folder-namen ohne underscores
    alias = {
        "finishedwork": "finished_work",
        "workaction": "work_action",
        "processdetails": "process_detail",
        "processdetail": "process_detail",
        "teamvehicle": "team_vehicle",
        "emptyspace": "empty_space",
    }
    cat = alias.get(cat, cat)

    if cat not in VALID_IMAGE_CATEGORIES:
        return "finished_work"
    return cat


def _normalize_post(post: Dict[str, Any]) -> Dict[str, Any]:
    cat = (
        post.get("category")
        or post.get("image_context")
        or post.get("image_category")
    )
    post["category"] = _normalize_category(cat)
    post.setdefault("results", {})
    return post


# ============================================================
# 🧠 FILESYSTEM SYNC (PREVIEW + APPROVED)
# ============================================================

def _sync_filesystem(client: str):
    data = _load()
    posts = data["posts"]

    preview_dir = (
        BASE_DIR / "backend" / "clients" / client / "output" / "preview"
    )
    approved_dir = (
        BASE_DIR / "backend" / "clients" / client / "output" / "approved"
    )

    def split_variant(stem: str):
        if stem.endswith("_facebook"):
            return stem[:-9], "facebook"
        if stem.endswith("_linkedin"):
            return stem[:-9], "linkedin"
        return stem, "instagram"

    files_by_id: Dict[str, Dict[str, str]] = {}

    def collect(dir_path: Path, folder: str):
        if not dir_path.exists():
            return

        patterns = ["*.png", "*.PNG", "*.jpg", "*.JPG", "*.jpeg", "*.JPEG"]
        for pat in patterns:
            for f in dir_path.glob(pat):
                base_id, platform = split_variant(f.stem)
                files_by_id.setdefault(base_id, {})
                files_by_id[base_id][platform] = (
                    f"/static/{client}/output/{folder}/{f.name}"
                )

    # PRIORITÄT: preview > approved
    collect(approved_dir, "approved")
    collect(preview_dir, "preview")

    posts_by_id = {
        p["id"]: p for p in posts if p.get("client") == client
    }

    touched_ids = set()

    for post_id, platform_map in files_by_id.items():
        post = posts_by_id.get(post_id)

        if not post:
            post = {
                "id": post_id,
                "client": client,
                "type": "manual",
                "category": "finished_work",
                "content_category": "manual",
                "preview": "",
                "caption": "",
                "results": {},
                "status": "preview",
                "created_at": datetime.utcnow().isoformat(),
            }
            posts.append(post)

        post = _normalize_post(post)
        _inject_foundation_caption(post, client)

        from core.caption_builder import build_caption

        from core.caption_builder import build_caption

        # 🔥 FORCE 3 PLATFORMS (single image, multi platform)
        base_preview = platform_map.get("instagram") or next(iter(platform_map.values()))

        for pf in ("instagram", "facebook", "linkedin"):
            post.setdefault("results", {})
            post["results"].setdefault(pf, {})

            # Preview: gleiches Bild für alle
            post["results"][pf]["preview_url"] = base_preview

            # Caption: erzwinge saubere Kategorie
            try:
                post["results"][pf]["caption"] = build_caption(
                    client=client,
                    category=post.get("type") if post.get("type") in ("foundation","trust","service") else "foundation",
                    platform=pf,
                    post_id=post.get("id"),
                )
            except Exception as e:
                post["results"][pf]["caption"] = ""

            # 🔥 CAPTION INJECT (plattform + post_id)
            try:
                post["results"][pf]["caption"] = build_caption(
                    client=client,
                    category=post.get("type") or post.get("category") or "foundation",
                    platform=pf,
                    post_id=post.get("id"),
                )
            except Exception:
                post["results"][pf]["caption"] = ""

        if "instagram" in platform_map:
            post["preview"] = platform_map["instagram"]

        touched_ids.add(post_id)

    # CLEANUP: preview posts ohne Dateien → löschen
    cleaned: List[Dict[str, Any]] = []

    for p in posts:
        if p.get("client") != client:
            cleaned.append(p)
            continue

        status = (p.get("status") or "").lower()

        if status in {"approved", "scheduled", "posted", "published"}:
            cleaned.append(p)
            continue

        if p["id"] in touched_ids:
            cleaned.append(p)

    data["posts"] = cleaned
    _save(data)



# ============================================================
# 🧠 FOUNDATION CAPTION LOADER
# ============================================================
def _load_foundation_captions(client: str) -> dict:
    path = CLIENTS_DIR / client / "captions" / "foundation.json"
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


# ============================================================
# 🔍 READ
# ============================================================

def get_post_by_id(post_id: str) -> Optional[Dict[str, Any]]:
    data = _load()
    for p in data["posts"]:
        if p.get("id") == post_id:
            return p
    return None


def ensure_post_exists(post_id: str, client: str) -> Dict[str, Any]:
    data = _load()

    for p in data["posts"]:
        if p.get("id") == post_id:
            return p

    post = {
        "id": post_id,
        "client": client,
        "type": "manual",
        "category": "finished_work",
        "content_category": "manual",
        "preview": "",
        "caption": "",
        "results": {},
        "status": "preview",
        "created_at": datetime.utcnow().isoformat(),
    }

    data["posts"].append(post)
    _save(data)
    return post



# ============================================================
# 🔄 SYNC STATUS FROM FILESYSTEM (SINGLE SOURCE OF TRUTH)
# ============================================================
from api.helpers.dashboard_helpers import (
    PREVIEW_DIR,
    APPROVED_DIR,
    POSTING_QUEUE_DIR,
    POSTED_DIR,
)

def _sync_status_from_fs(post: dict) -> str:
    pid = post.get("id")

    if any(POSTED_DIR.glob(f"{pid}*")):
        return "posted"
    if any(POSTING_QUEUE_DIR.glob(f"{pid}*")):
        return "scheduled"
    if any(APPROVED_DIR.glob(f"{pid}*")):
        return "approved"
    if any(PREVIEW_DIR.glob(f"{pid}*")):
        return "preview"

    return post.get("status", "preview")

def get_posts(client: str) -> List[Dict[str, Any]]:
    _sync_filesystem(client)
    data = _load()
    posts = [p for p in data["posts"] if p.get("client") == client]

    # 🔌 ENRICH POSTS FOR DASHBOARD
    for p in posts:
        results = p.get("results", {}) or {}

        # 🔤 CAPTIONS INJIZIEREN (FOUNDATION / SERVICE / TRUST)
        from core.caption_builder import build_caption
        post_id = p.get("id")

        # Kategorie aus Post-ID ableiten
        if post_id.startswith("fp_"):
            category = "foundation"
        elif post_id.startswith("tr_"):
            category = "trust"
        elif post_id.startswith("sv_"):
            category = "service"
        else:
            category = "foundation"

        for platform in ("instagram", "facebook", "linkedin"):
            results.setdefault(platform, {})
            if not results[platform].get("caption"):
                results[platform]["caption"] = build_caption(
                    client=client,
                    category=category,
                    platform=platform,
                    post_id=post_id,
                )

        p["previews"] = {
            "instagram": results.get("instagram", {}).get("preview_url"),
            "facebook":  results.get("facebook", {}).get("preview_url"),
            "linkedin":  results.get("linkedin", {}).get("preview_url"),
        }

        # 🧠 FOUNDATION CAPTIONS (Dashboard only)
        from core.caption_builder import build_caption

        for pf in ("instagram", "facebook", "linkedin"):
            res = p.setdefault("results", {}).setdefault(pf, {})
            if not res.get("caption"):
                res["caption"] = build_caption(
                    client=client,
                    category="foundation",
                    platform=pf,
                    post_id=p.get("id"),
                )

        # Status aus FS überschreiben (Single Source of Truth)
        try:
            p["status"] = _sync_status_from_fs(p)
        except Exception:
            pass

    return posts


# ============================================================
# ✏️ UPDATE POST (PATCH)
# ============================================================

def update_post(post_id: str, patch: dict):
    """
    Partial update eines Posts anhand seiner ID.
    """
    data = _load()
    updated = False

    for p in data.get("posts", []):
        if p.get("id") == post_id:
            if isinstance(patch, dict):
                p.update(patch)
            updated = True
            break

    if not updated:
        raise KeyError(f"Post not found: {post_id}")

    _save(data)
    return True