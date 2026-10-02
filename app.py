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
st.set_page_config(page_title="Global Servet & Finans Terminali", page_icon="🌐", layout="wide")

# --- MODERN ÖZEL CSS STİLİ ---
st.markdown("""
<style>
/* Modern Üst Sekme (Tab) Çubuğu Tasarımı */
.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
    background-color: rgba(255, 255, 255, 0.04);
    padding: 6px;
    border-radius: 14px;
    border: 1px solid rgba(255, 255, 255, 0.08);
}
.stTabs [data-baseweb="tab"] {
    height: 48px;
    border-radius: 10px;
    padding: 0px 24px;
    font-weight: 600;
    font-size: 15px;
    color: #94a3b8;
    transition: all 0.2s ease-in-out;
}
.stTabs [aria-selected="true"] {
    background-color: #2563eb !important;
    color: #ffffff !important;
    box-shadow: 0 4px 14px rgba(37, 99, 235, 0.4);
}
/* Metrik Kartları */
div[data-testid="stMetric"] {
    background: rgba(255, 255, 255, 0.03);
    padding: 14px 16px;
    border-radius: 12px;
    border: 1px solid rgba(255, 255, 255, 0.08);
}
/* Haber Kartı */
.news-card {
    background: rgba(255, 255, 255, 0.03);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 10px;
    padding: 14px;
    margin-bottom: 12px;
}
</style>
""", unsafe_allow_html=True)

# --- KULLANICI OTURUM KONTROLÜ (SESSION STATE) ---
if "kullanici" not in st.session_state:
    st.session_state.kullanici = None

# Giriş yapılmamışsa Giriş / Kayıt / Demo ekranını göster
if not st.session_state.kullanici:
    st.title("🌐 Global Servet & Finans Terminali")
    st.write("Borsa İstanbul, Amerikan Borsaları (NASDAQ/NYSE), Kripto Paralar ve Altın tek ekranda!")
    
    col_auth, col_info = st.columns([1.1, 0.9], gap="large")
    
    with col_auth:
        tab_giris, tab_kayit, tab_demo = st.tabs(["🔑 Giriş Yap", "📝 Kayıt Ol", "👀 Demo İncele"])
        
        with tab_giris:
            st.subheader("Hesabınıza Giriş Yapın")
            giris_email = st.text_input("E-posta Adresi", key="giris_email")
            giris_sifre = st.text_input("Şifre", type="password", key="giris_sifre")
            
            if st.button("Giriş Yap", type="primary", use_container_width=True):
                if not giris_email or not giris_sifre:
                    st.error("Lütfen e-posta ve şifrenizi girin!")
                else:
                    basarili, mesaj, user_data = database.kullanici_giris_yap(giris_email, giris_sifre)
                    if basarili:
                        st.session_state.kullanici = user_data
                        st.success(mesaj)
                        st.rerun()
                    else:
                        st.error(mesaj)
                        
        with tab_kayit:
            st.subheader("Yeni Hesap Oluştur")
            kayit_ad = st.text_input("Ad Soyad", key="kayit_ad")
            kayit_email = st.text_input("E-posta Adresi", key="kayit_email")
            kayit_sifre = st.text_input("Şifre Belirleyin", type="password", key="kayit_sifre")
            kayit_sifre_tekrar = st.text_input("Şifreyi Tekrar Girin", type="password", key="kayit_sifre_tekrar")
            
            if st.button("Kayıt Ol ve Başla", type="primary", use_container_width=True):
                if not kayit_ad or not kayit_email or not kayit_sifre:
                    st.error("Lütfen tüm alanları doldurun!")
                elif kayit_sifre != kayit_sifre_tekrar:
                    st.error("Girdiğiniz şifreler birbiriyle uyuşmuyor!")
                elif len(kayit_sifre) < 4:
                    st.error("Şifreniz en az 4 karakter olmalıdır!")
                else:
                    basarili, mesaj = database.kullanici_kayit_ol(kayit_email, kayit_sifre, kayit_ad)
                    if basarili:
                        _, _, user_data = database.kullanici_giris_yap(kayit_email, kayit_sifre)
                        st.session_state.kullanici = user_data
                        st.success(f"Tebrikler {kayit_ad}! Hesabınız ve örnek çoklu varlık portföyünüz oluşturuldu.")
                        st.rerun()
                    else:
                        st.error(mesaj)
                        
        with tab_demo:
            st.subheader("Hesap Açmadan İnceleyin")
            st.write("Kaydolmadan önce sistemi ve analiz araçlarını test etmek isterseniz tek tıkla misafir olarak giriş yapabilirsiniz.")
            if st.button("🚀 Demo Olarak Başlat", use_container_width=True):
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
        st.markdown("### 🌟 All-in-One Terminal Özellikleri")
        st.markdown("""
        - 💼 **Kişisel Portföy & Servet:** BIST, ABD Hisseleri, Kripto ve Altın yatırımlarınızın kâr/zararını canlı kurla tek ekranda takip edin.
        - 🔍 **Piyasa & Şirket Keşfi:** Portföyünüzde olmayan binlerce hissenin bilançosunu, F/K oranını ve canlı haberlerini inceleyin.
        - 🔮 **Makine Öğrenmesi (ML) Fiyat Projeksiyonu:** Akakçe/Cimri usulü 7 günlük trend tahmini ve güven aralığı.
        - 📰 **Canlı Finans Haberleri:** Bloomberg, Reuters ve KAP kaynaklı anlık haber akışı.
        - 🤖 **Google Gemini Yapay Zeka:** Küresel risk yönetimi ve şirket araştırma raporları.
        """)
        st.info("💡 **İpucu:** Aile üyeleriniz veya arkadaşlarınız kendi hesaplarını açtığında herkes yalnızca kendi portföyünü görür.")
        
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
    """Sembolün varlık sınıfını, para birimini ve bayrağını döndürür."""
    s = sembol.upper().strip()
    if s.endswith(".IS"):
        return "BIST Hissesi", "TRY", "🇹🇷"
    elif s == "GRAM_ALTIN" or s.startswith("GC=") or s.startswith("SI="):
        para = "TRY" if s == "GRAM_ALTIN" else "USD"
        return "Emtia & Altın", para, "🥇"
    elif s.endswith("-USD") or s.endswith("-TRY") or s in ["BTC", "ETH", "SOL", "AVAX", "DOGE", "XRP"]:
        return "Kripto Para", "USD", "🪙"
    elif "USDTRY" in s or "EURTRY" in s:
        return "Döviz / Nakit", "TRY", "💵"
    else:
        return "ABD Borsası", "USD", "🇺🇸"

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
st.sidebar.markdown(f"### 👤 {user.get('ad_soyad', 'Yatırımcı')}")
st.sidebar.caption(f"📧 `{user_email}`")
st.sidebar.info(f"💵 **Canlı Kur:** 1 USD = **{usd_try:.2f} TL**")

if is_demo:
    st.sidebar.warning("👀 **Demo Modundasınız**")

if st.sidebar.button("🚪 Çıkış Yap", use_container_width=True):
    st.session_state.kullanici = None
    st.session_state.pop("demo_portfoy", None)
    st.rerun()

st.sidebar.divider()
st.sidebar.header("⚙️ Varlık Yönetimi")

# 1. Çoklu Varlık Ekleme / Güncelleme Formu
st.sidebar.subheader("➕ Varlık Ekle / Güncelle")
varlik_turu = st.sidebar.selectbox(
    "Varlık Türü Seçin:",
    ["🇹🇷 BIST Hissesi", "🇺🇸 ABD Hissesi (NASDAQ/NYSE)", "🪙 Kripto Para", "🥇 Altın & Emtia"],
    key="secilen_varlik_turu"
)

with st.sidebar.form("varlik_ekle_formu"):
    if "BIST" in varlik_turu:
        yeni_sembol = st.text_input("Hisse Sembolü (BIST)", placeholder="örn: THYAO, FROTO, ASELS").upper().strip()
        para_birimi = "TL"
    elif "ABD" in varlik_turu:
        yeni_sembol = st.text_input("Hisse Kodu (ABD)", placeholder="örn: AAPL, NVDA, TSLA, MSFT").upper().strip()
        para_birimi = "$ USD"
    elif "Kripto" in varlik_turu:
        yeni_sembol = st.text_input("Kripto Kodu", placeholder="örn: BTC, ETH, SOL, DOGE").upper().strip()
        para_birimi = "$ USD"
    else:
        emtia_secim = st.selectbox("Emtia / Maden Seçin:", ["Gram Altın (TL)", "Ons Altın ($ GC=F)", "Gümüş ($ SI=F)"])
        if "Gram Altın" in emtia_secim:
            yeni_sembol = "GRAM_ALTIN"
            para_birimi = "TL"
        elif "Ons Altın" in emtia_secim:
            yeni_sembol = "GC=F"
            para_birimi = "$ USD"
        else:
            yeni_sembol = "SI=F"
            para_birimi = "$ USD"
            
    yeni_maliyet = st.number_input(f"Alış Maliyeti ({para_birimi})", min_value=0.0, step=0.5, format="%.2f")
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
            
        st.success(f"{yeni_sembol} başarıyla kaydedildi!")
        st.rerun()

# 2. Varlık Silme Formu
if portfoy:
    st.sidebar.divider()
    st.sidebar.subheader("🗑️ Varlık Sil")
    silinecek_hisse = st.sidebar.selectbox("Silmek istediğiniz varlık:", list(portfoy.keys()))
    if st.sidebar.button("Varlığı Portföyden Çıkar", use_container_width=True):
        if is_demo:
            st.session_state.demo_portfoy.pop(silinecek_hisse, None)
        else:
            database.kullanici_hisse_sil(user_email, silinecek_hisse)
        st.sidebar.warning(f"{silinecek_hisse} silindi!")
        st.rerun()

st.sidebar.divider()
st.sidebar.subheader("⚡ Hızlı İşlemler")
col_btn1, col_btn2 = st.sidebar.columns(2)
with col_btn1:
    if st.button("🧹 Sıfırla", use_container_width=True):
        if is_demo:
            st.session_state.demo_portfoy = {}
        else:
            database.kullanici_portfoyu_sifirla(user_email)
        st.rerun()
with col_btn2:
    if st.button("📥 Örnek Veri", use_container_width=True):
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
    st.sidebar.subheader("🤖 Yapay Zeka Asistanı")
    gemini_key = st.sidebar.text_input(
        "Gemini API Anahtarı:", 
        type="password", 
        help="aistudio.google.com adresinden ücretsiz alabilirsiniz."
    )
else:
    st.sidebar.divider()
    st.sidebar.caption("🤖 Yapay zeka asistanı aktif")


# ==============================================================================
# 🏛️ ANA EKRAN: 2 BÜYÜK AMİRAL SEKME (PORTFÖYÜM & PİYASA KEŞİF)
# ==============================================================================

tab_portfoy, tab_kesif = st.tabs([
    "💼 Portföyüm & Varlıklarım",
    "🔍 Piyasa & Şirket Keşif Terminali"
])

# ------------------------------------------------------------------------------
# 💼 SEKME 1: PORTFÖYÜM & VARLIKLARIM (KİŞİSEL SERVET PANELİ)
# ------------------------------------------------------------------------------
with tab_portfoy:
    st.title("💼 Kişisel Portföy & Servet Paneli")
    st.write("Borsa İstanbul, Amerikan Borsaları, Kripto Paralar ve Altın yatırımlarınız tek ekranda.")

    if not portfoy:
        st.info("💡 Portföyünüz şu an boş. Sol menüden yeni varlık ekleyebilir veya '📥 Örnek Veri' butonuna tıklayarak örnek karma portföyü yükleyebilirsiniz.")
    else:
        # Hesaplama değişkenleri
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

        with st.spinner("⏳ Portföy verileri ve canlı kurlar yükleniyor..."):
            for sembol, bilgi in portfoy.items():
                maliyet = float(bilgi["maliyet"])
                adet = float(bilgi["adet"])
                kategori, para, ikon = varlik_sinifi_belirle(sembol)
                
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
                    "Varlık": f"{ikon} {sembol}",
                    "Kategori": kategori,
                    "Miktar (Adet)": adet,
                    "Alış Maliyeti": maliyetMetni,
                    "Güncel Fiyat": fiyatMetni,
                    "Toplam Değer (TL)": f"{varlikGuncelToplami:,.2f} TL",
                    "Kâr/Zarar (TL)": f"{karDurumuTL:+,.2f} TL",
                    "Kâr/Zarar (%)": round(karDurumuYuzde, 2)
                })
                
                pastaEtiketler.append(f"{ikon} {sembol}")
                pastaDegerler.append(varlikGuncelToplami)
                kategoriDegerler[f"{ikon} {kategori}"] = kategoriDegerler.get(f"{ikon} {kategori}", 0.0) + varlikGuncelToplami
                
                if karDurumuYuzde > enYuksekKar:
                    enYuksekKar = karDurumuYuzde
                    enIyiVarlik = f"{ikon} {sembol}"
                if karDurumuYuzde < enDusukKar:
                    enDusukKar = karDurumuYuzde
                    enKotuVarlik = f"{ikon} {sembol}"

        toplamKarTL = toplamGuncelDegerTL - toplamMaliyetTL
        toplamKarYuzde = ((toplamGuncelDegerTL - toplamMaliyetTL) / toplamMaliyetTL) * 100 if toplamMaliyetTL > 0 else 0.0

        # BIST 100 (XU100) Getirisi
        try:
            bist_veri = yf.Ticker("XU100.IS").history(period="6mo")
            bist_getiri = ((bist_veri['Close'].iloc[-1] - bist_veri['Close'].iloc[0]) / bist_veri['Close'].iloc[0]) * 100
        except Exception:
            bist_getiri = 0.0

        fark = toplamKarYuzde - bist_getiri

        # 4'lü Özet KPI Kartları (Hem TL Hem USD)
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric(label="Toplam Yatırılan Maliyet", value=f"{toplamMaliyetTL:,.2f} TL", delta=f"≈ ${toplamMaliyetTL / usd_try:,.2f} USD")
        with col2:
            st.metric(label="Toplam Portföy Değeri", value=f"{toplamGuncelDegerTL:,.2f} TL", delta=f"≈ ${toplamGuncelDegerTL / usd_try:,.2f} USD")
        with col3:
            st.metric(label="Toplam Net Kâr/Zarar", value=f"{toplamKarTL:+,.2f} TL", delta=f"%{toplamKarYuzde:+.2f}")
        with col4:
            st.metric(label="BIST 100 vs Portföy (6 Ay)", value=f"BIST: %{bist_getiri:.1f}", delta=f"%{fark:+.1f} Fark")

        st.divider()
        st.subheader("📋 Portföy Tablosu")
        st.dataframe(tabloVerisi, use_container_width=True)

        st.divider()
        st.subheader("🥧 Portföy Varlık & Kategori Dağılımı")

        tab_pasta1, tab_pasta2 = st.tabs(["🏷️ Varlık Sınıfı Dağılımı", "📌 Tekil Varlık Dağılımı"])
        with tab_pasta1:
            fig_kat = px.pie(names=list(kategoriDegerler.keys()), values=list(kategoriDegerler.values()), hole=0.45, color_discrete_sequence=px.colors.qualitative.Prism)
            fig_kat.update_traces(textposition='inside', textinfo='percent+label', hovertemplate="<b>%{label}</b><br>Toplam: %{value:,.2f} TL<br>Pay: %{percent}<extra></extra>")
            fig_kat.update_layout(margin=dict(t=10, b=10, l=10, r=10), height=350)
            st.plotly_chart(fig_kat, use_container_width=True)

        with tab_pasta2:
            fig_pasta = px.pie(names=pastaEtiketler, values=pastaDegerler, hole=0.45, color_discrete_sequence=px.colors.qualitative.Safe)
            fig_pasta.update_traces(textposition='inside', textinfo='percent+label', hovertemplate="<b>%{label}</b><br>Toplam: %{value:,.2f} TL<br>Pay: %{percent}<extra></extra>")
            fig_pasta.update_layout(margin=dict(t=10, b=10, l=10, r=10), height=350)
            st.plotly_chart(fig_pasta, use_container_width=True)

        # Şampiyon ve Düşen Kutuları
        if enIyiVarlik and enKotuVarlik:
            col_iyi, col_kotu = st.columns(2)
            with col_iyi:
                st.success(f"🏆 **En Çok Kazandıran:** {enIyiVarlik} (%{enYuksekKar:+.2f})")
            with col_kotu:
                st.error(f"🔻 **En Çok Kaybettiren:** {enKotuVarlik} (%{enDusukKar:+.2f})")

        st.divider()
        st.subheader("📊 Portföy Varlık Analizi & 🔮 7 Günlük ML Tahmini")

        secilen = st.selectbox("İncelemek istediğiniz portföy varlığını seçin:", list(portfoy.keys()), key="portfoy_secim")
        secilen_kat, secilen_para, secilen_ikon = varlik_sinifi_belirle(secilen)
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

            # 🔮 ML Regresyon Tahmini
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

            # İnteraktif Trend Grafiği (Düzgün kesik çizgili)
            fig_trend = go.Figure()
            fig_trend.add_trace(go.Scatter(x=gecmisSecilen.index, y=gecmisSecilen['Close'], name=f'Kapanış ({secilen_para})', line=dict(color='#00b4d8', width=2.5)))
            fig_trend.add_trace(go.Scatter(x=gecmisSecilen.index, y=gecmisSecilen['SMA20'], name='SMA 20 (Kısa Vade)', line=dict(color='#f77f00', width=1.5)))
            fig_trend.add_trace(go.Scatter(x=gecmisSecilen.index, y=gecmisSecilen['SMA50'], name='SMA 50 (Orta Vade)', line=dict(color='#9d4edd', width=1.5)))
            fig_trend.add_hline(y=secilenMaliyet, line_dash="dash", line_color="#e63946", annotation_text=f"Maliyetim ({secilenMaliyet:.2f} {secilen_para})", annotation_position="top left")

            fig_trend.add_trace(go.Scatter(x=fut_dates, y=fut_prices, name='🔮 7 Günlük ML Tahmini', mode='lines', line=dict(color='#c084fc', width=2.5, dash='dash')))
            fig_trend.add_trace(go.Scatter(x=fut_dates, y=fut_prices + std_hata, name='Tahmin Üst Sınır', mode='lines', line=dict(color='rgba(0,0,0,0)', width=0), showlegend=False, hoverinfo='skip'))
            fig_trend.add_trace(go.Scatter(x=fut_dates, y=fut_prices - std_hata, name='Güven Aralığı', mode='lines', fill='tonexty', fillcolor='rgba(192, 132, 252, 0.15)', line=dict(color='rgba(0,0,0,0)', width=0), hoverinfo='skip'))

            fig_trend.update_layout(title=f"📈 {secilen_ikon} {secilen} - Canlı Fiyat & Gelecek 7 Günlük Projeksiyon", xaxis_title="Tarih", yaxis_title=f"Fiyat ({secilen_para})", hovermode="x unified", height=460, margin=dict(t=40, b=20, l=20, r=20))
            st.plotly_chart(fig_trend, use_container_width=True)

            # Akakçe / Cimri Tarzı Kart
            st.markdown("#### 🔮 Makine Öğrenmesi Fiyat Projeksiyonu (Sonraki 7 Gün)")
            col_ml1, col_ml2, col_ml3 = st.columns(3)
            with col_ml1:
                st.metric(label="7 Gün Sonraki Model Hedefi", value=f"{tahmin_7gun:,.2f} {secilen_para}", delta=f"%{tahmin_fark_yuzde:+.2f} Beklenen Yön")
            with col_ml2:
                st.metric(label="Model Güven Bandı", value=f"±{std_hata:.2f} {secilen_para}")
            with col_ml3:
                egim_yorum = "Yükseliş Eğilimi 🚀" if gunluk_egim > 0 else "Düzeltme Eğilimi 📉"
                st.metric(label="Günlük Trend İvmesi", value=f"{gunluk_egim:+.2f} {secilen_para}/Gün", delta=egim_yorum)

            # 3'lü İndikatör Sinyal Rozetleri
            c_ind1, c_ind2, c_ind3 = st.columns(3)
            with c_ind1:
                if guncel_rsi > 70:
                    st.warning(f"⚠️ **RSI: {guncel_rsi:.1f}**\nAşırı Alım")
                elif guncel_rsi < 30:
                    st.success(f"💎 **RSI: {guncel_rsi:.1f}**\nAşırı Satım")
                else:
                    st.info(f"⚖️ **RSI: {guncel_rsi:.1f}**\nNötr Bölge")
            with c_ind2:
                if macd_al:
                    st.success(f"🟢 **MACD: {guncel_macd:.2f}**\nBoğa Gücü")
                else:
                    st.error(f"🔴 **MACD: {guncel_macd:.2f}**\nAyı Baskısı")
            with c_ind3:
                if golden_cross:
                    st.success(f"🏆 **Trend:** Altın Kesişim\nSMA 20 > SMA 50")
                else:
                    st.error(f"💀 **Trend:** Düşüş Eğilimi\nSMA 20 < SMA 50")

            # Mini Backtest
            with st.expander(f"🧪 Strateji Testi: {secilen} için MACD Kârlı mıydı?"):
                try:
                    df_sim = gecmisSecilen.copy()
                    df_sim['Pozisyon'] = (df_sim['MACD'] > df_sim['Signal']).astype(int).shift(1)
                    df_sim['Gunluk_Getiri'] = df_sim['Close'].pct_change()
                    df_sim['Strateji_Getiri'] = df_sim['Gunluk_Getiri'] * df_sim['Pozisyon']
                    getiri_bh = ((1 + df_sim['Gunluk_Getiri'].dropna()).prod() - 1) * 100
                    getiri_strat = ((1 + df_sim['Strateji_Getiri'].dropna()).prod() - 1) * 100
                    col_sim1, col_sim2 = st.columns(2)
                    with col_sim1:
                        st.metric("Alıp Bekleme (Buy & Hold)", f"%{getiri_bh:.2f}")
                    with col_sim2:
                        fark_strat = getiri_strat - getiri_bh
                        st.metric("MACD Sinyal Stratejisi", f"%{getiri_strat:.2f}", delta=f"%{fark_strat:.2f} Strateji Farkı")
                except Exception:
                    st.caption("Veri hesaplanamadı.")

            # Gemini AI Yorumu
            st.divider()
            st.subheader("🤖 Yapay Zeka Portföy Analisti (Google Gemini)")
            if st.button("🧠 Portföyümü ve Varlığımı Yorumla", key="gemini_portfoy_btn"):
                if not gemini_key:
                    st.warning("Sol menüden Gemini API anahtarınızı girin!")
                else:
                    with st.spinner("🤖 Gemini portföyünüzü inceliyor..."):
                        try:
                            from google import genai
                            client = genai.Client(api_key=gemini_key)
                            prompt = f"""
Sen Borsa İstanbul, Amerikan Borsaları ve Kripto konusunda uzman kıdemli bir küresel portföy yöneticisisin.
Yatırımcı: {user.get('ad_soyad')}
Toplam Servet: {toplamGuncelDegerTL:,.2f} TL (≈ ${toplamGuncelDegerTL / usd_try:,.2f} USD)
Toplam Maliyet: {toplamMaliyetTL:,.2f} TL
Net Kâr/Zarar: {toplamKarTL:+,.2f} TL (%{toplamKarYuzde:+.2f})
Dolar Kuru: {usd_try:.2f} TL
Varlıklar: {list(portfoy.keys())}
Dağılım: {kategoriDegerler}
İncelenen Varlık: {secilen} ({secilen_kat}) | Fiyat: {guncel_son_fiyat:,.2f} {secilen_para} | 14G RSI: {guncel_rsi:.1f} | 7 Günlük Model Hedefi: {tahmin_7gun:,.2f} {secilen_para} (%{tahmin_fark_yuzde:+.2f})
Lütfen 3 başlıkta profesyonel Türkçe analiz sun:
1. 📊 Küresel Portföy Sağlık & Risk Değerlendirmesi
2. 🔍 {secilen} Teknik & Projeksiyon Yorumu
3. 💡 Kısa & Orta Vade Stratejik Öneriler
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
# 🔍 SEKME 2: PİYASA & ŞİRKET KEŞİF TERMİNALİ (BLOOMBERG & FINTABLES VARYANTI)
# ------------------------------------------------------------------------------
with tab_kesif:
    st.markdown("## 🔍 Piyasa & Şirket Keşif Terminali")
    st.write("Portföyünüzde olsun veya olmasın; BIST, NASDAQ, Kripto ve Altın varlıklarını derinlemesine inceleyin, bilançosunu ve canlı haberlerini okuyun.")

    # 1. Popüler Trend Varlıklar & Serbest Arama
    st.markdown("##### ⚡ Hızlı Varlık Seçimi veya Serbest Arama")
    
    col_kat, col_hisse, col_arama = st.columns([1.2, 1.3, 1.5])
    
    with col_kat:
        kesif_kategori = st.selectbox(
            "Piyasa / Varlık Grubu:",
            [
                "🇹🇷 Borsa İstanbul (BIST)",
                "🇺🇸 Wall Street (Amerikan Borsası)",
                "🪙 Kripto Paralar",
                "🥇 Emtia & Değerli Madenler"
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
        serbest_arama = st.text_input("Veya Doğrudan Sembol Yazın:", placeholder="örn: MGROS.IS, NFLX, PEPE-USD").upper().strip()

    # Hangisi geçerli? Eğer serbest arama kutusu doluysa o, yoksa açılır menüdeki
    aktif_kesif_sembol = serbest_arama if serbest_arama else secilen_hizli

    st.divider()

    # Varlık verilerini çek
    with st.spinner(f"🔍 {aktif_kesif_sembol} şirket verileri, bilanço oranları ve haberler yükleniyor..."):
        k_kat, k_para, k_ikon = varlik_sinifi_belirle(aktif_kesif_sembol)
        k_gecmis = varlik_gecmisi_getir(aktif_kesif_sembol, period="1y")
        
        # yfinance info sözlüğü
        k_info = {}
        try:
            if aktif_kesif_sembol != "GRAM_ALTIN":
                t_obj = yf.Ticker(aktif_kesif_sembol)
                k_info = t_obj.info if hasattr(t_obj, 'info') else {}
        except Exception:
            k_info = {}

    if k_gecmis.empty:
        st.error(f"❌ '{aktif_kesif_sembol}' için veri bulunamadı. Lütfen sembolü doğru yazdığınızdan emin olun (örn: BIST için FROTO.IS, ABD için TSLA).")
    else:
        guncel_kesif_fiyat = float(k_gecmis['Close'].iloc[-1])
        onceki_kesif_fiyat = float(k_gecmis['Close'].iloc[-2]) if len(k_gecmis) > 1 else guncel_kesif_fiyat
        gunluk_degisim_yuzde = ((guncel_kesif_fiyat - onceki_kesif_fiyat) / onceki_kesif_fiyat) * 100

        # Başlık ve Temel Bilgiler
        sirket_uzun_adi = k_info.get("longName", aktif_kesif_sembol)
        sektor = k_info.get("sector", k_kat)
        endustri = k_info.get("industry", "Piyasa Varlığı")

        col_header1, col_header2 = st.columns([2.5, 1.5])
        with col_header1:
            st.markdown(f"### {k_ikon} {sirket_uzun_adi} (`{aktif_kesif_sembol}`)")
            st.caption(f"📂 **Kategori:** {k_kat} | 🏢 **Sektör:** {sektor} | 📌 **Faaliyet:** {endustri}")
        with col_header2:
            st.metric(
                label=f"Anlık Fiyat ({k_para})",
                value=f"{guncel_kesif_fiyat:,.2f} {k_para}",
                delta=f"%{gunluk_degisim_yuzde:+.2f} (Günlük)"
            )

        # 6'lı Finansal Bilanço & Değerleme Çarpanları Grid'i
        m_cap = k_info.get("marketCap")
        m_cap_str = f"{m_cap / 1e9:,.2f} Milyar {k_para}" if m_cap else "Bilinmiyor"
        
        pe_ratio = k_info.get("trailingPE")
        pe_str = f"{pe_ratio:.2f}" if pe_ratio else "—"
        
        pb_ratio = k_info.get("priceToBook")
        pb_str = f"{pb_ratio:.2f}" if pb_ratio else "—"
        
        div_yield = k_info.get("dividendYield")
        div_str = f"%{div_yield * 100:.2f}" if div_yield else "%0.00"
        
        h_52 = k_info.get("fiftyTwoWeekHigh")
        l_52 = k_info.get("fiftyTwoWeekLow")
        h52_str = f"{h_52:.2f} {k_para}" if h_52 else "—"
        l52_str = f"{l_52:.2f} {k_para}" if l_52 else "—"

        st.markdown("##### 📊 Temel Analiz & Bilanço Göstergeleri")
        c_val1, c_val2, c_val3, c_val4, c_val5 = st.columns(5)
        with c_val1:
            st.metric("Piyasa Değeri", m_cap_str)
        with c_val2:
            st.metric("F/K Oranı (P/E)", pe_str, help="Fiyat/Kazanç oranı. Sektör ortalamasına göre ne kadar kârlı?")
        with c_val3:
            st.metric("PD/DD (P/B)", pb_str, help="Piyasa Değeri / Defter Değeri oranı.")
        with c_val4:
            st.metric("Temettü Verimi", div_str, help="Yıllık kâr payı dağıtım oranı.")
        with c_val5:
            st.metric("52 Haftalık Zirve/Dip", f"{h52_str} / {l52_str}")

        # İnteraktif Fiyat Grafiği (1 Yıllık)
        fig_kesif_trend = go.Figure()
        fig_kesif_trend.add_trace(go.Scatter(
            x=k_gecmis.index,
            y=k_gecmis['Close'],
            name=f'{aktif_kesif_sembol} Kapanış',
            line=dict(color='#00b4d8', width=2.5)
        ))
        # 20 ve 50 günlük SMA
        sma20_k = k_gecmis['Close'].rolling(20).mean()
        sma50_k = k_gecmis['Close'].rolling(50).mean()
        fig_kesif_trend.add_trace(go.Scatter(x=k_gecmis.index, y=sma20_k, name='SMA 20', line=dict(color='#f77f00', width=1.5)))
        fig_kesif_trend.add_trace(go.Scatter(x=k_gecmis.index, y=sma50_k, name='SMA 50', line=dict(color='#9d4edd', width=1.5)))

        fig_kesif_trend.update_layout(
            title=f"📈 {aktif_kesif_sembol} - Son 1 Yıllık Fiyat & Trend Grafiği",
            xaxis_title="Tarih",
            yaxis_title=f"Fiyat ({k_para})",
            hovermode="x unified",
            height=400,
            margin=dict(t=40, b=20, l=20, r=20)
        )
        st.plotly_chart(fig_kesif_trend, use_container_width=True)

        # ----------------------------------------------------------------------
        # 📰 CANLI FİNANS HABERLERİ AKIŞI
        # ----------------------------------------------------------------------
        st.divider()
        st.markdown(f"### 📰 {aktif_kesif_sembol} ile İlgili Canlı Haberler & Medya")
        
        arama_kelimesi = sirket_uzun_adi if sirket_uzun_adi != aktif_kesif_sembol else aktif_kesif_sembol.replace(".IS", "").replace("-USD", "")
        haberler = get_live_news(arama_kelimesi, count=4)

        if not haberler:
            st.info(f"💡 {aktif_kesif_sembol} hakkında son 24 saatte yeni bir haber akışı bulunamadı.")
        else:
            col_hab1, col_hab2 = st.columns(2)
            for idx, hab in enumerate(haberler):
                target_col = col_hab1 if idx % 2 == 0 else col_hab2
                with target_col:
                    st.markdown(f"""
                    <div class="news-card">
                        <span style="color: #38bdf8; font-size: 12px; font-weight: bold;">📰 {hab['source']}</span>
                        <span style="color: #64748b; font-size: 11px; float: right;">🕒 {hab['date']}</span>
                        <div style="font-weight: 600; font-size: 14px; margin-top: 6px; color: #f1f5f9;">{hab['headline']}</div>
                        <div style="margin-top: 10px;">
                            <a href="{hab['link']}" target="_blank" style="color: #60a5fa; font-size: 12px; text-decoration: none; font-weight: bold;">🔗 Haberi Oku ↗</a>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

        # ----------------------------------------------------------------------
        # 🤖 GEMINI AI ŞİRKET & HABER RAPORU
        # ----------------------------------------------------------------------
        st.divider()
        st.markdown("### 🤖 Google Gemini Şirket & Bilanço Değerlendirmesi")
        st.write("Yapay zeka analisti şirketin çarpanlarını, faaliyet alanını ve son haberlerini özetlesin.")

        if st.button(f"🧠 {aktif_kesif_sembol} Hakkında Yapay Zeka Raporu Al", key="gemini_kesif_btn"):
            if not gemini_key:
                st.warning("Lütfen sol menüden ücretsiz Gemini API anahtarınızı girin!")
            else:
                with st.spinner("🤖 Gemini şirket bilançosunu ve haberleri inceliyor..."):
                    try:
                        from google import genai
                        client = genai.Client(api_key=gemini_key)
                        
                        haber_metinleri = "\n".join([f"- {h['headline']} ({h['source']})" for h in haberler])
                        
                        prompt_kesif = f"""
Sen Wall Street ve Borsa İstanbul'da kıdemli bir Hisse Senedi Araştırma (Equity Research) analistisin.
Aşağıda incelenen şirketin canlı verileri yer alıyor:

- Şirket / Varlık: {sirket_uzun_adi} ({aktif_kesif_sembol})
- Kategori: {k_kat} | Sektör: {sektor}
- Güncel Fiyat: {guncel_kesif_fiyat:,.2f} {k_para}
- Piyasa Değeri: {m_cap_str}
- F/K Oranı: {pe_str} | PD/DD: {pb_str} | Temettü Verimi: {div_str}
- 52 Haftalık Aralık: {l52_str} - {h52_str}

Son Canlı Haber Başlıkları:
{haber_metinleri if haber_metinleri else 'Öne çıkan yeni bir haber bulunamadı.'}

Lütfen yatırımcıya şu 3 başlık altında net, Türkçe ve profesyonel bir şirket raporu hazırla:
1. 🏢 **İş Modeli ve Sektörel Konumu:** (Şirket ne iş yapar, sektördeki gücü nedir?)
2. 📊 **Bilanço & Değerleme Yorumu:** (F/K, PD/DD oranları ve temettü verimi ne anlatıyor? Şirket pahalı mı, makul mü?)
3. 📰 **Piyasa Algısı ve Haber Özeti:** (Son haber akışı şirket için pozitif mi negatif mi?)

(Yatırım tavsiyesi olmadığını belirten kısa bir not ekle).
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
                        st.error(f"Yapay zeka analizi alınamadı: {err}")

        # ----------------------------------------------------------------------
        # 🎯 PORTFÖYE HIZLI EKLEME AKSİYON KARTI
        # ----------------------------------------------------------------------
        st.divider()
        with st.expander(f"➕ Beğendin mi? {aktif_kesif_sembol} Varlığını Portföyüne Ekle!"):
            st.write(f"Bu varlığı kendi kişisel portföyünüze eklemek için alış maliyetinizi ve miktarınızı girin:")
            col_add1, col_add2, col_add3 = st.columns(3)
            with col_add1:
                hizli_maliyet = st.number_input("Alış Maliyeti", value=float(guncel_kesif_fiyat), format="%.2f", key="hizli_maliyet_in")
            with col_add2:
                hizli_adet = st.number_input("Adet / Miktar", min_value=0.0001, value=10.0, step=1.0, format="%.4f", key="hizli_adet_in")
            with col_add3:
                st.write("")
                st.write("")
                if st.button("🚀 Portföyüme Kaydet", type="primary", use_container_width=True, key="hizli_kaydet_btn"):
                    if is_demo:
                        st.session_state.demo_portfoy[aktif_kesif_sembol] = {"maliyet": float(hizli_maliyet), "adet": float(hizli_adet)}
                    else:
                        database.kullanici_hisse_ekle_guncelle(user_email, aktif_kesif_sembol, float(hizli_maliyet), float(hizli_adet))
                    st.success(f"✅ {aktif_kesif_sembol} başarıyla portföyünüze eklendi! 'Portföyüm' sekmesinden görüntüleyebilirsiniz.")
                    st.rerun()