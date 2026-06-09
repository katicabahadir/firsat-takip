from flask import Flask, render_template_string

app = Flask(__name__)

# v3.5: Gelişmiş Raporlama, Dinamik Grafikler ve Anlık Filtreleme Altyapısı
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <title>Gelişmiş Fırsat Takip Portalı</title>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Segoe UI', sans-serif; }
        body { background-color: #f4f6f9; color: #333; }
        header { background-color: #1e3a8a; color: white; padding: 15px 20px; display: flex; justify-content: space-between; align-items: center; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        nav button { background: none; border: 1px solid white; color: white; padding: 8px 15px; margin-left: 10px; border-radius: 4px; cursor: pointer; font-weight: bold; transition: 0.2s; }
        nav button:hover, nav button.active { background-color: white; color: #1e3a8a; }
        .container { max-width: 1400px; margin: 20px auto; padding: 0 20px; }
        .sayfa { display: none; }
        .sayfa.active { display: block; }
        
        /* Özet Kartları */
        .dashboard-summary { display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; margin-bottom: 20px; }
        .card { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); border-left: 5px solid #1e3a8a; display: flex; justify-content: space-between; align-items: center; }
        .card.success { border-left-color: #10b981; }
        .card.warning { border-left-color: #f59e0b; }
        .card h3 { font-size: 13px; color: #6b7280; text-transform: uppercase; font-weight: 600; }
        .card .value { font-size: 24px; font-weight: bold; margin-top: 5px; }
        
        /* Ana Blok Düzeni */
        .ana-icerik { display: flex; gap: 20px; align-items: flex-start; }
        .sol-kolon { width: 350px; display: flex; flex-direction: column; gap: 20px; }
        .form-section, .grafik-section { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
        .sag-tablo { background: white; flex: 1; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); min-height: 500px; }
        
        h2 { font-size: 16px; margin-bottom: 15px; color: #1e3a8a; border-bottom: 2px solid #f3f4f6; padding-bottom: 5px; display: flex; align-items: center; gap: 8px; }
        .form-group { margin-bottom: 12px; }
        .form-group label { display: block; margin-bottom: 4px; font-weight: 600; font-size: 13px; color: #4b5563; }
        .form-group input, .form-group select { width: 100%; padding: 9px; border: 1px solid #d1d5db; border-radius: 6px; font-size: 14px; outline: none; }
        .form-group input:focus, .form-group select:focus { border-color: #1e3a8a; }
        button.btn-primary { width: 100%; background-color: #1e3a8a; color: white; border: none; padding: 12px; border-radius: 6px; font-weight: bold; cursor: pointer; font-size: 14px; transition: 0.2s; }
        button.btn-primary:hover { background-color: #1d4ed8; }
        
        /* Filtreleme Çubuğu */
        .filtre-bar { background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 6px; padding: 12px; margin-bottom: 15px; display: grid; grid-template-columns: 2fr repeat(3, 1fr); gap: 10px; }
        
        /* Tablo Stilleri */
        table { width: 100%; border-collapse: collapse; font-size: 14px; }
        th, td { padding: 12px; border-bottom: 1px solid #e5e7eb; text-align: left; }
        th { background-color: #f8fafc; color: #475569; font-weight: 600; }
        tr:hover { background-color: #f8fafc; }
        .btn-delete { background: none; border: none; color: #ef4444; cursor: pointer; transition: 0.2s; }
        .btn-delete:hover { color: #b91c1c; }
        
        /* Rozetler */
        .badge { padding: 4px 8px; border-radius: 4px; font-size: 12px; font-weight: bold; background-color: #e0f2fe; color: #0369a1; }
        .badge.kazanildi { background-color: #d1fae5; color: #065f46; }
        .badge.kaybedildi { background-color: #fee2e2; color: #991b1b; }
        .badge.teklif { background-color: #fef3c7; color: #b45309; }
        .badge.ertelendi { background-color: #f3f4f6; color: #374151; }
        
        ul { list-style: none; }
        li { display: flex; justify-content: space-between; padding: 8px 10px; border-bottom: 1px solid #eee; background: #fafafa; margin-bottom: 5px; border-radius: 4px; font-size: 14px; }
        .grafik-konteyner { position: relative; width: 100%; height: 220px; display: flex; justify-content: center; }
    </style>
</head>
<body>

    <header>
        <h1><i class="fa-solid fa-chart-pie"></i> Fırsat Yönetim Paneli v3.5</h1>
        <nav>
            <button onclick="sayfaDegistir('firsatlar-sayfa')" id="btn-firsatlar-sayfa" class="active"><i class="fa-solid fa-table-list"></i> Fırsat Takibi</button>
            <button onclick="sayfaDegistir('ayarlar-sayfa')" id="btn-ayarlar-sayfa"><i class="fa-solid fa-sliders"></i> Dinamik Veri Tanımları</button>
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
                    <div><h3>Kazanılan Toplam Ciro</h3><div class="value" id="m-kazanilan">0 TL</div></div>
                    <i class="fa-solid fa-wallet fa-2x" style="color:#10b981"></i>
                </div>
                <div class="card warning">
                    <div><h3>Ağırlıklı Tahmini Gelir (SUMPRODUCT)</h3><div class="value" id="m-tahmin">0 TL</div></div>
                    <i class="fa-solid fa-calculator fa-2x" style="color:#f59e0b"></i>
                </div>
            </div>

            <div class="ana-icerik">
                <div class="sol-kolon">
                    <div class="form-section">
                        <h2><i class="fa-solid fa-plus-circle"></i> Yeni Fırsat Ekle</h2>
                        <form id="firsatForm">
                            <div class="form-group">
                                <label>Müşteri / Kurum</label>
                                <select id="f-musteri" required><option value="">Seçin...</option></select>
                            </div>
                            <div class="form-group">
                                <label>Ürün / Çözüm</label>
                                <select id="f-urun" required><option value="">Seçin...</option></select>
                            </div>
                            <div class="form-group">
                                <label>Beklenen Gelir (TL)</label>
                                <input type="number" id="f-gelir" value="0" min="0">
                            </div>
                            <div class="form-group">
                                <label>Kazanma Olasılığı (%)</label>
                                <input type="number" id="f-olasilik" value="50" min="0" max="100">
                            </div>
                            <div class="form-group">
                                <label>Fırsat Statüsü</label>
                                <select id="f-statu" required></select>
                            </div>
                            <div class="form-group">
                                <label>Tahmini Kapanış</label>
                                <input type="date" id="f-tarih">
                            </div>
                            <button type="submit" class="btn-primary">Fırsatı Havuza Kaydet</button>
                        </form>
                    </div>

                    <div class="grafik-section">
                        <h2><i class="fa-solid fa-chart-donut"></i> Hacimsel Statü Dağılımı</h2>
                        <div class="grafik-konteyner">
                            <canvas id="statuGrafik"></canvas>
                        </div>
                    </div>
                </div>

                <div class="sag-tablo">
                    <h2><i class="fa-solid fa-list"></i> Güncel Fırsat Havuzu</h2>
                    
                    <div class="filtre-bar">
                        <input type="text" id="arama-firma" placeholder="Firma / Kurum adına göre ara..." oninput="verileriTazele()">
                        <select id="filtre-musteri" onchange="verileriTazele()"><option value="">Tüm Müşteriler</option></select>
                        <select id="filtre-urun" onchange="verileriTazele()"><option value="">Tüm Ürünler</option></select>
                        <select id="filtre-statu" onchange="verileriTazele()"><option value="">Tüm Statüler</option></select>
                    </div>

                    <table>
                        <thead>
                            <tr>
                                <th>Müşteri / Kurum</th>
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
                        <input type="text" id="yeni-musteri" placeholder="Yeni Kurum Adı" style="flex:1; padding:8px; border:1px solid #ddd; border-radius:4px;">
                        <button type="button" onclick="dinamikEkle('musteriler', 'yeni-musteri')" style="padding:8px 12px; background:#1e3a8a; color:white; border:none; border-radius:4px; cursor:pointer;">Ekle</button>
                    </div>
                    <ul id="liste-musteriler"></ul>
                </div>

                <div class="sol-form" style="width:100%">
                    <h2><i class="fa-solid fa-box"></i> Dinamik Ürünler</h2>
                    <div style="display:flex; gap:5px; margin-bottom:15px;">
                        <input type="text" id="yeni-urun" placeholder="Yeni Ürün/Modül" style="flex:1; padding:8px; border:1px solid #ddd; border-radius:4px;">
                        <button type="button" onclick="dinamikEkle('urunler', 'yeni-urun')" style="padding:8px 12px; background:#1e3a8a; color:white; border:none; border-radius:4px; cursor:pointer;">Ekle</button>
                    </div>
                    <ul id="liste-urunler"></ul>
                </div>

                <div class="sol-form" style="width:100%">
                    <h2><i class="fa-solid fa-circle-check"></i> Dinamik Statüler</h2>
                    <div style="display:flex; gap:5px; margin-bottom:15px;">
                        <input type="text" id="yeni-statu" placeholder="Yeni Satış Adımı" style="flex:1; padding:8px; border:1px solid #ddd; border-radius:4px;">
                        <button type="button" onclick="dinamikEkle('statuler', 'yeni-statu')" style="padding:8px 12px; background:#1e3a8a; color:white; border:none; border-radius:4px; cursor:pointer;">Ekle</button>
                    </div>
                    <ul id="liste-statuler"></ul>
                </div>
            </div>
        </div>
    </div>

    <script>
        // Veri Yapısı (LocalStorage Senkronize)
        let db = JSON.parse(localStorage.getItem('firsat_takip_db')) || {
            musteriler: [{id: 1, ad: "Kocaeli Büyükşehir Belediyesi"}, {id: 2, ad: "Konya Büyükşehir Belediyesi"}],
            urunler: [{id: 1, ad: "QDMS"}, {id: 2, ad: "Ensemble"}, {id: 3, ad: "Synergy CSP"}, {id: 4, ad: "BEAM"}],
            statuler: [{id: 1, ad: "Açık"}, {id: 2, ad: "Teklif Verildi"}, {id: 3, ad: "Kazanıldı"}, {id: 4, ad: "Kaybedildi"}, {id: 5, ad: "Ertelendi"}],
            firsatlar: []
        };

        document.getElementById('f-tarih').valueAsDate = new Date();
        let myChart = null; // Grafik nesnesi holding alanı

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

        // ANA YENİLEME VE HESAPLAMA MOTORU
        function verileriTazele() {
            // Dropdown ve Filtre Seçeneklerini Doldur
            setupDropdown('f-musteri', db.musteriler, 'Müşteri Seçin...', 'filtre-musteri', 'Tüm Müşteriler');
            setupDropdown('f-urun', db.urunler, 'Ürün Seçin...', 'filtre-urun', 'Tüm Ürünler');
            setupDropdown('f-statu', db.statuler, null, 'filtre-statu', 'Tüm Statüler');

            renderAyarlarListesi('liste-musteriler', db.musteriler, 'musteriler');
            renderAyarlarListesi('liste-urunler', db.urunler, 'urunler');
            renderAyarlarListesi('liste-statuler', db.statuler, 'statuler');

            const tbody = document.getElementById('firsat-tablo-vucut');
            tbody.innerHTML = '';
            
            let acikToplam = 0, kazanilanToplam = 0, agirlikliTahmin = 0;
            
            // Grafik için veri havuzu
            let grafikVerileri = {};
            db.statuler.forEach(s => grafikVerileri[s.ad] = 0);

            // Aktif Filtre Değerlerini Al (3. Aşama)
            const aramaMetni = document.getElementById('arama-firma').value.toLowerCase();
            const fMusteri = document.getElementById('filtre-musteri').value;
            const fUrun = document.getElementById('filtre-urun').value;
            const fStatu = document.getElementById('filtre-statu').value;

            let gosterilenFirsatSayisi = 0;

            db.firsatlar.forEach((f, index) => {
                const musteriObj = db.musteriler.find(m => m.id == f.musteri_id);
                const urunObj = db.urunler.find(u => u.id == f.urun_id);
                const statuObj = db.statuler.find(s => s.id == f.statu_id);

                const musteriAd = musteriObj?.ad || '-';
                const urunAd = urunObj?.ad || '-';
                const statuAd = statuObj?.ad || 'Açık';
                
                const gelir = parseFloat(f.beklenen_gelir) || 0;
                const olasilik = parseFloat(f.olasilik) || 0;

                // Üst Kart Hesaplamaları (Tüm Havuz Üzerinden)
                if(statuAd === 'Kazanıldı') {
                    kazanilanToplam += gelir;
                } else if(statuAd !== 'Kaybedildi') {
                    acikToplam += gelir;
                    agirlikliTahmin += (gelir * (olasilik / 100));
                }

                // Grafik Datası Biriktir
                if(grafikVerileri[statuAd] !== undefined) {
                    grafikVerileri[statuAd] += gelir;
                }

                // Filtreleme Kontrolleri
                if (aramaMetni && !musteriAd.toLowerCase().includes(aramaMetni)) return;
                if (fMusteri && f.musteri_id != fMusteri) return;
                if (fUrun && f.urun_id != fUrun) return;
                if (fStatu && f.statu_id != fStatu) return;

                gosterilenFirsatSayisi++;

                const tr = document.createElement('tr');
                const t = f.tarih ? f.tarih.split('-').reverse().join('.') : '-';
                
                tr.innerHTML = `
                    <td><strong>${musteriAd}</strong></td>
                    <td>${urunAd}</td>
                    <td>${paraFormat(gelir)}</td>
                    <td>%${olasilik}</td>
                    <td><span class="badge ${durumSinifiGuncelle(statuAd)}">${statuAd}</span></td>
                    <td>${t}</td>
                    <td><button type="button" class="btn-delete" onclick="firsatSil(${index})"><i class="fa-solid fa-trash-can"></i></button></td>
                `;
                tbody.appendChild(tr);
            });

            if (gosterilenFirsatSayisi === 0) {
                tbody.innerHTML = '<tr><td colspan="7" style="text-align:center; color:#999; padding:20px;">Aranan kriterlere uygun fırsat kaydı bulunamadı.</td></tr>';
            }

            // Kartları Yazdır
            document.getElementById('m-acik').innerText = paraFormat(acikToplam);
            document.getElementById('m-kazanilan').innerText = paraFormat(kazanilanToplam);
            document.getElementById('m-tahmin').innerText = paraFormat(agirlikliTahmin);

            // Grafiği Çiz / Güncelle (2. Aşama)
            grafikGuncelle(grafikVerileri);
        }

        // ÇİFT YÖNLÜ DROPDOWN AYARLAYICI
        function setupDropdown(formId, liste, formVarsayilan, filtreId, filtreVarsayilan) {
            const formEl = document.getElementById(formId);
            const filtreEl = document.getElementById(filtreId);
            
            const eskiFormVal = formEl.value;
            const eskiFiltreVal = filtreEl.value;

            formEl.innerHTML = formVarsayilan ? `<option value="">${formVarsayilan}</option>` : '';
            filtreEl.innerHTML = `<option value="">${filtreVarsayilan}</option>`;

            liste.forEach(item => {
                const opt = `<option value="${item.id}">${item.ad}</option>`;
                formEl.innerHTML += opt;
                filtreEl.innerHTML += opt;
            });

            if(eskiFormVal) formEl.value = eskiFormVal;
            if(eskiFiltreVal) filtreEl.value = eskiFiltreVal;
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

        // CHART.JS DİNAMİK GRAFİK FONKSİYONU
        function grafikGuncelle(veriObj) {
            const ctx = document.getElementById('statuGrafik').getContext('2d');
            const etiketler = Object.keys(veriObj);
            const degerler = Object.values(veriObj);

            if (myChart) {
                myChart.data.labels = etiketler;
                myChart.data.datasets[0].data = degerler;
                myChart.update();
            } else {
                myChart = new Chart(ctx, {
                    type: 'doughnut',
                    data: {
                        labels: etiketler,
                        datasets: [{
                            data: degerler,
                            backgroundColor: ['#3b82f6', '#f59e0b', '#10b981', '#ef4444', '#6b7280'],
                            borderWidth: 1
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {
                            legend: { position: 'bottom', labels: { boxWidth: 12, font: { size: 11 } } }
                        }
                    }
                });
            }
        }

        // VERİ EKLEME VE SİLME AKSİYONLARI
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
            if(confirm('Bu fırsat kaydını havuzdan silmek istediğinize emin misiniz?')) {
                db.firsatlar.splice(index, 1);
                dbKaydet();
            }
        }

        // Açılış Tetikleyicisi
        verileriTazele();
    </script>
</body>
</html>
"""

@app.route('/')
def ana_sayfa():
    return render_template_string(HTML_TEMPLATE)
