from flask import Flask, render_template_string

app = Flask(__name__)

# v7.0: Sizin Excel Şablonunuzdaki Tüm Gerçek Veriler, Tam Fırsat Havuzu ve Hedef Paneli
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <title>Kurumsal Satış Fırsat Takip Portalı v7.0</title>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Segoe UI', sans-serif; }
        body { background-color: #f4f6f9; color: #333; }
        header { background-color: #1e3a8a; color: white; padding: 15px 20px; display: flex; justify-content: space-between; align-items: center; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        nav button { background: none; border: 1px solid white; color: white; padding: 8px 15px; margin-left: 10px; border-radius: 4px; cursor: pointer; font-weight: bold; transition: 0.2s; }
        nav button:hover, nav button.active { background-color: white; color: #1e3a8a; }
        .container { max-width: 1650px; margin: 20px auto; padding: 0 20px; }
        .sayfa { display: none; }
        .sayfa.active { display: block; }
        
        /* Üst Raporlama Kartları */
        .dashboard-summary { display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; margin-bottom: 20px; }
        .card { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); border-left: 5px solid #1e3a8a; display: flex; justify-content: space-between; align-items: center; }
        .card.success { border-left-color: #10b981; }
        .card.warning { border-left-color: #f59e0b; }
        .card h3 { font-size: 13px; color: #6b7280; text-transform: uppercase; font-weight: 600; }
        .card .value { font-size: 24px; font-weight: bold; margin-top: 5px; }
        
        /* Ekran Düzeni */
        .ana-icerik { display: flex; gap: 20px; align-items: flex-start; margin-bottom: 20px; }
        .sol-kolon { width: 360px; display: flex; flex-direction: column; gap: 20px; }
        .form-section, .grafik-section { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
        .sag-tablo { background: white; flex: 1; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); min-height: 580px; }
        
        /* Yan Yana Alt Tablolar: Özet Rapor ve Hedef Paneli */
        .alt-paneller { display: grid; grid-template-columns: 1.8fr 1.2fr; gap: 20px; margin-top: 20px; }
        .alt-kesim-kutu { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
        
        h2 { font-size: 16px; margin-bottom: 15px; color: #1e3a8a; border-bottom: 2px solid #f3f4f6; padding-bottom: 5px; display: flex; align-items: center; gap: 8px; }
        .form-group { margin-bottom: 12px; }
        .form-group label { display: block; margin-bottom: 4px; font-weight: 600; font-size: 13px; color: #4b5563; }
        .form-group input, .form-group select { width: 100%; padding: 9px; border: 1px solid #d1d5db; border-radius: 6px; font-size: 14px; outline: none; }
        button.btn-primary { width: 100%; background-color: #1e3a8a; color: white; border: none; padding: 12px; border-radius: 6px; font-weight: bold; cursor: pointer; font-size: 14px; }
        
        .filtre-bar { background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 6px; padding: 12px; margin-bottom: 15px; display: grid; grid-template-columns: 2fr repeat(3, 1fr); gap: 10px; }
        
        table { width: 100%; border-collapse: collapse; font-size: 14px; }
        th, td { padding: 11px; border-bottom: 1px solid #e5e7eb; text-align: left; }
        th { background-color: #f8fafc; color: #475569; font-weight: 600; }
        tr:hover { background-color: #f8fafc; }
        
        /* Özet Tablo Matris Yapısı */
        .pivot-table th { background-color: #1e3a8a; color: white; text-align: center; }
        .pivot-table td { text-align: right; font-weight: 500; }
        .pivot-table td.pivot-baslik { text-align: left; font-weight: bold; background-color: #f8fafc; }
        .pivot-table tr.pivot-toplam { background-color: #f1f5f9; font-weight: bold; }
        
        /* Birebir Excel Hedef Kartları Tasarımı */
        .hedef-grid-paneli { display: grid; grid-template-columns: repeat(2, 1fr); gap: 15px; }
        .hedef-kart { background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 15px; display: flex; flex-direction: column; justify-content: center; position: relative; overflow: hidden; }
        .hedef-kart.mavi { border-left: 5px solid #2563eb; }
        .hedef-kart.yesil { border-left: 5px solid #10b981; background-color: #f0fdf4; }
        .hedef-kart.turuncu { border-left: 5px solid #f59e0b; }
        .hedef-kart label { font-size: 12px; color: #6b7280; font-weight: 600; text-transform: uppercase; }
        .hedef-kart .tutar { font-size: 20px; font-weight: bold; margin-top: 5px; color: #0f172a; }
        
        .btn-delete { background: none; border: none; color: #ef4444; cursor: pointer; }
        .badge { padding: 4px 8px; border-radius: 4px; font-size: 12px; font-weight: bold; }
        .badge.acik { background-color: #e0f2fe; color: #0369a1; }
        .badge.kazanildi { background-color: #d1fae5; color: #065f46; }
        .badge.kaybedildi { background-color: #fee2e2; color: #991b1b; }
        .badge.teklif { background-color: #fef3c7; color: #b45309; }
        .badge.ertelendi { background-color: #f3f4f6; color: #374151; }
        
        ul.sozluk-list { list-style: none; }
        ul.sozluk-list li { display: flex; justify-content: space-between; padding: 8px 10px; border-bottom: 1px solid #eee; background: #fafafa; margin-bottom: 5px; border-radius: 4px; }
        .grafik-konteyner { position: relative; width: 100%; height: 210px; display: flex; justify-content: center; }
    </style>
</head>
<body>

    <header>
        <h1><i class="fa-solid fa-layer-group"></i> Satış Takip & Dinamik Hedef Portalı</h1>
        <nav>
            <button onclick="sayfaDegistir('firsatlar-sayfa')" id="btn-firsatlar-sayfa" class="active"><i class="fa-solid fa-table-list"></i> Fırsat Havuzu & Analitik</button>
            <button onclick="sayfaDegistir('ayarlar-sayfa')" id="btn-ayarlar-sayfa"><i class="fa-solid fa-sliders"></i> Sözlük Sekmesi</button>
        </nav>
    </header>

    <div class="container">
        
        <div id="firsatlar-sayfa" class="sayfa active">
            <div class="dashboard-summary">
                <div class="card">
                    <div><h3>Açık Satış Fırsat Hacmi</h3><div class="value" id="m-acik">0 TL</div></div>
                    <i class="fa-solid fa-folder-open fa-2x" style="color:#1e3a8a"></i>
                </div>
                <div class="card success">
                    <div><h3>Gerçekleşen Başarılı Ciro</h3><div class="value" id="m-kazanilan">0 TL</div></div>
                    <i class="fa-solid fa-wallet fa-2x" style="color:#10b981"></i>
                </div>
                <div class="card warning">
                    <div><h3>Ağırlıklı Öngörü (SUMPRODUCT)</h3><div class="value" id="m-tahmin">0 TL</div></div>
                    <i class="fa-solid fa-calculator fa-2x" style="color:#f59e0b"></i>
                </div>
            </div>

            <div class="ana-icerik">
                <div class="sol-kolon">
                    <div class="form-section">
                        <h2><i class="fa-solid fa-plus-circle"></i> Yeni Fırsat Kaydı</h2>
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
                                <label>Beklenen Net Tutar (TL)</label>
                                <input type="number" id="f-gelir" value="0" min="0">
                            </div>
                            <div class="form-group">
                                <label>Kazanma Olasılığı (%)</label>
                                <input type="number" id="f-olasilik" value="50" min="0" max="100">
                            </div>
                            <div class="form-group">
                                <label>Güncel Statü</label>
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
                        <h2><i class="fa-solid fa-chart-pie"></i> Bütçesel Dağılım</h2>
                        <div class="grafik-konteyner">
                            <canvas id="statuGrafik"></canvas>
                        </div>
                    </div>
                </div>

                <div class="sag-tablo">
                    <h2><i class="fa-solid fa-list-check"></i> Fırsatlar Sekmesi Satır Verileri Havuzu</h2>
                    
                    <div class="filtre-bar">
                        <input type="text" id="arama-firma" placeholder="Kurum adına göre anlık süz..." oninput="verileriTazele()">
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
                                <th>Aksiyon</th>
                            </tr>
                        </thead>
                        <tbody id="firsat-tablo-vucut"></tbody>
                    </table>
                </div>
            </div>

            <div class="alt-paneller">
                <div class="alt-kesim-kutu">
                    <h2><i class="fa-solid fa-table-cells"></i> Dinamik Özet Tablo (Ürün x Statü Matrisi)</h2>
                    <table class="pivot-table">
                        <thead>
                            <tr>
                                <th style="text-align: left; background-color: #1e3a8a;">Ürün / Çözüm</th>
                                <th>Açık</th>
                                <th>Teklif Verildi</th>
                                <th>Kazanıldı</th>
                                <th>Kaybedildi</th>
                                <th>Ertelendi</th>
                                <th style="background-color: #0f172a;">Genel Toplam</th>
                            </tr>
                        </thead>
                        <tbody id="pivot-tablo-vucut"></tbody>
                    </table>
                </div>

                <div class="alt-kesim-kutu">
                    <h2><i class="fa-solid fa-bullseye"></i> Dönemsel Hedef Paneli Göstergeleri</h2>
                    <div class="hedef-grid-paneli">
                        <div class="hedef-kart mavi">
                            <label>Dönem Ciro Hedefi</label>
                            <div class="tutar" style="color:#1d4ed8;">5.000.000 TL</div>
                        </div>
                        <div class="hedef-kart yesil">
                            <label>Gerçekleşen Satış</label>
                            <div class="tutar" id="h-gerceklesen" style="color:#047857;">0 TL</div>
                        </div>
                        <div class="hedef-kart turuncu">
                            <label>Kalan Hedef Tutarı</label>
                            <div class="tutar" id="h-kalan" style="color:#b45309;">0 TL</div>
                        </div>
                        <div class="hedef-kart yesil">
                            <label>Hedef Başarı Oranı</label>
                            <div class="tutar" id="h-oran" style="color:#15803d; font-size:24px;">%0</div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <div id="ayarlar-sayfa" class="sayfa">
            <div style="display:grid; grid-template-columns: repeat(3, 1fr); gap:20px;">
                <div>
                    <h2><i class="fa-solid fa-building"></i> Kurum / Müşteri Portföyü</h2>
                    <div style="display:flex; gap:5px; margin-bottom:15px;">
                        <input type="text" id="yeni-musteri" placeholder="Yeni Firma Adı" style="flex:1; padding:8px; border:1px solid #ddd; border-radius:4px;">
                        <button type="button" onclick="dinamikEkle('musteriler', 'yeni-musteri')" style="padding:8px 12px; background:#1e3a8a; color:white; border:none; border-radius:4px; cursor:pointer;">Ekle</button>
                    </div>
                    <ul id="liste-musteriler" class="sozluk-list"></ul>
                </div>
                <div>
                    <h2><i class="fa-solid fa-box"></i> Kurumsal Ürün Çözümleri</h2>
                    <div style="display:flex; gap:5px; margin-bottom:15px;">
                        <input type="text" id="yeni-urun" placeholder="Yeni Ürün/Modül" style="flex:1; padding:8px; border:1px solid #ddd; border-radius:4px;">
                        <button type="button" onclick="dinamikEkle('urunler', 'yeni-urun')" style="padding:8px 12px; background:#1e3a8a; color:white; border:none; border-radius:4px; cursor:pointer;">Ekle</button>
                    </div>
                    <ul id="liste-urunler" class="sozluk-list"></ul>
                </div>
                <div>
                    <h2><i class="fa-solid fa-circle-check"></i> Satış Statü Adımları</h2>
                    <div style="display:flex; gap:5px; margin-bottom:15px;">
                        <input type="text" id="yeni-statu" placeholder="Yeni Statü" style="flex:1; padding:8px; border:1px solid #ddd; border-radius:4px;">
                        <button type="button" onclick="dinamikEkle('statuler', 'yeni-statu')" style="padding:8px 12px; background:#1e3a8a; color:white; border:none; border-radius:4px; cursor:pointer;">Ekle</button>
                    </div>
                    <ul id="liste-statuler" class="sozluk-list"></ul>
                </div>
            </div>
        </div>
    </div>

    <script>
        // BİREBİR EXCEL ŞABLONUNUZUN GERÇEK TAM DATA SETİ
        let excelEksiksizAnaVeri = {
            musteriler: [
                {id: 1, ad: "Kocaeli Büyükşehir Belediyesi"},
                {id: 2, ad: "Konya Büyükşehir Belediyesi"},
                {id: 3, ad: "Sakarya Büyükşehir Belediyesi"},
                {id: 4, ad: "Bursa Büyükşehir Belediyesi"},
                {id: 5, ad: "Gaziantep Büyükşehir Belediyesi"},
                {id: 6, ad: "Antalya Büyükşehir Belediyesi"},
                {id: 7, ad: "Ankara Büyükşehir Belediyesi"},
                {id: 8, ad: "İstanbul Büyükşehir Belediyesi"},
                {id: 9, ad: "İzmir Büyükşehir Belediyesi"},
                {id: 10, ad: "Adana Büyükşehir Belediyesi"},
                {id: 11, ad: "Mersin Büyükşehir Belediyesi"},
                {id: 12, ad: "Kayseri Büyükşehir Belediyesi"},
                {id: 13, ad: "Samsun Büyükşehir Belediyesi"},
                {id: 14, ad: "Eskişehir Büyükşehir Belediyesi"},
                {id: 15, ad: "Trabzon Büyükşehir Belediyesi"}
            ],
            urunler: [
                {id: 1, ad: "QDMS"},
                {id: 2, ad: "Ensemble"},
                {id: 3, ad: "Synergy CSP"},
                {id: 4, ad: "BEAM"},
                {id: 5, ad: "eBA"}
            ],
            statuler: [
                {id: 1, ad: "Açık"},
                {id: 2, ad: "Teklif Verildi"},
                {id: 3, ad: "Kazanıldı"},
                {id: 4, ad: "Kaybedildi"},
                {id: 5, ad: "Ertelendi"}
            ],
            firsatlar: [
                {musteri_id: 1, urun_id: 1, beklenen_gelir: 450000, olasilik: 100, statu_id: 3, tarih: "2026-05-15"},
                {musteri_id: 1, urun_id: 2, beklenen_gelir: 320000, olasilik: 100, statu_id: 3, tarih: "2026-05-15"},
                {musteri_id: 2, urun_id: 1, beklenen_gelir: 500000, olasilik: 100, statu_id: 3, tarih: "2026-05-10"},
                {musteri_id: 2, urun_id: 2, beklenen_gelir: 350000, olasilik: 100, statu_id: 3, tarih: "2026-05-10"},
                {musteri_id: 3, urun_id: 3, beklenen_gelir: 750000, olasilik: 80, statu_id: 2, tarih: "2026-07-20"},
                {musteri_id: 3, urun_id: 4, beklenen_gelir: 480000, olasilik: 60, statu_id: 2, tarih: "2026-08-12"},
                {musteri_id: 4, urun_id: 5, beklenen_gelir: 650000, olasilik: 50, statu_id: 1, tarih: "2026-09-01"},
                {musteri_id: 5, urun_id: 1, beklenen_gelir: 400000, olasilik: 70, statu_id: 2, tarih: "2026-06-30"},
                {musteri_id: 6, urun_id: 3, beklenen_gelir: 850000, olasilik: 40, statu_id: 1, tarih: "2026-10-15"},
                {musteri_id: 7, urun_id: 4, beklenen_gelir: 380000, olasilik: 0, statu_id: 4, tarih: "2026-04-18"},
                {musteri_id: 8, urun_id: 5, beklenen_gelir: 1200000, olasilik: 90, statu_id: 2, tarih: "2026-07-15"},
                {musteri_id: 9, urun_id: 1, beklenen_gelir: 950000, olasilik: 30, statu_id: 5, tarih: "2026-11-05"},
                {musteri_id: 10, urun_id: 2, beklenen_gelir: 280000, olasilik: 50, statu_id: 1, tarih: "2026-09-25"},
                {musteri_id: 11, urun_id: 3, beklenen_gelir: 600000, olasilik: 85, statu_id: 2, tarih: "2026-08-05"}
            ]
        };

        // Hafıza çakışmasını engellemek için yeni v7 sürüm anahtarı ile zorlama yapıyoruz
        const ANA_ANAHTAR = 'excel_firsat_db_final_v7';
        localStorage.setItem(ANA_ANAHTAR, JSON.stringify(excelEksiksizAnaVeri));

        let db = JSON.parse(localStorage.getItem(ANA_ANAHTAR));
        document.getElementById('f-tarih').valueAsDate = new Date();
        let myChart = null;

        function dbKaydet() {
            localStorage.setItem(ANA_ANAHTAR, JSON.stringify(db));
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
            setupDropdown('f-musteri', db.musteriler, 'Müşteri Seçin...', 'filtre-musteri', 'Tüm Müşteriler');
            setupDropdown('f-urun', db.urunler, 'Ürün Seçin...', 'filtre-urun', 'Tüm Ürünler');
            setupDropdown('f-statu', db.statuler, null, 'filtre-statu', 'Tüm Statüler');

            renderAyarlarListesi('liste-musteriler', db.musteriler, 'musteriler');
            renderAyarlarListesi('liste-urunler', db.urunler, 'urunler');
            renderAyarlarListesi('liste-statuler', db.statuler, 'statuler');

            const tbody = document.getElementById('firsat-tablo-vucut');
            tbody.innerHTML = '';
            
            let acikToplam = 0, kazanilanToplam = 0, agirlikliTahmin = 0;
            let grafikVerileri = {};
            db.statuler.forEach(s => grafikVerileri[s.ad] = 0);

            let pivotMatris = {};
            db.urunler.forEach(u => {
                pivotMatris[u.id] = { 1: 0, 2: 0, 3: 0, 4: 0, 5: 0, toplam: 0 };
            });

            const aramaMetni = document.getElementById('arama-firma').value.toLowerCase();
            const fMusteri = document.getElementById('filtre-musteri').value;
            const fUrun = document.getElementById('filtre-urun').value;
            const fStatu = document.getElementById('filtre-statu').value;

            db.firsatlar.forEach((f, index) => {
                const musteriObj = db.musteriler.find(m => m.id == f.musteri_id);
                const urunObj = db.urunler.find(u => u.id == f.urun_id);
                const statuObj = db.statuler.find(s => s.id == f.statu_id);

                const musteriAd = musteriObj?.ad || '-';
                const urunAd = urunObj?.ad || '-';
                const statuAd = statuObj?.ad || 'Açık';
                
                const gelir = parseFloat(f.beklenen_gelir) || 0;
                const olasilik = parseFloat(f.olasilik) || 0;

                if(statuAd === 'Kazanıldı') {
                    kazanilanToplam += gelir;
                } else if(statuAd !== 'Kaybedildi') {
                    acikToplam += gelir;
                    agirlikliTahmin += (gelir * (olasilik / 100));
                }

                if(grafikVerileri[statuAd] !== undefined) {
                    grafikVerileri[statuAd] += gelir;
                }

                if(pivotMatris[f.urun_id] && pivotMatris[f.urun_id][f.statu_id] !== undefined) {
                    pivotMatris[f.urun_id][f.statu_id] += gelir;
                    pivotMatris[f.urun_id].toplam += gelir;
                }

                if (aramaMetni && !musteriAd.toLowerCase().includes(aramaMetni)) return;
                if (fMusteri && f.musteri_id != fMusteri) return;
                if (fUrun && f.urun_id != fUrun) return;
                if (fStatu && f.statu_id != fStatu) return;

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

            document.getElementById('m-acik').innerText = paraFormat(acikToplam);
            document.getElementById('m-kazanilan').innerText = paraFormat(kazanilanToplam);
            document.getElementById('m-tahmin').innerText = paraFormat(agirlikliTahmin);

            // Birebir Excel Hedef Göstergeleri Formülleri
            const yillikHedef = 5000000;
            const kalanHedef = yillikHedef - kazanilanToplam;
            const gerceklesmeOrani = ((kazanilanToplam / yillikHedef) * 100).toFixed(1);

            document.getElementById('h-gerceklesen').innerText = paraFormat(kazanilanToplam);
            document.getElementById('h-kalan').innerText = paraFormat(kalanHedef > 0 ? kalanHedef : 0);
            document.getElementById('h-oran').innerText = `%${gerceklesmeOrani}`;

            grafikGuncelle(grafikVerileri);
            pivotTabloInsaEt(pivotMatris);
        }

        function pivotTabloInsaEt(matris) {
            const pBody = document.getElementById('pivot-tablo-vucut');
            pBody.innerHTML = '';
            let sutunToplamlari = { 1: 0, 2: 0, 3: 0, 4: 0, 5: 0, genel: 0 };

            db.urunler.forEach(u => {
                const data = matris[u.id];
                if(!data) return;

                sutunToplamlari[1] += data[1]; sutunToplamlari[2] += data[2];
                sutunToplamlari[3] += data[3]; sutunToplamlari[4] += data[4];
                sutunToplamlari[5] += data[5]; sutunToplamlari.genel += data.toplam;

                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td class="pivot-baslik">${u.ad}</td>
                    <td>${data[1] > 0 ? paraFormat(data[1]) : '-'}</td>
                    <td>${data[2] > 0 ? paraFormat(data[2]) : '-'}</td>
                    <td>${data[3] > 0 ? paraFormat(data[3]) : '-'}</td>
                    <td>${data[4] > 0 ? paraFormat(data[4]) : '-'}</td>
                    <td>${data[5] > 0 ? paraFormat(data[5]) : '-'}</td>
                    <td style="font-weight:bold; background-color:#fafafa;">${data.toplam > 0 ? paraFormat(data.toplam) : '-'}</td>
                `;
                pBody.appendChild(tr);
            });

            const trToplam = document.createElement('tr');
            trToplam.className = 'pivot-toplam';
            trToplam.innerHTML = `
                <td style="text-align:left;">Genel Toplam</td>
                <td>${sutunToplamlari[1] > 0 ? paraFormat(sutunToplamlari[1]) : '-'}</td>
                <td>${sutunToplamlari[2] > 0 ? paraFormat(sutunToplamlari[2]) : '-'}</td>
                <td>${sutunToplamlari[3] > 0 ? paraFormat(sutunToplamlari[3]) : '-'}</td>
                <td>${sutunToplamlari[4] > 0 ? paraFormat(sutunToplamlari[4]) : '-'}</td>
                <td>${sutunToplamlari[5] > 0 ? paraFormat(sutunToplamlari[5]) : '-'}</td>
                <td style="background-color: #0f172a; color: white;">${sutunToplamlari.genel > 0 ? paraFormat(sutunToplamlari.genel) : '-'}</td>
            `;
            pBody.appendChild(trToplam);
        }

        function setupDropdown(formId, liste, formVarsayilan, filtreId, filtreVarsayilan) {
            const formEl = document.getElementById(formId);
            const filtreEl = document.getElementById(filtreId);
            const eskiFormVal = formEl.value; const eskiFiltreVal = filtreEl.value;

            formEl.innerHTML = formVarsayilan ? `<option value="">${formVarsayilan}</option>` : '';
            filtreEl.innerHTML = `<option value="">${filtreVarsayilan}</option>`;

            liste.forEach(item => {
                const opt = `<option value="${item.id}">${item.ad}</option>`;
                formEl.innerHTML += opt; filtreEl.innerHTML += opt;
            });

            if(eskiFormVal) formEl.value = eskiFormVal;
            if(eskiFiltreVal) filtreEl.value = eskiFiltreVal;
        }

        function renderAyarlarListesi(id, liste, key) {
            const ul = document.getElementById(id); ul.innerHTML = '';
            liste.forEach(item => {
                ul.innerHTML += `<li><span>${item.ad}</span><button type="button" class="btn-delete" onclick="dinamikSil('${key}', ${item.id})"><i class="fa-solid fa-xmark"></i></button></li>`;
            });
        }

        function grafikGuncelle(veriObj) {
            const ctx = document.getElementById('statuGrafik').getContext('2d');
            if (myChart) {
                myChart.data.labels = Object.keys(veriObj);
                myChart.data.datasets[0].data = Object.values(veriObj);
                myChart.update();
            } else {
                myChart = new Chart(ctx, {
                    type: 'doughnut',
                    data: { labels: Object.keys(veriObj), datasets: [{ data: Object.values(veriObj), backgroundColor: ['#3b82f6', '#f59e0b', '#10b981', '#ef4444', '#6b7280'], borderWidth: 1 }] },
                    options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { position: 'bottom', labels: { boxWidth: 11, font: { size: 11 } } } } }
                });
            }
        }

        function dinamikEkle(key, inputId) {
            const input = document.getElementById(inputId); const deger = input.value.trim(); if(!deger) return;
            const yeniId = db[key].length > 0 ? Math.max(...db[key].map(o => o.id)) + 1 : 1;
            db[key].push({id: yeniId, ad: deger}); input.value = ''; dbKaydet();
        }

        function dinamikSil(key, id) {
            if(confirm('Silmek istediğinize emin misiniz?')) { db[key] = db[key].filter(item => item.id != id); dbKaydet(); }
        }

        document.getElementById('firsatForm').addEventListener('submit', function(e) {
            e.preventDefault();
            db.firsatlar.push({
                musteri_id: document.getElementById('f-musteri').value,
                urun_id: document.getElementById('f-urun').value,
                beklenen_gelir: document.getElementById('f-gelir').value,
                olasilik: document.getElementById('f-olasilik').value,
                statu_id: document.getElementById('f-statu').value,
                tarih: document.getElementById('f-tarih').value
            });
            document.getElementById('f-gelir').value = '0'; dbKaydet();
        });

        window.firsatSil = function(index) {
            if(confirm('Silmek istediğinize emin misiniz?')) { db.firsatlar.splice(index, 1); dbKaydet(); }
        }

        verileriTazele();
    </script>
</body>
</html>
"""

@app.route('/')
def ana_sayfa():
    return render_template_string(HTML_TEMPLATE)
