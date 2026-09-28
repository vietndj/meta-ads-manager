#!/bin/bash
cd "$(dirname "$0")"
python3 ads_sync_engine.py
python3 build_dashboard.py
./deploy.sh
