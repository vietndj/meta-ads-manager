import json

with open('/Users/vietmac/Documents/CODE/meta-ads-manager/true_roas.json', 'r', encoding='utf-8') as f:
    results = json.load(f)

# Phân loại
lai_dam = [c for c in results if c['true_roas'] >= 1.5 and c['revenue'] > 0]
lead_rac = [c for c in results if c['true_roas'] < 1.5 and c['spend'] > 500000]

def format_currency(value):
    return f"{int(value):,} ₫"

def generate_table_rows(campaigns):
    rows = ""
    for i, c in enumerate(campaigns):
        row_class = "zebra-row" if i % 2 == 1 else "white-row"
        rows += f"""
        <tr class="{row_class}">
            <td style="padding: 12px; border-bottom: 1px solid #e2e8f0; font-weight: 500;">{c['campaign_name']}</td>
            <td style="padding: 12px; border-bottom: 1px solid #e2e8f0; color: #ef4444;">{format_currency(c['spend'])}</td>
            <td style="padding: 12px; border-bottom: 1px solid #e2e8f0; color: #10b981; font-weight: 600;">{format_currency(c['revenue'])}</td>
            <td style="padding: 12px; border-bottom: 1px solid #e2e8f0; font-weight: bold; text-align: right;">{c['true_roas']}</td>
        </tr>
        """
    return rows

html_content = f"""<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Hệ Thống Đối Soát True ROAS - VIDEO SYSTEM</title>
    <style>
        :root {{
            --bg: #f8fafc;
            --text: #1e293b;
            --border: #e2e8f0;
            --white: #ffffff;
        }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            background-color: var(--bg);
            color: var(--text);
            line-height: 1.6;
            margin: 0;
            padding: 40px 20px;
        }}
        .container {{
            max-width: 960px;
            margin: 0 auto;
        }}
        .badge {{
            display: inline-block;
            padding: 4px 12px;
            background: #0f172a;
            color: white;
            border-radius: 999px;
            font-size: 12px;
            font-weight: bold;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 16px;
        }}
        h1 {{
            font-size: 32px;
            margin: 0 0 40px 0;
            line-height: 1.2;
            letter-spacing: -1px;
        }}
        .section {{
            background: var(--white);
            border-radius: 12px;
            padding: 24px;
            margin-bottom: 40px;
            box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);
            border: 1px solid var(--border);
        }}
        h2.green {{ color: #059669; border-bottom: 2px solid #34d399; padding-bottom: 10px; margin-top: 0; }}
        h2.red {{ color: #dc2626; border-bottom: 2px solid #f87171; padding-bottom: 10px; margin-top: 0; }}
        table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 14px;
        }}
        th {{
            text-align: left;
            padding: 12px;
            border-bottom: 2px solid #cbd5e1;
            color: #64748b;
            font-weight: 600;
        }}
        th.right {{ text-align: right; }}
        .zebra-row {{ background-color: #f8fafc; }}
        .white-row {{ background-color: #ffffff; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="badge">VIDEO SYSTEM - REPORT</div>
        <h1>Đối Soát True ROAS<br>Giữa ADS & STU</h1>

        <div class="section">
            <h2 class="green">🚀 CHIẾN DỊCH LÃI ĐẬM (NÊN VÍT GA)</h2>
            <table>
                <thead>
                    <tr>
                        <th>Tên Chiến Dịch</th>
                        <th>Đã Chi Tiêu (ADS)</th>
                        <th>Thu Về (STU)</th>
                        <th class="right">True ROAS</th>
                    </tr>
                </thead>
                <tbody>
                    {generate_table_rows(lai_dam)}
                </tbody>
            </table>
        </div>

        <div class="section">
            <h2 class="red">❌ CHIẾN DỊCH LEAD RÁC (CẦN TẮT)</h2>
            <table>
                <thead>
                    <tr>
                        <th>Tên Chiến Dịch</th>
                        <th>Đã Chi Tiêu (ADS)</th>
                        <th>Thu Về (STU)</th>
                        <th class="right">True ROAS</th>
                    </tr>
                </thead>
                <tbody>
                    {generate_table_rows(lead_rac)}
                </tbody>
            </table>
        </div>
    </div>
</body>
</html>
"""

with open('/Users/vietmac/Documents/CODE/meta-ads-manager/true_roas_report.html', 'w', encoding='utf-8') as f:
    f.write(html_content)

print("Đã tạo true_roas_report.html")
