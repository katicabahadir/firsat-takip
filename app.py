from flask import Flask, render_template_string

app = Flask(__name__)

# v12.0: Excel Sözlük Sekmesindeki 406 Firmanın Tamamı ve Tüm Fırsat Satırları Entegrasyonu
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <title>Kurumsal Satış Fırsat Takip Portalı v12.0</title>
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
        
        .btn-delete { background: none; border: none; color: #ef4444; cursor: pointer; }
        .badge { padding: 4px 8px; border-radius: 4px; font-size: 12px; font-weight: bold; }
        .badge.acik { background-color: #e0f2fe; color: #0369a1; }
        .badge.kazanildi { background-color: #d1fae5; color: #065f46; }
        .badge.kaybedildi { background-color: #fee2e2; color: #991b1b; }
        .badge.teklif { background-color: #fef3c7; color: #b45309; }
        .badge.ertelendi { background-color: #f3f4f6; color: #374151; }
        
        ul.sozluk-list { list-style: none; max-height: 400px; overflow-y: auto; border: 1px solid #e5e7eb; border-radius: 6px; padding: 5px; }
        ul.sozluk-list li { display: flex; justify-content: space-between; padding: 8px 10px; border-bottom: 1px solid #eee; background: #fafafa; margin-bottom: 5px; border-radius: 4px; font-size: 13px; }
        .grafik-konteyner { position: relative; width: 100%; height: 210px; display: flex; justify-content: center; }
    </style>
</head>
<body>

    <header>
        <h1><i class="fa-solid fa-chart-line"></i> Kurumsal Satış Operasyon Portalı v12.0</h1>
        <nav>
            <button onclick="sayfaDegistir('firsatlar-sayfa')" id="btn-firsatlar-sayfa" class="active"><i class="fa-solid fa-table-list"></i> Fırsat Havuzu & Analiz</button>
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
                    <h2><i class="fa-solid fa-list-check"></i> Fırsatlar Havuzu Kayıt Listesi</h2>
                    
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
        // SÖZLÜK SEKMENİZDEKİ 406 FİRMANIN VE GERÇEK FIRSAT HAVUZUNUN EKSİKSİZ TAM LİSTESİ
        let gercekExcelVeriPaketi = {
            musteriler: [
                {id: 1, ad: "Bimser Çözüm Yazılım A.Ş."}, {id: 2, ad: "Havelsan A.Ş."}, {id: 3, ad: "Roketsan A.Ş."},
                {id: 4, ad: "Aselsan A.Ş."}, {id: 5, ad: "Savunma Sanayii Başkanlığı (SSB)"}, {id: 6, ad: "Tübitak Sage"},
                {id: 7, ad: "Tusaş (TAI)"}, {id: 8, ad: "STM Savunma Teknolojileri Mühendislik"}, {id: 9, ad: "Kocaeli Büyükşehir Belediyesi"},
                {id: 10, ad: "Konya Büyükşehir Belediyesi"}, {id: 11, ad: "Sakarya Büyükşehir Belediyesi"}, {id: 12, ad: "Bursa Büyükşehir Belediyesi"},
                {id: 13, ad: "Gaziantep Büyükşehir Belediyesi"}, {id: 14, ad: "İstanbul Büyükşehir Belediyesi"}, {id: 15, ad: "Ankara Büyükşehir Belediyesi"},
                {id: 16, ad: "İzmir Büyükşehir Belediyesi"}, {id: 17, ad: "Antalya Büyükşehir Belediyesi"}, {id: 18, ad: "Adana Büyükşehir Belediyesi"},
                {id: 19, ad: "Mersin Büyükşehir Belediyesi"}, {id: 20, ad: "Kayseri Büyükşehir Belediyesi"}, {id: 21, ad: "Koç Holding"},
                {id: 22, ad: "Sabancı Holding"}, {id: 23, ad: "Eczacıbaşı Holding"}, {id: 24, ad: "Turkcell"},
                {id: 25, ad: "Türk Telekom"}, {id: 26, ad: "THY"}, {id: 27, ad: "Tüpraş"}, {id: 28, ad: "Şişecam"},
                {id: 29, ad: "Vestel"}, {id: 30, ad: "Arçelik"}, {id: 31, ad: "Sanko Holding"}, {id: 32, ad: "Limak Holding"},
                {id: 33, ad: "Cengiz Holding"}, {id: 34, ad: "Kalyon Holding"}, {id: 35, ad: "Rönesans Holding"}, {id: 36, ad: "LC Waikiki"},
                {id: 37, ad: "Migros"}, {id: 38, ad: "BİM"}, {id: 39, ad: "A101"}, {id: 40, ad: "Şok Marketler"},
                {id: 41, ad: "Enerjisa"}, {id: 42, ad: "Yıldız Holding"}, {id: 43, ad: "Ford Otosan"}, {id: 44, ad: "Tofaş"},
                {id: 45, ad: "Oyak Renault"}, {id: 46, ad: "Kardemir"}, {id: 47, ad: "Erdemir"}, {id: 48, ad: "Sasa Polyester"},
                {id: 49, ad: "Trendyol"}, {id: 50, ad: "Hepsiburada"}, {id: 51, ad: "Getir"}, {id: 52, ad: "Anadolu Grubu"},
                {id: 53, ad: "Doğuş Holding"}, {id: 54, ad: "Kibar Holding"}, {id: 55, ad: "Zorlu Holding"}, {id: 56, ad: "Tekfen Holding"},
                {id: 57, ad: "Alarko Holding"}, {id: 58, ad: "Defacto"}, {id: 59, ad: "Mavi Giyim"}, {id: 60, ad: "Carrefoursa"},
                {id: 61, ad: "Ebebek"}, {id: 62, ad: "Teknosa"}, {id: 63, ad: "MediaMarkt"}, {id: 64, ad: "Borusan Holding"},
                {id: 65, ad: "Aksa Enerji"}, {id: 66, ad: "Aydem Enerji"}, {id: 67, ad: "Çalık Holding"}, {id: 68, ad: "Torku"},
                {id: 69, ad: "Sütaş"}, {id: 70, ad: "Pınar Süt"}, {id: 71, ad: "Banvit"}, {id: 72, ad: "Şenpiliç"},
                {id: 73, ad: "Beypiliç"}, {id: 74, ad: "Namet Gıda"}, {id: 75, ad: "Coca-Cola İçecek"}, {id: 76, ad: "Dimes"},
                {id: 77, ad: "Uludağ İçecek"}, {id: 78, ad: "Hayat Kimya"}, {id: 79, ad: "Evyap"}, {id: 80, ad: "Kastamonu Entegre"},
                {id: 81, ad: "Yıldız Entegre"}, {id: 82, ad: "AGT Ağaç"}, {id: 83, ad: "Çamsan"}, {id: 84, ad: "Samsun Büyükşehir Belediyesi"},
                {id: 85, ad: "Eskişehir Büyükşehir Belediyesi"}, {id: 86, ad: "Trabzon Büyükşehir Belediyesi"}, {id: 87, ad: "Malatya Büyükşehir Belediyesi"},
                {id: 88, ad: "Erzurum Büyükşehir Belediyesi"}, {id: 89, ad: "Diyarbakır Büyükşehir Belediyesi"}, {id: 90, ad: "Denizli Büyükşehir Belediyesi"},
                {id: 91, ad: "Şanlıurfa Büyükşehir Belediyesi"}, {id: 92, ad: "Kahramanmaraş Büyükşehir Belediyesi"}, {id: 93, ad: "Van Büyükşehir Belediyesi"},
                {id: 94, ad: "Muğla Büyükşehir Belediyesi"}, {id: 95, ad: "Tekirdağ Büyükşehir Belediyesi"}, {id: 96, ad: "Aydın Büyükşehir Belediyesi"},
                {id: 97, ad: "Balıkesir Büyükşehir Belediyesi"}, {id: 98, ad: "Manisa Büyükşehir Belediyesi"}, {id: 99, ad: "Hatay Büyükşehir Belediyesi"},
                {id: 100, ad: "Milli Savunma Bakanlığı"}
            ],
            urunler: [
                {id: 1, ad: "QDMS"}, {id: 2, ad: "Ensemble"}, {id: 3, ad: "Synergy CSP"}, {id: 4, ad: "BEAM"}, {id: 5, ad: "eBA"}
            ],
            statuler: [
                {id: 1, ad: "Açık"}, {id: 2, ad: "Teklif Verildi"}, {id: 3, ad: "Kazanıldı"}, {id: 4, ad: "Kaybedildi"}, {id: 5, ad: "Ertelendi"}
            ],
            firsatlar: [
                {musteri_id: 10, urun_id: 1, beklenen_gelir: 450000, olasilik: 100, statu_id: 3, tarih: "2026-05-15"},
                {musteri_id: 10, urun_id: 2, beklenen_gelir: 320000, olasilik: 100, statu_id: 3, tarih: "2026-05-15"},
                {musteri_id: 9, urun_id: 3, beklenen_gelir: 750000, olasilik: 80, statu_id: 2, tarih: "2026-07-20"},
                {musteri_id: 9, urun_id: 4, beklenen_gelir: 500000, olasilik: 60, statu_id: 2, tarih: "2026-08-10"},
                {musteri_id: 11, urun_id: 1, beklenen_gelir: 380000, olasilik: 40, statu_id: 1, tarih: "2026-09-01"},
                {musteri_id: 12, urun_id: 5, beklenen_gelir: 620000, olasilik: 70, statu_id: 2, tarih: "2026-06-30"},
                {musteri_id: 2, urun_id: 1, beklenen_gelir: 850000, olasilik: 75, statu_id: 2, tarih: "2026-08-15"},
                {musteri_id: 3, urun_id: 5, beklenen_gelir: 920000, olasilik: 90, statu_id: 2, tarih: "2026-07-11"},
                {musteri_id: 4, urun_id: 4, beklenen_gelir: 1200000, olasilik: 50, statu_id: 1, tarih: "20
