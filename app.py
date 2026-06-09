from flask import Flask, render_template_string

app = Flask(__name__)

# Vercel Serverless yapısıyla tam uyumlu, tarayıcı tabanlı gelişmiş dinamik sistem
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
        
        /* Özet Kartları */
        .dashboard-summary { display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; margin-bottom: 20px; }
        .card { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); border-left: 5px solid #1e3a8a; display: flex; justify-content: space-between; align-items: center; }
        .card.success { border-left-color: #10b981; }
        .card.warning { border-left-color: #f59e0b; }
        .card h3 { font-size: 14px; color: #6b7280; text-transform: uppercase; }
        .card .value { font-size: 24px; font-weight: bold; margin-top: 5px; }
        
        /* Düzen */
        .icerik-turu { display: flex; gap: 20px; }
        .sol-form { background: white; width: 350px; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); height: fit-content; }
        .sag-tablo { background: white; flex: 1; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
        
        h2 { font-size: 18px; margin-bottom: 15px; color: #1e3a8a; border-bottom: 2px solid #f3f4f6; padding-bottom: 5px; }
        .form-group { margin-bottom: 15px; }
        .form-group label { display: block; margin-bottom: 5px; font-weight: 600; font-size: 14px; }
        .form-group input, .form-group select { width: 100%; padding: 10px; border: 1px solid #d1d5db; border-radius: 6px; font-size: 14px; }
        button.btn-primary { width: 100%; background-color: #1e3a8a; color: white; border: none; padding: 12px; border-radius: 6px; font-weight: bold; cursor: pointer; font-size: 15px; }
        button.btn-primary:hover { background-color: #1d4ed8; }
        
        table { width: 100%; border-collapse: collapse; margin-top: 10px; font-size: 14px; }
        th, td { padding: 12px; border-bottom: 1px solid #e5e7eb; text-align: left; }
        th { background-color: #f8fafc; color: #475569; }
        .btn-delete { background: none; border: none; color: #ef4444; cursor: pointer; }
        .badge { padding: 4px 8px; border-radius: 4px; font-size: 12px; font-weight: bold; background-color: #e0f2fe; color: #0369a1; }
        .badge.kazanildi { background-color: #d1fae5; color: #065f46; }
        .badge.kaybedildi { background-color: #fee2e2; color: #991b1b; }
        .badge.teklif { background-color: #fef3c7; color: #b45309; }
        .badge.ertelendi { background-color: #f3f4f6; color: #374151; }
        
        ul { list-style: none; }
        li { display: flex; justify-content: space-between; padding: 8px 10px; border-bottom: 1px solid #eee; background: #fafafa; margin-bottom: 5px; border-radius: 4px; font-size: 14px; }
    </style>
</head>
<body>

    <header>
        <h1><i class="fa-solid fa-layer-group"></i> Fırsat Yönetim Paneli v3.0</h1>
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
                        <button type="button" onclick="dinamikEkle('musteriler', 'yeni-musteri')" style="padding:8px 12px; background:#1e3a8a; color:white; border:none; border-radius:4px; cursor:pointer;">Ekle</button>
                    </div>
                    <ul id="liste-musteriler"></ul>
                </div>

                <div class="sol-form" style="width:100%">
                    <h2><i class="fa-solid fa-box"></i> Dinamik Ürünler / Çözümler</h2>
                    <div style="display:flex; gap:5px; margin-bottom:15px;">
                        <input type="text" id="yeni-urun" placeholder="Yeni Ürün Adı" style="flex:1; padding:8px; border:1px solid #ddd; border-radius:4px;">
                        <button type="button" onclick="dinamikEkle('urunler', 'yeni-urun')" style="padding:8px 12px; background:#1e3a8a; color:white; border:none; border-radius:4px; cursor:pointer;">Ekle</button>
                    </div>
                    <ul id="liste-urunler"></ul>
                </div>

                <div class="sol-form" style="width:100%">
                    <h2><i class="fa-solid fa-circle-check"></i> Dinamik Statüler</h2>
                    <div style="display:flex; gap:5px; margin-bottom:15px;">
                        <input type="text" id="yeni-statu" placeholder="Yeni Statü Adı" style="flex:1; padding:8px; border:1px solid #ddd; border-radius:4px;">
                        <button type="button" onclick="dinamikEkle('statuler', 'yeni-statu')" style="padding:8px 12px; background:#1e3a8a; color:white; border:none; border-radius:4px; cursor:pointer;">Ekle</button>
                    </div>
                    <ul id="liste-statuler"></ul>
                </div>
            </div>
        </div>

    </div>

    <script>
        // Tarayıcı hafızasını ana veri tabanı olarak kullanma altyapısı (Vercel çökmesini önler)
        let db = JSON.parse(localStorage.getItem('firsat_takip_db')) || {
            musteriler: [{id: 1, ad: "Örnek Belediye"}, {id: 2, ad: "X Şirketi"}],
            urunler: [{id: 1, ad: "QDMS Çözümü"}, {id: 2, ad: "Ensemble Modülü"}],
            statuler: [{id: 1, ad: "Açık"}, {id: 2, ad: "Teklif Verildi"}, {id: 3, ad: "Kazanıldı"}, {id: 4, ad: "Kaybedildi"}, {id: 5, ad: "Ertelendi"}],
            firsatlar: []
        };

        document.getElementById('f-tarih').valueAsDate = new Date();

        function dbKaydet() {
            localStorage.setItem('firsat_takip_db', JSON.stringify(db));
            verileriTazele();
        }

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

        function durumSinifiGuncelle(durum) {
            if(durum === 'Açık') return 'acik';
            if(durum === 'Teklif Verildi') return 'teklif';
            if(durum === 'Kazanıldı') return 'kazanildi';
            if(durum === 'Kaybedildi') return 'kaybedildi';
            return 'ertelendi';
        }

        function verileriTazele() {
            // Açılır kutuları doldur
            setupDropdown('f-musteri', db.musteriler, 'Müşteri Seçin...');
            setupDropdown('f-urun', db.urunler, 'Ürün Seçin...');
            setupDropdown('f-statu', db.statuler, null);

            // Tanımlama listelerini doldur
            renderAyarlarListesi('liste-musteriler', db.musteriler, 'musteriler');
            renderAyarlarListesi('liste-urunler', db.urunler, 'urunler');
            renderAyarlarListesi('liste-statuler', db.statuler, 'statuler');

            // Fırsat tablosunu ve metrikleri bas
            const tbody = document.getElementById('firsat-tablo-vucut');
            tbody.innerHTML = '';
            
            let acikToplam = 0, kazanilanToplam = 0, agirlikliTahmin = 0;

            if (db.firsatlar.length === 0) {
                tbody.innerHTML = '<tr><td colspan="7" style="text-align:center; color:#999; padding:20px;">Henüz eklenmiş satış fırsatı bulunmuyor.</td></tr>';
            }

            db.firsatlar.forEach((f, index) => {
                const musteri = db.musteriler.find(m => m.id == f.musteri_id)?.ad || '-';
                const urun = db.urunler.find(u => u.id == f.urun_id)?.ad || '-';
                const statu = db.statuler.find(s => s.id == f.statu_id)?.ad || 'Açık';
                
                const gelir = parseFloat(f.beklenen_gelir) || 0;
                const olasilik = parseFloat(f.olasilik) || 0;

                if(statu === 'Kazanıldı') {
                    kazanilanToplam += gelir;
                } else if(statu !== 'Kaybedildi') {
                    acikToplam += gelir;
                    agirlikliTahmin += (gelir * (olasilik / 100)); // Excel Topla.Çarpım mantığı
                }

                const tr = document.createElement('tr');
                const t = f.tarih ? f.tarih.split('-').reverse().join('.') : '-';
                
                tr.innerHTML = `
                    <td><strong>${musteri}</strong></td>
                    <td>${urun}</td>
                    <td>${paraFormat(gelir)}</td>
                    <td>%${olasilik}</td>
                    <td><span class="badge ${durumSinifiGuncelle(statu)}">${statu}</span></td>
                    <td>${t}</td>
                    <td><button type="button" class="btn-delete" onclick="firsatSil(${index})"><i class="fa-solid fa-trash-can"></i></button></td>
                `;
                tbody.appendChild(tr);
            });

            document.getElementById('m-acik').innerText = paraFormat(acikToplam);
            document.getElementById('m-kazanilan').innerText = paraFormat(kazanilanToplam);
            document.getElementById('m-tahmin').innerText = paraFormat(agirlikliTahmin);
        }

        function setupDropdown(id, liste, varsayilanMetin) {
            const el = document.getElementById(id);
            const eskiDeger = el.value;
            el.innerHTML = varsayilanMetin ? `<option value="">${varsayilanMetin}</option>` : '';
            liste.forEach(item => {
                el.innerHTML += `<option value="${item.id}">${item.ad}</option>`;
            });
            if(eskiDeger) el.value = eskiDeger;
        }

        function renderAyarlarListesi(id, liste, key) {
            const ul = document.getElementById(id);
            ul.innerHTML = '';
            liste.forEach(item => {
                ul.innerHTML += `<li>
                    <span>${item.ad}</span>
                    <button type="button" class="btn-delete" onclick="dinamikSil('${key}', ${item.id})"><i class="fa-solid fa-xmark"></i></button>
                </li>`;
            });
        }

        function dinamikEkle(key, inputId) {
            const input = document.getElementById(inputId);
            const deger = input.value.trim();
            if(!deger) return;

            const yeniId = db[key].length > 0 ? Math.max(...db[key].map(o => o.id)) + 1 : 1;
            db[key].push({id: yeniId, ad: deger});
            input.value = '';
            dbKaydet();
        }

        function dinamikSil(key, id) {
            if(confirm('Bu tanımı silmek istediğinize emin misiniz?')) {
                db[key] = db[key].filter(item => item.id != id);
                dbKaydet();
            }
        }

        document.getElementById('firsatForm').addEventListener('submit', function(e) {
            e.preventDefault();
            const yeniFirsat = {
                musteri_id: document.getElementById('f-musteri').value,
                urun_id: document.getElementById('f-urun').value,
                beklenen_gelir: document.getElementById('f-gelir').value,
                olasilik: document.getElementById('f-olasilik').value,
                statu_id: document.getElementById('f-statu').value,
                tarih: document.getElementById('f-tarih').value
            };
            db.firsatlar.push(yeniFirsat);
            document.getElementById('f-gelir').value = '0';
            document.getElementById('f-olasilik').value = '50';
            dbKaydet();
        });

        window.firsatSil = function(index) {
            if(confirm('Bu fırsat kaydını silmek istiyor musunuz?')) {
                db.firsatlar.splice(index, 1);
                dbKaydet();
            }
        }

        // İlk açılış
        verileriTazele();
    </script>
</body>
</html>
"""

@app.route('/')
def ana_sayfa():
    return render_template_string(HTML_TEMPLATE)
