#!/bin/bash

CLIENT="mtm_client"
DAYS=("default" "default" "default")

echo "🚀 START 3-DAY CONTENT PREVIEW"
echo "--------------------------------"

for i in "${!DAYS[@]}"; do
  DAY=$((i+1))
  CONTEXT="${DAYS[$i]}"

  echo ""
  echo "🟢 DAY $DAY | CONTEXT: $CONTEXT"

  python -m backend.master_agent.master "$CLIENT"
done

echo ""
echo "✅ TEST DONE"
echo "📁 CHECK:"
echo "clients/$CLIENT/output/preview"