import os
import sqlite3
import time
import requests
from dotenv import load_dotenv
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Load env
load_dotenv()
ACCESS_TOKEN = os.getenv('META_ACCESS_TOKEN', os.getenv('ACCESS_TOKEN'))
if not ACCESS_TOKEN:
    print("Error: ACCESS_TOKEN not found in .env")
    exit(1)

BUSINESS_IDS = [
    '302759613542558', # DeltaA
    '1924164801857576', # VNCreative
    '848852578616163' # Fedu (Academy)
]

BASE_URL = 'https://graph.facebook.com/v19.0'
DB_PATH = 'db/meta_ads.db'

# Setup session with retry
session = requests.Session()
retries = Retry(total=3, backoff_factor=1, status_forcelist=[ 500, 502, 503, 504, 429 ])
session.mount('https://', HTTPAdapter(max_retries=retries))

def init_db():
    os.makedirs('db', exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ad_accounts (
            account_id TEXT PRIMARY KEY,
            name TEXT,
            currency TEXT,
            account_status INTEGER,
            business_id TEXT,
            business_name TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS campaign_insights (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            account_id TEXT,
            campaign_id TEXT,
            campaign_name TEXT,
            campaign_status TEXT,
            spend REAL,
            impressions INTEGER,
            clicks INTEGER,
            conversions INTEGER,
            cpa REAL,
            cpc REAL,
            cpm REAL,
            reach INTEGER,
            frequency REAL,
            roas REAL
        )
    ''')
    
    # Clean old data
    cursor.execute('DELETE FROM ad_accounts')
    cursor.execute('DELETE FROM campaign_insights')
    conn.commit()
    return conn

def api_get(url, params=None):
    if params is None:
        params = {}
    params['access_token'] = ACCESS_TOKEN
    try:
        response = session.get(url, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"API Error: {e}")
        return None

def fetch_data(conn):
    cursor = conn.cursor()
    for b_id in BUSINESS_IDS:
        print(f"Fetching ad accounts for business {b_id}")
        url = f"{BASE_URL}/{b_id}/owned_ad_accounts"
        params = {'fields': 'id,name,currency,account_status,business_name'}
        
        has_next = True
        while has_next:
            data = api_get(url, params)
            if not data:
                break
                
            for acc in data.get('data', []):
                acc_status = acc.get('account_status')
                b_name = acc.get('business_name', 'Unknown')
                
                # Replace restricted words
                b_name = b_name.replace('Fedu', 'Academy').replace('FEDU', 'ACADEMY')
                acc_name = acc.get('name', 'Unknown').replace('Fedu', 'Academy').replace('FEDU', 'ACADEMY')
                
                cursor.execute('''
                    INSERT OR REPLACE INTO ad_accounts (account_id, name, currency, account_status, business_id, business_name)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (acc['id'], acc_name, acc.get('currency', 'USD'), acc_status, b_id, b_name))
                
                if acc_status == 1:
                    print(f"  Fetching insights for active account {acc_name} ({acc['id']})")
                    fetch_insights(conn, acc['id'])
            
            paging = data.get('paging', {})
            cursors = paging.get('cursors', {})
            if 'after' in cursors and 'next' in paging:
                params['after'] = cursors['after']
            else:
                has_next = False
    
    conn.commit()

def fetch_insights(conn, account_id):
    cursor = conn.cursor()
    url = f"{BASE_URL}/{account_id}/insights"
    params = {
        'level': 'campaign',
        'date_preset': 'last_90d',
        'time_increment': '1',
        'fields': 'campaign_id,campaign_name,spend,impressions,clicks,actions,purchase_roas,cpc,cpm,reach,frequency,date_start'
    }
    
    has_next = True
    while has_next:
        data = api_get(url, params)
        if not data:
            break
            
        for row in data.get('data', []):
            campaign_id = row.get('campaign_id')
            campaign_name = row.get('campaign_name', 'Unknown').replace('Fedu', 'Academy').replace('FEDU', 'ACADEMY')
            spend = float(row.get('spend', 0))
            impressions = int(row.get('impressions', 0))
            clicks = int(row.get('clicks', 0))
            reach = int(row.get('reach', 0))
            frequency = float(row.get('frequency', 0))
            cpc = float(row.get('cpc', 0))
            cpm = float(row.get('cpm', 0))
            date = row.get('date_start')
            
            conversions = 0
            roas = 0.0
            
            for action in row.get('actions', []):
                if action.get('action_type') == 'purchase':
                    conversions += int(action.get('value', 0))
            
            for roas_item in row.get('purchase_roas', []):
                if roas_item.get('action_type') == 'purchase':
                    roas = float(roas_item.get('value', 0))
            
            cpa = spend / conversions if conversions > 0 else 0.0
            
            cursor.execute('''
                INSERT INTO campaign_insights (
                    date, account_id, campaign_id, campaign_name, campaign_status, 
                    spend, impressions, clicks, conversions, cpa, cpc, cpm, reach, frequency, roas
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                date, account_id, campaign_id, campaign_name, 'ACTIVE', 
                spend, impressions, clicks, conversions, cpa, cpc, cpm, reach, frequency, roas
            ))
            
        paging = data.get('paging', {})
        cursors = paging.get('cursors', {})
        if 'after' in cursors and 'next' in paging:
            params['after'] = cursors['after']
        else:
            has_next = False
    
    conn.commit()

def main():
    print("Starting sync...")
    conn = init_db()
    fetch_data(conn)
    
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM ad_accounts')
    acc_count = cursor.fetchone()[0]
    cursor.execute('SELECT COUNT(*) FROM campaign_insights')
    ins_count = cursor.fetchone()[0]
    
    print(f"Sync complete. Accounts: {acc_count}, Insights records: {ins_count}")
    conn.close()

if __name__ == '__main__':
    main()
