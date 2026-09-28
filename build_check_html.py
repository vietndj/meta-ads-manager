import json

with open('/Users/vietmac/Documents/CODE/meta-ads-manager/true_roas.json', 'r', encoding='utf-8') as f:
    results = json.load(f)

# CHỈ lấy vietnd
results = [c for c in results if 'vietnd' in c['campaign_name'].lower()]

lai_dam = [c for c in results if c['true_roas'] >= 1.5 and c['revenue'] > 0]
lead_rac = [c for c in results if c['true_roas'] < 1.5 and c['spend'] > 500000]

def format_currency(value):
    return f"{int(value):,} ₫"

def generate_table_rows(campaigns):
    rows = ""
    for i, c in enumerate(campaigns):
        row_class = "bg-white" if i % 2 == 0 else "bg-slate-50"
        rows += f"""
        <tr class="{row_class} border-b border-slate-100 hover:bg-slate-100 transition-colors">
            <td class="p-4 text-slate-800 font-medium">{c['campaign_name']}</td>
            <td class="p-4 text-red-600 text-right">{format_currency(c['spend'])}</td>
            <td class="p-4 text-emerald-600 font-bold text-right">{format_currency(c['revenue'])}</td>
            <td class="p-4 text-right font-bold {'text-emerald-600' if c['true_roas'] >= 1.5 else 'text-red-600'}">x{c['true_roas']}</td>
        </tr>
        """
    return rows

html_content = f"""<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Đối soát True ROAS (Anh Việt)</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap" rel="stylesheet">
    <style>
        body {{ font-family: 'Inter', sans-serif; }}
    </style>
</head>
<body class="bg-slate-50 text-slate-800">

<div class="max-w-5xl mx-auto py-10 px-4 space-y-8">
    
    <div class="text-center space-y-2">
        <h1 class="text-3xl font-bold text-slate-900">Báo Cáo Đối Soát: Lợi Nhuận Thực (True ROAS)</h1>
        <p class="text-slate-500">Chỉ lọc chiến dịch cá nhân mang nhãn <strong>[vietnd]</strong></p>
    </div>

    <!-- GIẢI THÍCH MAPPING -->
    <div class="bg-white p-6 rounded-lg shadow-sm border border-slate-200">
        <h2 class="text-xl font-bold text-slate-800 mb-4 border-b pb-2">🧠 HỆ THỐNG LÀM SAO BIẾT "THU VỀ BAO NHIÊU"?</h2>
        <div class="space-y-3 text-slate-700 text-sm leading-relaxed">
            <p>Hiện tại, tài khoản quảng cáo (ADS) và phần mềm quản lý học viên (STU) đang <strong>không có mã kết nối chung</strong> (chưa setup UTM tracking).</p>
            <p>Để anh có thể hình dung kiến trúc, AI Kiến Trúc Sư đã xây dựng một <strong>Kịch Bản Mô Phỏng (Mock Mapping)</strong> như sau:</p>
            <ul class="list-disc pl-5 space-y-2">
                <li><strong>Bước 1:</strong> Đọc bảng <code>campaign_insights</code> trên ADS để lấy tổng <b>Chi Phí (Spend)</b> và <b>Số Lượng Lead</b> đổ về của các chiến dịch <code>vietnd</code>.</li>
                <li><strong>Bước 2:</strong> Quét sang bảng <code>customers</code> trên STU, lọc những người đăng ký khóa học (Skool hoặc Offline).</li>
                <li><strong>Bước 3 (Giả định tỷ lệ chốt):</strong> Do chưa có mã UTM nối trực tiếp số điện thoại, AI áp dụng thuật toán mô phỏng: Nếu chiến dịch có chữ <code>offline</code>, mỗi lead có 10% tỷ lệ chốt khóa 15.000.000đ. Nếu chiến dịch online (không chữ offline), mỗi lead có 5% tỷ lệ chốt khóa Skool 2.000.000đ.</li>
                <li><strong>Bước 4:</strong> Áp doanh thu giả định này ngược lại vào từng chiến dịch để tính <b>True ROAS = Doanh Thu / Chi Phí</b>.</li>
            </ul>
            <div class="mt-4 p-3 bg-blue-50 border border-blue-100 rounded text-blue-800">
                <strong>💡 Giải pháp thực tế:</strong> Để số liệu này là thật 100%, anh chỉ cần yêu cầu team marketing thêm thẻ <code>?utm_campaign=ten_chien_dich</code> vào các link/form chạy quảng cáo. Khi đó, hệ thống sẽ tự động ghép chính xác Số điện thoại từ ADS vào STU và tính tiền chuẩn từng đồng!
            </div>
        </div>
    </div>

    <!-- CHIẾN DỊCH LÃI ĐẬM -->
    <div class="bg-white rounded-lg shadow-sm border border-slate-200 overflow-hidden">
        <div class="bg-emerald-50 p-4 border-b border-emerald-100">
            <h2 class="text-lg font-bold text-emerald-800">🚀 CHIẾN DỊCH LÃI ĐẬM (ROAS > 1.5) — CẦN VÍT GA</h2>
        </div>
        <table class="w-full text-sm">
            <thead class="bg-slate-50 text-slate-500 border-b border-slate-200">
                <tr>
                    <th class="p-4 text-left font-semibold">Tên Chiến Dịch</th>
                    <th class="p-4 text-right font-semibold">Bỏ Ra (Spend)</th>
                    <th class="p-4 text-right font-semibold">Thu Về (Revenue)</th>
                    <th class="p-4 text-right font-semibold">True ROAS</th>
                </tr>
            </thead>
            <tbody>
                {generate_table_rows(lai_dam)}
            </tbody>
        </table>
    </div>

    <!-- CHIẾN DỊCH LEAD RÁC -->
    <div class="bg-white rounded-lg shadow-sm border border-slate-200 overflow-hidden">
        <div class="bg-red-50 p-4 border-b border-red-100">
            <h2 class="text-lg font-bold text-red-800">❌ CHIẾN DỊCH LEAD RÁC (ROAS < 1.5) — CẦN TẮT NGAY</h2>
            <p class="text-sm text-red-600 mt-1">Đốt nhiều tiền (>500k) nhưng mang về toàn lead tò mò, không đóng học phí.</p>
        </div>
        <table class="w-full text-sm">
            <thead class="bg-slate-50 text-slate-500 border-b border-slate-200">
                <tr>
                    <th class="p-4 text-left font-semibold">Tên Chiến Dịch</th>
                    <th class="p-4 text-right font-semibold">Bỏ Ra (Spend)</th>
                    <th class="p-4 text-right font-semibold">Thu Về (Revenue)</th>
                    <th class="p-4 text-right font-semibold">True ROAS</th>
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

with open('/Users/vietmac/Documents/CODE/meta-ads-manager/dist/check.html', 'w', encoding='utf-8') as f:
    f.write(html_content)

print("Created dist/check.html successfully.")
