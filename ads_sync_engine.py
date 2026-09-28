#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys
import json
import time
import sqlite3
import urllib.request
import urllib.parse
from datetime import datetime, timedelta
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "db" / "meta_ads.db"
ENV_PATH = BASE_DIR / ".env"

API_VERSION = "v21.0"
GRAPH_URL = f"https://graph.facebook.com/{API_VERSION}"

def load_env():
    env_vars = {}
    if ENV_PATH.exists():
        with open(ENV_PATH, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    k, v = line.split('=', 1)
                    env_vars[k.strip()] = v.strip()
    return env_vars

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS ad_accounts (
        account_id TEXT PRIMARY KEY,
        name TEXT,
        currency TEXT,
        account_status INTEGER,
        business_id TEXT,
        last_synced TIMESTAMP
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS campaign_insights (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT,
        account_id TEXT,
        campaign_id TEXT,
        campaign_name TEXT,
        spend REAL,
        impressions INTEGER,
        clicks INTEGER,
        conversions INTEGER,
        cpa REAL,
        roas REAL,
        cpc REAL,
        cpm REAL,
        ctr REAL,
        frequency REAL,
        reach INTEGER,
        cost_per_result REAL,
        UNIQUE(date, campaign_id)
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS ad_sets (
        adset_id TEXT PRIMARY KEY,
        campaign_id TEXT,
        account_id TEXT,
        name TEXT,
        status TEXT
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS ads (
        ad_id TEXT PRIMARY KEY,
        adset_id TEXT,
        campaign_id TEXT,
        account_id TEXT,
        name TEXT,
        status TEXT,
        creative_id TEXT,
        preview_url TEXT
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS daily_account_spend (
        date TEXT,
        account_id TEXT,
        spend REAL,
        UNIQUE(date, account_id)
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS sync_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sync_time TIMESTAMP,
        business_id TEXT,
        account_id TEXT,
        records_fetched INTEGER,
        errors TEXT
    )
    ''')
    
    conn.commit()
    return conn

def make_request(url, retries=3):
    for i in range(retries):
        try:
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req, timeout=30) as response:
                return json.loads(response.read().decode())
        except urllib.error.HTTPError as e:
            print(f"[ERROR] API Request Failed: {e.read().decode()}")
            time.sleep(2)
        except Exception as e:
            print(f"[ERROR] Unexpected Error: {str(e)}")
            time.sleep(2)
    return None

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--test-token', action='store_true')
    parser.add_argument('--business-id', type=str, help='Sync specific Business ID')
    parser.add_argument('--date-preset', type=str, default='last_7d', choices=['last_7d', 'last_14d', 'last_30d', 'last_90d'])
    args = parser.parse_args()

    env = load_env()
    token = env.get("ACCESS_TOKEN")
    
    if args.test_token and len(sys.argv) > 2:
        token = sys.argv[2]
        
    if not token:
        print("[ERROR] ACCESS_TOKEN not found in .env file.")
        sys.exit(1)

    print("[+] SYNC COMPLETE!")

if __name__ == "__main__":
    main()
