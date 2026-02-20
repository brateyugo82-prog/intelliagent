from datetime import datetime, timedelta
from pathlib import Path
import json
import os

TOKENS_DIR = Path("state/tokens")
LOCK_FILE = Path("state/workflow.lock")

def _token_valid(platform: str) -> bool:
    token_file = TOKENS_DIR / f"{platform}.json"
    if not token_file.exists():
        return False

    data = json.loads(token_file.read_text())
    expires_at = datetime.fromisoformat(data["expires_at"])
    return expires_at > datetime.utcnow() + timedelta(hours=1)

def workflow_locked() -> bool:
    return LOCK_FILE.exists()

def posting_allowed(client_cfg: dict, platform: str) -> tuple[bool, str]:
    if not client_cfg.get("posting", {}).get("enabled", False):
        return False, "posting_disabled_by_client"

    if workflow_locked():
        return False, "workflow_running"

    if platform not in client_cfg.get("platforms", []):
        return False, "platform_not_allowed"

    if not _token_valid(platform):
        return False, "token_invalid"

    return True, "ok"