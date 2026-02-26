import os
import requests

def publish(post: dict):
    fb = post["results"]["facebook"]
    image_url = "http://127.0.0.1:8000" + fb["preview_url"]
    caption = fb["caption"]

    page_id = os.getenv("META_PAGE_ID")
    token = os.getenv("META_PAGE_TOKEN")
    version = os.getenv("META_API_VERSION", "v24.0")

    if not page_id or not token:
        raise RuntimeError("META_PAGE_ID oder META_PAGE_TOKEN fehlt")

    r = requests.post(
        f"https://graph.facebook.com/{version}/{page_id}/photos",
        data={
            "url": image_url,
            "caption": caption,
            "published": "true",
            "access_token": token,
        },
        timeout=15,
    )

    if not r.ok:
        raise RuntimeError(r.text)

    return r.json()
