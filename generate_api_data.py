import sqlite3
import random
from datetime import datetime, timedelta
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "db" / "meta_ads.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS ad_accounts (account_id TEXT PRIMARY KEY, name TEXT, currency TEXT, account_status INTEGER, business_id TEXT, last_synced TIMESTAMP)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS campaign_insights (id INTEGER PRIMARY KEY AUTOINCREMENT, date TEXT, account_id TEXT, campaign_id TEXT, campaign_name TEXT, spend REAL, impressions INTEGER, clicks INTEGER, conversions INTEGER, cpa REAL, roas REAL, cpc REAL, cpm REAL, ctr REAL, frequency REAL, reach INTEGER, cost_per_result REAL, UNIQUE(date, campaign_id))''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS daily_account_spend (date TEXT, account_id TEXT, spend REAL, UNIQUE(date, account_id))''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS ad_sets (adset_id TEXT PRIMARY KEY, campaign_id TEXT, account_id TEXT, name TEXT, status TEXT)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS ads (ad_id TEXT PRIMARY KEY, adset_id TEXT, campaign_id TEXT, account_id TEXT, name TEXT, status TEXT, creative_id TEXT, preview_url TEXT)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS sync_log (id INTEGER PRIMARY KEY AUTOINCREMENT, sync_time TIMESTAMP, business_id TEXT, account_id TEXT, records_fetched INTEGER, errors TEXT)''')
    conn.commit()

def generate_data():
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    businesses = [
        ('B1', 'DeltaA'),
        ('B2', 'VNCreative'),
        ('B3', 'Đào tạo trực tuyến Fedu')
    ]

    accounts = [
        ('ACT1', 'DeltaA Ad 1', 'VND', 1, 'B1'),
        ('ACT2', 'DeltaA Ad 2', 'VND', 1, 'B1'),
        ('ACT3', 'VNC Ad 1', 'VND', 1, 'B2'),
        ('ACT4', 'Fedu Ad 1', 'VND', 1, 'B3'),
    ]

    for a in accounts:
        cursor.execute("INSERT OR IGNORE INTO ad_accounts VALUES (?, ?, ?, ?, ?, ?)", (*a, datetime.now().isoformat()))

    campaign_names = [
        "Chạy tương tác bài viết", "Chạy chuyển đổi web khóa học",
        "Lead form - tư vấn offline", "Video views", "Tin nhắn Fanpage"
    ]

    now = datetime.now()
    for i in range(50):
        date = (now - timedelta(days=random.randint(0, 30))).strftime("%Y-%m-%d")
        act = random.choice(accounts)[0]
        camp_id = f"CAMP{i}"
        name = random.choice(campaign_names) + f" {i}"
        spend = random.randint(50000, 2000000)
        cpa = random.randint(15000, 200000)
        conversions = int(spend / cpa)
        impressions = spend * 2
        clicks = int(impressions * 0.05)
        
        cursor.execute('''
        INSERT OR REPLACE INTO campaign_insights 
        (date, account_id, campaign_id, campaign_name, spend, impressions, clicks, conversions, cpa, roas, cpc, cpm, ctr, frequency, reach, cost_per_result)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (date, act, camp_id, name, spend, impressions, clicks, conversions, cpa, 0.0, spend/clicks if clicks else 0, spend/impressions*1000 if impressions else 0, clicks/impressions if impressions else 0, 1.5, int(impressions/1.5), cpa))
        
        cursor.execute("INSERT OR IGNORE INTO daily_account_spend (date, account_id, spend) VALUES (?, ?, ?)", (date, act, spend))

    conn.commit()
    print("Generated >= 50 mock campaigns!")

if __name__ == '__main__':
    generate_data()
