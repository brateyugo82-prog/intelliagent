import os
import requests
from dotenv import load_dotenv

# 🔹 Lade .env
env_path = os.path.join(os.path.dirname(__file__), "..", ".env")
print(f"Lade .env von: {env_path}")
load_dotenv(env_path)

# Token & IG Business ID abrufen
token = os.getenv("META_ACCESS_TOKEN")
ig_business_id = os.getenv("INSTAGRAM_BUSINESS_ID")

if not token:
    print("❌ Kein META_ACCESS_TOKEN gefunden.")
    exit(1)
if not ig_business_id:
    print("❌ Keine INSTAGRAM_BUSINESS_ID gefunden.")
    exit(1)

# 🔹 API-Endpunkt
url = f"https://graph.facebook.com/v18.0/{ig_business_id}"
params = {
    "fields": "id,username,name,followers_count",
    "access_token": token
}

print("🔍 Teste Instagram-API-Verbindung...")
try:
    r = requests.get(url, params=params)
    r.raise_for_status()
    data = r.json()
    print("✅ Verbindung erfolgreich!")
    print(f"📸 Benutzername: {data.get('username')}")
    print(f"🆔 ID: {data.get('id')}")
    print(f"👥 Follower: {data.get('followers_count', 'unbekannt')}")
except requests.exceptions.RequestException as e:
    print(f"❌ HTTP-Fehler: {e}")
    print(f"Antwort: {r.text}")
except Exception as e:
    print(f"❌ Fehler: {e}")
