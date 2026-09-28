import sqlite3
import json
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "db" / "meta_ads.db"

def export():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    data = {
        "updated_at": datetime.now().isoformat(),
        "businesses": [],
        "accounts": [dict(r) for r in cursor.execute("SELECT * FROM ad_accounts").fetchall()],
        "campaigns": [dict(r) for r in cursor.execute("SELECT * FROM campaign_insights").fetchall()],
        "daily_spend": [dict(r) for r in cursor.execute("SELECT * FROM daily_account_spend").fetchall()],
        "summary": {}
    }
    
    total_spend = sum(c['spend'] for c in data['campaigns'])
    total_conversions = sum(c['conversions'] for c in data['campaigns'])
    data['summary']['total_spend'] = total_spend
    data['summary']['total_conversions'] = total_conversions
    data['summary']['avg_cpa'] = total_spend / total_conversions if total_conversions > 0 else 0
    
    with open(BASE_DIR / "dist" / "data.json", "w") as f:
        json.dump(data, f)
        
    print("Exported data.json")

if __name__ == '__main__':
    export()
