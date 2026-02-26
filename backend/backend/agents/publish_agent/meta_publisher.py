import os
import requests


def post_to_facebook(message: str) -> dict:
    """
    Postet einen Text-Post auf eine Facebook Page
    """
    page_id = os.getenv("META_PAGE_ID")
    token = os.getenv("META_PAGE_TOKEN")
    version = os.getenv("META_API_VERSION", "v24.0")

    if not page_id or not token:
        raise RuntimeError("META_PAGE_ID oder META_PAGE_TOKEN fehlt")

    url = f"https://graph.facebook.com/{version}/{page_id}/feed"

    r = requests.post(
        url,
        data={
            "message": message,
            "access_token": token,
        },
        timeout=10,
    )

    r.raise_for_status()
    return r.json()
