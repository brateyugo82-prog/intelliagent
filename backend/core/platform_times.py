from datetime import datetime, timedelta, timezone
from core.platforms import PLATFORMS

def build_platform_times(now: datetime | None = None) -> dict:
    if now is None:
        now = datetime.now(timezone.utc)

    times = {}

    for platform, cfg in PLATFORMS.items():
        delay = cfg.get("delay_minutes")
        if delay is None:
            times[platform] = None
        else:
            times[platform] = (now + timedelta(minutes=delay)).isoformat()

    return times
