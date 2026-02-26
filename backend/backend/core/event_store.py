import json
from pathlib import Path
from datetime import datetime

def track_event(client_dir: Path, event: dict):
    path = client_dir / "state" / "events.jsonl"
    path.parent.mkdir(parents=True, exist_ok=True)

    event["timestamp"] = datetime.utcnow().isoformat()

    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(event, ensure_ascii=False) + "\n")