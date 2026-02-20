"""
Dynamischer Master Agent – WEEKLY ONLY (STABLE SSOT)
"""

import importlib
import uuid
import shutil
import json
from datetime import datetime, date, timezone
from pathlib import Path
from typing import Any, List

from core.logger import logger
from core.preview_mockup import create_platform_mockup
from core.branding_renderer import apply_branding
from core.client_config import load_client_config
from core.post_store import add_post
from core.caption_builder import build_caption

# ==================================================
# PATHS / CONSTANTS
# ==================================================

BASE_DIR = Path(__file__).resolve().parents[1]
CLIENTS_DIR = BASE_DIR / "clients"

PLATFORMS = ["instagram", "facebook", "linkedin"]

CONTENT_TO_IMAGE_CONTEXT = {
    "service": "finished_work",
    "lead": "work_action",
    "trust": "process_detail",
    "soft": "team_vehicle",
    "entruempelung": "empty_space",
}

IMAGE_TO_CONTENT = {v: k for k, v in CONTENT_TO_IMAGE_CONTEXT.items()}
IMAGE_CONTEXT_CHOICES = set(IMAGE_TO_CONTENT.keys())

# ==================================================
# WEEKLY HELPERS
# ==================================================

def load_weekly_plan(client: str) -> dict:
    path = CLIENTS_DIR / client / "content_rules" / "weekly_plan.json"
    if not path.exists():
        raise RuntimeError("❌ weekly_plan.json fehlt")

    data = json.loads(path.read_text(encoding="utf-8"))
    return data.get("week", data)


def get_today_key() -> str:
    return datetime.today().strftime("%A").lower()


def _extract_content_categories(entries: Any) -> List[str]:
    if not isinstance(entries, list):
        return []

    cats = []
    for e in entries:
        if isinstance(e, dict):
            c = e.get("content_category")
            if isinstance(c, str):
                cats.append(c.lower())
    return cats


# ==================================================
# SINGLE POST CREATION (WEEKLY CORE)
# ==================================================

def create_single_post(client: str, category: str) -> str:
    raw = category.strip().lower()

    if raw in IMAGE_CONTEXT_CHOICES:
        image_context = raw
        content_category = IMAGE_TO_CONTENT.get(raw, "service")
    else:
        content_category = raw
        image_context = CONTENT_TO_IMAGE_CONTEXT.get(content_category)

    if not image_context:
        raise RuntimeError(f"❌ Unbekannte Kategorie: {content_category}")

    cfg = load_client_config(client)
    post_id = str(uuid.uuid4())

    logger.info(
        f"[WEEKLY] post_id={post_id} | content={content_category} | image={image_context}"
    )

    # ---------------------------
    # DESIGN
    # ---------------------------
    design_agent = importlib.import_module("agents.design_agent.agent")
    design_result = design_agent.run(
        client=client,
        context={"image_context": image_context},
    )

    raw_image = Path(design_result["design"])

    branded = apply_branding(
        image_path=str(raw_image),
        brand_ctx={
            "client_name": client,
            "logo": cfg["brand_assets"]["logo"],
            "contact_overlay": cfg["brand_assets"]["contact_overlay"],
        },
        image_context=image_context,
        platform="instagram",
        run_date=date.today(),
    )

    source_dir = CLIENTS_DIR / client / "output" / "source"
    preview_dir = CLIENTS_DIR / client / "output" / "preview"
    source_dir.mkdir(parents=True, exist_ok=True)
    preview_dir.mkdir(parents=True, exist_ok=True)

    branded_source = source_dir / f"{post_id}.png"
    shutil.copyfile(branded, branded_source)

    results = {}
    instagram_caption = ""

    # ---------------------------
    # CAPTIONS + PREVIEWS
    # ---------------------------
    for pf in PLATFORMS:
        base_caption = build_caption(
            client=client,
            category=content_category,
            platform=pf,
        )

        # 🔁 FALLBACK: Plattform leer → Instagram
        if not base_caption and pf != "instagram":
            base_caption = build_caption(
                client=client,
                category=content_category,
                platform="instagram",
            )

        final_caption = base_caption.strip()

        fname = f"{post_id}.png" if pf == "instagram" else f"{post_id}_{pf}.png"

        create_platform_mockup(
            image_path=str(branded_source),
            text=final_caption,
            output_path=str(preview_dir / fname),
            platform=pf,
        )

        results[pf] = {
            "preview_url": f"/static/{client}/output/preview/{fname}",
            "caption": final_caption,
            "image_context": image_context,
        }

        if pf == "instagram":
            instagram_caption = final_caption

    # ---------------------------
    # STORE POST (PREVIEW)
    # ---------------------------
    add_post(
        {
            "id": post_id,
            "client": client,
            "category": image_context,
            "content_category": content_category,
            "preview": f"/static/{client}/output/preview/{post_id}.png",
            "caption": instagram_caption,
            "results": results,
            "status": "preview",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "source_image_path": f"/static/{client}/output/source/{post_id}.png",
        }
    )

    return post_id


# ==================================================
# WORKFLOW ENTRYPOINT (NO FOUNDATION)
# ==================================================

def run_workflow(
    client: str,
    mode: str,
    content_category: str | None = None,
):
    weekly_plan = load_weekly_plan(client)

    if mode == "today":
        today = get_today_key()
        cats = _extract_content_categories(weekly_plan.get(today))
        if not cats:
            raise RuntimeError("❌ Keine Kategorie für heute")
        return {"post_id": create_single_post(client, cats[0])}

    if mode == "week":
        created = {}
        for day, entries in weekly_plan.items():
            cats = _extract_content_categories(entries)
            if cats:
                created[day] = [create_single_post(client, cats[0])]
        return {"created": created}

    if mode == "single":
        if not content_category:
            raise RuntimeError("❌ content_category fehlt")
        return {"post_id": create_single_post(client, content_category)}

    raise RuntimeError(f"❌ Unbekannter Modus: {mode}")