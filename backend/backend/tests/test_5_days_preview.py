import subprocess
import sys
from pathlib import Path

# --------------------------------------------------
# CONFIG
# --------------------------------------------------
CLIENT = "mtm_client"
PLATFORMS = ["instagram", "linkedin", "facebook"]

# 5 Tage – feste Rotation
DAYS = [
    ("DAY 1", "default"),
    ("DAY 2", "handwerk"),
    ("DAY 3", "service"),
    ("DAY 4", "default"),
    ("DAY 5", "handwerk"),
]

PROJECT_ROOT = Path(__file__).resolve().parents[2]
MASTER = PROJECT_ROOT / "backend" / "master_agent" / "master.py"
PYTHON = sys.executable  # nutzt die aktive venv

# --------------------------------------------------
# RUN
# --------------------------------------------------
print("\n🚀 START 5-DAY CONTENT PREVIEW TEST")
print("----------------------------------")

for day_label, category in DAYS:
    print(f"\n🟢 {day_label} | CATEGORY: {category.upper()}")

    for platform in PLATFORMS:
        print(f"   ▶ {platform.upper()}")

        cmd = [
            PYTHON,
            str(MASTER),
            CLIENT,
            platform,
            category  # ⬅️ Kategorie explizit übergeben
        ]

        subprocess.run(cmd, check=False)

print("\n✅ TEST DONE")
print("📁 CHECK OUTPUT:")
print("clients/mtm_client/output/preview\n")