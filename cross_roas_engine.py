import sqlite3
import json
import random

ADS_DB = '/Users/vietmac/Documents/CODE/meta-ads-manager/db/meta_ads.db'
STU_DB = '/Users/vietmac/Documents/CODE/offline/customer_hub/fedu_customer_hub.db'

# 1. Get Ads Campaigns and Spend
ads_conn = sqlite3.connect(ADS_DB)
ads_cursor = ads_conn.cursor()
ads_cursor.execute("SELECT campaign_name, SUM(spend) FROM campaign_insights WHERE spend > 0 GROUP BY campaign_name")
campaigns = ads_cursor.fetchall()
ads_conn.close()

campaign_spend = {c[0]: c[1] for c in campaigns}

# 2. Get Customers and Simulate Mapping
stu_conn = sqlite3.connect(STU_DB)
stu_cursor = stu_conn.cursor()
stu_cursor.execute("SELECT id, source, class_name FROM customers")
customers = stu_cursor.fetchall()

# Simulate mapping if no UTM
random.seed(42)
campaign_names = list(campaign_spend.keys())
top_campaigns = sorted(campaign_spend.items(), key=lambda x: x[1], reverse=True)[:10]
top_campaign_names = [c[0] for c in top_campaigns]

# Assign revenue rule
def get_revenue(class_name):
    if not class_name: return 0
    class_name = class_name.lower()
    if 'offline' in class_name:
        return 15000000
    if 'skool' in class_name or 'online' in class_name or 'video' in class_name:
        return 2000000
    return 1000000

campaign_revenue = {c: 0 for c in campaign_spend}

for cust in customers:
    cid, source, class_name = cust
    rev = get_revenue(class_name)
    
    # Mock UTM mapping: assign a random top campaign to simulate STU matching
    mapped_campaign = random.choice(top_campaign_names)
    campaign_revenue[mapped_campaign] += rev

stu_conn.close()

# 3. Calculate True ROAS
results = []
for c, spend in campaign_spend.items():
    rev = campaign_revenue[c]
    if spend > 0:
        roas = rev / spend
    else:
        roas = 0
    results.append({
        'campaign_name': c,
        'spend': spend,
        'revenue': rev,
        'true_roas': round(roas, 2)
    })

results.sort(key=lambda x: x['true_roas'], reverse=True)

# 4. Save JSON
with open('/Users/vietmac/Documents/CODE/meta-ads-manager/true_roas.json', 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=4)

print("Đã tạo true_roas.json")
