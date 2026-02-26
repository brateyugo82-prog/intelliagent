"""
Invoice Agent v1.0
------------------
- Erstellt Monatsabrechnung auf Basis von leads.csv
"""

from pathlib import Path
from datetime import datetime
import csv

BASE_DIR = Path(__file__).resolve().parents[1]


def run(client: str, price_per_lead: float = 15.0):

    data_dir = BASE_DIR / "clients" / client / "data"
    leads_path = data_dir / "leads.csv"
    invoice_path = data_dir / "invoices.csv"

    if not leads_path.exists():
        return {"error": "leads.csv nicht gefunden"}

    with open(leads_path, newline="", encoding="utf-8") as f:
        lead_count = sum(1 for _ in f) - 1  # Header abziehen

    total = lead_count * price_per_lead
    month = datetime.now().strftime("%Y-%m")

    if not invoice_path.exists():
        with open(invoice_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                "date", "month", "client",
                "total_leads", "price_per_lead", "total_amount_eur"
            ])

    with open(invoice_path, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            datetime.now().isoformat(),
            month,
            client,
            lead_count,
            price_per_lead,
            total
        ])

    return {
        "client": client,
        "month": month,
        "leads": lead_count,
        "amount_eur": total
    }