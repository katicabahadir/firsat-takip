from flask import Flask, render_template_string

app = Flask(__name__)

# v14.0: Bağımsız Veri Yükleme Sekmesi, Toplu Fırsat Girişi ve Tablosal Hedef Paneli
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <title>Kurumsal Satış Fırsat Takip Portalı v14.0</title>
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
        
        /* Üst Metrik Kartları */
        .dashboard-summary { display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; margin-bottom: 20px; }
        .card { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); border-left: 5px solid #1e3a8a; display: flex; justify-content: space-between; align-items: center; }
        .card.success { border-left-color: #10b981; }
        .card.warning { border-left-color: #f59e0b; }
        .card h3 { font-size: 13px; color: #6b7280; text-transform: uppercase; font-weight: 600; }
        .card .value { font-size: 24px; font-weight: bold; margin-top: 5px; }
        
        /* Ekran Düzeni Layout */
        .ana-icerik { display: flex; gap: 20px; align-items: flex-start; margin-bottom: 20px; }
        .sol-kolon { width: 360px; display: flex; flex-direction: column; gap: 20px; }
        .form-section, .grafik-section { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
        .sag-tablo { background: white; flex: 1; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); min-height: 580px; }
        
        /* Alt Panel Düzeni */
        .alt-paneller { display: grid; grid-template-columns: 1.1fr 0.9fr; gap: 20px; margin-top: 20px; }
        .alt-kesim-kutu { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
        
        h2 { font-size: 16px; margin-bottom: 15px; color: #1e3a8a; border-bottom: 2px solid #f3f4f6; padding-bottom: 5px; display: flex; align-items: center; justify-content: space-between; gap: 8px; }
        .form-group { margin-bottom: 12px; }
        .form-group label { display: block; margin-bottom: 4px; font-weight: 600; font-size: 13px; color: #4b5563; }
        .form-group input, .form-group select { width: 100%; padding: 9px; border: 1px solid #d1d5db; border-radius: 6px; font-size: 14px; outline: none; }
        button.btn-primary { width: 100%; background-color: #1e3a8a; color: white; border: none; padding: 12px; border-radius: 6px; font-weight: bold; cursor: pointer; font-size: 14px; }
        button.btn-primary:hover { background-color: #1d4ed8; }
        
        button.btn-success { background-color: #10b981; color: white; border: none; padding: 8px 14px; border-radius: 6px; font-weight: bold; cursor: pointer; font-size: 13px; display: flex; align-items: center; gap: 6px; }
        button.btn-success:hover { background-color: #059669; }
        
        .filtre-bar { background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 6px; padding: 12px; margin-bottom: 15px; display: grid; grid-template-columns: 2fr repeat(3, 1fr); gap: 10px; }
        
        table { width: 100%; border-collapse: collapse; font-size: 14px; }
        th, td { padding: 11px; border-bottom: 1px solid #e5e7eb; text-align: left; }
        th { background-color: #f8fafc; color: #475569; font-weight: 600; }
        tr:hover { background-color: #f8fafc; }
        
        .pivot-table th { background-color: #1e3a8a; color: white; text-align: center; }
        .pivot-table td { text-align: right; font-weight: 500; }
        .pivot-table td.pivot-baslik { text-align: left; font-weight: bold; background-color: #f8fafc; }
        .pivot-table tr.pivot-toplam { background-color: #f1f5f9; font-weight: bold; }
        
        /* DERLİ TOPLU HEDEF TABLOSU TASARIMI (GÖRSELDEKİ GİBİ BİRLEŞİK) */
        .hedef-tablo { width: 100%; border-collapse: collapse; margin-top: 5px; }
        .hedef-tablo th { background-color: #f1f5f9; color: #334155; font-weight: 700; text-align: center; border: 1px solid #cbd5e1; font-size: 13px; }
        .hedef-tablo td { border: 1px solid #cbd5e1; text-align: center; font-size: 16px; font-weight: bold; padding: 14px; background-color: #fff; }
        
        .progress-container { display: flex; align-items: center; gap: 10px; justify-content: center; width: 100%; }
        .excel-progress-bar { flex: 1; max-width: 150px; background-color: #e2e8f0; height: 12px; border-radius: 6px; overflow: hidden; border: 1px solid #cbd5e1; }
        .excel-progress-fill { height: 100%; background: linear-gradient(90deg, #10b981, #059669); width: 0%; }
        
        /* Veri Yükleme Düzeni */
        .yukleme-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
        .yukleme-kart { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); border: 1px dashed #cbd5e1; }
        textarea.excel-input { width: 100%; height: 180px; padding: 10px; border: 1px solid #cbd5e1; border-radius: 6px; font-family: monospace; font-size: 12px; resize: vertical; outline: none; margin-bottom: 12px; }
        
        .btn-delete { background: none; border: none; color: #ef4444; cursor: pointer; }
        .badge { padding: 4px 8px; border-radius: 4px; font-size: 12px; font-weight: bold; }
        .badge.acik { background-color: #e0f2fe; color: #0369a1; }
        .badge.kazanildi { background-color: #d1fae5; color: #065f46; }
        .badge.kaybedildi { background-color: #fee2e2; color: #991b1b; }
        .badge.teklif { background-color: #fef3c7; color: #b45309; }
        .badge.ertelendi { background-color: #f3f4f6; color: #374151; }
        
        ul.sozluk-list { list-style: none; max-height: 300px; overflow-y: auto; border: 1px solid #e5e7eb; border-radius: 6px; padding: 5px; }
        ul.sozluk-list li { display: flex; justify-content: space-between; padding: 8px 10px; border-bottom: 1px solid #eee; background: #fafafa; margin-bottom: 5px; border-radius: 4px; font-size: 13px; }
        .grafik-konteyner { position: relative; width: 100%; height: 210px; display: flex; justify-content: center; }
    </style>
</head>
<body>

    <header>
        <h1><i class="fa-solid fa-file-excel"></i> Akıllı Satış Fırsat Yönetim Portalı</h1>
        <nav>
            <button onclick="sayfaDegistir('firsatlar-sayfa')" id="btn-firsatlar-sayfa" class="active"><i class="fa-solid fa-table-list"></i> Fırsat Havuzu & Analiz</button>
            <button onclick="sayfaDegistir('yukleme-sayfa')" id="btn-yukleme-sayfa"><i class="fa-solid fa-cloud-arrow-up"></i> Veri Yükleme Merkezi</button>
            <button onclick="sayfaDegistir('ayarlar-sayfa')" id="btn-ayarlar-sayfa"><i class="fa-solid fa-sliders"></i> Sözlük Tanımları</button>
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
                    <h2><i class="fa-solid fa-bullseye"></i> Excel Birebir Hedef Takip Matrisi</h2>
                    <table class="hedef-tablo">
                        <thead>
                            <tr>
                                <th>YILLIK HEDEF</th>
                                <th>GERÇEKLEŞEN SATIŞ</th>
                                <th>KALAN HEDEF TUTARI</th>
                                <th>HEDEF BAŞARI ORANI</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr>
                                <td style="color: #1e40af;">5.000.000 TL</td>
                                <td id="h-gerceklesen" style="color: #166534;">0 TL</td>
                                <td id="h-kalan" style="color: #b45309;">0 TL</td>
                                <td>
                                    <div class="progress-container">
                                        <span id="h-oran" style="color: #0f172a;">%0</span>
                                        <div class="excel-progress-bar">
                                            <div class="excel-progress-fill" id="h-progress"></div>
                                        </div>
                                    </div>
                                </td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>
        </div>

        <div id="yukleme-sayfa" class="sayfa">
            <div class="yukleme-grid">
                <div class="yukleme-kart">
                    <h2><i class="fa-solid fa-building"></i> 1. Excel'den Toplu Müşteri Yükleme</h2>
                    <p style="font-size:13px; color:#64748b; margin-bottom:12px;">Excel'den kopyaladığınız şirket isimlerini (Her satıra bir tane gelecek şekilde) buraya yapıştırın:</p>
                    <textarea id="excelMusteriMetin" class="excel-input" placeholder="Örn:\nBimser Çözüm\nHavelsan\nRoketsan"></textarea>
                    <button type="button" class="btn-success" onclick="topluMusteriYukle()"><i class="fa-solid fa-upload"></i> Firmaları Sözlüğe Aktar</button>
                </div>

                <div class="yukleme-kart">
                    <h2><i class="fa-solid fa-table"></i> 2. Excel'den Toplu Fırsat Havuzu Yükleme</h2>
                    <p style="font-size:13px; color:#64748
