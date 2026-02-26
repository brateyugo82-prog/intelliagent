import os
import requests
from dotenv import load_dotenv

# 🔹 Pfad zur globalen .env
env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
print(f"Lade .env von: {env_path}")

# .env laden
load_dotenv(env_path)

# Token prüfen
token = os.getenv("META_ACCESS_TOKEN")

if not token:
    print("❌ Kein META_ACCESS_TOKEN in .env gefunden.")
    exit(1)
else:
    print(f"✅ META_ACCESS_TOKEN geladen: {token[:40]}...")

# 🔹 Test-Request an Meta Graph API
url = "https://graph.facebook.com/v23.0/me"
params = {"access_token": token}

try:
    r = requests.get(url, params=params)
    r.raise_for_status()
    data = r.json()
    print("✅ Erfolgreich verbunden mit Meta Graph API.")
    print(f"Name: {data.get('name', 'Unbekannt')}")
    print(f"ID: {data.get('id', 'Keine ID gefunden')}")
except requests.exceptions.RequestException as e:
    print(f"❌ HTTP-Fehler: {e}")
except Exception as e:
    print(f"❌ Fehler: {e}")
