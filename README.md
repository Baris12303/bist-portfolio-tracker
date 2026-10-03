# Global Finans ve Servet Terminali

> **Canli Terminal Erisimi:** [bist-terminal.streamlit.app](https://bist-terminal.streamlit.app)

Kuresel varlik siniflarini (BIST hisseleri, NASDAQ/NYSE, Kripto Varliklar ve Degerli Madenler) tek bir merkezden kurumsal kalitede yonetmek uzere tasarlanmis tam tesekkullu bir FinTech web terminalidir. 

SOLID prensipleri isiginda insa edilmis, performans ve guvenlik odakli modern bir altyapi uzerine kurulmustur.

---

## Ozet Mimarisi ve Temel Yetkinlikler

- **Supabase Bulut Altyapisi:** Kullanici kimlik dogrulama (Auth) ve portfoy kayitlari Supabase uzerinden sifrelenmis veri akisiyla saglanir. Parolalar sunucuya yazilmadan once kriptografik olarak (SHA-256) ozetlenir.
- **Akilli Portfoy Dengeleme (Rebalancing) Robotu:** 
  - 4 farkli strateji modeline (Dengeli Dort Ayak, Teknoloji, Defansif, Ozel) gore varlik agirliklarini analiz eder.
  - Portfoy sapmasini (drift) tespit ederek, kullanicinin tercihine gore "satisli" (zero-cash) veya "yeni tasarruf enjekte etme" modlarinda matematiksel lot al/sat receteleri olusturur.
- **Temettu ve Pasif Gelir Radari:** Sirketlerin hisse basina net nakit dagitimi (dividendRate) uzerinden aylik / yillik pasif nakit akisi projeksiyonu ve erken emeklilik hedefine ulasim yuzdesi cikarir.
- **Yapay Zeka Istihbarati (Google Gemini):** 
  - Canli piyasa haberlerini isleyerek otomatik AI Algi Radari (Boga/Ayi/Notr duygu analizi) olusturur.
  - Yatirimcinin kuresel portfoyune profesyonel risk ve strateji raporlari sunar.
- **Hedef Fiyat ve Akilli Alarm Sistemi:**
  - Varlik bazli Kar Hedefi (Take-Profit) ve Zarar Kes (Stop-Loss) seviyeleri takibi.
  - 14 gunluk RSI indikatoru ve trend formasyonlariyla entegre asiri alim/satim dip taramasi.
  - Cift anahtarli site ici hub ve stateful throttling algoritmasiyla guvence altina alinmis SMTP E-Posta bildirim gonderimi.

---

## Teknolojik Yigin (Tech Stack)

- **Platform:** Python 3.11+, Streamlit
- **Veritabani:** Supabase (PostgreSQL)
- **Finansal Veri Agi:** yfinance, urllib XML RSS
- **Gorsellestirme:** Plotly (Grafikler)
- **AI Analiz:** Google GenAI SDK (Gemini 2.0 Flash)

---

## Yerel Gelistirme Ortami Kurulumu

Proje repolarini yerel makinenize indirdikten sonra asagidaki adimlarla terminali baslatabilirsiniz:

1. Bagimliliklari yukleyin:
```bash
pip install -r requirements.txt
```

2. `.streamlit/secrets.toml` dosyasini olusturun ve cevresel degiskenlerinizi (Supabase, Gemini API, SMTP kimlik bilgileri) tanimlayin.

3. Sunucuyu ayaga kaldirin:
```bash
streamlit run app.py
```