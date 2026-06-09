from flask import Flask, render_template_string



app = Flask(__name__)# v17.0: Tüm gereksiz matrisler silindi, sadece görseldeki tablo yapısı bırakıldı.

HTML_TEMPLATE = """

<!DOCTYPE html>

<html lang="tr">

<head>

<meta charset="UTF-8">

<title>Satış Hedef Takip</title>

<link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">

<style>

* { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Segoe UI', sans-serif; }

body { background-color: #f4f6f9; color: #333; }

header { background-color: #1e3a8a; color: white; padding: 15px 20px; }

.container { max-width: 1200px; margin: 20px auto; padding: 20px; }

.hedef-ozet-kutusu { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }

h2 { color: #1e3a8a; margin-bottom: 15px; font-size: 18px; }

table { width: 100%; border-collapse: collapse; margin-top: 10px; }

th { background-color: #f8fafc; border: 1px solid #e2e8f0; padding: 12px; text-align: center; color: #475569; }

td { border: 1px solid #e2e8f0; padding: 15px; text-align: center; font-weight: bold; }

.btn-success { background-color: #10b981; color: white; border: none; padding: 10px 20px; border-radius: 5px; cursor: pointer; margin-top: 10px; }

</style>

</head>

<body>

<header><h1>Satış Hedef Takip Paneli</h1></header>

<div class="container">

<div class="hedef-ozet-kutusu">

<h2><i class="fa-solid fa-chart-line"></i> Yıllık Satış Hedef & Gerçekleşen</h2>

<table>

<thead>

<tr>

<th>DÖNEM</th>

<th>YILLIK HEDEF (TL)</th>

<th>GERÇEKLEŞEN SATIŞ (TL)</th>

<th>KALAN HEDEF (TL)</th>

<th>BAŞARI ORANI</th>

</tr>

</thead>

<tbody id="hedef-vucut">

<tr>

<td>2026</td>

<td style="color:#1e40af;">5.000.000 TL</td>

<td id="h-gercek" style="color:#166534;">0 TL</td>

<td id="h-kalan" style="color:#b45309;">5.000.000 TL</td>

<td id="h-oran" style="color:#0f172a;">%0</td>

</tr>

</tbody>

</table>

<button class="btn-success" onclick="verileriTazele()"><i class="fa-solid fa-rotate"></i> Verileri Güncelle</button>

</div>

</div>

<script>

let db = JSON.parse(localStorage.getItem('excel_esnek_firsat_db_v15_1')) || {firsatlar: []};


function verileriTazele() {

let kazanilan = 0;

db.firsatlar.forEach(f => {

if(f.statu_id == 3) kazanilan += parseFloat(f.beklenen_gelir || 0);

});

let hedef = 5000000;

let kalan = hedef - kazanilan;

let oran = ((kazanilan / hedef) * 100).toFixed(1);


document.getElementById('h-gercek').innerText = new Intl.NumberFormat('tr-TR', {style: 'currency', currency: 'TRY'}).format(kazanilan);

document.getElementById('h-kalan').innerText = new Intl.NumberFormat('tr-TR', {style: 'currency', currency: 'TRY'}).format(kalan > 0 ? kalan : 0);

document.getElementById('h-oran').innerText = '%' + oran;

}

verileriTazele();

</script>

</body>

</html>

"""@app.route('/')def ana_sayfa():

return render_template_string(HTML_TEMPLATE) 

