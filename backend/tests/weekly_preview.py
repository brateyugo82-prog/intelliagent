import os
import subprocess
import json
import shutil
from datetime import datetime

PLATFORMS = ["instagram", "facebook", "linkedin"]
DAYS = 5


def run_weekly_preview(client: str):
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    project_root = os.path.dirname(base_dir)

    preview_root = os.path.join(
        project_root,
        "backend",
        "clients",
        client,
        "output",
        "preview",
        f"week_{datetime.now().strftime('%Y-%m-%d')}"
    )
    os.makedirs(preview_root, exist_ok=True)

    print(f"\n🚀 WOCHEN-PREVIEW | Client={client}\n")

    for day in range(1, DAYS + 1):
        print(f"\n📅 TAG {day}")

        day_dir = os.path.join(preview_root, f"day_{day}")
        os.makedirs(day_dir, exist_ok=True)

        image_lock_file = os.path.join(day_dir, "image.json")

        # --------------------------------------------------
        # 1️⃣ BILD EINMAL PRO TAG FESTLEGEN
        # --------------------------------------------------
        if not os.path.exists(image_lock_file):
            print("   🖼 Bild wird einmalig gewählt")

            result = subprocess.run(
                [
                    "python",
                    "-m",
                    "backend.master_agent.master",
                    client,
                    "instagram"  # Plattform egal – Bild ist das Ziel
                ],
                cwd=project_root,
                capture_output=True,
                text=True,
                check=True
            )

            # Master speichert das Bild intern → wir lesen es aus Preview
            preview_base = os.path.join(
                project_root,
                "backend",
                "clients",
                client,
                "output",
                "preview"
            )

            previews = sorted(
                f for f in os.listdir(preview_base)
                if f.endswith("_instagram_preview.png")
            )

            if not previews:
                raise RuntimeError("❌ Kein Preview-Bild gefunden")

            latest_preview = os.path.join(preview_base, previews[-1])

            with open(image_lock_file, "w", encoding="utf-8") as f:
                json.dump(
                    {"preview_image": latest_preview},
                    f,
                    indent=2
                )
        else:
            print("   🔒 Tagesbild bereits festgelegt")

        # --------------------------------------------------
        # 2️⃣ ALLE PLATTFORMEN → GLEICHES BILD, ANDERER TEXT
        # --------------------------------------------------
        with open(image_lock_file, "r", encoding="utf-8") as f:
            locked = json.load(f)

        os.environ["FIXED_PREVIEW_IMAGE"] = locked["preview_image"]

        for platform in PLATFORMS:
            print(f"   ▶ {platform}")

            subprocess.run(
                [
                    "python",
                    "-m",
                    "backend.master_agent.master",
                    client,
                    platform
                ],
                cwd=project_root,
                check=True
            )

        os.environ.pop("FIXED_PREVIEW_IMAGE", None)

    print("\n✅ WOCHEN-PREVIEW FERTIG\n")


if __name__ == "__main__":
    import sys
    run_weekly_preview(sys.argv[1])