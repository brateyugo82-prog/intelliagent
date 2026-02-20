from pathlib import Path
from core.post_store import ensure_post_exists, update_post

CLIENT = "mtm_client"
BASE = Path(__file__).resolve().parents[1]
OUT = BASE / "clients" / CLIENT / "output"

MAP = {
    "preview": "preview",
    "approved": "approved",
    "posting_queue": "scheduled",
    "posted": "posted",
}

def base_id(name: str) -> str:
    return (
        name.replace("_facebook", "")
            .replace("_linkedin", "")
            .split(".")[0]
    )

def run():
    seen = set()

    for folder, status in MAP.items():
        p = OUT / folder
        if not p.exists():
            continue

        for f in p.iterdir():
            if not f.is_file():
                continue
            if f.suffix.lower() not in (".png", ".jpg", ".jpeg", ".webp"):
                continue

            pid = base_id(f.name)
            if pid in seen:
                continue

            seen.add(pid)

            ensure_post_exists(client=CLIENT, post_id=pid)

            static_url = f"/static/{CLIENT}/output/{folder}/{f.name}"

            update_post(pid, {
                "status": status,
                "preview": static_url,
            })

    print("✅ REBUILD DONE")
    print("→ posts:", len(seen))

if __name__ == "__main__":
    run()
