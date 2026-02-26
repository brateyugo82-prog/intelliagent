import os
from dotenv import load_dotenv

env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
print(f"Lade .env von: {env_path}")

if os.path.exists(env_path):
    print("✅ .env gefunden.")
else:
    print("❌ .env nicht gefunden!")

load_dotenv(env_path)

token = os.getenv("META_ACCESS_TOKEN")
if token:
    print(f"✅ META_ACCESS_TOKEN gefunden: {token[:50]}...")
else:
    print("❌ Kein META_ACCESS_TOKEN gefunden.")
