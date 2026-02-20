"""
✅ Quality Agent v1.2 — Smart Quality Gate (FINAL)
-------------------------------------------------
- Stoppt Floskeln
- Prüft Bild-Text-Passung
- Lässt gute Texte durch
- Erzwingt sinnvolles, kontrolliertes Rewrite
"""

from typing import Dict, Any, List


# ------------------------------------------------------------
# ❌ Verbotene Marketing-Floskeln
# ------------------------------------------------------------
FORBIDDEN_PHRASES = [
    "fachmännisch",
    "reibungslos",
    "wir kümmern uns um alles",
    "vertrauen sie uns",
    "ihr zuverlässiger partner",
    "neuer lebensabschnitt",
    "exzellente arbeit",
    "mit herz und leidenschaft",
]

# ------------------------------------------------------------
# ✅ Erwünschte Nutzenbegriffe
# ------------------------------------------------------------
ALLOWED_BENEFITS = [
    "sauber",
    "geordnet",
    "aufgeräumt",
    "bereit",
    "fertig",
    "übersichtlich",
    "klar",
]

# ------------------------------------------------------------
# ❌ Prozess-Wörter (NICHT bei fertigen Bildern)
# ------------------------------------------------------------
PROCESS_WORDS = [
    "montieren",
    "aufbauen",
    "arbeiten",
    "im gange",
    "laufend",
    "während",
]


# ------------------------------------------------------------
# 🚀 Hauptfunktion
# ------------------------------------------------------------
def run(
    text_output: Dict[str, Any],
    image_description: str | None = None,
    image_type: str | None = None,
    **kwargs
) -> Dict[str, Any]:

    image_text = text_output.get("image_text", "")
    cta_text = text_output.get("cta", "")

    image_text_lower = image_text.lower().strip()
    cta_text_lower = cta_text.lower().strip()
    reasons: List[str] = []

    # --------------------------------------------------------
    # Guard: Bildtext vorhanden?
    # --------------------------------------------------------
    if not image_text_lower:
        return {
            "quality": "fail",
            "confidence_score": 0.0,
            "reasons": ["Kein Bildtext vorhanden"],
            "action": "discard",
        }

    # --------------------------------------------------------
    # 1️⃣ Marketing-Floskeln im Bildtext VERBOTEN (strikt)
    # --------------------------------------------------------
    for phrase in FORBIDDEN_PHRASES:
        if phrase in image_text_lower:
            reasons.append(f"Marketing-Floskel im Bildtext: '{phrase}'")

    # --------------------------------------------------------
    # 2️⃣ Prozess-Wörter bei fertigem Bild im Bildtext VERBOTEN (strikt)
    # --------------------------------------------------------
    if image_type == "finished_room":
        for word in PROCESS_WORDS:
            if word in image_text_lower:
                reasons.append(
                    f"Prozess-Wort im Bildtext bei fertigem Bild: '{word}'"
                )

    # --------------------------------------------------------
    # 3️⃣ Klarer Nutzen im Bildtext?
    # --------------------------------------------------------
    if not any(b in image_text_lower for b in ALLOWED_BENEFITS):
        reasons.append("Kein klarer Nutzen im Bildtext erkennbar")

    # --------------------------------------------------------
    # 4️⃣ Instagram-Stil (max. 3 Sätze) nur im Bildtext
    # --------------------------------------------------------
    sentence_count = (
        image_text_lower.count(".") +
        image_text_lower.count("!") +
        image_text_lower.count("?")
    )

    if sentence_count > 3:
        reasons.append("Zu viele Sätze im Bildtext für Instagram")

    # --------------------------------------------------------
    # ❌ Fehler → Rewrite oder Discard
    # --------------------------------------------------------
    if reasons:
        score = max(0.0, 1.0 - 0.25 * len(reasons))

        return {
            "quality": "warning" if score >= 0.6 else "fail",
            "confidence_score": round(score, 2),
            "reasons": reasons,
            "action": "rewrite" if score >= 0.6 else "discard",
            "rewrite_instruction": (
                "Formuliere NUR den Bildtext neu. Der CTA darf unverändert bleiben oder leer sein. "
                "Vermeide Marketing-Floskeln oder Prozessbeschreibungen im Bildtext. "
                "Beschreibe ausschließlich das sichtbare Endergebnis auf dem Bild. "
                "Maximal 3 kurze, sachliche Sätze. Fokus auf Ordnung, Sauberkeit und Klarheit."
            ) if score >= 0.6 else None,
        }

    # --------------------------------------------------------
    # ✅ PASS
    # --------------------------------------------------------
    return {
        "quality": "pass",
        "confidence_score": 0.95,
        "checked_rules": [
            "no_fluff_in_image_text",
            "image_state_match",
            "clear_benefit_in_image_text",
            "instagram_style_in_image_text",
        ],
    }