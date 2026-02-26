#!/bin/bash

echo "🚀 START 3-DAY FULL PLATFORM PREVIEW TEST"
echo "-----------------------------------------"

CLIENT="mtm_client"
DAYS=("default" "handwerk" "service")
PLATFORMS=("instagram" "facebook" "linkedin")

for DAY in "${!DAYS[@]}"; do
  CATEGORY="${DAYS[$DAY]}"
  echo ""
  echo "🟢 DAY $((DAY+1)) | CATEGORY: $CATEGORY"

  for PLATFORM in "${PLATFORMS[@]}"; do
    echo "   ▶ $PLATFORM"
    python -m backend.master_agent.master "$CLIENT" "$PLATFORM" \
      --image_context "$CATEGORY"
  done
done

echo ""
echo "✅ TEST DONE"
echo "📁 CHECK OUTPUT:"
echo "clients/$CLIENT/output/preview"
