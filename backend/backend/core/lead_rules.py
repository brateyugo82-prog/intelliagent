from typing import Dict, List

SERVICE_KEYWORDS = {
    "umzug": [
        "umzug", "umziehen", "wohnungswechsel", "hausstand",
        "möbeltransport", "umzugsfirma"
    ],
    "montage": [
        "montage", "aufbau", "abbau", "schrank", "küche",
        "möbel montieren"
    ],
    "transport": [
        "transport", "abholen", "liefern", "lieferung",
        "möbel fahren"
    ],
}

def detect_services(text: str) -> List[str]:
    """
    Detects service categories based on keyword matches.
    """
    text_l = text.lower()
    found = []

    for service, keywords in SERVICE_KEYWORDS.items():
        for kw in keywords:
            if kw in text_l:
                found.append(service)
                break

    return found


def is_potential_lead(text: str) -> bool:
    """
    Basic heuristic: message contains service intent.
    """
    return len(detect_services(text)) > 0


def classify_lead(text: str) -> Dict:
    """
    Full classification result (used by LeadStore).
    """
    services = detect_services(text)

    return {
        "services": services,
        "is_lead": len(services) > 0,
        "confidence": "high" if len(services) >= 1 else "low",
    }
