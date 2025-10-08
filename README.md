# Multi-Agenten-Architektur

## Projektstruktur

```
Agenten/
├── backend/
│   ├── agents/
│   │   ├── content_agent/
│   │   ├── design_agent/
│   │   ├── publish_agent/
│   │   ├── analytics_agent/
│   │   └── communication_agent/
│   ├── clients/
│   │   └── example_client/
│   │       ├── config.json
│   │       └── output/
│   ├── logs/
│   ├── reports/
│   ├── tests/
│   ├── main.py
│   ├── master_agent.py
│   ├── requirements.txt
│   ├── render.yaml
│   └── .env.example
├── frontend-app/
│   ├── pages/
│   │   └── index.js
│   ├── vercel.json
│   ├── .env.example
│   └── README.md
└── README.md
```

## Backend (FastAPI, Render)
- Starte lokal:
  ```bash
  cd backend
  python3 -m venv .venv && source .venv/bin/activate
  pip install -r requirements.txt
  uvicorn main:app --reload
  ```
- Deployment: Siehe `render.yaml` (Starter Plan, Python, FastAPI)
- `.env` für API-Keys/Secrets anlegen (siehe `.env.example`)
- Jeder Agent autark, orchestriert durch `master_agent.py`
- Clients: `backend/clients/<client_name>/config.json` und `output/`
- Logs: `backend/logs/`, Reports: `backend/reports/`
- Tests: `pytest backend/tests/`

## Frontend (Next.js, Vercel)
- Starte lokal:
  ```bash
  cd frontend-app
  npm install
  npm run dev
  ```
- Deployment: Siehe `vercel.json`
- `.env` für Backend-URL anlegen (siehe `.env.example`)
- `.env.local` im Frontend (`frontend-app/.env.local`) für die Backend-URL (z. B. lokal: `http://localhost:8000`, auf Vercel: Render-URL).
- Jeder Kunde hat in `backend/clients/<client_name>/` eine eigene `.env` Datei für API-Keys (z. B. `OPENAI_API_KEY`, `INSTAGRAM_API_KEY`, ...).
- Kundenspezifische Dateien (z. B. Logo, Label, Templates) kommen in `backend/clients/<client_name>/assets/`.
- Die .env Variablen und Assets werden beim Workflow-Start automatisch geladen und sind für alle Agents verfügbar.
- UI: Button „Workflow starten“ → POST an `${NEXT_PUBLIC_BACKEND_URL}/workflow/start`
- Ergebnis wird angezeigt

## Lokaler Start

- Backend starten:
  ```bash
  make backend
  ```
- Frontend starten:
  ```bash
  make frontend
  ```

## Makefile-Befehle
- `make setup` – Erstellt Grundstruktur und Dummy-Files
- `make backend` – Startet FastAPI Dev-Server
- `make frontend` – Startet Next.js Dev-Server
- `make test` – Führt pytest im Backend aus
- `make clean` – Löscht Logs, Reports und Client-Outputs
- `make lint` – Überprüft auf ignorierte Dateien im Git-Index oder als untracked

## Makefile-Targets für lokale Entwicklung
- `make backend-dev` – Startet das Backend im venv (Port 8000)
- `make frontend-dev` – Startet das Frontend (Port 3000)
- `make dev` – Startet Backend und Frontend parallel (beide im Vordergrund, ideal für lokale Entwicklung)
- `make stop` – Beendet beide Dev-Server (uvicorn und npm run dev)

> Für lokale Entwicklung reicht meist:
> ```bash
> make dev
> ```
> und zum Beenden:
> ```bash
> make stop
> ```

- `make help` zeigt alle verfügbaren Targets und deren Beschreibung an.

## .env pro Client
- Jeder Client in `backend/clients/<client_name>/` hat eine `.env` für API-Keys und einen `assets/`-Ordner für kundenspezifische Dateien.
- Die Variablen werden beim Workflow-Start automatisch geladen.

## Hinweise
- Logging, Fehlerbehandlung und Docstrings in allen Agents
- Unit Tests prüfen Dict/JSON-Ausgabe aller Agents
- Reports/Logs werden im Backend abgelegt

## Git & .gitignore
- Die `.gitignore` ist so konfiguriert, dass keine sensiblen Dateien (z. B. `.env`, Kunden-Assets, Outputs, Logs) ins Repository gelangen.
- Mit `make lint` kannst du prüfen, ob versehentlich ignorierte Dateien im Git-Index oder als untracked vorliegen:

```bash
make lint
```

Bei Problemen erscheint eine Warnung im Terminal.

## Kundenstruktur anlegen

Jeder Kunde liegt in `backend/clients/<client_name>/` und hat:
- `config.json` (Konfiguration, z. B. `{}`)
- `.env` (API Keys, Secrets, Platzhalter)
- `assets/` (für kundenspezifische Dateien wie Logos, Labels, Templates)
- `output/` (für Ergebnisse)

Beispiel für einen neuen Kunden:

```
backend/clients/kundeX/
├── config.json
├── .env
├── output/
└── assets/
```

Dupliziere einfach den Ordner `template_client` als Vorlage für neue Kunden.

## Workflow für einen bestimmten Kunden starten

```bash
python backend/master_agent/master.py <client_name>
```

Das Ergebnis landet in `backend/clients/<client_name>/output/workflow_result.json`.

## Client-Konfiguration: config.json
Jeder Client benötigt eine `config.json` mit folgendem Aufbau:

```
{
  "name": "kunde1",
  "api_keys": {
    "OPENAI_API_KEY": "",
    "INSTAGRAM_API_KEY": "",
    "FACEBOOK_API_KEY": "",
    "LINKEDIN_API_KEY": "",
    "TIKTOK_API_KEY": ""
  },
  "topic": "Social Media Marketing"
}
```

- Das Feld `topic` ist Pflicht und wird beim Workflow-Start geloggt und im Ergebnis zurückgegeben.
- Beispiel siehe `backend/clients/template_client/config.json`.
