import json
import re
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]

PHONE_REGEX = re.compile(r'(\+49|0)[1-9][0-9]{7,12}')

def load_client_policies(client: str):
    policy_dir = BASE_DIR / "clients" / client / "policies"
    with open(policy_dir / "lead_qualification.json") as f:
        qualification = json.load(f)
    with open(policy_dir / "keyword_map.json") as f:
        keywords = json.load(f)
    return qualification, keywords

def normalize(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^a-z0-9äöüß\s]", " ", text)
    return text

def parse_lead_text(text: str, client: str) -> dict:
    qualification, keywords = load_client_policies(client)
    normalized = normalize(text)

    detected_services = set()
    for service, words in keywords.items():
        for w in words:
            if w in normalized:
                detected_services.add(service)

    has_phone = bool(PHONE_REGEX.search(text))

    return {
        "raw_text": text,
        "services": sorted(detected_services),
        "has_phone": has_phone,
        "is_relevant_service": any(
            s in qualification["services"] for s in detected_services
        )
    }
