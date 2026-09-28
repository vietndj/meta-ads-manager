#!/bin/bash
cd "$(dirname "$0")"
python3 export_json.py
wrangler pages deploy dist/ --project-name=ads-fedu-vn
echo "[+] Deployed to https://ads.fedu.vn"
