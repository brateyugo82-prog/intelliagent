import os
import requests

def _env(name: str) -> str:
    val = os.getenv(name)
    if not val:
        raise RuntimeError(f"ENV variable missing: {name}")
    return val

def publish(post: dict):
    ig = post["results"]["instagram"]
    image_url = "http://127.0.0.1:8000" + ig["preview_url"]
    caption = ig["caption"]

    ig_user_id = _env("INSTAGRAM_BUSINESS_ID")
    token = _env("META_PAGE_TOKEN")
    version = os.getenv("META_API_VERSION", "v24.0")

    # STEP 1: CREATE MEDIA
    r1 = requests.post(
        f"https://graph.facebook.com/{version}/{ig_user_id}/media",
        data={
            "image_url": image_url,
            "caption": caption,
            "access_token": token,
        },
        timeout=15,
    )
    if not r1.ok:
        raise RuntimeError(r1.text)

    creation_id = r1.json().get("id")
    if not creation_id:
        raise RuntimeError("No creation_id returned")

    # STEP 2: PUBLISH MEDIA
    r2 = requests.post(
        f"https://graph.facebook.com/{version}/{ig_user_id}/media_publish",
        data={
            "creation_id": creation_id,
            "access_token": token,
        },
        timeout=15,
    )
    if not r2.ok:
        raise RuntimeError(r2.text)

    return r2.json()
