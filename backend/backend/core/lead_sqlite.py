import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
DB_PATH = BASE_DIR / "db" / "leads.sqlite"


def get_leads_sqlite(client: str | None = None, status: str | None = None):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    query = "SELECT * FROM leads"
    params = []
    where = []

    if client:
        where.append("client = ?")
        params.append(client)

    if status:
        where.append("status = ?")
        params.append(status)

    if where:
        query += " WHERE " + " AND ".join(where)

    query += " ORDER BY created_at DESC"

    cur.execute(query, params)
    rows = cur.fetchall()
    conn.close()

    return [dict(r) for r in rows]
