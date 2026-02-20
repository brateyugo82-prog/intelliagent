from fastapi import APIRouter, HTTPException
from pathlib import Path
from datetime import datetime, timezone
import json

from core.post_store import add_post, get_post_by_id
from core.preview_mockup import create_platform_mockup

router = APIRouter(prefix="/api/foundation", tags=["foundation"])

CURRENT_FILE = Path(__file__).resolve()

BACKEND_DIR = CURRENT_FILE
while BACKEND_DIR.name != "backend":
    BACKEND_DIR = BACKEND_DIR.parent

CLIENTS_DIR = BACKEND_DIR / "clients"


def _build_caption(block: dict) -> str:
    """
    Baut finale Caption aus:
    - text
    - cta (Liste)
    - hashtags (Liste)
    """
    parts: list[str] = []

    text = block.get("text", "").strip()
    if text:
        parts.append(text)

    ctas = block.get("cta") or []
    if isinstance(ctas, list) and ctas:
        parts.append("\n".join(ctas))

    hashtags = block.get("hashtags") or []
    if isinstance(hashtags, list) and hashtags:
        parts.append(" ".join(hashtags))

    return "\n\n".join(parts).strip()


@router.post("/create-previews/{client}")
def create_foundation_previews(client: str):
    client_dir = CLIENTS_DIR / client
    foundation_path = client_dir / "foundation_posts.json"
    assets_dir = client_dir / "assets" / "foundation"
    preview_dir = client_dir / "output" / "preview"

    if not foundation_path.exists():
        raise HTTPException(404, "foundation_posts.json fehlt")

    if not assets_dir.exists():
        raise HTTPException(404, "assets/foundation Ordner fehlt")

    preview_dir.mkdir(parents=True, exist_ok=True)

    data = json.loads(foundation_path.read_text(encoding="utf-8"))
    created = []

    for fp in data.get("posts", []):
        post_id = fp.get("id")
        image_file = fp.get("image_file")
        platforms = fp.get("platforms", {})

        if not post_id or not image_file:
            continue

        if get_post_by_id(post_id):
            continue

        image_path = assets_dir / image_file
        if not image_path.exists():
            continue

        results = {}

        for platform in ["instagram", "facebook", "linkedin"]:
            block = platforms.get(platform)

            # Facebook kann Text von Instagram übernehmen
            if isinstance(block, dict) and block.get("use_text_from") == "instagram":
                block = platforms.get("instagram", {})

            if not isinstance(block, dict):
                continue

            caption = _build_caption(block)

            preview_file = (
                f"{post_id}.png"
                if platform == "instagram"
                else f"{post_id}_{platform}.png"
            )

            preview_path = preview_dir / preview_file

            create_platform_mockup(
                image_path=str(image_path),
                text=caption,
                output_path=str(preview_path),
                platform=platform,
            )

            results[platform] = {
                "preview_url": f"/static/{client}/output/preview/{preview_file}",
                "caption": caption,
            }

        add_post(
            {
                "id": post_id,
                "client": client,
                "preview": results.get("instagram", {}).get("preview_url"),
                "caption": results.get("instagram", {}).get("caption", ""),
                "results": results,
                "status": "preview",
                "content_category": "foundation",
                "created_at": datetime.now(timezone.utc).isoformat(),
                "source_image_path": f"/static/{client}/assets/foundation/{image_file}",
            }
        )

        created.append(post_id)

    return {
        "status": "ok",
        "created": created,
        "count": len(created),
    }