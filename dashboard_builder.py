#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
META ADS DASHBOARD BUILDER
Tạo trang báo cáo tĩnh HTML từ SQLite (Zebra Striping, No-Line, High Density UI)
"""

import sqlite3
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "db" / "meta_ads.db"
OUTPUT_HTML = BASE_DIR / "ads-dashboard.html"

# Ngưỡng CPA cảnh báo (Ví dụ: CPA > 50,000 VND)
CPA_ALERT_THRESHOLD = 50000

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Meta Ads Dashboard</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
        body { font-family: 'Inter', sans-serif; background-color: #f8fafc; color: #1e293b; margin: 0; padding: 20px; }
        .table-container { background: white; border-radius: 12px; box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1); overflow: hidden; }
        table { width: 100%; border-collapse: collapse; text-align: left; }
        th { background: #0f172a; color: white; padding: 12px 16px; font-weight: 600; text-transform: uppercase; font-size: 0.75rem; letter-spacing: 0.05em; }
        td { padding: 12px 16px; border-bottom: 1px solid #e2e8f0; font-size: 0.875rem; }
        tr:nth-child(even) { background-color: #f1f5f9; } /* Zebra striping */
        tr:hover { background-color: #e2e8f0; }
        .alert-row td { background-color: #fee2e2 !important; color: #991b1b; }
        .alert-badge { background: #ef4444; color: white; padding: 2px 8px; border-radius: 999px; font-size: 0.7rem; font-weight: bold; }
        .success-badge { background: #22c55e; color: white; padding: 2px 8px; border-radius: 999px; font-size: 0.7rem; font-weight: bold; }
        
        .header-panel { display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px; }
        .metric-card { background: white; padding: 20px; border-radius: 12px; box-shadow: 0 2px 4px rgb(0 0 0 / 0.05); flex: 1; margin: 0 10px; text-align: center; }
        .metric-card:first-child { margin-left: 0; }
        .metric-card:last-child { margin-right: 0; }
        .metric-value { font-size: 1.5rem; font-weight: 700; color: #0f172a; margin-top: 8px; }
    </style>
</head>
<body>
    <div class="max-w-7xl mx-auto">
        <div class="header-panel">
            <div>
                <h1 class="text-3xl font-bold tracking-tight text-slate-900">Chiến dịch Meta Ads</h1>
                <p class="text-sm text-slate-500 mt-1">Cập nhật lúc: {update_time}</p>
            </div>
            <div>
                <span class="bg-slate-200 text-slate-700 px-3 py-1 rounded-full text-sm font-semibold">Tài khoản DeltaA & Các TK khác</span>
            </div>
        </div>

        <div class="flex mb-8">
            <div class="metric-card">
                <div class="text-sm text-slate-500 font-semibold uppercase">Tổng Chi Phí (7 Ngày)</div>
                <div class="metric-value">{total_spend:,} ₫</div>
            </div>
            <div class="metric-card">
                <div class="text-sm text-slate-500 font-semibold uppercase">Tổng Chuyển Đổi (Leads)</div>
                <div class="metric-value">{total_conversions:,}</div>
            </div>
            <div class="metric-card">
                <div class="text-sm text-slate-500 font-semibold uppercase">CPA Trung Bình</div>
                <div class="metric-value">{avg_cpa:,} ₫</div>
            </div>
        </div>

        <h2 class="text-xl font-bold mb-4 text-slate-800">Hiệu suất Chiến dịch (Sắp xếp theo chi phí)</h2>
        <div class="table-container">
            <table>
                <thead>
                    <tr>
                        <th>Tên Chiến Dịch</th>
                        <th>Ngày</th>
                        <th>Chi Phí (VND)</th>
                        <th>Lượt Hiển Thị</th>
                        <th>Chuyển Đổi</th>
                        <th>CPA (VND)</th>
                        <th>Trạng Thái</th>
                    </tr>
                </thead>
                <tbody>
                    {table_rows}
                </tbody>
            </table>
        </div>
    </div>
</body>
</html>
"""

def format_currency(value):
    return "{:,.0f}".format(value).replace(',', '.')

def build_dashboard():
    if not DB_PATH.exists():
        print("[ERROR] Database not found. Run sync engine first.")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Tính tổng quan
    cursor.execute("SELECT SUM(spend), SUM(conversions) FROM campaign_insights")
    row = cursor.fetchone()
    total_spend = row[0] or 0
    total_conversions = row[1] or 0
    avg_cpa = total_spend / total_conversions if total_conversions > 0 else 0
    
    # Lấy danh sách chiến dịch (gom nhóm theo ngày)
    cursor.execute('''
        SELECT campaign_name, date, spend, impressions, conversions, cpa 
        FROM campaign_insights 
        ORDER BY date DESC, spend DESC 
        LIMIT 100
    ''')
    
    rows_html = ""
    for r in cursor.fetchall():
        name, date, spend, imp, conv, cpa = r
        
        is_alert = cpa > CPA_ALERT_THRESHOLD and conv > 0
        is_warning = conv == 0 and spend > CPA_ALERT_THRESHOLD
        
        row_class = "alert-row" if is_alert or is_warning else ""
        
        if is_alert or is_warning:
            status_badge = '<span class="alert-badge">ĐẮT / ĐỐT TIỀN</span>'
        elif conv > 0 and cpa <= CPA_ALERT_THRESHOLD:
            status_badge = '<span class="success-badge">TỐT</span>'
        else:
            status_badge = '<span class="text-xs text-slate-400">Đang chạy</span>'
            
        rows_html += f"""
        <tr class="{row_class}">
            <td class="font-semibold text-slate-800">{name}</td>
            <td class="text-slate-600">{date}</td>
            <td class="font-medium">{format_currency(spend)}</td>
            <td class="text-slate-600">{format_currency(imp)}</td>
            <td class="font-bold">{conv}</td>
            <td class="font-bold">{format_currency(cpa)}</td>
            <td>{status_badge}</td>
        </tr>
        """
        
    html_content = HTML_TEMPLATE.format(
        update_time=datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
        total_spend=format_currency(total_spend),
        total_conversions=format_currency(total_conversions),
        avg_cpa=format_currency(avg_cpa),
        table_rows=rows_html
    )
    
    with open(OUTPUT_HTML, 'w', encoding='utf-8') as f:
        f.write(html_content)
        
    print(f"[+] Dashboard generated at: {OUTPUT_HTML}")

if __name__ == "__main__":
    build_dashboard()
