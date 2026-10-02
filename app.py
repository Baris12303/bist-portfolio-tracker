import streamlit as st
import yfinance as yf
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
import requests
import database

def get_yf_session():
    """Yahoo Finance sorguları için tarayıcı kimlikli güvenli oturum döndürür."""
    s = requests.Session()
    s.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7',
    })
    return s

# Sayfa Başlığı ve Geniş Ekran Düzeni
st.set_page_config(page_title="Global Finans & Servet Terminali", page_icon="◆", layout="wide")

# --- DERİN KARBON & LÜKS TİPOGRAFİ ÖZEL CSS ---
st.markdown("""
<style>
/* Temel Koyu Tema Arka Planı & Tipografi */
.main, .stApp {
    background-color: #080b11;
    color: #e2e8f0;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
}

/* Üst Sekmeler: Bağımsız, Yumuşak Köşeli ve Ferah Kart Tasarımı */
.react-aria-SelectionIndicator,
[data-testid="stTab"] .react-aria-SelectionIndicator,
.stTabs [data-testid="stTab"] .react-aria-SelectionIndicator,
[data-baseweb="tab-highlight"],
div[data-baseweb="tab-highlight"],
[data-baseweb="tab-border"],
div[data-baseweb="tab-border"] {
    display: none !important;
    visibility: hidden !important;
    height: 0px !important;
    width: 0px !important;
    opacity: 0 !important;
    background: transparent !important;
    background-color: transparent !important;
    border: none !important;
}

.stTabs [role="tablist"]::after,
[data-testid="stTabs"] div[role="tablist"]::after,
.stTabs div[role="tablist"]::after {
    display: none !important;
    content: none !important;
    height: 0px !important;
    border: none !important;
    background: transparent !important;
}

.stTabs [role="tablist"],
.stTabs [data-baseweb="tab-list"],
[data-testid="stTabs"] [role="tablist"] {
    background: transparent !important;
    background-color: transparent !important;
    border: none !important;
    border-bottom: none !important;
    box-shadow: none !important;
    gap: 12px !important;
    padding: 8px 0px 16px 0px !important;
}

.stTabs [data-testid="stTab"],
.stTabs [role="tab"],
.stTabs [data-baseweb="tab"] {
    height: auto !important;
    min-height: 48px !important;
    padding: 12px 26px !important;
    border-radius: 12px !important;
    background: rgba(255, 255, 255, 0.02) !important;
    border: 1px solid rgba(255, 255, 255, 0.07) !important;
    color: #64748b !important;
    font-size: 14px !important;
    font-weight: 500 !important;
    letter-spacing: 0.015em !important;
    box-shadow: none !important;
    transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1) !important;
    display: inline-flex !important;
    align-items: center !important;
    justify-content: center !important;
}

.stTabs [data-testid="stTab"]:hover,
.stTabs [role="tab"]:hover,
.stTabs [data-baseweb="tab"]:hover {
    color: #94a3b8 !important;
    background: rgba(255, 255, 255, 0.045) !important;
    border-color: rgba(255, 255, 255, 0.12) !important;
}

.stTabs [data-testid="stTab"][data-selected="true"],
.stTabs [data-testid="stTab"][aria-selected="true"],
.stTabs [data-testid="stTab"][data-selected],
.stTabs [role="tab"][aria-selected="true"],
.stTabs [aria-selected="true"] {
    background: rgba(255, 255, 255, 0.07) !important;
    color: #f8fafc !important;
    font-weight: 600 !important;
    border: 1px solid rgba(255, 255, 255, 0.15) !important;
    box-shadow: 0 4px 18px rgba(0, 0, 0, 0.35) !important;
    border-radius: 12px !important;
}

.stTabs [data-testid="stTab"] p,
.stTabs [data-testid="stTab"] span {
    margin: 0 !important;
    padding: 0 !important;
}

/* Lüks Metrik Kartları */
div[data-testid="stMetric"] {
    background: linear-gradient(180deg, rgba(255, 255, 255, 0.025) 0%, rgba(255, 255, 255, 0.008) 100%);
    padding: 16px 20px;
    border-radius: 12px;
    border: 1px solid rgba(255, 255, 255, 0.06);
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.25);
    transition: transform 0.25s cubic-bezier(0.4, 0, 0.2, 1), border-color 0.25s cubic-bezier(0.4, 0, 0.2, 1);
}
div[data-testid="stMetric"]:hover {
    transform: translateY(-2px);
    border-color: rgba(255, 255, 255, 0.14);
}
div[data-testid="stMetricLabel"] {
    font-size: 11px !important;
    text-transform: uppercase !important;
    letter-spacing: 0.06em !important;
    font-weight: 600 !important;
    color: #64748b !important;
}
div[data-testid="stMetricValue"] {
    font-size: 21px !important;
    font-weight: 600 !important;
    color: #f1f5f9 !important;
    letter-spacing: -0.01em !important;
    white-space: nowrap !important;
    overflow: hidden !important;
    text-overflow: ellipsis !important;
    transition: all 0.2s ease !important;
}
div[data-testid="stMetric"]:hover div[data-testid="stMetricValue"] {
    white-space: normal !important;
    overflow: visible !important;
    word-break: break-word !important;
}

/* Minimalist Haber Kartları */
.news-card {
    background: rgba(255, 255, 255, 0.018);
    border: 1px solid rgba(255, 255, 255, 0.06);
    border-radius: 12px;
    padding: 16px 18px;
    margin-bottom: 12px;
    transition: transform 0.25s cubic-bezier(0.4, 0, 0.2, 1), border-color 0.25s cubic-bezier(0.4, 0, 0.2, 1);
}
.news-card:hover {
    transform: translateY(-2px);
    border-color: rgba(255, 255, 255, 0.16);
    background: rgba(255, 255, 255, 0.03);
}

/* Şık Butonlar */
.stButton > button {
    border-radius: 10px;
    font-weight: 500;
    letter-spacing: 0.02em;
    transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
    border: 1px solid rgba(255, 255, 255, 0.08);
}
.stButton > button:hover {
    border-color: rgba(255, 255, 255, 0.2);
    transform: translateY(-1px);
}
</style>
""", unsafe_allow_html=True)

# --- KULLANICI OTURUM KONTROLÜ (SESSION STATE) ---
if "kullanici" not in st.session_state:
    st.session_state.kullanici = None

# Giriş yapılmamışsa Giriş / Kayıt / Demo ekranını göster
if not st.session_state.kullanici:
    st.title("Global Finans & Servet Terminali")
    st.caption("Borsa İstanbul, Amerikan Borsaları (NASDAQ/NYSE), Kripto Varlıklar ve Emtia tek merkezde.")
    
    col_auth, col_info = st.columns([1.1, 0.9], gap="large")
    
    with col_auth:
        tab_giris, tab_kayit, tab_demo = st.tabs(["Giriş Yap", "Hesap Aç", "Demo İncele"])
        
        with tab_giris:
            st.subheader("Hesabınıza Giriş Yapın")
            giris_email = st.text_input("E-posta Adresi", key="giris_email")
            giris_sifre = st.text_input("Parola", type="password", key="giris_sifre")
            
            if st.button("Giriş Yap", type="primary", use_container_width=True):
                if not giris_email or not giris_sifre:
                    st.error("Lütfen e-posta ve parolanızı girin.")
                else:
                    basarili, mesaj, user_data = database.kullanici_giris_yap(giris_email, giris_sifre)
                    if basarili:
                        st.session_state.kullanici = user_data
                        st.success(mesaj)
                        st.rerun()
                    else:
                        st.error(mesaj)
                        
        with tab_kayit:
            st.subheader("Yeni Hesap Oluşturun")
            kayit_ad = st.text_input("Ad Soyad", key="kayit_ad")
            kayit_email = st.text_input("E-posta Adresi", key="kayit_email")
            kayit_sifre = st.text_input("Parola Belirleyin", type="password", key="kayit_sifre")
            kayit_sifre_tekrar = st.text_input("Parolayı Doğrulayın", type="password", key="kayit_sifre_tekrar")
            
            if st.button("Kayıt Ol ve Başla", type="primary", use_container_width=True):
                if not kayit_ad or not kayit_email or not kayit_sifre:
                    st.error("Lütfen tüm alanları doldurun.")
                elif kayit_sifre != kayit_sifre_tekrar:
                    st.error("Girdiğiniz parolalar birbiriyle uyuşmuyor.")
                elif len(kayit_sifre) < 4:
                    st.error("Parolanız en az 4 karakter olmalıdır.")
                else:
                    basarili, mesaj = database.kullanici_kayit_ol(kayit_email, kayit_sifre, kayit_ad)
                    if basarili:
                        _, _, user_data = database.kullanici_giris_yap(kayit_email, kayit_sifre)
                        st.session_state.kullanici = user_data
                        st.success(f"Hesabınız oluşturuldu: {kayit_ad}")
                        st.rerun()
                    else:
                        st.error(mesaj)
                        
        with tab_demo:
            st.subheader("Demo Olarak İnceleyin")
            st.write("Hesap oluşturmadan sistemi ve analitik araçları örnek verilerle test edebilirsiniz.")
            if st.button("Demo Oturumu Başlat", use_container_width=True):
                st.session_state.kullanici = {
                    "email": "demo@bistterminal.com",
                    "ad_soyad": "Misafir Yatırımcı",
                    "rol": "demo"
                }
                st.session_state.demo_portfoy = {
                    "THYAO.IS": {"maliyet": 270.00, "adet": 50.0},
                    "TUPRS.IS": {"maliyet": 165.00, "adet": 100.0},
                    "AKBNK.IS": {"maliyet": 58.00, "adet": 300.0},
                    "NVDA": {"maliyet": 115.00, "adet": 12.0},
                    "GRAM_ALTIN": {"maliyet": 2900.00, "adet": 16.0},
                    "BTC-USD": {"maliyet": 62000.00, "adet": 0.02},
                }
                st.rerun()
                
    with col_info:
        st.markdown("### Terminal Mimarisi & Yetkinlikler")
        st.markdown("""
        - **Kişisel Portföy & Servet:** BIST, ABD Hisseleri, Kripto ve Altın yatırımlarınız tek ekranda.
        - **Piyasa & Şirket Keşfi:** BIST ve küresel hisselerin temel oranları, çarpanları ve canlı haber akışı.
        - **7 Günlük Makine Öğrenmesi Projeksiyonu:** Lineer regresyon ve standart sapma güven bandı.
        - **Canlı Piyasa Haberleri:** Bloomberg, Reuters ve KAP odaklı haber entegrasyonu.
        - **Google Gemini Analisti:** Küresel risk yönetimi ve hisse araştırma bültenleri.
        """)
        
    st.stop()

# --- YARDIMCI VERİ & KUR FONKSİYONLARI ---

@st.cache_data(ttl=300)
def get_usd_try_rate() -> float:
    """Anlık USD/TRY kurunu çeker."""
    try:
        usd = yf.Ticker("USDTRY=X").history(period="2d")
        if not usd.empty:
            return float(usd['Close'].iloc[-1])
    except Exception:
        pass
    return 34.50

def varlik_sinifi_belirle(sembol: str):
    """Sembolün varlık sınıfını, para birimini ve rozetini döndürür."""
    s = sembol.upper().strip()
    if s.endswith(".IS"):
        return "BIST Hissesi", "TRY", "[BIST]"
    elif s == "GRAM_ALTIN" or s.startswith("GC=") or s.startswith("SI="):
        para = "TRY" if s == "GRAM_ALTIN" else "USD"
        return "Emtia & Maden", para, "[EMTİA]"
    elif s.endswith("-USD") or s.endswith("-TRY") or s in ["BTC", "ETH", "SOL", "AVAX", "DOGE", "XRP"]:
        return "Kripto Varlık", "USD", "[KRİPTO]"
    elif "USDTRY" in s or "EURTRY" in s:
        return "Nakit & Döviz", "TRY", "[DÖVİZ]"
    else:
        return "ABD Borsası", "USD", "[ABD]"

def varlik_gecmisi_getir(sembol: str, period="6mo") -> pd.DataFrame:
    """BIST, ABD, Kripto veya Gram Altın geçmiş verisini çeker."""
    s = sembol.upper().strip()
    if s == "GRAM_ALTIN":
        try:
            ons = yf.Ticker("GC=F").history(period=period)['Close']
            usd = yf.Ticker("USDTRY=X").history(period=period)['Close']
            ons.index = ons.index.date
            usd.index = usd.index.date
            df_merged = pd.concat([ons, usd], axis=1, keys=['ons', 'usd']).ffill().dropna()
            gram_series = (df_merged['ons'] / 31.1034768) * df_merged['usd']
            df = pd.DataFrame({'Close': gram_series})
            df.index = pd.to_datetime(df.index)
            return df
        except Exception:
            return pd.DataFrame()
    else:
        try:
            hisse = yf.Ticker(s)
            df = hisse.history(period=period)
            return df
        except Exception:
            return pd.DataFrame()

@st.cache_data(ttl=600)
def get_live_news(query: str, count: int = 4):
    """Google News RSS feed üzerinden Türkçe canlı finans haberlerini çeker."""
    url = f"https://news.google.com/rss/search?q={urllib.parse.quote(query)}&hl=tr&gl=TR&ceid=TR:tr"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        content = urllib.request.urlopen(req, timeout=4).read()
        root = ET.fromstring(content)
        items = root.findall('./channel/item')[:count]
        news_list = []
        for it in items:
            title = it.find('title').text if it.find('title') is not None else ''
            link = it.find('link').text if it.find('link') is not None else '#'
            pubDate = it.find('pubDate').text if it.find('pubDate') is not None else ''
            parts = title.rsplit(' - ', 1)
            headline = parts[0]
            source = parts[1] if len(parts) > 1 else 'Finans Medyası'
            news_list.append({
                'headline': headline,
                'source': source,
                'link': link,
                'date': pubDate[:16]
            })
        return news_list
    except Exception:
        return []

@st.cache_data(ttl=1800)
def get_company_fundamentals(symbol: str) -> dict:
    """Şirket temel analiz çarpanlarını çeker ve 30 dk önbelleğe alır."""
    if symbol == "GRAM_ALTIN":
        return {}
    try:
        session = get_yf_session()
        t = yf.Ticker(symbol, session=session)
        info = t.info if hasattr(t, 'info') and isinstance(t.info, dict) else {}
        fi = getattr(t, 'fast_info', None)
        
        market_cap = info.get("marketCap")
        if not market_cap and fi:
            market_cap = getattr(fi, 'market_cap', None) or (fi.get('marketCap') if hasattr(fi, 'get') else None)
            
        pe = info.get("trailingPE") or info.get("forwardPE")
        pb = info.get("priceToBook")
        div_y = info.get("dividendYield") or info.get("trailingAnnualDividendYield")
        div_r = info.get("dividendRate")
        
        h52 = info.get("fiftyTwoWeekHigh")
        l52 = info.get("fiftyTwoWeekLow")
        if not h52 and fi:
            h52 = getattr(fi, 'year_high', None) or (fi.get('yearHigh') if hasattr(fi, 'get') else None)
        if not l52 and fi:
            l52 = getattr(fi, 'year_low', None) or (fi.get('yearLow') if hasattr(fi, 'get') else None)

        if not info and market_cap is None:
            raise ValueError(f"'{symbol}' verisi alınamadı.")

        sec = info.get("sector")
        sec_str = sec if sec and str(sec).lower() != "none" else "Piyasa Şirketi"

        ind = info.get("industry")
        ind_str = ind if ind and str(ind).lower() != "none" else "Sanayi & Hizmet"

        lname = info.get("longName")
        lname_str = lname if lname and str(lname).lower() != "none" else symbol
            
        return {
            "longName": lname_str,
            "sector": sec_str,
            "industry": ind_str,
            "marketCap": market_cap,
            "trailingPE": pe,
            "priceToBook": pb,
            "dividendYield": div_y,
            "dividendRate": div_r,
            "fiftyTwoWeekHigh": h52,
            "fiftyTwoWeekLow": l52,
        }
    except Exception as e:
        raise e

@st.cache_data(ttl=7200)
def get_ai_news_sentiment(symbol: str, headlines_tuple: tuple, api_key: str) -> dict:
    """Haber başlıklarını Gemini ile analiz edip piyasa duygu skorunu 2 saat önbelleğe alır."""
    if not api_key or not headlines_tuple:
        return {}
    try:
        from google import genai
        import json, re, datetime
        client = genai.Client(api_key=api_key)
        headlines_text = "\n".join([f"- {h}" for h in headlines_tuple[:5]])
        prompt = f"""
Sen Wall Street ve Borsa İstanbul konusunda uzman kurumsal bir Finansal İstihbarat Analistisin.
Varlık: {symbol}
Aşağıdaki son canlı haber başlıklarını analiz et ve piyasanın algısını değerlendir:
{headlines_text}

LÜTFEN SADECE VE SADECE aşağıdaki JSON formatında tek bir JSON objesi üret:
{{
  "skor": "Boğa (Pozitif)" veya "Nötr (Dengeli)" veya "Ayı (Negatif)",
  "yuzde": 75,
  "ozet": "2 cümlelik net, kurumsal piyasa algısı ve haber özeti."
}}
JSON dışında hiçbir ek metin veya açıklama yazma.
"""
        modeller = ["gemini-2.0-flash", "gemini-1.5-flash", "gemini-1.5-pro"]
        try:
            live_models = [m.name for m in client.models.list() if "gemini" in m.name.lower() and "embed" not in m.name.lower()]
            if live_models:
                modeller = live_models
        except Exception:
            pass

        raw_text = ""
        for m_name in modeller:
            try:
                res = client.models.generate_content(model=m_name, contents=prompt)
                if res and res.text:
                    raw_text = res.text.strip()
                    break
            except Exception:
                continue

        if not raw_text:
            return {}

        match = re.search(r'\{.*\}', raw_text, re.DOTALL)
        if match:
            parsed = json.loads(match.group(0))
            parsed["zaman"] = datetime.datetime.now().strftime("%H:%M")
            return parsed
        return {}
    except Exception:
        return {}


# --- AKILLI PORTFÖY DENGELEME ROBOTU MOTORU (SOLID - SRP) ---

REBALANCE_STRATEJILERI = {
    "Dengeli Dört Ayak (All-Weather)": {
        "BIST Hissesi": 25.0,
        "ABD Borsası": 25.0,
        "Emtia & Maden": 25.0,
        "Kripto Varlık": 25.0,
        "aciklama": "Ray Dalio modeli; ekonomik döngülere karşı risk ve getiriyi 4 ana sütuna eşit (%25) dağıtır."
    },
    "Teknoloji & Büyüme (Agresif)": {
        "BIST Hissesi": 20.0,
        "ABD Borsası": 40.0,
        "Emtia & Maden": 10.0,
        "Kripto Varlık": 30.0,
        "aciklama": "Yüksek risk toleransı; küresel yapay zeka, teknoloji ve kripto yükseliş ivmesine odaklanır."
    },
    "Defansif & Temettü (Muhafazakar)": {
        "BIST Hissesi": 35.0,
        "ABD Borsası": 15.0,
        "Emtia & Maden": 40.0,
        "Kripto Varlık": 10.0,
        "aciklama": "Sermaye koruma ve nakit akışı; kıymetli madenler ve BIST temettü devlerine ağırlık verir."
    },
    "Özel Dağılım (Kişiselleştirilmiş)": {
        "BIST Hissesi": 25.0,
        "ABD Borsası": 25.0,
        "Emtia & Maden": 25.0,
        "Kripto Varlık": 25.0,
        "aciklama": "Kendi yatırım felsefenize göre hedef yüzdeleri serbestçe belirleyin."
    }
}

def hesapla_portfoy_rebalancing(
    kategori_degerler: dict, 
    toplam_deger_tl: float, 
    hedef_oranlar: dict, 
    eklenecek_nakit_tl: float = 0.0, 
    mod: str = "satisli",
    portfoy: dict = None,
    portfoy_fiyatlari_tl: dict = None
) -> dict:
    """
    Portföy hedef ağırlıkları ile mevcut ağırlıklar arasındaki sapmayı (drift)
    ölçer ve hem sınıf hem tekil varlık bazında matematiksel alış/satış reçetesi üretir.
    """
    ana_siniflar = ["BIST Hissesi", "ABD Borsası", "Emtia & Maden", "Kripto Varlık"]
    hedef_toplam = (toplam_deger_tl + eklenecek_nakit_tl) if mod == "tasarruf" else toplam_deger_tl
    
    sinif_analizleri = []
    for kat in ana_siniflar:
        mevcut_deger = float(kategori_degerler.get(kat, 0.0))
        mevcut_oran = (mevcut_deger / toplam_deger_tl * 100.0) if toplam_deger_tl > 0 else 0.0
        hedef_oran = float(hedef_oranlar.get(kat, 0.0))
        hedef_deger = hedef_toplam * (hedef_oran / 100.0)
        
        sapma_yuzde = mevcut_oran - hedef_oran
        fark_tl = hedef_deger - mevcut_deger
        
        durum = "Dengede"
        if sapma_yuzde > 2.0:
            durum = "Aşırı Ağırlık"
        elif sapma_yuzde < -2.0:
            durum = "Düşük Ağırlık"
            
        sinif_analizleri.append({
            "sinif": kat,
            "mevcut_deger": mevcut_deger,
            "mevcut_oran": mevcut_oran,
            "hedef_oran": hedef_oran,
            "hedef_deger": hedef_deger,
            "sapma_yuzde": sapma_yuzde,
            "fark_tl": fark_tl,
            "durum": durum
        })

    # Lot Reçetesini Oluşturma
    recete_emirleri = []
    toplam_alis_tl = 0.0
    toplam_satis_tl = 0.0

    if portfoy and portfoy_fiyatlari_tl:
        sinif_varliklari = {kat: [] for kat in ana_siniflar}
        for sembol, bilgi in portfoy.items():
            k_sinif, _, _ = varlik_sinifi_belirle(sembol)
            if k_sinif in sinif_varliklari:
                fiyat_tl, _ = portfoy_fiyatlari_tl.get(sembol, (0.0, "TL"))
                adet = float(bilgi.get("adet", 0.0))
                guncel_deger = fiyat_tl * adet
                sinif_varliklari[k_sinif].append({
                    "sembol": sembol,
                    "fiyat_tl": fiyat_tl,
                    "adet": adet,
                    "deger_tl": guncel_deger
                })

        if mod == "satisli":
            for sa in sinif_analizleri:
                kat = sa["sinif"]
                fark = sa["fark_tl"]
                varliklar = sinif_varliklari.get(kat, [])
                
                if not varliklar:
                    if fark > 500:
                        recete_emirleri.append({
                            "islem": "AL",
                            "varlik": f"{kat} (Yeni Pozisyon)",
                            "lot_metin": f"+{fark:,.0f} TL",
                            "tutar_tl": fark,
                            "sinif": kat
                        })
                        toplam_alis_tl += fark
                    continue
                    
                kat_toplam_deger = sum(v["deger_tl"] for v in varliklar)
                
                if fark > 0: # Alış
                    for v in varliklar:
                        pay = (v["deger_tl"] / kat_toplam_deger) if kat_toplam_deger > 0 else (1.0 / len(varliklar))
                        varliga_tutar = fark * pay
                        if v["fiyat_tl"] > 0:
                            lot = (varliga_tutar / v["fiyat_tl"])
                            if kat == "Kripto Varlık":
                                lot_str = f"+{lot:.4f}"
                            elif kat == "Emtia & Maden":
                                lot_str = f"+{lot:.2f} Gr"
                            else:
                                lot_int = int(round(lot))
                                lot_str = f"+{lot_int:,} Lot" if lot_int > 0 else None
                                
                            if lot_str and (lot > 0.0001) and (varliga_tutar >= 100.0 or kat == "Kripto Varlık"):
                                recete_emirleri.append({
                                    "islem": "AL",
                                    "varlik": v["sembol"],
                                    "lot_metin": lot_str,
                                    "tutar_tl": varliga_tutar,
                                    "sinif": kat
                                })
                                toplam_alis_tl += varliga_tutar
                elif fark < 0: # Satış
                    satis_hedefi = abs(fark)
                    for v in varliklar:
                        pay = (v["deger_tl"] / kat_toplam_deger) if kat_toplam_deger > 0 else (1.0 / len(varliklar))
                        varliga_satis = satis_hedefi * pay
                        if v["fiyat_tl"] > 0:
                            lot = (varliga_satis / v["fiyat_tl"])
                            if kat == "Kripto Varlık":
                                lot_str = f"-{lot:.4f}"
                            elif kat == "Emtia & Maden":
                                lot_str = f"-{lot:.2f} Gr"
                            else:
                                lot_int = int(round(lot))
                                lot_str = f"-{lot_int:,} Lot" if lot_int > 0 else None
                                
                            if lot_str and (lot > 0.0001) and (varliga_satis >= 100.0 or kat == "Kripto Varlık"):
                                recete_emirleri.append({
                                    "islem": "SAT",
                                    "varlik": v["sembol"],
                                    "lot_metin": lot_str,
                                    "tutar_tl": varliga_satis,
                                    "sinif": kat
                                })
                                toplam_satis_tl += varliga_satis
        else:
            # Mod B: Tasarruf Ekleme (Yalnızca AL, satış yok)
            eksik_siniflar = [sa for sa in sinif_analizleri if sa["fark_tl"] > 0]
            toplam_eksik_tl = sum(sa["fark_tl"] for sa in eksik_siniflar)
            
            if toplam_eksik_tl > 0 and eklenecek_nakit_tl > 0:
                for sa in eksik_siniflar:
                    kat = sa["sinif"]
                    kat_pay = sa["fark_tl"] / toplam_eksik_tl
                    kat_nakit = eklenecek_nakit_tl * kat_pay
                    varliklar = sinif_varliklari.get(kat, [])
                    
                    if not varliklar:
                        recete_emirleri.append({
                            "islem": "AL",
                            "varlik": f"{kat} (Yeni Pozisyon)",
                            "lot_metin": f"+{kat_nakit:,.0f} TL",
                            "tutar_tl": kat_nakit,
                            "sinif": kat
                        })
                        toplam_alis_tl += kat_nakit
                        continue
                        
                    kat_toplam_deger = sum(v["deger_tl"] for v in varliklar)
                    for v in varliklar:
                        pay = (v["deger_tl"] / kat_toplam_deger) if kat_toplam_deger > 0 else (1.0 / len(varliklar))
                        varliga_tutar = kat_nakit * pay
                        if v["fiyat_tl"] > 0 and varliga_tutar > 0:
                            lot = (varliga_tutar / v["fiyat_tl"])
                            if kat == "Kripto Varlık":
                                lot_str = f"+{lot:.4f}"
                            elif kat == "Emtia & Maden":
                                lot_str = f"+{lot:.2f} Gr"
                            else:
                                lot_int = int(round(lot))
                                lot_str = f"+{lot_int:,} Lot" if lot_int > 0 else None
                                
                            if lot_str and (lot > 0.0001) and (varliga_tutar >= 100.0 or kat == "Kripto Varlık"):
                                recete_emirleri.append({
                                    "islem": "AL",
                                    "varlik": v["sembol"],
                                    "lot_metin": lot_str,
                                    "tutar_tl": varliga_tutar,
                                    "sinif": kat
                                })
                                toplam_alis_tl += varliga_tutar

    return {
        "sinif_analizleri": sinif_analizleri,
        "recete_emirleri": recete_emirleri,
        "toplam_alis_tl": toplam_alis_tl,
        "toplam_satis_tl": toplam_satis_tl,
        "hedef_toplam": hedef_toplam
    }

# --- GİRİŞ YAPILMIŞ KULLANICI AKIŞI ---
user = st.session_state.kullanici
user_email = user["email"]
is_demo = user.get("rol") == "demo"
usd_try = get_usd_try_rate()

# Portföy verisini getir
if is_demo:
    if "demo_portfoy" not in st.session_state:
        st.session_state.demo_portfoy = {
            "THYAO.IS": {"maliyet": 270.00, "adet": 50.0},
            "TUPRS.IS": {"maliyet": 165.00, "adet": 100.0},
            "AKBNK.IS": {"maliyet": 58.00, "adet": 300.0},
            "NVDA": {"maliyet": 115.00, "adet": 12.0},
            "GRAM_ALTIN": {"maliyet": 2900.00, "adet": 16.0},
            "BTC-USD": {"maliyet": 62000.00, "adet": 0.02},
        }
    portfoy = st.session_state.demo_portfoy
else:
    portfoy = database.kullanici_portfoyu_getir(user_email)

# --- SOL MENÜ (KULLANICI BİLGİSİ & PORTFÖY YÖNETİMİ) ---
st.sidebar.markdown(f"**Yatırımcı:** {user.get('ad_soyad', 'Kullanıcı')}")
st.sidebar.caption(f"{user_email}")
st.sidebar.caption(f"Piyasa Kuru: 1 USD = **{usd_try:.2f} TL**")

if is_demo:
    st.sidebar.markdown("""
    <div style="background: rgba(56, 189, 248, 0.06); border: 1px solid rgba(56, 189, 248, 0.18); border-radius: 10px; padding: 10px 14px; margin: 10px 0;">
        <span style="font-size: 11px; font-weight: 600; color: #38bdf8; text-transform: uppercase; letter-spacing: 0.05em;">✦ Demo Hesabı Aktif</span>
        <div style="font-size: 11.5px; color: #cbd5e1; margin-top: 4px; line-height: 1.4;">
            Portföyünüzü buluta kalıcı kaydetmek için oturumu kapatıp <b>ücretsiz hesap</b> açabilirsiniz.
        </div>
    </div>
    """, unsafe_allow_html=True)

if st.sidebar.button("Oturumu Kapat", use_container_width=True):
    st.session_state.kullanici = None
    st.session_state.pop("demo_portfoy", None)
    st.rerun()

st.sidebar.divider()
st.sidebar.markdown("#### Varlık Yönetimi")

# 1. Çoklu Varlık Ekleme / Güncelleme Formu
varlik_turu = st.sidebar.selectbox(
    "Varlık Sınıfı:",
    ["BIST Hissesi", "ABD Borsası (NASDAQ/NYSE)", "Kripto Varlık", "Emtia & Kıymetli Maden"],
    key="secilen_varlik_turu"
)

with st.sidebar.form("varlik_ekle_formu"):
    if "BIST" in varlik_turu:
        yeni_sembol = st.text_input("Sembol (BIST)", placeholder="Örn: THYAO, FROTO, ASELS").upper().strip()
        para_birimi = "TL"
    elif "ABD" in varlik_turu:
        yeni_sembol = st.text_input("Sembol (ABD)", placeholder="Örn: AAPL, NVDA, TSLA, MSFT").upper().strip()
        para_birimi = "$ USD"
    elif "Kripto" in varlik_turu:
        yeni_sembol = st.text_input("Kripto Kodu", placeholder="Örn: BTC, ETH, SOL, DOGE").upper().strip()
        para_birimi = "$ USD"
    else:
        emtia_secim = st.selectbox("Emtia Türü:", ["Gram Altın (TL)", "Ons Altın ($ GC=F)", "Gümüş ($ SI=F)"])
        if "Gram Altın" in emtia_secim:
            yeni_sembol = "GRAM_ALTIN"
            para_birimi = "TL"
        elif "Ons Altın" in emtia_secim:
            yeni_sembol = "GC=F"
            para_birimi = "$ USD"
        else:
            yeni_sembol = "SI=F"
            para_birimi = "$ USD"
            
    yeni_maliyet = st.number_input(f"Birim Maliyet ({para_birimi})", min_value=0.0, step=0.5, format="%.2f")
    yeni_adet = st.number_input("Adet / Miktar / Lot", min_value=0.0001, step=1.0, value=1.0, format="%.4f")
    
    ekle_butonu = st.form_submit_button("Varlığı Kaydet", type="primary", use_container_width=True)
    if ekle_butonu and yeni_sembol:
        if "BIST" in varlik_turu and not yeni_sembol.endswith(".IS") and "." not in yeni_sembol:
            yeni_sembol = f"{yeni_sembol}.IS"
        elif "Kripto" in varlik_turu and not yeni_sembol.endswith("-USD"):
            yeni_sembol = f"{yeni_sembol}-USD"
            
        if is_demo:
            st.session_state.demo_portfoy[yeni_sembol] = {"maliyet": float(yeni_maliyet), "adet": float(yeni_adet)}
        else:
            database.kullanici_hisse_ekle_guncelle(user_email, yeni_sembol, float(yeni_maliyet), float(yeni_adet))
            
        st.success(f"{yeni_sembol} portföye kaydedildi.")
        st.rerun()

# 2. Varlık Silme Formu
if portfoy:
    st.sidebar.divider()
    silinecek_hisse = st.sidebar.selectbox("Kaldırılacak Varlık:", list(portfoy.keys()))
    if st.sidebar.button("Varlığı Portföyden Kaldır", use_container_width=True):
        if is_demo:
            st.session_state.demo_portfoy.pop(silinecek_hisse, None)
        else:
            database.kullanici_hisse_sil(user_email, silinecek_hisse)
        st.sidebar.warning(f"{silinecek_hisse} kaldırıldı.")
        st.rerun()

st.sidebar.divider()
col_btn1, col_btn2 = st.sidebar.columns(2)
with col_btn1:
    if st.button("Sıfırla", use_container_width=True):
        if is_demo:
            st.session_state.demo_portfoy = {}
        else:
            database.kullanici_portfoyu_sifirla(user_email)
        st.rerun()
with col_btn2:
    if st.button("Örnek Portföy", use_container_width=True):
        if is_demo:
            st.session_state.demo_portfoy = {
                "THYAO.IS": {"maliyet": 270.00, "adet": 50.0},
                "TUPRS.IS": {"maliyet": 165.00, "adet": 100.0},
                "AKBNK.IS": {"maliyet": 58.00, "adet": 300.0},
                "NVDA": {"maliyet": 115.00, "adet": 12.0},
                "GRAM_ALTIN": {"maliyet": 2900.00, "adet": 16.0},
                "BTC-USD": {"maliyet": 62000.00, "adet": 0.02},
            }
        else:
            database.kullanici_ornek_portfoy_yukle(user_email)
        st.rerun()

# 3. Yapay Zeka Anahtarı
gemini_key = st.secrets.get("GEMINI_API_KEY", "")
if not gemini_key:
    st.sidebar.divider()
    gemini_key = st.sidebar.text_input(
        "Gemini API Anahtarı:", 
        type="password", 
        help="aistudio.google.com üzerinden temin edilebilir."
    )
else:
    st.sidebar.divider()
    st.sidebar.caption("Yapay zeka asistanı aktif")


# ==============================================================================
# ANA EKRAN: 2 BÜYÜK AMİRAL SEKME (PORTFÖY & PİYASA KEŞİF)
# ==============================================================================

tab_portfoy, tab_kesif = st.tabs([
    "Portföy & Servet Yönetimi",
    "Piyasa & Şirket Keşif Terminali"
])

# ------------------------------------------------------------------------------
# SEKME 1: PORTFÖY & SERVET YÖNETİMİ
# ------------------------------------------------------------------------------
with tab_portfoy:
    st.title("Kişisel Portföy & Servet Paneli")
    st.caption("Borsa İstanbul, Amerikan Borsaları, Kripto Varlıklar ve Emtia tek ekranda konsolide edilmiştir.")

    if not portfoy:
        st.info("Portföyünüzde henüz kayıtlı varlık bulunmamaktadır. Sol menüden varlık ekleyebilir veya 'Örnek Portföy' butonuna tıklayabilirsiniz.")
    else:
        toplamMaliyetTL = 0.0
        toplamGuncelDegerTL = 0.0
        enIyiVarlik = ""
        enYuksekKar = -999999
        enKotuVarlik = ""
        enDusukKar = 999999

        tabloVerisi = []
        pastaEtiketler = []
        pastaDegerler = []
        kategoriDegerler = {}
        portfoy_fiyatlari_tl = {}

        with st.spinner("Piyasa verileri konsolide ediliyor..."):
            for sembol, bilgi in portfoy.items():
                maliyet = float(bilgi["maliyet"])
                adet = float(bilgi["adet"])
                kategori, para, rozet = varlik_sinifi_belirle(sembol)
                
                gecmis = varlik_gecmisi_getir(sembol, period="6mo")
                if gecmis.empty:
                    continue
                    
                guncelFiyatYerel = float(gecmis['Close'].iloc[-1])
                
                if para == "USD":
                    maliyetTL = maliyet * usd_try
                    guncelFiyatTL = guncelFiyatYerel * usd_try
                    fiyatMetni = f"${guncelFiyatYerel:,.2f}"
                    maliyetMetni = f"${maliyet:,.2f}"
                else:
                    maliyetTL = maliyet
                    guncelFiyatTL = guncelFiyatYerel
                    fiyatMetni = f"{guncelFiyatYerel:,.2f} TL"
                    maliyetMetni = f"{maliyet:,.2f} TL"
                    
                portfoy_fiyatlari_tl[sembol] = (guncelFiyatTL, para)
                varlikMaliyetToplami = maliyetTL * adet
                varlikGuncelToplami = guncelFiyatTL * adet
                
                toplamMaliyetTL += varlikMaliyetToplami
                toplamGuncelDegerTL += varlikGuncelToplami
                
                karDurumuYuzde = ((guncelFiyatYerel - maliyet) / maliyet) * 100 if maliyet > 0 else 0.0
                karDurumuTL = (guncelFiyatTL - maliyetTL) * adet
                
                tabloVerisi.append({
                    "Varlık": f"{rozet} {sembol}",
                    "Kategori": kategori,
                    "Miktar": adet,
                    "Maliyet": maliyetMetni,
                    "Piyasa Fiyatı": fiyatMetni,
                    "Toplam Değer": f"{varlikGuncelToplami:,.2f} TL",
                    "Net Kâr / Zarar": f"{karDurumuTL:+,.2f} TL",
                    "Getiri (%)": round(karDurumuYuzde, 2)
                })
                
                pastaEtiketler.append(f"{sembol}")
                pastaDegerler.append(varlikGuncelToplami)
                kategoriDegerler[kategori] = kategoriDegerler.get(kategori, 0.0) + varlikGuncelToplami
                
                if karDurumuYuzde > enYuksekKar:
                    enYuksekKar = karDurumuYuzde
                    enIyiVarlik = sembol
                if karDurumuYuzde < enDusukKar:
                    enDusukKar = karDurumuYuzde
                    enKotuVarlik = sembol

        toplamKarTL = toplamGuncelDegerTL - toplamMaliyetTL
        toplamKarYuzde = ((toplamGuncelDegerTL - toplamMaliyetTL) / toplamMaliyetTL) * 100 if toplamMaliyetTL > 0 else 0.0

        try:
            bist_veri = yf.Ticker("XU100.IS").history(period="6mo")
            bist_getiri = ((bist_veri['Close'].iloc[-1] - bist_veri['Close'].iloc[0]) / bist_veri['Close'].iloc[0]) * 100
        except Exception:
            bist_getiri = 0.0

        fark = toplamKarYuzde - bist_getiri

        # 4'lü Üst KPI Kartları
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric(label="Toplam Yatırılan Maliyet", value=f"{toplamMaliyetTL:,.2f} TL", delta=f"${toplamMaliyetTL / usd_try:,.2f} USD", delta_color="off")
        with col2:
            st.metric(label="Konsolide Portföy Değeri", value=f"{toplamGuncelDegerTL:,.2f} TL", delta=f"${toplamGuncelDegerTL / usd_try:,.2f} USD", delta_color="off")
        with col3:
            st.metric(label="Toplam Net Getiri", value=f"{toplamKarTL:+,.2f} TL", delta=f"{toplamKarYuzde:+.2f}%")
        with col4:
            st.metric(label="BIST 100 Karşılaştırması", value=f"Endeks: %{bist_getiri:.1f}", delta=f"{fark:+.1f}% Göreceli Fark")

        st.divider()
        st.dataframe(tabloVerisi, use_container_width=True)

        st.divider()
        tab_pasta1, tab_pasta2, tab_temettu, tab_dengeleme = st.tabs([
            "Varlık Sınıfı Dağılımı", 
            "Pozisyon Bazında Dağılım", 
            "Temettü & Pasif Gelir Radarı",
            "Akıllı Portföy Dengeleme"
        ])
        
        luxury_colors = ['#38bdf8', '#10b981', '#f59e0b', '#a855f7', '#ec4899', '#64748b']
        
        with tab_pasta1:
            fig_kat = px.pie(names=list(kategoriDegerler.keys()), values=list(kategoriDegerler.values()), hole=0.55, color_discrete_sequence=luxury_colors)
            fig_kat.update_traces(textposition='inside', textinfo='percent+label', hovertemplate="<b>%{label}</b><br>Toplam: %{value:,.2f} TL<br>Pay: %{percent}<extra></extra>")
            fig_kat.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color='#94a3b8'), margin=dict(t=10, b=10, l=10, r=10), height=340)
            st.plotly_chart(fig_kat, use_container_width=True)

        with tab_pasta2:
            fig_pasta = px.pie(names=pastaEtiketler, values=pastaDegerler, hole=0.55, color_discrete_sequence=luxury_colors)
            fig_pasta.update_traces(textposition='inside', textinfo='percent+label', hovertemplate="<b>%{label}</b><br>Toplam: %{value:,.2f} TL<br>Pay: %{percent}<extra></extra>")
            fig_pasta.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color='#94a3b8'), margin=dict(t=10, b=10, l=10, r=10), height=340)
            st.plotly_chart(fig_pasta, use_container_width=True)

        with tab_temettu:
            st.markdown("##### Portföy Temettü & Pasif Gelir Projeksiyonu")
            temettu_satirlari = []
            toplam_yillik_temettu = 0.0

            for sembol, veri in portfoy.items():
                adet = float(veri.get("adet", 1.0))
                try:
                    fund = get_company_fundamentals(sembol)
                except Exception:
                    fund = {}
                div_rate = fund.get("dividendRate")
                div_yield = fund.get("dividendYield")
                
                if sembol in portfoy_fiyatlari_tl:
                    fiyat_tl, p_para = portfoy_fiyatlari_tl[sembol]
                else:
                    _, p_para, _ = varlik_sinifi_belirle(sembol)
                    fiyat_tl = float(veri.get("maliyet", 0.0)) * (usd_try if p_para == "USD" else 1.0)

                # Detay A: dividendRate varsa doğrudan hisse başına net nakit ile hesapla
                hisse_yillik = 0.0
                gosterim_verim = "—"
                if div_rate and not pd.isna(div_rate) and div_rate > 0:
                    rate_tl = div_rate * usd_try if p_para == "USD" else div_rate
                    hisse_yillik = adet * rate_tl
                    toplam_yillik_temettu += hisse_yillik
                    if div_yield and not pd.isna(div_yield) and div_yield > 0:
                        y_val = div_yield * 100 if div_yield < 1 else div_yield
                        gosterim_verim = f"%{y_val:.2f} ({div_rate:.2f} {p_para}/Lot)"
                    else:
                        gosterim_verim = f"{div_rate:.2f} {p_para}/Lot"
                elif div_yield and not pd.isna(div_yield) and div_yield > 0:
                    div_pct = (div_yield / 100) if div_yield > 1 else div_yield
                    hisse_yillik = (adet * fiyat_tl) * div_pct
                    toplam_yillik_temettu += hisse_yillik
                    gosterim_verim = f"%{div_pct * 100:.2f}"

                if hisse_yillik > 0:
                    temettu_satirlari.append({
                        "Varlık": sembol,
                        "Adet": f"{adet:,.2f}",
                        "Fiyat": f"{fiyat_tl:,.2f} TL",
                        "Temettü / Lot": gosterim_verim,
                        "Yıllık Tahmini Gelir": f"{hisse_yillik:,.2f} TL",
                        "_hisse_yillik_num": hisse_yillik,
                        "_fiyat_tl_num": fiyat_tl,
                        "_adet_num": adet
                    })

            col_t1, col_t2, col_t3 = st.columns(3)
            with col_t1:
                st.metric(
                    label="Yıllık Tahmini Pasif Gelir",
                    value=f"{toplam_yillik_temettu:,.2f} TL",
                    help="Portföyünüzdeki hisselerin net nakit dağıtım tutarlarına (dividendRate) göre yıllık nakit akışı tahmini."
                )
            with col_t2:
                aylik_nakit = toplam_yillik_temettu / 12
                st.metric(
                    label="Aylık Ortalama Nakit Akışı",
                    value=f"{aylik_nakit:,.2f} TL / Ay",
                    help="Yıllık temettü gelirinin 12 aya bölünmüş eşdeğer aylık pasif maaş karşılığı."
                )
            with col_t3:
                portfoy_verim = (toplam_yillik_temettu / toplamGuncelDegerTL * 100) if toplamGuncelDegerTL > 0 else 0.0
                st.metric(
                    label="Portföy Temettü Verimi",
                    value=f"%{portfoy_verim:.2f}",
                    help="Toplam konsolide portföy büyüklüğünüze oranla yıllık net temettü verimi."
                )

            if temettu_satirlari:
                df_goster = pd.DataFrame([{k: v for k, v in row.items() if not k.startswith('_')} for row in temettu_satirlari])
                st.dataframe(df_goster, use_container_width=True)
            else:
                st.info("Portföyünüzde şu an temettü dağıtan bir hisse senedi bulunmuyor veya çarpanları sıfır görünüyor.")

            # Detay B: Kullanıcı Hedefi + Sepet Dengesini Bozmadan Hedefe Ulaşma Reçetesi
            st.divider()
            st.markdown("###### Temettü Emekliliği Hedef Simülatörü")
            col_h1, col_h2 = st.columns([1.5, 2.5])
            with col_h1:
                hedef_aylik = st.number_input(
                    "Aylık Hedef Pasif Gelir (TL):",
                    min_value=1000.0,
                    max_value=1000000.0,
                    value=25000.0,
                    step=2500.0,
                    help="Hedeflediğiniz aylık ortalama net pasif temettü geliri."
                )
            with col_h2:
                ilerleme = min(aylik_nakit / hedef_aylik, 1.0) if hedef_aylik > 0 else 0.0
                st.write("")
                st.progress(ilerleme)
                st.caption(f"✦ **Hedef İlerlemesi:** {hedef_aylik:,.0f} TL/Ay Hedefinizin **%{ilerleme*100:.1f}** kadarı mevcut hisselerinizce karşılanıyor.")

            # Hedefe Ulaşma Matematiksel Reçetesi
            if aylik_nakit < hedef_aylik:
                aylik_acik = hedef_aylik - aylik_nakit
                yillik_acik = aylik_acik * 12

                recete_parcalari = []
                if temettu_satirlari and toplam_yillik_temettu > 0:
                    for row in temettu_satirlari:
                        pay = row["_hisse_yillik_num"] / toplam_yillik_temettu
                        hisseye_dusen_yillik = yillik_acik * pay
                        hisse_basina_yillik = row["_hisse_yillik_num"] / row["_adet_num"] if row["_adet_num"] > 0 else 0.0
                        if hisse_basina_yillik > 0:
                            gereken_ek_lot = int(np.ceil(hisseye_dusen_yillik / hisse_basina_yillik))
                            recete_parcalari.append(f"+{gereken_ek_lot:,} lot **{row['Varlık']}**")
                
                recete_str = ", ".join(recete_parcalari) if recete_parcalari else "portföyünüze temettü verimi yüksek hisseler eklenmesi"

                st.markdown(f"""
                <div style="background: rgba(255, 255, 255, 0.015); border: 1px solid rgba(255, 255, 255, 0.06); border-radius: 10px; padding: 12px 16px; margin-top: 10px;">
                    <div style="font-size: 11px; text-transform: uppercase; letter-spacing: 0.05em; font-weight: 600; color: #94a3b8;">✦ Sepet Dengeleme & Hedefe Ulaşma Reçetesi</div>
                    <div style="font-size: 12.5px; color: #cbd5e1; margin-top: 5px; line-height: 1.5;">
                        Aylık <b>{hedef_aylik:,.0f} TL</b> hedefe ulaşmak için yıllık <b>{yillik_acik:,.0f} TL</b> ek nakit akışı gerekiyor.
                        Mevcut hisse dağılım dengenizi koruyarak bu açığı kapatmak için portföyünüze yaklaşık: <b>{recete_str}</b> takviyesi yapılması önerilir.
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.success("Tebrikler! Mevcut portföyünüz belirlediğiniz aylık pasif gelir hedefini fazlasıyla karşılıyor.")

        with tab_dengeleme:
            st.markdown("##### Akıllı Portföy Dengeleme & Rebalance Robotu")
            st.caption("Piyasa dalgalanmalarının bozduğu varlık ağırlıklarını stratejik hedefinize geri döndürmek için otomatik al/sat reçetesi üretir.")

            # 1. Strateji ve Mod Seçimi
            col_strat1, col_strat2 = st.columns([1.5, 1.5])
            with col_strat1:
                secilen_strat_adi = st.selectbox(
                    "Stratejik Dağılım Modeli:",
                    list(REBALANCE_STRATEJILERI.keys()),
                    key="rebalance_strat_secim"
                )
                strat_bilgi = REBALANCE_STRATEJILERI[secilen_strat_adi]
                st.caption(f"✦ **Model Felsefesi:** {strat_bilgi['aciklama']}")

            with col_strat2:
                rebalance_mod = st.radio(
                    "Dengeleme Yaklaşımı:",
                    ["Kâr Satışı ile Dengeleme (Sıfır Nakit)", "Yeni Tasarruf Ekleme (Satışsız)"],
                    horizontal=True,
                    key="rebalance_mod_secim"
                )
                secilen_mod_kodu = "satisli" if "Sıfır Nakit" in rebalance_mod else "tasarruf"
                if secilen_mod_kodu == "satisli":
                    st.caption("✦ Hedefi aşan varlıklardan kâr satışı yapılır; elde edilen nakitle geride kalanlar alınır.")
                else:
                    st.caption("✦ Hiçbir varlık satılmaz; eklenen yeni tasarruf en geride kalan sınıflara paylaştırılır.")

            # Hedef Yüzdelerin Alınması
            hedef_oranlar = {}
            if secilen_strat_adi == "Özel Dağılım (Kişiselleştirilmiş)":
                st.markdown("###### Özel Hedef Yüzdelerinizi Belirleyin (Toplam %100 Olmalıdır):")
                c_oz1, c_oz2, c_oz3, c_oz4 = st.columns(4)
                with c_oz1:
                    h_bist = st.number_input("% Borsa İstanbul", min_value=0.0, max_value=100.0, value=25.0, step=5.0, key="h_bist_in")
                with c_oz2:
                    h_abd = st.number_input("% Amerikan Borsası", min_value=0.0, max_value=100.0, value=25.0, step=5.0, key="h_abd_in")
                with c_oz3:
                    h_altin = st.number_input("% Altın & Emtia", min_value=0.0, max_value=100.0, value=25.0, step=5.0, key="h_altin_in")
                with c_oz4:
                    h_kripto = st.number_input("% Kripto Varlık", min_value=0.0, max_value=100.0, value=25.0, step=5.0, key="h_kripto_in")
                
                toplam_hedef_yuzde = h_bist + h_abd + h_altin + h_kripto
                if abs(toplam_hedef_yuzde - 100.0) > 0.01:
                    st.warning(f"Hedef oranların toplamı %{toplam_hedef_yuzde:.0f}. Kusursuz dengeleme için toplam %100 olmalıdır.")
                hedef_oranlar = {
                    "BIST Hissesi": h_bist,
                    "ABD Borsası": h_abd,
                    "Emtia & Maden": h_altin,
                    "Kripto Varlık": h_kripto
                }
            else:
                hedef_oranlar = {
                    "BIST Hissesi": strat_bilgi["BIST Hissesi"],
                    "ABD Borsası": strat_bilgi["ABD Borsası"],
                    "Emtia & Maden": strat_bilgi["Emtia & Maden"],
                    "Kripto Varlık": strat_bilgi["Kripto Varlık"]
                }

            # Tasarruf Ekleme Miktarı (Mod B ise)
            ek_nakit_tl = 0.0
            if secilen_mod_kodu == "tasarruf":
                col_nakit1, col_nakit2 = st.columns([1.5, 2.5])
                with col_nakit1:
                    ek_nakit_tl = st.number_input(
                        "Portföye Eklenecek Yeni Tasarruf (TL):",
                        min_value=500.0,
                        max_value=10000000.0,
                        value=15000.0,
                        step=2500.0,
                        key="rebalance_ek_nakit_in"
                    )
                with col_nakit2:
                    st.write("")
                    st.info(f"✦ Bu ay eklenecek **{ek_nakit_tl:,.0f} TL**, portföyünüzün hedef dağılımına en uzak varlıklara otomatik paylaştırılacaktır.")

            # Matematiksel Motoru Çalıştır (SRP)
            sonuc = hesapla_portfoy_rebalancing(
                kategori_degerler=kategoriDegerler,
                toplam_deger_tl=toplamGuncelDegerTL,
                hedef_oranlar=hedef_oranlar,
                eklenecek_nakit_tl=ek_nakit_tl,
                mod=secilen_mod_kodu,
                portfoy=portfoy,
                portfoy_fiyatlari_tl=portfoy_fiyatlari_tl
            )

            st.divider()

            # 2. Sapma & Denge Radarı (4 Varlık Sınıfı Kıyas Kartları)
            st.markdown("###### Mevcut Ağırlık vs. Stratejik Hedef Radarı")
            c_rad1, c_rad2, c_rad3, c_rad4 = st.columns(4)
            sutunlar_radar = [c_rad1, c_rad2, c_rad3, c_rad4]

            for idx, sa in enumerate(sonuc["sinif_analizleri"]):
                col_r = sutunlar_radar[idx]
                with col_r:
                    kat_adi = sa["sinif"]
                    mev_pct = sa["mevcut_oran"]
                    hed_pct = sa["hedef_oran"]
                    sapma = sa["sapma_yuzde"]
                    durum = sa["durum"]

                    if durum == "Aşırı Ağırlık":
                        badge_bg = "rgba(239, 68, 68, 0.12)"
                        badge_color = "#f87171"
                        badge_border = "rgba(239, 68, 68, 0.25)"
                        durum_etiket = f"Aşırı Ağırlık (+%{sapma:.1f})"
                    elif durum == "Düşük Ağırlık":
                        badge_bg = "rgba(56, 189, 248, 0.12)"
                        badge_color = "#38bdf8"
                        badge_border = "rgba(56, 189, 248, 0.25)"
                        durum_etiket = f"Düşük Ağırlık (%{sapma:.1f})"
                    else:
                        badge_bg = "rgba(34, 197, 94, 0.12)"
                        badge_color = "#4ade80"
                        badge_border = "rgba(34, 197, 94, 0.25)"
                        durum_etiket = "Dengede"

                    st.markdown(f"""
                    <div style="background: rgba(255, 255, 255, 0.02); border: 1px solid rgba(255, 255, 255, 0.06); border-radius: 12px; padding: 14px 16px; margin-bottom: 8px;">
                        <div style="font-size: 11px; text-transform: uppercase; letter-spacing: 0.05em; font-weight: 600; color: #94a3b8; margin-bottom: 6px;">
                            {kat_adi}
                        </div>
                        <div style="display: flex; align-items: baseline; justify-content: space-between; margin-bottom: 8px;">
                            <span style="font-size: 20px; font-weight: 600; color: #f1f5f9;">%{mev_pct:.1f}</span>
                            <span style="font-size: 12px; color: #64748b;">Hedef: %{hed_pct:.1f}</span>
                        </div>
                        <div style="background: {badge_bg}; color: {badge_color}; border: 1px solid {badge_border}; font-size: 10.5px; font-weight: 600; padding: 3px 8px; border-radius: 12px; text-align: center;">
                            ● {durum_etiket}
                        </div>
                        <div style="font-size: 11px; color: #64748b; margin-top: 8px; text-align: center;">
                            Mevcut: {sa['mevcut_deger']:,.0f} TL
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

            # 3. Akıllı Alış / Satış Reçetesi
            st.divider()
            emirler = sonuc["recete_emirleri"]

            if not emirler:
                st.success("Tebrikler! Portföyünüz seçilen stratejik hedef dağılımıyla tam dengede. Herhangi bir al/sat işlemine gerek yok.")
            else:
                st.markdown("###### Dengeleme İçin Önerilen Lot ve İşlem Reçetesi")
                col_em1, col_em2 = st.columns(2)
                
                satis_emirleri = [e for e in emirler if e["islem"] == "SAT"]
                alis_emirleri = [e for e in emirler if e["islem"] == "AL"]

                with col_em1:
                    st.markdown("""
                    <div style="font-size: 12px; text-transform: uppercase; letter-spacing: 0.05em; font-weight: 600; color: #f87171; margin-bottom: 8px;">
                        ● Kâr Satış Emirleri (Nakit Yarat)
                    </div>
                    """, unsafe_allow_html=True)
                    if not satis_emirleri:
                        st.caption("Bu stratejide herhangi bir satış işlemi önerilmiyor.")
                    else:
                        for se in satis_emirleri:
                            st.markdown(f"""
                            <div style="background: rgba(239, 68, 68, 0.04); border: 1px solid rgba(239, 68, 68, 0.15); border-radius: 10px; padding: 10px 14px; margin-bottom: 8px; display: flex; justify-content: space-between; align-items: center;">
                                <div>
                                    <div style="font-size: 13.5px; font-weight: 600; color: #f1f5f9;">{se['varlik']}</div>
                                    <div style="font-size: 11px; color: #94a3b8;">{se['sinif']}</div>
                                </div>
                                <div style="text-align: right;">
                                    <div style="font-size: 14px; font-weight: 600; color: #f87171;">{se['lot_metin']}</div>
                                    <div style="font-size: 11px; color: #64748b;">≈ {se['tutar_tl']:,.0f} TL</div>
                                </div>
                            </div>
                            """, unsafe_allow_html=True)

                with col_em2:
                    st.markdown("""
                    <div style="font-size: 12px; text-transform: uppercase; letter-spacing: 0.05em; font-weight: 600; color: #4ade80; margin-bottom: 8px;">
                        ● Alım & Takviye Emirleri (Açığı Kapat)
                    </div>
                    """, unsafe_allow_html=True)
                    if not alis_emirleri:
                        st.caption("Bu stratejide herhangi bir ek alım işlemi gerekmiyor.")
                    else:
                        for ae in alis_emirleri:
                            st.markdown(f"""
                            <div style="background: rgba(34, 197, 94, 0.04); border: 1px solid rgba(34, 197, 94, 0.15); border-radius: 10px; padding: 10px 14px; margin-bottom: 8px; display: flex; justify-content: space-between; align-items: center;">
                                <div>
                                    <div style="font-size: 13.5px; font-weight: 600; color: #f1f5f9;">{ae['varlik']}</div>
                                    <div style="font-size: 11px; color: #94a3b8;">{ae['sinif']}</div>
                                </div>
                                <div style="text-align: right;">
                                    <div style="font-size: 14px; font-weight: 600; color: #4ade80;">{ae['lot_metin']}</div>
                                    <div style="font-size: 11px; color: #64748b;">≈ {ae['tutar_tl']:,.0f} TL</div>
                                </div>
                            </div>
                            """, unsafe_allow_html=True)

                ozet_metin = ""
                if secilen_mod_kodu == "satisli":
                    ozet_metin = f"Bu reçete uygulandığında yaklaşık <b>{sonuc['toplam_satis_tl']:,.0f} TL</b> nakit yaratılacak ve bu tutar eksik sınıflara dağıtılarak portföyünüz %100 hedef modeline kavuşacaktır."
                else:
                    ozet_metin = f"Eklediğiniz <b>{ek_nakit_tl:,.0f} TL</b> yeni tasarruf, mevcut varlıklarınız satılmadan doğrudan geride kalan sınıflara paylaştırılmıştır."

                st.markdown(f"""
                <div style="background: rgba(255, 255, 255, 0.015); border: 1px solid rgba(255, 255, 255, 0.06); border-radius: 10px; padding: 12px 16px; margin-top: 12px;">
                    <div style="font-size: 11px; text-transform: uppercase; letter-spacing: 0.05em; font-weight: 600; color: #38bdf8;">✦ Rebalance Sonuç Özeti</div>
                    <div style="font-size: 12.5px; color: #cbd5e1; margin-top: 4px; line-height: 1.5;">
                        {ozet_metin}
                    </div>
                </div>
                """, unsafe_allow_html=True)

        # Öne Çıkan Getiriler
        if enIyiVarlik and enKotuVarlik:
            col_iyi, col_kotu = st.columns(2)
            with col_iyi:
                st.caption(f"En Yüksek Performans: **{enIyiVarlik}** (%{enYuksekKar:+.2f})")
            with col_kotu:
                st.caption(f"En Düşük Performans: **{enKotuVarlik}** (%{enDusukKar:+.2f})")

        st.divider()
        st.subheader("Varlık Analizi & Fiyat Projeksiyonu")

        secilen = st.selectbox("Analiz Edilecek Portföy Varlığı:", list(portfoy.keys()), key="portfoy_secim")
        secilen_kat, secilen_para, secilen_rozet = varlik_sinifi_belirle(secilen)
        gecmisSecilen = varlik_gecmisi_getir(secilen, period="6mo")
        secilenMaliyet = float(portfoy[secilen]["maliyet"])

        if not gecmisSecilen.empty:
            gecmisSecilen['SMA20'] = gecmisSecilen['Close'].rolling(window=20).mean()
            gecmisSecilen['SMA50'] = gecmisSecilen['Close'].rolling(window=50).mean()

            fark_fiyat = gecmisSecilen['Close'].diff()
            kazanc = fark_fiyat.where(fark_fiyat > 0, 0.0).rolling(window=14).mean()
            kayip = (-fark_fiyat.where(fark_fiyat < 0, 0.0)).rolling(window=14).mean()
            rs = kazanc / kayip
            gecmisSecilen['RSI'] = 100 - (100 / (1 + rs))
            guncel_rsi = float(gecmisSecilen['RSI'].iloc[-1])

            ema12 = gecmisSecilen['Close'].ewm(span=12, adjust=False).mean()
            ema26 = gecmisSecilen['Close'].ewm(span=26, adjust=False).mean()
            gecmisSecilen['MACD'] = ema12 - ema26
            gecmisSecilen['Signal'] = gecmisSecilen['MACD'].ewm(span=9, adjust=False).mean()
            gecmisSecilen['Hist'] = gecmisSecilen['MACD'] - gecmisSecilen['Signal']

            guncel_macd = float(gecmisSecilen['MACD'].iloc[-1])
            guncel_signal = float(gecmisSecilen['Signal'].iloc[-1])
            guncel_sma20 = float(gecmisSecilen['SMA20'].iloc[-1])
            guncel_sma50 = float(gecmisSecilen['SMA50'].iloc[-1])

            macd_al = guncel_macd > guncel_signal
            golden_cross = guncel_sma20 > guncel_sma50

            # 7 Günlük ML Regresyon Tahmini
            gunler = np.arange(len(gecmisSecilen))
            fiyatlar = gecmisSecilen['Close'].values
            p = np.polyfit(gunler, fiyatlar, deg=1)
            trend_modeli = np.poly1d(p)
            tahmin_gecmis = trend_modeli(gunler)
            std_hata = float(np.std(fiyatlar - tahmin_gecmis))

            son_tarih = gecmisSecilen.index[-1]
            fut_indices = np.arange(len(gecmisSecilen) - 1, len(gecmisSecilen) + 7)
            fut_prices = trend_modeli(fut_indices)
            fut_dates = [son_tarih] + list(pd.date_range(start=son_tarih + pd.Timedelta(days=1), periods=7, freq='D'))

            tahmin_7gun = float(fut_prices[-1])
            guncel_son_fiyat = float(fiyatlar[-1])
            tahmin_fark_yuzde = ((tahmin_7gun - guncel_son_fiyat) / guncel_son_fiyat) * 100
            gunluk_egim = float(p[0])

            # İnteraktif Trend Grafiği
            fig_trend = go.Figure()
            fig_trend.add_trace(go.Scatter(x=gecmisSecilen.index, y=gecmisSecilen['Close'], name=f'Kapanış ({secilen_para})', line=dict(color='#38bdf8', width=2.5)))
            fig_trend.add_trace(go.Scatter(x=gecmisSecilen.index, y=gecmisSecilen['SMA20'], name='SMA 20', line=dict(color='#fbbf24', width=1.5)))
            fig_trend.add_trace(go.Scatter(x=gecmisSecilen.index, y=gecmisSecilen['SMA50'], name='SMA 50', line=dict(color='#a855f7', width=1.5)))
            fig_trend.add_hline(y=secilenMaliyet, line_dash="dash", line_color="#f43f5e", annotation_text=f"Maliyet ({secilenMaliyet:.2f} {secilen_para})", annotation_position="top left")

            fig_trend.add_trace(go.Scatter(x=fut_dates, y=fut_prices, name='7 Günlük Projeksiyon', mode='lines', line=dict(color='#c084fc', width=2.5, dash='dash')))
            fig_trend.add_trace(go.Scatter(x=fut_dates, y=fut_prices + std_hata, name='Tahmin Üst Sınır', mode='lines', line=dict(color='rgba(0,0,0,0)', width=0), showlegend=False, hoverinfo='skip'))
            fig_trend.add_trace(go.Scatter(x=fut_dates, y=fut_prices - std_hata, name='Güven Aralığı', mode='lines', fill='tonexty', fillcolor='rgba(192, 132, 252, 0.12)', line=dict(color='rgba(0,0,0,0)', width=0), hoverinfo='skip'))

            fig_trend.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#94a3b8'),
                xaxis=dict(gridcolor='rgba(255,255,255,0.04)', zerolinecolor='rgba(255,255,255,0.05)'),
                yaxis=dict(gridcolor='rgba(255,255,255,0.04)', zerolinecolor='rgba(255,255,255,0.05)'),
                title=f"{secilen} — Fiyat Trendi ve 7 Günlük Model Projeksiyonu",
                xaxis_title="Tarih",
                yaxis_title=f"Fiyat ({secilen_para})",
                hovermode="x unified",
                height=450,
                margin=dict(t=40, b=20, l=20, r=20)
            )
            st.plotly_chart(fig_trend, use_container_width=True)

            # Akakçe/Cimri usulü Projeksiyon Kartları
            col_ml1, col_ml2, col_ml3 = st.columns(3)
            with col_ml1:
                st.metric(label="7 Günlük Model Hedefi", value=f"{tahmin_7gun:,.2f} {secilen_para}", delta=f"{tahmin_fark_yuzde:+.2f}%")
            with col_ml2:
                st.metric(label="Model Güven Aralığı", value=f"±{std_hata:.2f} {secilen_para}")
            with col_ml3:
                egim_yorum = "Pozitif İvme" if gunluk_egim > 0 else "Negatif İvme"
                st.metric(label="Günlük Trend Eğimi", value=f"{gunluk_egim:+.2f} {secilen_para}/Gün", delta=egim_yorum)

            # Minimalist Durum Rozetleri
            c_ind1, c_ind2, c_ind3 = st.columns(3)
            with c_ind1:
                if guncel_rsi > 70:
                    st.caption(f"● **RSI {guncel_rsi:.1f}** — Aşırı Alım Bölgesi")
                elif guncel_rsi < 30:
                    st.caption(f"● **RSI {guncel_rsi:.1f}** — Aşırı Satım (Fırsat Bölgesi)")
                else:
                    st.caption(f"● **RSI {guncel_rsi:.1f}** — Nötr Denge")
            with c_ind2:
                if macd_al:
                    st.caption(f"● **MACD {guncel_macd:.2f}** — Pozitif İvme (Alıcı Üstünlüğü)")
                else:
                    st.caption(f"● **MACD {guncel_macd:.2f}** — Negatif İvme (Satıcı Baskısı)")
            with c_ind3:
                if golden_cross:
                    st.caption("● **Trend:** SMA 20 > SMA 50 (Yükseliş Trendi)")
                else:
                    st.caption("● **Trend:** SMA 20 < SMA 50 (Düşüş Eğilimi)")

            # Strateji Simülasyonu
            with st.expander(f"Strateji Simülasyonu: {secilen} MACD Kesişim Performansı"):
                try:
                    df_sim = gecmisSecilen.copy()
                    df_sim['Pozisyon'] = (df_sim['MACD'] > df_sim['Signal']).astype(int).shift(1)
                    df_sim['Gunluk_Getiri'] = df_sim['Close'].pct_change()
                    df_sim['Strateji_Getiri'] = df_sim['Gunluk_Getiri'] * df_sim['Pozisyon']
                    getiri_bh = ((1 + df_sim['Gunluk_Getiri'].dropna()).prod() - 1) * 100
                    getiri_strat = ((1 + df_sim['Strateji_Getiri'].dropna()).prod() - 1) * 100
                    col_sim1, col_sim2 = st.columns(2)
                    with col_sim1:
                        st.metric("Alıp Bekleme Getirisi", f"%{getiri_bh:.2f}")
                    with col_sim2:
                        fark_strat = getiri_strat - getiri_bh
                        st.metric("MACD Sinyal Stratejisi", f"%{getiri_strat:.2f}", delta=f"{fark_strat:+.2f}%")
                except Exception:
                    st.caption("Geçmiş veri hesaplanamadı.")

            # Seçilen Varlık Canlı Haberleri & AI Algı Radarı
            h_arama = secilen.replace(".IS", "").replace("-USD", "")
            portfoy_haberler = get_live_news(h_arama, count=2)
            if portfoy_haberler:
                st.markdown(f"###### {secilen} — Canlı Haber Akışı & Piyasa Algısı")
                if gemini_key:
                    h_tuple = tuple(h['headline'] for h in portfoy_haberler)
                    s_data = get_ai_news_sentiment(secilen, h_tuple, gemini_key)
                    if s_data:
                        sk = s_data.get("skor", "Nötr (Dengeli)")
                        yz = s_data.get("yuzde", 50)
                        oz = s_data.get("ozet", "")
                        zm = s_data.get("zaman", "")
                        
                        is_p = any(w in sk.lower() for w in ["boğa", "pozitif", "yükseliş"])
                        is_n = any(w in sk.lower() for w in ["ayı", "negatif", "düşüş"])
                        bg = "rgba(34, 197, 94, 0.12)" if is_p else ("rgba(239, 68, 68, 0.12)" if is_n else "rgba(234, 179, 8, 0.12)")
                        clr = "#4ade80" if is_p else ("#f87171" if is_n else "#facc15")
                        bdr = "rgba(34, 197, 94, 0.25)" if is_p else ("rgba(239, 68, 68, 0.25)" if is_n else "rgba(234, 179, 8, 0.25)")

                        st.markdown(f"""
                        <div style="background: rgba(255, 255, 255, 0.02); border: 1px solid rgba(255, 255, 255, 0.07); border-radius: 12px; padding: 12px 16px; margin-bottom: 12px;">
                            <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 6px;">
                                <span style="font-size: 11px; text-transform: uppercase; letter-spacing: 0.06em; font-weight: 600; color: #64748b;">✦ AI Algı Radarı</span>
                                <span style="background: {bg}; color: {clr}; border: 1px solid {bdr}; font-size: 11px; font-weight: 600; padding: 2px 8px; border-radius: 16px;">● {sk} (%{yz})</span>
                            </div>
                            <div style="font-size: 13px; color: #e2e8f0; line-height: 1.4; margin-bottom: 6px;">
                                {oz}
                            </div>
                            <div style="font-size: 10.5px; color: #475569;">
                                ✦ Yapay Zeka Analizi • Güncelleme: {zm} (2 Saatlik Kurumsal Döngü)
                            </div>
                        </div>
                        """, unsafe_allow_html=True)

                col_ph1, col_ph2 = st.columns(2)
                for i_h, hab_item in enumerate(portfoy_haberler):
                    col_target = col_ph1 if i_h == 0 else col_ph2
                    with col_target:
                        st.markdown(f"""
                        <div class="news-card" style="padding: 12px 14px; margin-bottom: 8px;">
                            <span style="color: #38bdf8; font-size: 10.5px; font-weight: 600;">{hab_item['source']}</span>
                            <span style="color: #475569; font-size: 10.5px; float: right;">{hab_item['date']}</span>
                            <div style="font-weight: 500; font-size: 13px; margin-top: 6px; color: #f1f5f9; line-height: 1.3;">{hab_item['headline']}</div>
                            <div style="margin-top: 8px;">
                                <a href="{hab_item['link']}" target="_blank" style="color: #64748b; font-size: 11px; text-decoration: none;">Haberi Oku ↗</a>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)

            # Gemini Analiz Kartı
            st.divider()
            st.subheader("Yapay Zeka Portföy Analisti")
            if st.button("Portföy ve Varlık Analizi Oluştur", key="gemini_portfoy_btn"):
                if not gemini_key:
                    st.warning("Sol menüden Gemini API anahtarınızı tanımlayın.")
                else:
                    with st.spinner("Analiz hazırlanıyor..."):
                        try:
                            from google import genai
                            client = genai.Client(api_key=gemini_key)
                            prompt = f"""
Sen Wall Street ve Borsa İstanbul konusunda uzman kıdemli bir küresel portföy yöneticisisin.
Yatırımcı: {user.get('ad_soyad')}
Toplam Servet: {toplamGuncelDegerTL:,.2f} TL (≈ ${toplamGuncelDegerTL / usd_try:,.2f} USD)
Toplam Maliyet: {toplamMaliyetTL:,.2f} TL
Net Getiri: {toplamKarTL:+,.2f} TL (%{toplamKarYuzde:+.2f})
Dolar Kuru: {usd_try:.2f} TL
Varlıklar: {list(portfoy.keys())}
Dağılım: {kategoriDegerler}
İncelenen Varlık: {secilen} ({secilen_kat}) | Fiyat: {guncel_son_fiyat:,.2f} {secilen_para} | 14G RSI: {guncel_rsi:.1f} | 7 Günlük Model Hedefi: {tahmin_7gun:,.2f} {secilen_para} (%{tahmin_fark_yuzde:+.2f})
Lütfen 3 başlık altında profesyonel, net ve Türkçe bir analiz sun:
1. Küresel Portföy Sağlık & Risk Değerlendirmesi
2. {secilen} Teknik & Projeksiyon Yorumu
3. Kısa & Orta Vade Stratejik Öneriler
(Yatırım tavsiyesi olmadığını belirt).
"""
                            modeller = ["gemini-2.0-flash", "gemini-1.5-flash", "gemini-1.5-pro"]
                            try:
                                live_models = [m.name for m in client.models.list() if "gemini" in m.name.lower() and "embed" not in m.name.lower()]
                                if live_models:
                                    modeller = live_models
                            except Exception:
                                pass
                            for m_name in modeller:
                                try:
                                    res = client.models.generate_content(model=m_name, contents=prompt)
                                    st.markdown(res.text)
                                    break
                                except Exception:
                                    continue
                        except Exception as e:
                            st.error(f"Hata: {e}")


# ------------------------------------------------------------------------------
# SEKME 2: PİYASA & ŞİRKET KEŞİF TERMİNALİ
# ------------------------------------------------------------------------------
with tab_kesif:
    st.title("Piyasa & Şirket Keşif Terminali")
    st.caption("BIST, NASDAQ, Kripto ve Emtia varlıklarını temel çarpanları, bilançosu ve canlı haberleriyle inceleyin.")

    col_kat, col_hisse, col_arama = st.columns([1.2, 1.3, 1.5])
    with col_kat:
        kesif_kategori = st.selectbox(
            "Piyasa Grubu:",
            [
                "Borsa İstanbul (BIST)",
                "Amerikan Borsası (Wall Street)",
                "Kripto Varlıklar",
                "Emtia & Kıymetli Madenler"
            ],
            key="kesif_kategori_secim"
        )
        
    with col_hisse:
        if "BIST" in kesif_kategori:
            hizli_secenekler = ["THYAO.IS", "ASELS.IS", "FROTO.IS", "TUPRS.IS", "KCHOL.IS", "BIMAS.IS", "EREGL.IS", "SAHOL.IS", "SISE.IS", "GARAN.IS"]
        elif "Wall Street" in kesif_kategori:
            hizli_secenekler = ["NVDA", "AAPL", "TSLA", "MSFT", "AMZN", "GOOGL", "PLTR", "META", "AMD", "COIN"]
        elif "Kripto" in kesif_kategori:
            hizli_secenekler = ["BTC-USD", "ETH-USD", "SOL-USD", "AVAX-USD", "DOGE-USD", "XRP-USD"]
        else:
            hizli_secenekler = ["GRAM_ALTIN", "GC=F", "SI=F"]
            
        secilen_hizli = st.selectbox("Popüler Varlıklar:", hizli_secenekler, key="kesif_hizli_secim")

    with col_arama:
        serbest_arama = st.text_input("Doğrudan Sembol Girişi:", placeholder="Örn: THYAO, MGROS, NVDA, BTC-USD").upper().strip()

    aktif_kesif_sembol = serbest_arama if serbest_arama else secilen_hizli

    # Detay C: BIST (.IS), Kripto (-USD) ve Altın Sembol Otomasyonu
    if serbest_arama:
        s_temiz = serbest_arama.replace(" ", "").replace("_", "")
        if s_temiz in ["ALTIN", "GRAMALTIN", "GA"]:
            aktif_kesif_sembol = "GRAM_ALTIN"
        elif "." not in serbest_arama and "-" not in serbest_arama and len(serbest_arama) >= 2:
            test_df = varlik_gecmisi_getir(serbest_arama, period="5d")
            if test_df.empty:
                test_bist = varlik_gecmisi_getir(serbest_arama + ".IS", period="5d")
                if not test_bist.empty:
                    aktif_kesif_sembol = serbest_arama + ".IS"
                else:
                    test_kripto = varlik_gecmisi_getir(serbest_arama + "-USD", period="5d")
                    if not test_kripto.empty:
                        aktif_kesif_sembol = serbest_arama + "-USD"

    st.divider()

    with st.spinner(f"Veriler aktarılıyor: {aktif_kesif_sembol}..."):
        k_kat, k_para, k_rozet = varlik_sinifi_belirle(aktif_kesif_sembol)
        k_gecmis = varlik_gecmisi_getir(aktif_kesif_sembol, period="1y")
        try:
            k_info = get_company_fundamentals(aktif_kesif_sembol)
        except Exception:
            k_info = {}

    if k_gecmis.empty:
        st.error(f"'{aktif_kesif_sembol}' için veri bulunamadı. Lütfen sembol kodunu kontrol edin.")
    else:
        guncel_kesif_fiyat = float(k_gecmis['Close'].iloc[-1])
        onceki_kesif_fiyat = float(k_gecmis['Close'].iloc[-2]) if len(k_gecmis) > 1 else guncel_kesif_fiyat
        gunluk_degisim_yuzde = ((guncel_kesif_fiyat - onceki_kesif_fiyat) / onceki_kesif_fiyat) * 100

        sirket_uzun_adi = k_info.get("longName") or aktif_kesif_sembol
        sektor = k_info.get("sector")
        if not sektor or str(sektor).lower() == "none":
            sektor = k_kat
        endustri = k_info.get("industry")
        if not endustri or str(endustri).lower() == "none":
            endustri = "Piyasa Varlığı"

        col_header1, col_header2 = st.columns([2.5, 1.5])
        with col_header1:
            st.markdown(f"### {sirket_uzun_adi} (`{aktif_kesif_sembol}`)")
            st.caption(f"Sınıf: {k_kat} | Sektör: {sektor} | Faaliyet: {endustri}")
        with col_header2:
            st.metric(
                label=f"Piyasa Fiyatı ({k_para})",
                value=f"{guncel_kesif_fiyat:,.2f} {k_para}",
                delta=f"{gunluk_degisim_yuzde:+.2f}% (24s)"
            )

        # Detay D: Emtia & Altın Varlıkları İçin Özel Değerleme Paneli
        if aktif_kesif_sembol == "GRAM_ALTIN" or "=F" in aktif_kesif_sembol:
            st.markdown(f"""
            <div style="background: rgba(251, 191, 36, 0.025); border: 1px solid rgba(251, 191, 36, 0.16); border-radius: 12px; padding: 14px 18px; margin: 10px 0 16px 0;">
                <div style="font-size: 13px; font-weight: 600; color: #fbbf24; margin-bottom: 4px;">✦ Kıymetli Maden & Emtia Fiyatlandırma Modeli ({aktif_kesif_sembol})</div>
                <div style="font-size: 12.5px; color: #cbd5e1; line-height: 1.5;">
                    Altın ve değerli madenler şirket bilançosu barındırmaz; F/K (P/E), PD/DD veya Temettü gibi hisse çarpanları bulunmaz.
                    Fiyat oluşumu <b>Küresel ONS (GC=F)</b> ve <b>USD/TRY</b> paritesi üzerinden <code>(ONS / 31.1035) × USD/TRY</code> matematiksel formülüyle anlık hesaplanmaktadır.
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            # 5'li Finansal Bilanço & Değerleme Çarpanları
            m_cap = k_info.get("marketCap")
            if m_cap and not pd.isna(m_cap) and m_cap > 0:
                m_cap_str = f"{m_cap / 1e9:,.2f} Milyar {k_para}"
            else:
                m_cap_str = "—"
                
            pe_ratio = k_info.get("trailingPE")
            pe_str = f"{pe_ratio:.2f}" if (pe_ratio and not pd.isna(pe_ratio)) else "—"
            
            pb_ratio = k_info.get("priceToBook")
            pb_str = f"{pb_ratio:.2f}" if (pb_ratio and not pd.isna(pb_ratio)) else "—"
            
            div_yield = k_info.get("dividendYield")
            div_rate = k_info.get("dividendRate")
            if div_rate and not pd.isna(div_rate) and div_rate > 0:
                div_str = f"{div_rate:.2f} {k_para}"
                if div_yield and not pd.isna(div_yield) and div_yield > 0:
                    y_p = div_yield * 100 if div_yield < 1 else div_yield
                    div_str = f"%{y_p:.2f} ({div_rate:.2f} {k_para})"
            elif div_yield and not pd.isna(div_yield) and div_yield > 0:
                div_pct = div_yield * 100 if div_yield < 1 else div_yield
                div_str = f"%{div_pct:.2f}"
            else:
                div_str = "%0.00"
                
            # 52 Haftalık Zirve / Dip Garantisi (Geçmiş tablodan matematiksel hesaplama yedeği)
            h_52 = k_info.get("fiftyTwoWeekHigh")
            l_52 = k_info.get("fiftyTwoWeekLow")
            if (not h_52 or pd.isna(h_52)) and not k_gecmis.empty:
                h_52 = float(k_gecmis['Close'].max())
            if (not l_52 or pd.isna(l_52)) and not k_gecmis.empty:
                l_52 = float(k_gecmis['Close'].min())
                
            if h_52 and l_52 and not pd.isna(h_52) and not pd.isna(l_52):
                aralik_52_str = f"{l_52:,.2f} - {h_52:,.2f} {k_para}"
                aralik_52_help = f"52 Haftalık En Düşük: {l_52:,.2f} {k_para} | En Yüksek: {h_52:,.2f} {k_para}"
            else:
                aralik_52_str = "—"
                aralik_52_help = "52 haftalık fiyat aralığı hesaplanamadı."

            st.markdown("##### Temel Analiz & Bilanço Göstergeleri")
            c_val1, c_val2, c_val3, c_val4, c_val5 = st.columns(5)
            with c_val1:
                st.metric("Piyasa Değeri", m_cap_str)
            with c_val2:
                st.metric("F/K Oranı (P/E)", pe_str)
            with c_val3:
                st.metric("PD/DD (P/B)", pb_str)
            with c_val4:
                st.metric("Temettü Dağıtımı", div_str)
            with c_val5:
                st.metric("52 Haftalık Aralık", aralik_52_str, help=aralik_52_help)

        # İnteraktif 1 Yıllık Grafik
        fig_kesif_trend = go.Figure()
        fig_kesif_trend.add_trace(go.Scatter(x=k_gecmis.index, y=k_gecmis['Close'], name='Kapanış', line=dict(color='#38bdf8', width=2.5)))
        sma20_k = k_gecmis['Close'].rolling(20).mean()
        sma50_k = k_gecmis['Close'].rolling(50).mean()
        fig_kesif_trend.add_trace(go.Scatter(x=k_gecmis.index, y=sma20_k, name='SMA 20', line=dict(color='#fbbf24', width=1.5)))
        fig_kesif_trend.add_trace(go.Scatter(x=k_gecmis.index, y=sma50_k, name='SMA 50', line=dict(color='#a855f7', width=1.5)))

        fig_kesif_trend.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#94a3b8'),
            xaxis=dict(gridcolor='rgba(255,255,255,0.04)', zerolinecolor='rgba(255,255,255,0.05)'),
            yaxis=dict(gridcolor='rgba(255,255,255,0.04)', zerolinecolor='rgba(255,255,255,0.05)'),
            title=f"{aktif_kesif_sembol} — Son 1 Yıllık Fiyat & Trend Grafiği",
            xaxis_title="Tarih",
            yaxis_title=f"Fiyat ({k_para})",
            hovermode="x unified",
            height=390,
            margin=dict(t=40, b=20, l=20, r=20)
        )
        st.plotly_chart(fig_kesif_trend, use_container_width=True)

        # Canlı Finans Haberleri
        st.divider()
        st.markdown("##### Canlı Piyasa Haberleri & Basın Akışı")
        
        arama_kelimesi = sirket_uzun_adi if sirket_uzun_adi != aktif_kesif_sembol else aktif_kesif_sembol.replace(".IS", "").replace("-USD", "")
        haberler = get_live_news(arama_kelimesi, count=4)

        if not haberler:
            st.caption("Seçilen varlık hakkında güncel haber akışı bulunamadı.")
        else:
            if gemini_key:
                headlines_tuple = tuple(h['headline'] for h in haberler)
                sentiment_data = get_ai_news_sentiment(aktif_kesif_sembol, headlines_tuple, gemini_key)
                if sentiment_data:
                    skor = sentiment_data.get("skor", "Nötr (Dengeli)")
                    yuzde = sentiment_data.get("yuzde", 50)
                    ozet = sentiment_data.get("ozet", "")
                    zaman = sentiment_data.get("zaman", "")
                    
                    is_pos = any(w in skor.lower() for w in ["boğa", "pozitif", "yükseliş"])
                    is_neg = any(w in skor.lower() for w in ["ayı", "negatif", "düşüş"])
                    badge_bg = "rgba(34, 197, 94, 0.12)" if is_pos else ("rgba(239, 68, 68, 0.12)" if is_neg else "rgba(234, 179, 8, 0.12)")
                    badge_color = "#4ade80" if is_pos else ("#f87171" if is_neg else "#facc15")
                    badge_border = "rgba(34, 197, 94, 0.25)" if is_pos else ("rgba(239, 68, 68, 0.25)" if is_neg else "rgba(234, 179, 8, 0.25)")

                    st.markdown(f"""
                    <div style="background: rgba(255, 255, 255, 0.02); border: 1px solid rgba(255, 255, 255, 0.07); border-radius: 12px; padding: 14px 18px; margin-bottom: 16px;">
                        <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 8px;">
                            <span style="font-size: 11px; text-transform: uppercase; letter-spacing: 0.06em; font-weight: 600; color: #64748b;">✦ AI Piyasa Algı Radarı</span>
                            <span style="background: {badge_bg}; color: {badge_color}; border: 1px solid {badge_border}; font-size: 11.5px; font-weight: 600; padding: 2px 10px; border-radius: 20px;">● {skor} (%{yuzde})</span>
                        </div>
                        <div style="font-size: 13.5px; color: #e2e8f0; line-height: 1.5; font-weight: 400; margin-bottom: 8px;">
                            {ozet}
                        </div>
                        <div style="font-size: 11px; color: #475569; letter-spacing: 0.01em;">
                            ✦ Yapay Zeka İstihbaratı • Güncelleme: {zaman} (2 Saatlik Kurumsal Döngü)
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.caption("✦ Yapay zeka piyasa algı radarı için sol menüden Gemini API anahtarınızı tanımlayabilirsiniz.")

            col_hab1, col_hab2 = st.columns(2)
            for idx, hab in enumerate(haberler):
                target_col = col_hab1 if idx % 2 == 0 else col_hab2
                with target_col:
                    st.markdown(f"""
                    <div class="news-card">
                        <span style="color: #38bdf8; font-size: 11px; text-transform: uppercase; letter-spacing: 0.05em; font-weight: 600;">{hab['source']}</span>
                        <span style="color: #475569; font-size: 11px; float: right;">{hab['date']}</span>
                        <div style="font-weight: 500; font-size: 14px; margin-top: 8px; color: #f1f5f9; line-height: 1.4;">{hab['headline']}</div>
                        <div style="margin-top: 10px;">
                            <a href="{hab['link']}" target="_blank" style="color: #64748b; font-size: 12px; text-decoration: none; font-weight: 500;">Haberi Görüntüle ↗</a>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)


        # Portföye Ekleme
        st.divider()
        with st.expander(f"Portföye Ekle: {aktif_kesif_sembol}"):
            st.caption("Bu varlığı doğrudan kişisel portföyünüze ekleyin:")
            col_add1, col_add2, col_add3 = st.columns(3)
            with col_add1:
                hizli_maliyet = st.number_input("Birim Maliyet", value=float(guncel_kesif_fiyat), format="%.2f", key="hizli_maliyet_in")
            with col_add2:
                hizli_adet = st.number_input("Miktar / Lot", min_value=0.0001, value=10.0, step=1.0, format="%.4f", key="hizli_adet_in")
            with col_add3:
                st.write("")
                st.write("")
                if st.button("Portföye Kaydet", type="primary", use_container_width=True, key="hizli_kaydet_btn"):
                    if is_demo:
                        st.session_state.demo_portfoy[aktif_kesif_sembol] = {"maliyet": float(hizli_maliyet), "adet": float(hizli_adet)}
                    else:
                        database.kullanici_hisse_ekle_guncelle(user_email, aktif_kesif_sembol, float(hizli_maliyet), float(hizli_adet))
                    st.success(f"{aktif_kesif_sembol} portföye eklendi.")
                    st.rerun()