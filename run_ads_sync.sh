#!/bin/bash
# META ADS AUTOMATION SCRIPT

cd "$(dirname "$0")"

echo "======================================"
echo "META ADS SYNC - $(date)"
echo "======================================"

# Chạy đồng bộ dữ liệu API
python3 ads_sync_engine.py

# Xuất Dashboard HTML
python3 dashboard_builder.py

echo "Done!"
echo "======================================"
