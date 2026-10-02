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
import database

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

/* Üst Sekmeler: Kırmızı Çizgiyi Kaldır & Yumuşak Buzlu Cam Hap Tasarımı */
div[data-baseweb="tab-highlight"] {
    display: none !important;
}
div[data-baseweb="tab-border"] {
    display: none !important;
}
.stTabs [data-baseweb="tab-list"] {
    gap: 6px;
    background-color: rgba(255, 255, 255, 0.02) !important;
    padding: 5px;
    border-radius: 12px;
    border: 1px solid rgba(255, 255, 255, 0.05);
    border-bottom: 1px solid rgba(255, 255, 255, 0.05) !important;
}
.stTabs [data-baseweb="tab"] {
    height: 40px;
    border-radius: 8px;
    padding: 0px 20px;
    font-weight: 500;
    font-size: 13.5px;
    letter-spacing: 0.01em;
    color: #64748b;
    background: transparent !important;
    border: 1px solid transparent !important;
    box-shadow: none !important;
    transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
}
.stTabs [data-baseweb="tab"]:hover {
    color: #94a3b8 !important;
    background-color: rgba(255, 255, 255, 0.025) !important;
}
.stTabs [aria-selected="true"] {
    background: rgba(255, 255, 255, 0.06) !important;
    color: #f8fafc !important;
    border: 1px solid rgba(255, 255, 255, 0.09) !important;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.25) !important;
    border-radius: 8px !important;
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
    font-size: 24px !important;
    font-weight: 600 !important;
    color: #f1f5f9 !important;
    letter-spacing: -0.02em !important;
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
                    "THYAO.IS": {"maliyet": 265.00, "adet": 50.0},
                    "NVDA": {"maliyet": 115.00, "adet": 15.0},
                    "BTC-USD": {"maliyet": 62000.00, "adet": 0.08},
                    "GRAM_ALTIN": {"maliyet": 2850.00, "adet": 10.0},
                    "AKBNK.IS": {"maliyet": 58.00, "adet": 100.0},
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
        t = yf.Ticker(symbol)
        info = t.info if hasattr(t, 'info') and isinstance(t.info, dict) else {}
        fi = getattr(t, 'fast_info', None)
        
        market_cap = info.get("marketCap")
        if not market_cap and fi:
            market_cap = getattr(fi, 'market_cap', None) or (fi.get('marketCap') if hasattr(fi, 'get') else None)
            
        pe = info.get("trailingPE") or info.get("forwardPE")
        pb = info.get("priceToBook")
        div_y = info.get("dividendYield") or info.get("trailingAnnualDividendYield")
        
        h52 = info.get("fiftyTwoWeekHigh")
        l52 = info.get("fiftyTwoWeekLow")
        if not h52 and fi:
            h52 = getattr(fi, 'year_high', None) or (fi.get('yearHigh') if hasattr(fi, 'get') else None)
        if not l52 and fi:
            l52 = getattr(fi, 'year_low', None) or (fi.get('yearLow') if hasattr(fi, 'get') else None)
            
        return {
            "longName": info.get("longName", symbol),
            "sector": info.get("sector"),
            "industry": info.get("industry"),
            "marketCap": market_cap,
            "trailingPE": pe,
            "priceToBook": pb,
            "dividendYield": div_y,
            "fiftyTwoWeekHigh": h52,
            "fiftyTwoWeekLow": l52,
        }
    except Exception:
        return {}

# --- GİRİŞ YAPILMIŞ KULLANICI AKIŞI ---
user = st.session_state.kullanici
user_email = user["email"]
is_demo = user.get("rol") == "demo"
usd_try = get_usd_try_rate()

# Portföy verisini getir
if is_demo:
    if "demo_portfoy" not in st.session_state:
        st.session_state.demo_portfoy = {
            "THYAO.IS": {"maliyet": 265.00, "adet": 50.0},
            "NVDA": {"maliyet": 115.00, "adet": 15.0},
            "BTC-USD": {"maliyet": 62000.00, "adet": 0.08},
            "GRAM_ALTIN": {"maliyet": 2850.00, "adet": 10.0},
            "AKBNK.IS": {"maliyet": 58.00, "adet": 100.0},
        }
    portfoy = st.session_state.demo_portfoy
else:
    portfoy = database.kullanici_portfoyu_getir(user_email)

# --- SOL MENÜ (KULLANICI BİLGİSİ & PORTFÖY YÖNETİMİ) ---
st.sidebar.markdown(f"**Yatırımcı:** {user.get('ad_soyad', 'Kullanıcı')}")
st.sidebar.caption(f"{user_email}")
st.sidebar.caption(f"Piyasa Kuru: 1 USD = **{usd_try:.2f} TL**")

if is_demo:
    st.sidebar.caption("Oturum Modu: Demo Hesabı")

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
                "THYAO.IS": {"maliyet": 265.00, "adet": 50.0},
                "NVDA": {"maliyet": 115.00, "adet": 15.0},
                "BTC-USD": {"maliyet": 62000.00, "adet": 0.08},
                "GRAM_ALTIN": {"maliyet": 2850.00, "adet": 10.0},
                "AKBNK.IS": {"maliyet": 58.00, "adet": 100.0},
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
# 🏛️ ANA EKRAN: 2 BÜYÜK AMİRAL SEKME (PORTFÖY & PİYASA KEŞİF)
# ==============================================================================

tab_portfoy, tab_kesif = st.tabs([
    "Portföy & Servet Yönetimi",
    "Piyasa & Şirket Keşif Terminali"
])

# ------------------------------------------------------------------------------
# 💼 SEKME 1: PORTFÖY & SERVET YÖNETİMİ
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
            st.metric(label="Toplam Yatırılan Maliyet", value=f"{toplamMaliyetTL:,.2f} TL", delta=f"${toplamMaliyetTL / usd_try:,.2f} USD")
        with col2:
            st.metric(label="Konsolide Portföy Değeri", value=f"{toplamGuncelDegerTL:,.2f} TL", delta=f"${toplamGuncelDegerTL / usd_try:,.2f} USD")
        with col3:
            st.metric(label="Toplam Net Getiri", value=f"{toplamKarTL:+,.2f} TL", delta=f"%{toplamKarYuzde:+.2f}")
        with col4:
            st.metric(label="BIST 100 Karşılaştırması", value=f"Endeks: %{bist_getiri:.1f}", delta=f"%{fark:+.1f} Göreceli Fark")

        st.divider()
        st.dataframe(tabloVerisi, use_container_width=True)

        st.divider()
        tab_pasta1, tab_pasta2 = st.tabs(["Varlık Sınıfı Dağılımı", "Pozisyon Bazında Dağılım"])
        
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
                st.metric(label="7 Günlük Model Hedefi", value=f"{tahmin_7gun:,.2f} {secilen_para}", delta=f"%{tahmin_fark_yuzde:+.2f}")
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
                        st.metric("MACD Sinyal Stratejisi", f"%{getiri_strat:.2f}", delta=f"%{fark_strat:.2f}")
                except Exception:
                    st.caption("Geçmiş veri hesaplanamadı.")

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
                            modeller = [m.name for m in client.models.list() if "gemini" in m.name.lower()] or ["gemini-3.8-flash"]
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
# 🔍 SEKME 2: PİYASA & ŞİRKET KEŞİF TERMİNALİ
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
        serbest_arama = st.text_input("Doğrudan Sembol Girişi:", placeholder="Örn: MGROS.IS, NFLX, SOL-USD").upper().strip()

    aktif_kesif_sembol = serbest_arama if serbest_arama else secilen_hizli

    st.divider()

    with st.spinner(f"Veriler aktarılıyor: {aktif_kesif_sembol}..."):
        k_kat, k_para, k_rozet = varlik_sinifi_belirle(aktif_kesif_sembol)
        k_gecmis = varlik_gecmisi_getir(aktif_kesif_sembol, period="1y")
        k_info = get_company_fundamentals(aktif_kesif_sembol)

    if k_gecmis.empty:
        st.error(f"'{aktif_kesif_sembol}' için veri bulunamadı. Lütfen sembol kodunu kontrol edin.")
    else:
        guncel_kesif_fiyat = float(k_gecmis['Close'].iloc[-1])
        onceki_kesif_fiyat = float(k_gecmis['Close'].iloc[-2]) if len(k_gecmis) > 1 else guncel_kesif_fiyat
        gunluk_degisim_yuzde = ((guncel_kesif_fiyat - onceki_kesif_fiyat) / onceki_kesif_fiyat) * 100

        sirket_uzun_adi = k_info.get("longName", aktif_kesif_sembol)
        sektor = k_info.get("sector", k_kat)
        endustri = k_info.get("industry", "Piyasa Varlığı")

        col_header1, col_header2 = st.columns([2.5, 1.5])
        with col_header1:
            st.markdown(f"### {sirket_uzun_adi} (`{aktif_kesif_sembol}`)")
            st.caption(f"Sınıf: {k_kat} | Sektör: {sektor} | Faaliyet: {endustri}")
        with col_header2:
            st.metric(
                label=f"Piyasa Fiyatı ({k_para})",
                value=f"{guncel_kesif_fiyat:,.2f} {k_para}",
                delta=f"%{gunluk_degisim_yuzde:+.2f} (24s)"
            )

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
        if div_yield and not pd.isna(div_yield) and div_yield > 0:
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
            
        h52_str = f"{h_52:.2f} {k_para}" if (h_52 and not pd.isna(h_52)) else "—"
        l52_str = f"{l_52:.2f} {k_para}" if (l_52 and not pd.isna(l_52)) else "—"

        st.markdown("##### Temel Analiz & Bilanço Göstergeleri")
        c_val1, c_val2, c_val3, c_val4, c_val5 = st.columns(5)
        with c_val1:
            st.metric("Piyasa Değeri", m_cap_str)
        with c_val2:
            st.metric("F/K Oranı (P/E)", pe_str)
        with c_val3:
            st.metric("PD/DD (P/B)", pb_str)
        with c_val4:
            st.metric("Temettü Verimi", div_str)
        with c_val5:
            st.metric("52 Haftalık Aralık", f"{l52_str} - {h52_str}")

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

        # Gemini Şirket Raporu
        st.divider()
        st.markdown("##### Yapay Zeka Şirket & Değerleme Raporu")
        if st.button("Şirket ve Haber Raporu Üret", key="gemini_kesif_btn"):
            if not gemini_key:
                st.warning("Sol menüden Gemini API anahtarınızı tanımlayın.")
            else:
                with st.spinner("Rapor oluşturuluyor..."):
                    try:
                        from google import genai
                        client = genai.Client(api_key=gemini_key)
                        haber_metinleri = "\n".join([f"- {h['headline']} ({h['source']})" for h in haberler])
                        prompt_kesif = f"""
Sen Wall Street ve Borsa İstanbul'da kıdemli bir Hisse Senedi Araştırma (Equity Research) analistisin.
Varlık: {sirket_uzun_adi} ({aktif_kesif_sembol})
Sınıf: {k_kat} | Sektör: {sektor}
Piyasa Fiyatı: {guncel_kesif_fiyat:,.2f} {k_para}
Piyasa Değeri: {m_cap_str}
F/K: {pe_str} | PD/DD: {pb_str} | Temettü: {div_str}
52 Haftalık Aralık: {l52_str} - {h52_str}
Son Haber Başlıkları:
{haber_metinleri if haber_metinleri else 'Yeni haber bulunamadı.'}

Lütfen yatırımcıya 3 başlık altında net, profesyonel ve Türkçe bir rapor sun:
1. İş Modeli ve Sektörel Rekabet Gücü
2. Bilanço & Değerleme Çarpanları Yorumu (F/K, PD/DD, Temettü)
3. Piyasa Algısı ve Haber Akışı Yorumu
(Yatırım tavsiyesi olmadığını belirt).
"""
                        modeller = [m.name for m in client.models.list() if "gemini" in m.name.lower()] or ["gemini-3.8-flash"]
                        for m_name in modeller:
                            try:
                                res_kesif = client.models.generate_content(model=m_name, contents=prompt_kesif)
                                st.markdown(res_kesif.text)
                                break
                            except Exception:
                                continue
                    except Exception as err:
                        st.error(f"Hata: {err}")

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