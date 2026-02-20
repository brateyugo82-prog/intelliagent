from datetime import datetime
from core.platform_schedule import compute_platform_time
from core.post_store import update_post

def assign_platform_times(post_id: str, base_time: datetime, platforms: list):
    platform_times = {}

    for p in platforms:
        t = compute_platform_time(base_time, p)
        platform_times[p] = t.isoformat() if t else None

    update_post(post_id, {
        "platform_times": platform_times
    })

    return platform_times
