import sqlite3
import json
import os

DB_PATH = 'db/meta_ads.db'
OUT_PATH = 'dist/data.json'

def export():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Campaigns
    cursor.execute('''
        SELECT campaign_id, campaign_name, SUM(spend), SUM(impressions), 
               SUM(clicks), SUM(conversions), SUM(reach), MAX(date)
        FROM campaign_insights
        GROUP BY campaign_id, campaign_name
    ''')
    campaigns = []
    total_spend = 0
    total_conv = 0
    
    for row in cursor.fetchall():
        spend = row[2] or 0
        conv = row[5] or 0
        cpa = spend / conv if conv > 0 else 0
        
        campaigns.append({
            'id': row[0],
            'name': row[1].replace('Fedu', 'Academy').replace('FEDU', 'ACADEMY'),
            'spend': spend,
            'impressions': row[3] or 0,
            'clicks': row[4] or 0,
            'conversions': conv,
            'cpa': cpa,
            'roas': 0 # simplify for export
        })
        total_spend += spend
        total_conv += conv
        
    avg_cpa = total_spend / total_conv if total_conv > 0 else 0
    
    # Daily spend
    cursor.execute('''
        SELECT date, SUM(spend)
        FROM campaign_insights
        GROUP BY date
        ORDER BY date
    ''')
    daily_spend = []
    for row in cursor.fetchall():
        if row[0]:
            daily_spend.append({
                'date': row[0],
                'spend': row[1] or 0
            })
            
    from datetime import datetime
    data = {
        'updated_at': datetime.now().isoformat(),
        'summary': {
            'total_spend': total_spend,
            'total_conversions': total_conv,
            'avg_cpa': avg_cpa
        },
        'campaigns': campaigns,
        'daily_spend': daily_spend
    }
    
    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        
    print(f"Exported to {OUT_PATH}")

if __name__ == '__main__':
    export()
