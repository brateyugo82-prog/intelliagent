from datetime import datetime, timedelta

PLATFORM_OFFSETS = {
    "instagram": 0,
    "facebook": 7,   # Minuten Offset
    "linkedin": None # manuell
}

def compute_platform_time(base_time: datetime, platform: str):
    offset = PLATFORM_OFFSETS.get(platform)
    if offset is None:
        return None
    return base_time + timedelta(minutes=offset)
