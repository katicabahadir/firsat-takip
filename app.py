from flask import Flask, render_template_string, request, jsonify
import sqlite3
import os

app = Flask(__name__)
# Render platformunda verilerin silinmemesi için geçici hafıza yerine kalıcı dizin kontrolü
DB_PATH = "/opt/render/project/src/data/firsat_takip.db" if os.path.exists("/opt/render/project/src") else "firsat_takip.db"

if not os.path.exists(os.path.dirname(DB_PATH)) and os.path.dirname(DB_PATH) != "":
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def veritabani_kur():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS musteriler (id INTEGER PRIMARY KEY AUTOINCREMENT, ad TEXT UNIQUE NOT NULL)")
    cursor.execute("CREATE TABLE IF NOT EXISTS urunler (id INTEGER PRIMARY KEY AUTOINCREMENT, ad TEXT UNIQUE NOT NULL)")
    cursor.execute("CREATE TABLE IF NOT EXISTS statuler (id INTEGER PRIMARY KEY AUTOINCREMENT, ad TEXT UNIQUE NOT NULL)")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS firsatlar (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            musteri_id INTEGER,
            urun_id INTEGER,
            statu_id INTEGER,
            beklenen_gelir REAL,
            olasilik INTEGER,
            tahmini_kapanis TEXT,
            FOREIGN KEY(musteri_id) REFERENCES musteriler(id),
            FOREIGN KEY(urun_id) REFERENCES urunler(id),
            FOREIGN KEY(statu_id) REFERENCES statuler(id)
        )
    """)
    cursor.execute("SELECT COUNT(*) FROM statuler")
    if cursor.fetchone()[0] == 0:
        varsayilan_statuler = [("Açık",), ("Teklif Verildi",), ("Kazanıldı",), ("Kaybedildi",), ("Ertelendi",)]
        cursor.executemany("INSERT INTO statuler (ad) VALUES (?)", varsayilan_statuler)
    conn.commit()
    conn.close()

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <title>Dinamik Fırsat Takip Sistemi</title>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Segoe UI', sans-serif; }
        body { background-color: #f4f6f9; color: #333; }
        header { background-color: #1e3a8a; color: white; padding: 15px 20px; display: flex; justify-content: space-between; align-items: center; }
        nav button { background: none; border: 1px solid white; color: white; padding: 8px 15px; margin-left: 10px; border-radius: 4px; cursor: pointer; font-weight: bold; }
        nav button:hover, nav button.active { background-color: white; color: #1e3a8a; }
        .container { max-width: 1300px; margin: 20px auto; padding: 0 20px; }
        .sayfa { display: none; }
        .sayfa.active { display: block; }
        .dashboard-summary { display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; margin-bottom: 20px; }
        .card { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); border-left: 5px solid #1e3a8a; display: flex; justify-content: space-between; align-items: center; }
        .card.success { border-left-color: #10b981; }
        .card.warning { border-left-color: #f59e0b; }
        .card h3 { font-size: 14px; color: #6b7280; text-transform: uppercase; }
        .card .value { font-size: 24px; font-weight: bold; margin-top: 5px; }
        .icerik-turu { display: flex; gap: 20px; }
        .sol-form { background: white; width: 350px; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); height: fit-content; }
        .sag-tablo { background: white; flex: 1; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
        h2 { font-size: 18px; margin-bottom: 15px; color: #1e3a8a; border-bottom: 2px solid #f3f4f6; padding-bottom: 5px; }
        .form-group { margin-bottom: 15px; }
        .form-group label { display: block; margin-bottom: 5px; font-weight: 600; font-size: 14px; }
        .form-group input, .form-group select { width: 100%; padding: 10px; border: 1px solid #d1d5db; border-radius: 6px; }
        button.btn-primary { width: 100%; background-color: #1e3a8a; color: white; border: none; padding: 12px; border-radius: 6px; font-weight: bold; cursor: pointer; }
        table { width: 100%; border-collapse: collapse; margin-top: 10px; font-size: 14px; }
        th, td { padding: 12px; border-bottom: 1px solid #e5e7eb; text-align: left; }
        th { background-color: #f8fafc; color: #475569; }
        .btn-delete { background: none; border: none; color: #ef4444; cursor: pointer; }
        .badge { padding: 4px 8px; border-radius: 4px; font-size: 12px; font-weight: bold; background-color: #e0f2fe; color: #0369a1; }
        .badge.kazanildi { background-color: #d1fae5; color: #065f46; }
        .badge.kaybedildi { background-color: #fee2e2; color: #991b1b; }
    </style>
</head>
<body>
    <header>
        <h1><i class="fa-solid fa-layer-group"></i> Fırsat Yönetim Paneli v2.0</h1>
        <nav>
            <button onclick="sayfaDegistir('firsatlar-sayfa')" id="btn-firsatlar-sayfa" class="active">Fırsat Takibi</button>
            <button onclick="sayfaDegistir('ayarlar-sayfa')" id="btn-ayarlar-sayfa">Dinamik Veri Tanımları</button>
        </nav>
    </header>

    <div class="container">
        <div id="firsatlar-sayfa" class="sayfa active">
            <div class="dashboard-summary">
                <div class="card">
                    <div><h3>Açık Fırsatlar Toplamı</h3><div class="value" id="m-acik">0 TL</div></div>
                    <i class="fa-solid fa-folder-open fa-2x" style="color:#1e3a8a"></i>
                </div>
                <div class="card success">
                    <div><h3>Kazanılan Ciro</h3><div class="value" id="m-kazanilan">0 TL</div></div>
                    <i class="fa-solid fa-wallet fa-2x" style="color:#10b981"></i>
                </div>
                <div class="card warning">
                    <div><h3>Ağırlıklı Tahmini Gelir (SUMPRODUCT)</h3><div class="value" id="m-tahmin">0 TL</div></div>
                    <i class="fa-solid fa-calculator fa-2x" style="color:#f59e0b"></i>
                </div>
            </div>

            <div class="icerik-turu">
                <div class="sol-form">
                    <h2>Yeni Fırsat Ekle</h2>
                    <form id="firsatForm">
                        <div class="form-group">
                            <label>Müşteri / Firma (Dinamik)</label>
                            <select id="f-musteri" required><option value="">Seçin...</option></select>
                        </div>
                        <div class="form-group">
                            <label>Ürün / Çözüm (Dinamik)</label>
                            <select id="f-urun" required><option value="">Seçin...</option></select>
                        </div>
                        <div class="form-group">
                            <label>Beklenen Gelir (TL)</label>
                            <input type="number" id="f-gelir" value="0" min="0">
                        </div>
                        <div class="form-group">
                            <label>Olasılık (%)</label>
                            <input type="number" id="f-olasilik" value="50" min="0" max="100">
                        </div>
                        <div class="form-group">
                            <label>Fırsat Statüsü (Dinamik)</label>
                            <select id="f-statu" required></select>
                        </div>
                        <div class="form-group">
                            <label>Tahmini Kapanış</label>
                            <input type="date" id="f-tarih">
                        </div>
                        <button type="submit" class="btn-primary">Fırsatı Kaydet</button>
                    </form>
                </div>

                <div class="sag-tablo">
                    <h2>Fırsat Havuzu</h2>
                    <table>
                        <thead>
                            <tr>
                                <th>Müşteri / Firma</th>
                                <th>Ürün / Çözüm</th>
                                <th>Beklenen Gelir</th>
                                <th>Olasılık</th>
                                <th>Statü</th>
                                <th>Kapanış Tarihi</th>
                                <th>İşlem</th>
                            </tr>
                        </thead>
                        <tbody id="firsat-tablo-vucut"></tbody>
                    </table>
                </div>
            </div>
        </div>

        <div id="ayarlar-sayfa" class="sayfa">
            <div style="display:grid; grid-template-columns: repeat(3, 1fr); gap:20px;">
                <div class="sol-form" style="width:100%">
                    <h2><i class="fa-solid fa-building"></i> Dinamik Müşteriler</h2>
                    <div style="display:flex; gap:5px; margin-bottom:15px;">
                        <input type="text" id="yeni-musteri" placeholder="Yeni Firma Adı" style="flex:1; padding:8px; border:1px solid #ddd; border-radius:4px;">
                        <button onclick="dinamikEkle('musteriler', 'yeni-musteri')" style="padding:8px 12px; background:#1e3a8a; color:white; border:none; border-radius:4px; cursor:pointer;">Ekle</button>
                    </div>
                    <ul id="liste-musteriler" style="list-style:none;"></ul>
                </div>

                <div class="sol-form" style="width:100%">
                    <h2><i class="fa-solid fa-box"></i> Dinamik Ürünler</h2>
                    <div style="display:flex; gap:5px; margin-bottom:15px;">
                        <input type="text" id="yeni-urun" placeholder="Yeni Ürün Adı" style="flex:1; padding:8px; border:1px solid #ddd; border-radius:4px;">
                        <button onclick="dinamikEkle('urunler', 'yeni-urun')" style="padding:8px 12px; background:#1e3a8a; color:white; border:none; border-radius:4px; cursor:pointer;">Ekle</button>
                    </div>
                    <ul id="liste-urunler" style="list-style:none;"></ul>
                </div>

                <div class="sol-form" style="width:100%">
                    <h2><i class="fa-solid fa-circle-check"></i> Dinamik Statüler</h2>
                    <div style="display:flex; gap:5px; margin-bottom:15px;">
                        <input type="text" id="yeni-statu" placeholder="Yeni Statü" style="flex:1; padding:8px; border:1px solid #ddd; border-radius:4px;">
                        <button onclick="dinamikEkle('statuler', 'yeni-statu')" style="padding:8px 12px; background:#1e3a8a; color:white; border:none; border-radius:4px; cursor:pointer;">Ekle</button>
                    </div>
                    <ul id="liste-statuler" style="list-style:none;"></ul>
                </div>
            </div>
        </div>
    </div>

    <script>
        document.getElementById('f-tarih').valueAsDate = new Date();
        function sayfaDegistir(sayfaId) {
            document.querySelectorAll('.sayfa').forEach(s => s.classList.remove('active'));
            document.querySelectorAll('nav button').forEach(b => b.classList.remove('active'));
            document.getElementById(sayfaId).classList.add('active');
            document.getElementById('btn-' + sayfaId).classList.add('active');
            verileriTazele();
        }

        function paraFormat(deger) {
            return new Intl.NumberFormat('tr-TR', { style: 'currency', currency: 'TRY', maximumFractionDigits: 0 }).format(deger);
        }

        function verileriTazele() {
            fetch('/api/data').then(res => res.json()).then(data => {
                setupDropdown('f-musteri', data.musteriler, 'Müşteri Seçin...');
                setupDropdown('f-urun', data.urunler, 'Ürün Seçin...');
                setupDropdown('f-statu', data.statuler, null);
                renderAyarlarListesi('liste-musteriler', data.musteriler, 'musteriler');
                renderAyarlarListesi('liste-urunler', data.urunler, 'urunler');
                renderAyarlarListesi('liste-statuler', data.statuler, 'statuler');
            });

            fetch('/api/firsatlar').then(res => res.json()).then(firsatlar => {
                const tbody = document.getElementById('firsat-tablo-vucut');
                tbody.innerHTML = '';
                let acikToplam = 0, kazanilanToplam = 0, agirlikliTahmin = 0;

                firsatlar.forEach(f => {
                    const gelir = f.beklenen_gelir || 0;
                    const olasilik = f.olasilik || 0;
                    if(f.statu_ad === 'Kazanıldı') { kazanilanToplam += gelir; }
                    else if(f.statu_ad !== 'Kaybedildi') { acikToplam += gelir; agirlikliTahmin += (gelir * (olasilik / 100)); }

                    const tr = document.createElement('tr');
                    const t = f.tarih ? f.tarih.split('-').reverse().join('.') : '-';
                    let cls = f.statu_ad === 'Kazanıldı' ? 'kazanildi' : (f.statu_ad === 'Kaybedildi' ? 'kaybedildi' : '');
                    tr.innerHTML = `<td><strong>${f.musteri_ad || '-'}</strong></td><td>${f.urun_ad || '-'}</td><td>${paraFormat(gelir)}</td><td>%${olasilik}</td><td><span class="badge ${cls}">${f.statu_ad}</span></td><td>${t}</td><td><button class="btn-delete" onclick="firsatSil(${f.id})"><i class="fa-solid fa-trash-can"></i></button></td>`;
                    tbody.appendChild(tr);
                });
                document.getElementById('m-acik').innerText = paraFormat(acikToplam);
                document.getElementById('m-kazanilan').innerText = paraFormat(kazanilanToplam);
                document.getElementById('m-tahmin').innerText = paraFormat(agirlikliTahmin);
            });
        }

        function setupDropdown(id, liste, varsayilanMetin) {
            const el = document.getElementById(id); const eskiDeger = el.value;
            el.innerHTML = varsayilanMetin ? `<option value="">${varsayilanMetin}</option>` : '';
            liste.forEach(item => { el.innerHTML += `<option value="${item.id}">${item.ad}</option>`; });
            if(eskiDeger) el.value = eskiDeger;
        }

        function renderAyarlarListesi(id, liste, tabloAdi) {
            const ul = document.getElementById(id); ul.innerHTML = '';
            liste.forEach(item => {
                ul.innerHTML += `<li style="display:flex; justify-content:space-between; padding:6px 0; border-bottom:1px solid #eee;"><span>${item.ad}</span><button class="btn-delete" onclick="dinamikSil('${tabloAdi}', ${item.id})"><i class="fa-solid fa-xmark"></i></button></li>`;
            });
        }

        function dinamikEkle(tablo, inputId) {
            const input = document.getElementById(inputId); if(!input.value.trim()) return;
            fetch(`/api/tanim/${tablo}`, { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({ad: input.value.trim()}) }).then(() => { input.value = ''; verileriTazele(); });
        }

        function dinamikSil(tablo, id) {
            if(confirm('Bu tanımı silmek istediğinize emin misiniz?')) { fetch(`/api/tanim/${tablo}/${id}`, {method: 'DELETE'}).then(() => verileriTazele()); }
        }

        document.getElementById('firsatForm').addEventListener('submit', function(e) {
            e.preventDefault();
            const payload = { musteri_id: document.getElementById('f-musteri').value, urun_id: document.getElementById('f-urun').value, beklenen_gelir: document.getElementById('f-gelir').value, olasilik: document.getElementById('f-olasilik').value, statu_id: document.getElementById('f-statu').value, tarih: document.getElementById('f-tarih').value };
            fetch('/api/firsat', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(payload) }).then(() => { document.getElementById('f-gelir').value = '0'; document.getElementById('f-olasilik').value = '50'; verileriTazele(); });
        });

        window.firsatSil = function(id) { if(confirm('Bu fırsatı silmek istiyor musunuz?')) { fetch(`/api/firsat/${id}`, {method: 'DELETE'}).then(() => verileriTazele()); } }
        verileriTazele();
    </script>
</body>
</html>
"""

@app.route('/')
def ana_sayfa(): return render_template_string(HTML_TEMPLATE)

@app.route('/api/data', methods=['GET'])
def get_data():
    conn = get_db_connection()
    musteriler = conn.execute("SELECT * FROM musteriler ORDER BY ad").fetchall()
    urunler = conn.execute("SELECT * FROM urunler ORDER BY ad").fetchall()
    statuler = conn.execute("SELECT * FROM statuler").fetchall()
    conn.close()
    return jsonify({"musteriler": [dict(m) for m in musteriler], "urunler": [dict(u) for u in urunler], "statuler": [dict(s) for s in statuler]})

@app.route('/api/tanim/<tablo>', methods=['POST'])
def tanim_ekle(tablo):
    if tablo not in ['musteriler', 'urunler', 'statuler']: return "Hata", 400
    ad = request.json.get('ad')
    conn = get_db_connection()
    try: conn.execute(f"INSERT INTO {tablo} (ad) VALUES (?)", (ad,)); conn.commit()
    except sqlite3.IntegrityError: pass
    conn.close()
    return jsonify({"status": "success"})

@app.route('/api/tanim/<tablo>/<int:id>', methods=['DELETE'])
def tanim_sil(tablo, id):
    if tablo not in ['musteriler', 'urunler', 'statuler']: return "Hata", 400
    conn = get_db_connection()
    conn.execute(f"DELETE FROM {tablo} WHERE id = ?", (id,)); conn.commit(); conn.close()
    return jsonify({"status": "success"})

@app.route('/api/firsatlar', methods=['GET'])
def get_firsatlar():
    conn = get_db_connection()
    query = """
        SELECT f.id, f.beklenen_gelir, f.olasilik, f.tahmini_kapanis as tarih, m.ad as musteri_ad, u.ad as urun_ad, s.ad as statu_ad
        FROM firsatlar f LEFT JOIN musteriler m ON f.musteri_id = m.id LEFT JOIN urunler u ON f.urun_id = u.id LEFT JOIN statuler s ON f.statu_id = s.id
        ORDER BY f.id DESC
    """
    firsatlar = conn.execute(query).fetchall(); conn.close()
    return jsonify([dict(f) for f in firsatlar])

@app.route('/api/firsat', methods=['POST'])
def firsat_ekle():
    data = request.json; conn = get_db_connection()
    conn.execute("INSERT INTO firsatlar (musteri_id, urun_id, statu_id, beklenen_gelir, olasilik, tahmini_kapanis) VALUES (?, ?, ?, ?, ?, ?)", (data['musteri_id'], data['urun_id'], data['statu_id'], float(data['beklenen_gelir'] or 0), int(data['olasilik'] or 0), data['tarih'])); conn.commit(); conn.close()
    return jsonify({"status": "success"})

@app.route('/api/firsat/<int:id>', methods=['DELETE'])
def firsat_sil(id):
    conn = get_db_connection()
    conn.execute("DELETE FROM firsatlar WHERE id = ?", (id,)); conn.commit(); conn.close()
    return jsonify({"status": "success"})

if __name__ == '__main__':
    veritabani_kur()
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
