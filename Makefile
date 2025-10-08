# Makefile für IntelliAgent

setup: ## Erstellt Grundstruktur und Dummy-Files
	@echo "[Setup] Erstelle Grundstruktur und Dummy-Files..."
	@mkdir -p backend/clients/example_client/output
	@mkdir -p backend/clients/example_client/assets
	@touch backend/clients/example_client/.env
	@touch backend/clients/example_client/assets/.keep
	@touch backend/clients/example_client/output/.keep

frontend: ## Startet Next.js Dev-Server (legacy, nutze frontend-dev)
	cd frontend-app && npm run dev

backend: ## Startet FastAPI Dev-Server (legacy, nutze backend-dev)
	uvicorn backend.core.main:app --reload --port 8000

backend-dev: ## Startet das Backend im venv (empfohlen)
	@if [ ! -d backend/.venv ]; then \
	  echo "[ERROR] Virtuelle Umgebung nicht gefunden. Bitte zuerst 'python -m venv backend/.venv && source backend/.venv/bin/activate && pip install -r backend/requirements.txt' ausführen."; \
	  exit 1; \
	fi
	backend/.venv/bin/uvicorn backend.core.main:app --reload --port 8000

backend-alt: ## Startet das Backend im venv auf Port 8001
	@if [ ! -d backend/.venv ]; then \
	  echo "[ERROR] Virtuelle Umgebung nicht gefunden. Bitte zuerst 'python -m venv backend/.venv && source backend/.venv/bin/activate && pip install -r backend/requirements.txt' ausführen."; \
	  exit 1; \
	fi
	backend/.venv/bin/uvicorn backend.core.main:app --reload --port 8001

frontend-dev: ## Startet das Frontend mit Next.js
	cd frontend-app && npm run dev

dev: ## Startet Backend (im venv) und Frontend parallel (lokale Entwicklung)
	@if [ ! -d backend/.venv ]; then \
	  echo "[ERROR] Virtuelle Umgebung nicht gefunden. Bitte zuerst 'python -m venv backend/.venv && source backend/.venv/bin/activate && pip install -r backend/requirements.txt' ausführen."; \
	  exit 1; \
	fi
	backend/.venv/bin/uvicorn backend.core.main:app --reload --port 8000 & \
	cd frontend-app && npm run dev & \
	wait

backend-auto: ## Startet das Backend automatisch aus jedem Verzeichnis
	@if [ -d backend/core ]; then \
		echo "[INFO] Starte Backend aus Projektroot..."; \
		if [ ! -d backend/.venv ]; then \
			echo "[ERROR] Virtuelle Umgebung nicht gefunden. Bitte zuerst 'python -m venv backend/.venv && source backend/.venv/bin/activate && pip install -r backend/requirements.txt' ausführen."; \
			exit 1; \
		fi; \
		backend/.venv/bin/uvicorn backend.core.main:app --reload --port 8000; \
	elif [ -d core ]; then \
		echo "[INFO] Starte Backend aus backend/-Ordner..."; \
		if [ ! -d .venv ]; then \
			echo "[ERROR] Virtuelle Umgebung nicht gefunden. Bitte zuerst 'python -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt' ausführen."; \
			exit 1; \
		fi; \
		.venv/bin/uvicorn core.main:app --reload --port 8000; \
	else \
		echo "[ERROR] Konnte backend/core nicht finden."; \
		exit 1; \
	fi

frontend-auto: ## Startet das Frontend automatisch aus jedem Verzeichnis
	@if [ -f frontend-app/package.json ]; then \
		echo "[INFO] Starte Frontend aus Projektroot..."; \
		cd frontend-app && npm run dev; \
	elif [ -f package.json ]; then \
		echo "[INFO] Starte Frontend aus frontend_app/-Ordner..."; \
		npm run dev; \
	else \
		echo "[ERROR] Konnte frontend_app nicht finden."; \
		exit 1; \
	fi

dev-auto: ## Startet Backend und Frontend automatisch parallel (egal aus welchem Verzeichnis)
	$(MAKE) backend-auto & \
	$(MAKE) frontend-auto & \
	wait

stop: ## Beendet Backend- und Frontend-Dev-Server
	-pkill -f "uvicorn.*backend.core.main:app" || true
	-pkill -f "npm run dev" || true

kill-backend: ## Beendet alle Prozesse auf Port 8000
	-@lsof -ti :8000 | xargs kill -9 2>/dev/null || true

kill-frontend: ## Beendet alle Prozesse auf Port 3000
	-@lsof -ti :3000 | xargs kill -9 2>/dev/null || true

kill-all: ## Beendet alle Prozesse auf Port 8000 und 3000, gibt OK aus
	@$(MAKE) kill-backend
	@$(MAKE) kill-frontend
	@echo "[OK] Alle relevanten Ports freigegeben."

logs: ## Zeigt Info zu Backend-Logs (stdout)
	@echo "[INFO] Logs werden über stdout angezeigt (Render Dashboard oder lokal im Terminal)"

reset: ## Stoppt alle laufenden Server, killt Ports und startet dev neu
	@$(MAKE) stop
	@$(MAKE) kill-all
	@$(MAKE) dev
	@echo "[OK] Backend + Frontend neu gestartet."

test: ## Führt pytest im Backend aus
	cd backend && pytest

clean: ## Löscht Logs, Reports und Client-Outputs
	rm -rf logs/* reports/* backend/clients/*/output/*

lint: ## Prüft auf versehentlich getrackte ignorierte Dateien
	@echo "[Lint] Prüfe auf versehentlich getrackte ignorierte Dateien..."
	@if [ "$(shell git ls-files --ignored --exclude-standard)" != "" ]; then \
	  echo "[WARN] Ignorierte Dateien sind im Git-Index:"; \
	  git ls-files --ignored --exclude-standard; \
	  exit 1; \
	fi
	@if [ "$(shell git ls-files --others --exclude-standard)" != "" ]; then \
	  echo "[WARN] Nicht getrackte, aber ignorierte Dateien gefunden:"; \
	  git ls-files --others --exclude-standard; \
	  exit 1; \
	fi
	@echo "[OK] .gitignore greift sauber."

push: ## Commitet und pusht alle Änderungen (MESSAGE überschreibbar)
	@git add .
	@git commit -m "${MESSAGE}" || true
	@git push

# Standard-Commit-Message, falls keine MESSAGE übergeben wird
MESSAGE ?= chore: auto-push changes

help: ## Zeigt diese Hilfe an
	@grep -E '^[a-zA-Z_-]+:.*?## ' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "} {printf "\033[36m%-16s\033[0m %s\n", $$1, $$2}'
