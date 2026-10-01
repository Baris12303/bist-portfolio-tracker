# 📈 BIST Portföy Takip & Teknik Analiz Paneli

> 🌐 **Canlı Uygulama Linki:** [bist-terminal.streamlit.app](https://bist-terminal.streamlit.app)

Borsa İstanbul (BIST) hisselerini canlı olarak takip eden, portföy kâr/zarar durumunu anlık hesaplayan ve teknik analiz göstergeleri (SMA20, SMA50) sunan interaktif web gösterge paneli (dashboard).

## 🚀 Özellikler
- **Canlı Veri:** `yfinance` ile BIST hisselerinin anlık ve geçmiş fiyat verilerini çeker.
- **Finansal Göstergeler:** Toplam portföy değeri, yatırılan maliyet ve net kâr/zarar (TL ve %) metrikleri.
- **Portföy Analizi:** Portföyün en çok kazandıran ve kaybettiren hisselerini otomatik tespit eder.
- **İnteraktif Tablo:** Tüm hisseleri adet, maliyet, güncel fiyat ve getiri bazında sıralanabilir tabloda listeler.
- **Teknik Analiz Grafiği:** Seçilen hissenin 6 aylık fiyat trendini, kullanıcı maliyetini, **SMA20** (Kısa Vade) ve **SMA50** (Orta Vade) hareketli ortalamalarını görselleştirir.

## 🛠️ Kullanılan Teknolojiler
- **Python 3**
- **Streamlit** (Web Arayüzü)
- **Pandas** (Veri Analizi & İşleme)
- **yfinance** (Finansal Veri API)
- **Matplotlib** (Veri Görselleştirme)

## 💻 Kurulum & Çalıştırma

1. Repoyu klonlayın veya indirin:
```bash
git clone https://github.com/KULLANICI_ADIN/bist-portfolio-tracker.git
cd bist-portfolio-tracker
```

2. Gerekli kütüphaneleri yükleyin:
```bash
pip install -r requirements.txt
```

3. Web uygulamasını başlatın:
```bash
streamlit run app.py
```