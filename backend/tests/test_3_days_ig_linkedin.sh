#!/bin/bash

# --------------------------------------
# FIX: Projekt-Root sauber setzen
# --------------------------------------
PROJECT_ROOT="$(cd "$(dirname "$0")" && pwd)"
export PYTHONPATH="$PROJECT_ROOT"

echo "🚀 START 3-DAY IMAGE ROTATION TEST (IG + LINKEDIN)"
echo "--------------------------------------------------"
echo "📁 PROJECT_ROOT=$PROJECT_ROOT"
echo "🐍 PYTHONPATH=$PYTHONPATH"

CLIENT="mtm_client"
PLATFORMS=("instagram" "linkedin")

for DAY in 1 2 3; do
  echo ""
  echo "🟢 DAY $DAY"

  for PLATFORM in "${PLATFORMS[@]}"; do
    echo "   ▶ $PLATFORM"
    python -m backend.master_agent.master "$CLIENT" "$PLATFORM"
  done
done

echo ""
echo "✅ TEST DONE"
echo "📁 CHECK OUTPUT:"
echo "clients/mtm_client/output/preview"