from flask import Flask, render_template_string

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <title>Stratejik Satış Yönetim Paneli v21</title>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Segoe UI', sans-serif; }
        body { background-color: #f4f6f9; color: #333; }
        header { background-color: #1e3a8a; color: white; padding: 15px 20px; display: flex; justify-content: space-between; align-items: center; }
        .container { max-width: 1400px; margin: 20px auto; padding: 0 20px; }
        .panel { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); margin-bottom: 20px; }
        table { width: 100%; border-collapse: collapse; margin-top: 10px; }
        th { background-color: #1e3a8a; color: white; padding: 12px; border: 1px solid #ddd; text-align: center; }
        td { border: 1px solid #ddd; padding: 12px; text-align: center; font-weight: 600; }
        .progress-bar { height: 12px; background: #e2e8f0; border-radius: 6px; width: 100%; overflow: hidden; }
        .progress-fill { height: 100%; background: #10b981; }
        .nav-btn { background: #3b82f6; color: white; border: none; padding: 10px 15px; cursor: pointer; border-radius: 4px; }
    </style>
</head>
<body>
    <header>
        <h1>Satış Yönetim Paneli</h1>
        <nav><button class="nav-btn" onclick="location.reload()">Sistemi Yenile</button></nav>
    </header>
    <div class="container">
        <div class="panel">
            <h2><i class="fa-solid fa-chart-line"></i> Dönemsel Hedef Dashboard (2026)</h2>
            <table>
                <thead><tr><th>DÖNEM</th><th>HEDEF</th><th>GERÇEKLEŞEN</th><th>KALAN</th><th>BAŞARI %</th></tr></thead>
                <tbody id="dashboard-vucut"></tbody>
            </table>
        </div>
        <div class="panel">
            <h2><i class="fa-solid fa-table-cells"></i> Ürün Bazlı Performans</h2>
            <table>
                <thead><tr><th>ÜRÜN</th><th>AÇIK HACİM</th><th>KAZANILAN</th><th>HEDEF</th><th>KALAN</th></tr></thead>
                <tbody id="analiz-vucut"></tbody>
            </table>
        </div>
    </div>
    <script>
        let db = JSON.parse(localStorage.getItem('excel_esnek_firsat_db_v15_1')) || {firsatlar: [], urunler: []};
        function verileriTazele() {
            // Dashboard Hesaplama
            const body = document.getElementById('dashboard-vucut');
            body.innerHTML = '';
            const donemler = [
                {ad: "Q1", aylar: ["01", "02", "03"], hedef: 1250000},
                {ad: "Q2", aylar: ["04", "05", "06"], hedef: 1250000},
                {ad: "Q3", aylar: ["07", "08", "09"], hedef: 1250000},
                {ad: "Q4", aylar: ["10", "11", "12"], hedef: 1250000}
            ];
            donemler.forEach(d => {
                let kazanilan = 0;
                db.firsatlar.forEach(f => {
                    let ay = f.tarih ? f.tarih.split('-')[1] : "";
                    if(f.statu_id == 3 && d.aylar.includes(ay)) kazanilan += parseFloat(f.beklenen_gelir || 0);
                });
                let oran = ((kazanilan/d.hedef)*100).toFixed(1);
                body.innerHTML += `<tr><td>${d.ad}</td><td>${d.hedef.toLocaleString()} TL</td><td>${kazanilan.toLocaleString()} TL</td><td>${(d.hedef-kazanilan).toLocaleString()} TL</td><td>%${oran} <div class="progress-bar"><div class="progress-fill" style="width:${oran>100?100:oran}%"></div></div></td></tr>`;
            });
            // Ürün Bazlı Analiz
            const aBody = document.getElementById('analiz-vucut');
            aBody.innerHTML = '';
            db.urunler.forEach(u => {
                let acik = 0, kazanilan = 0;
                db.firsatlar.forEach(f => {
                    if(f.urun_id == u.id) {
                        if(f.statu_id == 3) kazanilan += parseFloat(f.beklenen_gelir || 0);
                        else acik += parseFloat(f.beklenen_gelir || 0);
                    }
                });
                let hedef = u.hedef || 1000000;
                let kalan = hedef - kazanilan;
                aBody.innerHTML += `<tr><td>${u.ad}</td><td>${acik.toLocaleString()} TL</td><td>${kazanilan.toLocaleString()} TL</td><td>${hedef.toLocaleString()} TL</td><td>${kalan>0?kalan.toLocaleString():0} TL</td></tr>`;
            });
        }
        verileriTazele();
    </script>
</body>
</html>
"""

@app.route('/')
def ana_sayfa():
    return render_template_string(HTML_TEMPLATE)
