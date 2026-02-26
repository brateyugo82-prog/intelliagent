#!/bin/bash

echo "🚀 WEEKLY CONTENT PREVIEW TEST (NO POSTING)"
echo "------------------------------------------"

CLIENT="mtm_client"
PLATFORMS=("instagram" "facebook" "linkedin" "tiktok")

# Reihenfolge der Bild-Kategorien pro Tag (frei anpassbar)
DAYS=(
  "default"
  "handwerk"
  "handwerk"
  "default"
  "handwerk"
  "default"
  "default"
)

for i in "${!DAYS[@]}"; do
  DAY_NUM=$((i+1))
  CATEGORY="${DAYS[$i]}"

  echo ""
  echo "🟢 DAY $DAY_NUM | CATEGORY: $CATEGORY"
  echo "----------------------------------"

  for PLATFORM in "${PLATFORMS[@]}"; do
    echo "   ▶ $PLATFORM"
    python -m backend.master_agent.master "$CLIENT" "$PLATFORM"
  done

  echo "   📁 Bild wird danach automatisch nach /used verschoben"
done

echo ""
echo "✅ WEEK PREVIEW DONE"
echo "📁 CHECK:"
echo "clients/$CLIENT/output/preview"