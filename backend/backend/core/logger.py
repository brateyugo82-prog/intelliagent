# Hinweis: Absolute Imports (backend.*) für Render + lokale Uvicorn-Kompatibilität
# Logging-Konfiguration für IntelliAgent Backend
# Hinweis: Render speichert stdout automatisch als Log. Ein Logfile ist nicht nötig.
# Vorteil: Kein FileNotFoundError, keine Abhängigkeit von backend/logs/.
# Lokal und in der Cloud identisches Verhalten.

import sys
import logging

logging.basicConfig(
    stream=sys.stdout,
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger("backend")
