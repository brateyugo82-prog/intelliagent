from backend.backend.core.platforms import PLATFORMS

def should_auto_publish(platform: str) -> bool:
    return PLATFORMS.get(platform, {}).get("auto_publish", False)

def is_manual(platform: str) -> bool:
    return PLATFORMS.get(platform, {}).get("manual", False)
