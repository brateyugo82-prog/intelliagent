import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

# ============================================================
# 🔒 STORE PATH
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[2]  # IntelliAgent/
STORE_PATH = BASE_DIR / "backend" / "runtime" / "posts.json"
STORE_PATH.parent.mkdir(parents=True, exist_ok=True)

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


def _normalize_post(post: Dict[str, Any]) -> Dict[str, Any]:
    cat = (
        post.get("category")
        or post.get("image_context")
        or post.get("image_category")
    )

    if cat not in VALID_IMAGE_CATEGORIES:
        cat = "finished_work"

    post["category"] = cat
    post.setdefault("results", {})
    return post


# ============================================================
# 🧠 FILESYSTEM SYNC (NUR PREVIEW + APPROVED)
# ============================================================

def _sync_filesystem(client: str):
    data = _load()
    posts = data["posts"]

    preview_dir = (
        BASE_DIR / "backend" / "clients" / client / "output" / "preview"
    )
    approved_dir = (
        BASE_DIR / "backend" / "clients" / client / "output" / "approved" / "used"
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
        for f in dir_path.glob("*.png"):
            base_id, platform = split_variant(f.stem)
            files_by_id.setdefault(base_id, {})
            files_by_id[base_id][platform] = (
                f"/static/{client}/output/{folder}/{f.name}"
            )

    # PRIORITÄT: preview > approved
    collect(approved_dir, "approved/used")
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

        for pf, url in platform_map.items():
            post.setdefault("results", {})
            post["results"].setdefault(pf, {})
            post["results"][pf]["preview_url"] = url

        if "instagram" in platform_map:
            post["preview"] = platform_map["instagram"]

        touched_ids.add(post_id)

    # 🔥 CLEANUP:
    # preview Posts ohne Dateien → löschen
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


def get_posts(client: str) -> List[Dict[str, Any]]:
    _sync_filesystem(client)
    data = _load()
    return [p for p in data["posts"] if p.get("client") == client]


# ============================================================
# ➕ CREATE
# ============================================================

def add_post(post: dict):
    data = _load()

    posts = data.get("posts", [])
    post_id = post.get("id")

    if not post_id:
        raise ValueError("Post requires an id")

    # 🔑 UPSERT: ersetze bestehenden Post mit gleicher ID
    replaced = False
    for i, p in enumerate(posts):
        if p.get("id") == post_id:
            posts[i] = post
            replaced = True
            break

    if not replaced:
        posts.append(post)

    data["posts"] = posts
    _save(data)


# ============================================================
# 🔄 STATUS UPDATE
# ============================================================

def update_status(post_id: str, status: str):
    data = _load()

    for p in data["posts"]:
        if p.get("id") == post_id:
            p["status"] = status
            if status == "posted":
                p["posted_at"] = datetime.utcnow().isoformat()
            break

    _save(data)


# ============================================================
# 🔧 GENERIC UPDATE
# ============================================================

def update_post(post_id: str, fields: Dict[str, Any]) -> Dict[str, Any]:
    data = _load()
    updated = None

    for p in data["posts"]:
        if p.get("id") == post_id:
            for k, v in fields.items():
                if v is None:
                    continue

                if k == "results" and isinstance(v, dict):
                    p.setdefault("results", {})
                    for pf, pf_data in v.items():
                        p["results"].setdefault(pf, {})
                        p["results"][pf].update(pf_data)
                else:
                    p[k] = v

            updated = _normalize_post(p)
            break

    if not updated:
        raise KeyError(f"Post nicht gefunden: {post_id}")

    _save(data)
    return updated
def mark_manual_required(post_id: str, platform: str):
    post = get_post_by_id(post_id)

    post.setdefault("platform_status", {})
    post["platform_status"][platform] = "manual"
    post["status"] = "scheduled_manual"

    update_post(post_id, post)

from datetime import datetime

def finalize_post_if_done(post_id: str):
    post = get_post_by_id(post_id)

    if all(v == "posted" for v in post.get("platform_status", {}).values()):
        post["status"] = "posted"
        post["published_at"] = datetime.utcnow().isoformat()

        update_post(post_id, post)
        return True

    return False
