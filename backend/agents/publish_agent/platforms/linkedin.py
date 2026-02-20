from typing import Dict, Any
from datetime import datetime

from core.logger import logger


def publish(post: Dict[str, Any]) -> Dict[str, Any]:
    """
    Simuliert das Publishing eines gespeicherten LinkedIn-Posts.
    KEINE Caption-Generierung.
    KEINE Entscheidungen.
    """

    post_id = post.get("id") or post.get("post_id")
    client = post.get("client")

    logger.info(
        f"[LinkedInPublisher] 💼 Publishing post_id={post_id} client={client}"
    )

    return {
        "platform": "linkedin",
        "platform_post_id": f"li_{post_id}",
        "published_at": datetime.utcnow().isoformat(),
        "status": "simulated",
    }