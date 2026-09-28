#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
META ADS SYNC ENGINE
Tự động đồng bộ dữ liệu tài khoản quảng cáo và insights từ Meta Graph API
"""

import os
import sys
import json
import sqlite3
import urllib.request
import urllib.parse
from datetime import datetime, timedelta
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "db" / "meta_ads.db"
ENV_PATH = BASE_DIR / ".env"

API_VERSION = "v18.0"
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
        UNIQUE(date, campaign_id)
    )
    ''')
    
    conn.commit()
    return conn

def make_request(url):
    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode())
    except urllib.error.HTTPError as e:
        print(f"[ERROR] API Request Failed: {e.read().decode()}")
        return None
    except Exception as e:
        print(f"[ERROR] Unexpected Error: {str(e)}")
        return None

def sync_businesses(token):
    print("[-] Fetching Meta Businesses...")
    url = f"{GRAPH_URL}/me/businesses?access_token={token}&fields=id,name"
    data = make_request(url)
    if not data or 'data' not in data:
        return []
    return data['data']

def sync_ad_accounts(token, business_id, conn):
    print(f"[-] Fetching Ad Accounts for Business {business_id}...")
    url = f"{GRAPH_URL}/{business_id}/client_ad_accounts?access_token={token}&fields=id,name,currency,account_status,business&limit=100"
    data = make_request(url)
    if not data or 'data' not in data:
        return []
    
    accounts = data['data']
    cursor = conn.cursor()
    now = datetime.now().isoformat()
    
    for act in accounts:
        act_id = act.get('id', '').replace('act_', '')
        cursor.execute('''
        INSERT INTO ad_accounts (account_id, name, currency, account_status, business_id, last_synced)
        VALUES (?, ?, ?, ?, ?, ?)
        ON CONFLICT(account_id) DO UPDATE SET
            name=excluded.name,
            account_status=excluded.account_status,
            last_synced=excluded.last_synced
        ''', (
            act_id, act.get('name', 'Unknown'), act.get('currency', 'VND'),
            act.get('account_status', 1), business_id, now
        ))
    conn.commit()
    return accounts

def sync_insights(token, account_id, conn):
    # Lấy dữ liệu 7 ngày gần nhất
    print(f"[-] Fetching Insights for Account {account_id}...")
    url = f"{GRAPH_URL}/act_{account_id}/insights?access_token={token}&fields=campaign_id,campaign_name,spend,impressions,clicks,actions,purchase_roas,date_start&date_preset=last_7d&level=campaign&limit=100"
    
    data = make_request(url)
    if not data or 'data' not in data:
        return
        
    insights = data['data']
    cursor = conn.cursor()
    
    for row in insights:
        spend = float(row.get('spend', 0))
        if spend == 0:
            continue
            
        conversions = 0
        actions = row.get('actions', [])
        for action in actions:
            if action.get('action_type') in ['lead', 'purchase', 'onsite_conversion.lead_grouped']:
                conversions += int(action.get('value', 0))
                
        cpa = spend / conversions if conversions > 0 else spend
        
        roas = 0.0
        purchase_roas = row.get('purchase_roas', [])
        for pr in purchase_roas:
            if pr.get('action_type') == 'omni_purchase':
                roas = float(pr.get('value', 0))
        
        cursor.execute('''
        INSERT INTO campaign_insights (date, account_id, campaign_id, campaign_name, spend, impressions, clicks, conversions, cpa, roas)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(date, campaign_id) DO UPDATE SET
            spend=excluded.spend,
            impressions=excluded.impressions,
            clicks=excluded.clicks,
            conversions=excluded.conversions,
            cpa=excluded.cpa,
            roas=excluded.roas
        ''', (
            row.get('date_start'),
            account_id,
            row.get('campaign_id'),
            row.get('campaign_name'),
            spend,
            int(row.get('impressions', 0)),
            int(row.get('clicks', 0)),
            conversions,
            cpa,
            roas
        ))
    conn.commit()

def main():
    env = load_env()
    token = env.get("ACCESS_TOKEN")
    
    if '--test-token' in sys.argv:
        if len(sys.argv) > 2:
            token = sys.argv[2]
        
    if not token:
        print("[ERROR] ACCESS_TOKEN not found in .env file.")
        print("Please create a .env file with ACCESS_TOKEN=your_token_here")
        sys.exit(1)
        
    conn = init_db()
    businesses = sync_businesses(token)
    
    for b in businesses:
        b_id = b['id']
        b_name = b['name']
        print(f"\n[+] Processing Business: {b_name} ({b_id})")
        accounts = sync_ad_accounts(token, b_id, conn)
        print(f"    Found {len(accounts)} ad accounts.")
        
        for act in accounts:
            act_id = act.get('id', '').replace('act_', '')
            sync_insights(token, act_id, conn)
            
    print("\n[+] SYNC COMPLETE!")

if __name__ == "__main__":
    main()
