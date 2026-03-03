#!/bin/bash
set -e

echo "=== EchoMap Analytics ==="
echo "PRODUCTION=${PRODUCTION:-false}"

# Preload cache in background so Streamlit can listen on 8501 immediately (avoids proxy killing container)
echo "Preloading cache from PostGIS (background)..."
python scripts/preload_cache.py >> /var/log/preload.log 2>&1 &

# Cron to refresh cache every 5 minutes
echo "*/5 * * * * cd /app && python scripts/preload_cache.py >> /var/log/preload.log 2>&1" | crontab -
cron

echo "Starting Streamlit..."
exec streamlit run dashboard/app.py \
    --server.port=8501 \
    --server.address=0.0.0.0 \
    --server.headless=true \
    --browser.gatherUsageStats=false
