"""
✅ FINAL VERSION – IntelliAgent Kosten-Analytics (OpenAI + Render)
----------------------------------------------------------------
Zeigt geschätzte monatliche Betriebskosten deiner Agenten-Pipeline an.
- OpenAI-Kosten (nach Anzahl Prompts)
- Render-Kosten (Plan-basiert)
- Domainkosten (optional fix)
"""

from fastapi import APIRouter
from datetime import datetime
from pathlib import Path
import json
import os

router = APIRouter(prefix="/api/stats", tags=["System Stats"])

# Basispreise
OPENAI_PRICE_PER_PROMPT = 0.00015 * 1000  # ~0.15 € pro 1000 Prompts
RENDER_STARTER_PLAN = 7.00  # €/Monat
DOMAIN_COST = 1.00  # €/Monat

LOG_FILE = Path("backend/logs/meta_events.json")


@router.get("/costs")
async def get_cost_estimate():
    """
    Gibt eine monatliche Kostenschätzung zurück basierend auf:
    - Anzahl gespeicherter Events in logs/meta_events.json
    - Durchschnittlicher Prompt-Nutzung
    - Render + Domain Fixkosten
    """
    total_events = 0
    total_prompts = 0

    if LOG_FILE.exists():
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    entry = json.loads(line.strip())
                    total_events += 1
                except json.JSONDecodeError:
                    continue

    # Schätzung: 1 Event = 3 Prompts (Communication + Publish + Analytics)
    total_prompts = total_events * 3

    # OpenAI-Kosten (sehr konservativ)
    openai_costs = round(total_prompts * 0.0015, 2)  # ca. 0.15€ / 100 Prompts

    total_costs = openai_costs + RENDER_STARTER_PLAN + DOMAIN_COST

    return {
        "timestamp": datetime.now().isoformat(),
        "events_tracked": total_events,
        "estimated_prompts": total_prompts,
        "openai_costs_eur": openai_costs,
        "render_costs_eur": RENDER_STARTER_PLAN,
        "domain_costs_eur": DOMAIN_COST,
        "total_estimated_costs_eur": total_costs,
        "note": "Diese Werte sind Schätzungen basierend auf Nutzung und Logs."
    }
