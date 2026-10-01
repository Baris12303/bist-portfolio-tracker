# 📈 BIST Portföy Takip & Yapay Zeka Destekli Teknik Analiz Terminali

> 🌐 **Canlı Uygulama Linki:** [bist-terminal.streamlit.app](https://bist-terminal.streamlit.app)

Borsa İstanbul (BIST) hisselerini anlık takip eden, SQLite veritabanı ile dinamik portföy yönetimi sunan, Plotly ile interaktif teknik analiz ve **Google Gemini AI** ile akıllı finansal yorumlama sağlayan tam teşekküllü bir FinTech web uygulaması.

---

## 🚀 Öne Çıkan Özellikler

- **🤖 Google Gemini AI Analisti:** Portföyün risk durumunu, kâr/zarar dengesini ve seçili hissenin teknik indikatörlerini LLM (Büyük Dil Modeli) ile anlık analiz eder ve Türkçe stratejik öneriler sunar.
- **💾 SQLite Veritabanı & CRUD Mimarisi:** Hisseler kod içinde statik tutulmaz; web arayüzünden yeni hisse eklenebilir, güncellenebilir veya silinebilir (`portfolio.db`).
- **📊 BIST 100 Benchmark (Alfa Metriği):** Portföyün son 6 aylık getirisini BIST 100 (`XU100.IS`) endeksi ile anlık kıyaslar; piyasanın ne kadar önünde veya gerisinde olduğunu hesaplar.
- **📉 İnteraktif Teknik Analiz (Plotly):** 
  - Fiyat, Maliyet Çizgisi, **SMA20** (Kısa Vade Trend) ve **SMA50** (Orta Vade Trend) göstergeleri.
  - **14 Günlük RSI (Göreceli Güç Endeksi):** Aşırı alım (>70) ve aşırı satım (<30) dinamik durum rozetleri.
  - Fare ile yakınlaşma (Zoom), gezinme ve birleşik bilgi kutucukları (Unified Hover).
- **🥧 Varlık Dağılımı (Donut Grafiği):** Portföydeki hisselerin toplam parasal değerini ve yüzde ağırlıklarını interaktif halka grafikle gösterir.
- **⚡ Hızlı İşlemler:** Tek tıkla portföyü sıfırlama veya hazır demo portföyü yükleme desteği.

---

## 🛠️ Kullanılan Teknolojiler

- **Python 3.11+**
- **Streamlit** (Reaktif Web Arayüzü & Cloud Deployment)
- **SQLite3** (İlişkisel Veritabanı & Kalıcı Veri Saklama)
- **Google GenAI SDK** (Gemini 3.8 / 2.5 Flash Yapay Zeka Modelleri)
- **Plotly Express & Graph Objects** (İnteraktif & Animasyonlu Finans Grafikleri)
- **yfinance** (Yahoo Finance Canlı Piyasa Veri API'si)
- **Pandas & NumPy** (Veri Manipülasyonu, Rolling Window & İndikatör Hesaplamaları)

---

## 💻 Kurulum & Yerel Çalıştırma

1. Repoyu klonlayın:
```bash
git clone https://github.com/Baris12303/bist-portfolio-tracker.git
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