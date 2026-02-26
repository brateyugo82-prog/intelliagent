from pathlib import Path
from fastapi import HTTPException

def static_to_fs(static_url: str, clients_dir: Path) -> Path:
    if not static_url.startswith("/static/"):
        raise HTTPException(400, f"Invalid static url: {static_url}")
    rel = static_url.replace("/static/", "", 1)
    return clients_dir / rel

def fs_exists_from_static(static_url: str, clients_dir: Path) -> bool:
    try:
        return static_to_fs(static_url, clients_dir).exists()
    except Exception:
        return False
