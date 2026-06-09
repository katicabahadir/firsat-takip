from flask import Flask, render_template_string

app = Flask(__name__)

# v13.1: Hatalardan Arındırılmış, Toplu Excel Kopyala-Yapıştır Destekli Altyapı
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <title>Kurumsal Satış Fırsat Takip Portalı v13.1</title>
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
        
        .dashboard-summary { display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; margin-bottom: 20px; }
        .card { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); border-left: 5px solid #1e3a8a; display: flex; justify-content: space-between; align-items: center; }
        .card.success { border-left-color: #10b981; }
        .card.warning { border-left-color: #f59e0b; }
        .card h3 { font-size: 13px; color: #6b7280; text-transform: uppercase; font-weight: 600; }
        .card .value { font-size: 24px; font-weight: bold; margin-top: 5px; }
        
        .ana-icerik { display: flex; gap: 20px; align-items: flex-start; margin-bottom: 20px; }
        .sol-kolon { width: 360px; display: flex; flex-direction: column; gap: 20px; }
        .form-section, .grafik-section { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
        .sag-tablo { background: white; flex: 1; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); min-height: 580px; }
        
        .alt-paneller { display: grid; grid-template-columns: 1.6fr 1.4fr; gap: 20px; margin-top: 20px; }
        .alt-kesim-kutu { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
        
        h2 { font-size: 16px; margin-bottom: 15px; color: #1e3a8a; border-bottom: 2px solid #f3f4f6; padding-bottom: 5px; display: flex; align-items: center; justify-content: space-between; gap: 8px; }
        .form-group { margin-bottom: 12px; }
        .form-group label { display: block; margin-bottom: 4px; font-weight: 600; font-size: 13px; color: #4b5563; }
        .form-group input, .form-group select { width: 100%; padding: 9px; border: 1px solid #d1d5db; border-radius: 6px; font-size: 14px; outline: none; }
        button.btn-primary { width: 100%; background-color: #1e3a8a; color: white; border: none; padding: 12px; border-radius: 6px; font-weight: bold; cursor: pointer; font-size: 14px; }
        
        button.btn-success { background-color: #10b981; color: white; border: none; padding: 8px 14px; border-radius: 6px; font-weight: bold; cursor: pointer; font-size: 13px; display: flex; align-items: center; gap: 6px; }
        
        .filtre-bar { background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 6px; padding: 12px; margin-bottom: 15px; display: grid; grid-template-columns: 2fr repeat(3, 1fr); gap: 10px; }
        
        table { width: 100%; border-collapse: collapse; font-size: 14px; }
        th, td { padding: 11px; border-bottom: 1px solid #e5e7eb; text-align: left; }
        th { background-color: #f8fafc; color: #475569; font-weight: 600; }
        
        .pivot-table th { background-color: #1e3a8a; color: white; text-align: center; }
        .pivot-table td { text-align: right; font-weight: 500; }
        .pivot-table td.pivot-baslik { text-align: left; font-weight: bold; background-color: #f8fafc; }
        .pivot-table tr.pivot-toplam { background-color: #f1f5f9; font-weight: bold; }
        
        .excel-hedef-container { display: flex; flex-direction: column; gap: 15px; background-color: #f8fafc; padding: 15px; border-radius: 8px; border: 1px solid #e2e8f0; }
        .hedef-kart-satir { display: grid; grid-template-columns: repeat(2, 1fr); gap: 15px; }
        .h-kutu { background: #ffffff; border: 1px solid #cbd5e1; border-radius: 6px; padding: 15px; display: flex; flex-direction: column; justify-content: center; box-shadow: 0 1px 3px rgba(0,0,0,0.02); }
        .h-kutu label { font-size: 11px; color: #64748b; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 4px; }
        .h-kutu .deger { font-size: 20px; font-weight: bold; color: #1e293b; }
        
        .progress-alani { display: flex; flex-direction: column; gap: 5px; margin-top: 5px; width: 100%; }
        .excel-progress-bar { width: 100%; background-color: #e2e8f0; height: 12px; border-radius: 6px; overflow: hidden; border: 1px solid #cbd5e1; }
        .excel-progress-fill { height: 100%; background: linear-gradient(90deg, #10b981, #059669); width: 0%; transition: width 0.5s ease-in-out; }
        
        .toplu-yapistir-kutu { background: #fff; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); margin-bottom: 20px; border: 1px dashed #cbd5e1; }
        textarea.excel-input { width: 100%; height: 110px; padding: 10px; border: 1px solid #cbd5e1; border-radius: 6px; font-family: monospace; font-size: 12px; resize: vertical; outline: none; margin-bottom: 10px; }
        
        .btn-delete { background: none; border: none; color: #ef4444; cursor: pointer; }
        .badge { padding: 4px 8px; border-radius: 4px; font-size: 12px; font-weight: bold; }
        .badge.acik { background-color: #e0f2fe; color: #0369a1; }
        .badge.kazanildi { background-color: #d1fae5; color: #065f46; }
        .badge.kaybedildi { background-color: #fee2e2; color: #991b1b; }
        .badge.teklif { background-color: #fef3c7; color: #b45309; }
        .badge.ertelendi { background-color: #f3f4f6; color: #374151; }
        
        ul.sozluk-list { list-style: none; max-height: 350px; overflow-y: auto; border: 1px solid #e5e7eb; border-radius: 6px; padding: 5px; }
        ul.sozluk-list li { display: flex; justify-content: space-between; padding: 8px 10px; border-bottom: 1px solid #eee; background: #fafafa; margin-bottom: 5px; border-radius: 4px; font-size: 13px; }
        .grafik-konteyner { position: relative; width: 100%; height: 210px; display: flex; justify-content: center; }
    </style>
</head>
<body>

    <header>
        <h1><i class="fa-solid fa-file-excel"></i> Akıllı Satış Fırsat Yönetim Portalı</h1>
        <nav>
            <button onclick="sayfaDegistir('firsatlar-sayfa')" id="btn-firsatlar-sayfa" class="active"><i class="fa-solid fa-table-list"></i> Fırsat Havuzu & Analiz</button>
            <button onclick="sayfaDegistir('ayarlar-sayfa')" id="btn-ayarlar-sayfa"><i class="fa-solid fa-sliders"></i> Sözlük Tanımları</button>
        </nav>
    </header>

    <div class="container">
        
        <div class="toplu-yapistir-kutu">
            <h2 style="border:none; margin-bottom:10px;"><i class="fa-solid fa-paste" style="color:#1e3a8a;"></i> Excel'den Toplu Müşteri Portföyü Yükleme Alanı</h2>
            <p style="font-size:13px; color:#64748b; margin-bottom:12px;">Excel'deki Sözlük sekmesinde yer alan firma isimlerinizin bulunduğu sütunu tamamen seçip kopyalayın ve aşağıdaki kutuya doğrudan yapıştırıp yükle butonuna basın.</p>
            <textarea id="excelMusteriMetin" class="excel-input" placeholder="Excel'den kopyaladığınız firma listesini buraya yapıştırın (Her satırda bir firma olacak şekilde)...&#10;Örn:&#10;Bimser Çözüm&#10;Havelsan&#10;Roketsan"></textarea>
            <div style="display:flex; gap:10px;">
                <button type="button" class="btn-success" onclick="topluMusteriYukle()"><i class="fa-solid fa-upload"></i> Yapıştırılan Firmaları Sözlüğe Aktar</button>
                <button type="button" style="background-color:#64748b; color:white;" class="btn-success" onclick="hafizayiSifirla()"><i class="fa-solid fa-trash-arrow-up"></i> Tüm Sistemi Sıfırla (Bomboş Yap)</button>
            </div>
        </div>

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
                        <h2><i class="fa-solid fa-plus-circle"></i> Yeni Fırsat Girişi</h2>
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
                                <label>Beklenen Tutar (TL)</label>
                                <input type="number" id="f-gelir" value="0" min="0">
                            </div>
                            <div class="form-group">
                                <label>Kazanma Olasılığı (%)</label>
                                <input type="number" id="f-olasilik" value="50" min="0" max="100">
                            </div>
                            <div class="form-group">
                                <label>Mevcut Statü</label>
                                <select id="f-statu" required></select>
                            </div>
                            <div class="form-group">
                                <label>Tahmini Kapanış</label>
                                <input type="date" id="f-tarih">
                            </div>
                            <button type="submit" class="btn-primary">Fırsatı Havuza Ekle</button>
                        </form>
                    </div>

                    <div class="grafik-section">
                        <h2><i class="fa-solid fa-chart-pie"></i> Hacimsel Dağılım</h2>
                        <div class="grafik-konteyner">
                            <canvas id="statuGrafik"></canvas>
                        </div>
                    </div>
                </div>

                <div class="sag-tablo">
                    <h2>
                        <span><i class="fa-solid fa-list-check"></i> Fırsatlar Havuzu Kayıt Listesi</span>
                        <button class="btn-success" onclick="excelDisariAktar()"><i class="fa-solid fa-file-arrow-down"></i> Mevcut Datayı Excel Olarak İndir</button>
                    </h2>
                    
                    <div class="filtre-bar">
                        <input type="text" id="arama-firma" placeholder="Kurum adına göre süz..." oninput="verileriTazele()">
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
                    <h2><i class="fa-solid fa-bullseye"></i> Excel Birebir Hedef Paneli</h2>
                    <div class="excel-hedef-container">
                        <div class="hedef-kart-satir">
                            <div class="h-kutu">
                                <label>Yıllık Hedef</label>
                                <div class="deger" style="color: #1e40af;">5.000.000 TL</div>
                            </div>
                            <div class="h-kutu">
                                <label>Gerçekleşen Satış</label>
                                <div class="deger" id="h-gerceklesen" style="color: #166534;">0 TL</div>
                            </div>
                        </div>
                        <div class="hedef-kart-satir">
                            <div class="h-kutu">
                                <label>Kalan Hedef Tutarı</label>
                                <div class="deger" id="h-kalan" style="color: #9a3412;">0 TL</div>
                            </div>
                            <div class="h-kutu">
                                <label>Hedef Başarı Oranı</label>
                                <div class="progress-alani">
                                    <div class="deger" id="h-oran" style="margin-top: 0; color: #0f172a;">%0</div>
                                    <div class="excel-progress-bar">
                                        <div class="excel-progress-fill" id="h-progress"></div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <div id="ayarlar-sayfa" class="sayfa">
            <div style="display:grid; grid-template-columns: repeat(3, 1fr); gap:20px;">
                <div>
                    <h2><i class="fa-solid fa-building"></i> Müşteri Portföyü Sözlüğü</h2>
                    <div style="display:flex; gap:5px; margin-bottom:15px;">
                        <input type="text" id="yeni-musteri" placeholder="Yeni Kurum Adı" style="flex:1; padding:8px; border:1px solid #ddd; border-radius:4px;">
                        <button type="button" onclick="dinamikEkle('musteriler', 'yeni-musteri')" style="padding:8px 12px; background:#1e3a8a; color:white; border:none; border-radius:4px; cursor:pointer;">Ekle</button>
                    </div>
                    <ul id="liste-musteriler" class="sozluk-list"></ul>
                </div>
                <div>
                    <h2><i class="fa-solid fa-box"></i> Kurumsal Ürün Çözümleri</h2>
                    <div style="display:flex; gap:5px; margin-bottom:15px;">
                        <input type="text" id="yeni-urun" placeholder="Yeni Çözüm Adı" style="flex:1; padding:8px; border:1px solid #ddd; border-radius:4px;">
                        <button type="button" onclick="dinamikEkle('urunler', 'yeni-urun')" style="padding:8px 12px; background:#1e3a8a; color:white; border:none; border-radius:4px; cursor:pointer;">Ekle</button>
                    </div>
                    <ul id="liste-urunler" class="sozluk-list"></ul>
                </div>
                <div>
                    <h2><i class="fa-solid fa-circle-check"></i> Süreç Durumları</h2>
                    <div style="display:flex; gap:5px; margin-bottom:15px;">
                        <input type="text" id="yeni-statu" placeholder="Yeni Satış Adımı" style="flex:1; padding:8px; border:1px solid #ddd; border-radius:4px;">
                        <button type="button" onclick="dinamikEkle('statuler', 'yeni-statu')" style="padding:8px 12px; background:#1e3a8a; color:white; border:none; border-radius:4px; cursor:pointer;">Ekle</button>
                    </div>
                    <ul id="liste-statuler" class="sozluk-list"></ul>
                </div>
            </div>
        </div>
    </div>

    <script>
        let bosTabloYapisi = {
            musteriler: [],
            urunler: [
                {id: 1, ad: "QDMS"}, {id: 2, ad: "Ensemble"}, {id: 3, ad: "Synergy CSP"}, {id: 4, ad: "BEAM"}, {id: 5, ad: "eBA"}
            ],
            statuler: [
                {id: 1, ad: "Açık"}, {id: 2, ad: "Teklif Verildi"}, {id: 3, ad: "Kazanıldı"}, {id: 4, ad: "Kaybedildi"}, {id: 5, ad: "Ertelendi"}
            ],
            firsatlar: []
        };

        const KEY_V13_1 = 'excel_esnek_firsat_db_v13_1';
        if (!localStorage.getItem(KEY_V13_1)) {
            localStorage.setItem(KEY_V13_1, JSON.stringify(bosTabloYapisi));
        }

        let db = JSON.parse(localStorage.getItem(KEY_V13_1));
        document.getElementById('f-tarih').valueAsDate = new Date();
        let myChart = null;

        function dbKaydet() {
            localStorage.setItem(KEY_V13_1, JSON.stringify(db));
            verileriTazele();
        }

        function hafizayiSifirla() {
            if(confirm('Sistemdeki tüm müşterileri ve fırsatları silerek paneli bomboş yapmak istediğinize emin misiniz?')) {
                localStorage.setItem(KEY_V13_1, JSON.stringify(bosTabloYapisi));
                db = JSON.parse(localStorage.getItem(KEY_V13_1));
                verileriTazele();
            }
        }

        function topluMusteriYukle() {
            const metin = document.getElementById('excelMusteriMetin').value.trim();
            if(!metin) { alert('Lütfen önce Excel sütunundan kopyaladığınız verileri yapıştırın.'); return; }
            
            const satirlar = metin.split('\\n');
            let eklenenSayisi = 0;
            
            satirlar.forEach(satir => {
                const temizAd = satir.trim();
                if(temizAd && !db.musteriler.some(m => m.ad.toLowerCase() === temizAd.toLowerCase())) {
                    const yeniId = db.musteriler.length > 0 ? Math.max(...db.musteriler.map(o => o.id)) + 1 : 1;
                    db.musteriler.push({id: yeniId, ad: temizAd});
                    eklenenSayisi++;
                }
            });
            
            document.getElementById('excelMusteriMetin').value = '';
            dbKaydet();
            alert('Excel listesindeki ' + eklenenSayisi + ' adet benzersiz firma sözlüğe başarıyla aktarıldı!');
        }

        function excelDisariAktar() {
            let csvIcerik = "data:text/csv;charset=utf-8,Musteri/Kurum,Urun/Cozum,Beklenen Gelir (TL),Olasilik (%),Statu,Kapanis Tarihi\\n";
            db.firsatlar.forEach(f => {
                const mAd = db.musteriler.find(m => m.id == f.musteri_id)?.ad || '-';
                const uAd = db.urunler.find(u => u.id == f.urun_id)?.ad || '-';
                const sAd = db.statuler.find(s => s.id == f.statu_id)?.ad || '-';
                csvIcerik += `"${mAd}","${uAd}",${f.beklenen_gelir},${f.olasilik},"${sAd}","${f.tarih}"\\n`;
            });
            const encodedUri = encodeURI(csvIcerik);
            const link = document.createElement("a");
            link.setAttribute("href", encodedUri);
            link.setAttribute("download", "Firsat_Takip_Sistemi_Export.csv");
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
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
                    <td><span class="badge ${statuAd === 'Açık'?'acik':statuAd==='Kazanıldı'?'kazanildi':statuAd==='Kaybedildi'?'kaybedildi':statuAd==='Teklif Verildi'?'teklif':'ertelendi'}">${statuAd}</span></td>
                    <td>${t}</td>
                    <td><button type="button" class="btn-delete" onclick="firsatSil(${index})"><i class="fa-solid fa-trash-can"></i></button></td>
                `;
                tbody.appendChild(tr);
            });

            document.getElementById('m-acik').innerText = paraFormat(acikToplam);
            document.getElementById('m-kazanilan').innerText = paraFormat(kazanilanToplam);
            document.getElementById('m-tahmin').innerText = paraFormat(agirlikliTahmin);

            const yillikHedef = 5000000;
            const kalanHedef = yillikHedef - kazanilanToplam;
            const gerceklesmeOrani = ((kazanilanToplam / yillikHedef) * 100).toFixed(1);

            document.getElementById('h-gerceklesen').innerText = paraFormat(kazanilanToplam);
            document.getElementById('h-kalan').innerText = paraFormat(kalanHedef > 0 ? kalanHedef : 0);
            document.getElementById('h-oran').innerText = `%${gerceklesmeOrani}`;
            document.getElementById('h-progress').style.width = `${gerceklesmeOrani > 100 ? 100 : gerceklesmeOrani}%`;

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
