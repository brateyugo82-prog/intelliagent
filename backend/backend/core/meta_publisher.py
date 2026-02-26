import os
from core.final_caption_builder import build_final_caption
import requests

# =================================================
# 📘 FACEBOOK FOTO POST
# =================================================
def post_photo_to_facebook(image_url: str, caption: str) -> dict:
    page_id = os.getenv("META_PAGE_ID")
    token = os.getenv("META_PAGE_TOKEN")
    version = os.getenv("META_API_VERSION", "v19.0")

    if not page_id or not token:
        raise RuntimeError("META_PAGE_ID oder META_PAGE_TOKEN fehlt")

    url = f"https://graph.facebook.com/{version}/{page_id}/photos"

    caption = build_final_caption(
        client="mtm_client",
        base_text=caption,
        category=str(os.getenv("POST_CATEGORY", "lead"))
    )
    r = requests.post(
        url,
        data={
            "url": image_url,
            "caption": caption,
            "access_token": token,
        },
        timeout=15,
    )

    r.raise_for_status()
    return r.json()


# =================================================
# 📸 INSTAGRAM FOTO POST
# =================================================
def post_photo_to_instagram(image_url: str, caption: str) -> dict:
    ig_user_id = os.getenv("META_IG_USER_ID")
    token = os.getenv("META_PAGE_TOKEN")
    version = os.getenv("META_API_VERSION", "v19.0")

    if not ig_user_id or not token:
        raise RuntimeError("META_IG_USER_ID oder META_PAGE_TOKEN fehlt")

    caption = build_final_caption(
        client="mtm_client",
        platform="instagram",
        base_text=caption,
        category=str(os.getenv("POST_CATEGORY", "lead"))
    )
    container_url = f"https://graph.facebook.com/{version}/{ig_user_id}/media"
    caption = build_final_caption(
        client="mtm_client",
        base_text=caption,
        category=str(os.getenv("POST_CATEGORY", "lead"))
    )
    r = requests.post(
        container_url,
        data={
            "image_url": image_url,
            "caption": caption,
            "access_token": token,
        },
        timeout=15,
    )
    r.raise_for_status()
    creation_id = r.json()["id"]

    publish_url = f"https://graph.facebook.com/{version}/{ig_user_id}/media_publish"
    r2 = requests.post(
        publish_url,
        data={
            "creation_id": creation_id,
            "access_token": token,
        },
        timeout=15,
    )
    r2.raise_for_status()
    return r2.json()
