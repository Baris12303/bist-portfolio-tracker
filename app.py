import streamlit as st
import yfinance as yf
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import database

# Sayfa Başlığı ve Geniş Ekran Düzeni
st.set_page_config(page_title="Global Servet & Portföy Terminali", page_icon="🌐", layout="wide")

# --- KULLANICI OTURUM KONTROLÜ (SESSION STATE) ---
if "kullanici" not in st.session_state:
    st.session_state.kullanici = None

# Giriş yapılmamışsa Giriş / Kayıt / Demo ekranını göster
if not st.session_state.kullanici:
    st.title("🌐 Global Servet & Portföy Terminali")
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
        - 🌐 **Çoklu Varlık Desteği:** BIST, Amerikan Hisseleri (Apple, Nvidia), Kripto Paralar (Bitcoin, Ethereum) ve Gram Altın tek sepette.
        - 💵 **Otomatik Kur Çevrimi:** USD ve TL varlıklarınız anlık kurlarla otomatik toplanır, toplam servetinizi hem TL hem Dolar görürsünüz.
        - 🔮 **Makine Öğrenmesi (ML) Fiyat Tahmini:** Akakçe/Cimri tarzı 7 günlük fiyat projeksiyonu ve güven bandı.
        - 📊 **İleri Seviye Teknik Analiz:** SMA 20, SMA 50, RSI (14) ve MACD (12,26,9) indikatörleri.
        - 🤖 **Google Gemini Yapay Zeka:** Portföy risk analizi ve varlıklarınıza özel kıdemli analist yorumları.
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
        # Otomatik uzantı tamamlama
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

# --- ANA EKRAN BAŞLIĞI VE ÖZET METRİKLER ---
st.title("🌐 Global Servet & Portföy Terminali")
st.write("Borsa İstanbul, Amerikan Borsaları, Kripto Paralar ve Altın yatırımlarınız tek ekranda.")

if not portfoy:
    st.info("💡 Portföyünüz şu an boş. Sol menüden yeni varlık ekleyebilir veya '📥 Örnek Veri' butonuna tıklayarak örnek karma portföyü yükleyebilirsiniz.")
    st.stop()

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

# Portföydeki her varlık için canlı veri çekimi ve kur dönüşümü
with st.spinner("⏳ Küresel piyasa verileri ve canlı kurlar yükleniyor..."):
    for sembol, bilgi in portfoy.items():
        maliyet = float(bilgi["maliyet"])
        adet = float(bilgi["adet"])
        kategori, para, ikon = varlik_sinifi_belirle(sembol)
        
        gecmis = varlik_gecmisi_getir(sembol, period="6mo")
        if gecmis.empty:
            continue
            
        guncelFiyatYerel = float(gecmis['Close'].iloc[-1])
        
        # Para birimi çevrimi
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
        
        # Varlık sınıfına göre toplama
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
    st.metric(
        label="Toplam Yatırılan Maliyet",
        value=f"{toplamMaliyetTL:,.2f} TL",
        delta=f"≈ ${toplamMaliyetTL / usd_try:,.2f} USD"
    )

with col2:
    st.metric(
        label="Toplam Portföy Değeri",
        value=f"{toplamGuncelDegerTL:,.2f} TL",
        delta=f"≈ ${toplamGuncelDegerTL / usd_try:,.2f} USD"
    )

with col3:
    st.metric(
        label="Toplam Net Kâr/Zarar",
        value=f"{toplamKarTL:+,.2f} TL",
        delta=f"%{toplamKarYuzde:+.2f}"
    )

with col4:
    st.metric(
        label="BIST 100 vs Portföy (6 Ay)",
        value=f"BIST: %{bist_getiri:.1f}",
        delta=f"%{fark:+.1f} Fark"
    )

st.divider()
st.subheader("📋 Küresel Portföy Detayları")
st.dataframe(tabloVerisi, use_container_width=True)

st.divider()
st.subheader("🥧 Portföy Varlık & Kategori Dağılımı")

tab_pasta1, tab_pasta2 = st.tabs(["🏷️ Varlık Sınıfı Dağılımı (Kategori)", "📌 Tekil Varlık Dağılımı"])

with tab_pasta1:
    fig_kat = px.pie(
        names=list(kategoriDegerler.keys()),
        values=list(kategoriDegerler.values()),
        hole=0.45,
        color_discrete_sequence=px.colors.qualitative.Prism
    )
    fig_kat.update_traces(textposition='inside', textinfo='percent+label', hovertemplate="<b>%{label}</b><br>Toplam: %{value:,.2f} TL<br>Pay: %{percent}<extra></extra>")
    fig_kat.update_layout(margin=dict(t=10, b=10, l=10, r=10), height=350)
    st.plotly_chart(fig_kat, use_container_width=True)

with tab_pasta2:
    fig_pasta = px.pie(
        names=pastaEtiketler,
        values=pastaDegerler,
        hole=0.45,
        color_discrete_sequence=px.colors.qualitative.Safe
    )
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
st.subheader("📊 Varlık Analizi & 🔮 Makine Öğrenmesi Fiyat Projeksiyonu")

secilen = st.selectbox("İncelemek istediğiniz varlığı seçin:", list(portfoy.keys()))

secilen_kat, secilen_para, secilen_ikon = varlik_sinifi_belirle(secilen)
gecmisSecilen = varlik_gecmisi_getir(secilen, period="6mo")
secilenMaliyet = float(portfoy[secilen]["maliyet"])

if gecmisSecilen.empty:
    st.warning("Seçilen varlık için geçmiş fiyat verisi çekilemedi.")
    st.stop()

# SMA Göstergeleri
gecmisSecilen['SMA20'] = gecmisSecilen['Close'].rolling(window=20).mean()
gecmisSecilen['SMA50'] = gecmisSecilen['Close'].rolling(window=50).mean()

# 14 Günlük RSI
fark_fiyat = gecmisSecilen['Close'].diff()
kazanc = fark_fiyat.where(fark_fiyat > 0, 0.0).rolling(window=14).mean()
kayip = (-fark_fiyat.where(fark_fiyat < 0, 0.0)).rolling(window=14).mean()
rs = kazanc / kayip
gecmisSecilen['RSI'] = 100 - (100 / (1 + rs))
guncel_rsi = float(gecmisSecilen['RSI'].iloc[-1])

# MACD (12, 26, 9)
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

# --- 🔮 MAKİNE ÖĞRENMESİ (REGRESYON İLE 7 GÜNLÜK TAHMİN) ---
gunler = np.arange(len(gecmisSecilen))
fiyatlar = gecmisSecilen['Close'].values

# Lineer Regresyon modeli (Trend Eğimi)
p = np.polyfit(gunler, fiyatlar, deg=1)
trend_modeli = np.poly1d(p)
tahmin_gecmis = trend_modeli(gunler)
std_hata = float(np.std(fiyatlar - tahmin_gecmis))

# Gelecek 7 günün indeksleri ve tarihleri
son_tarih = gecmisSecilen.index[-1]
fut_indices = np.arange(len(gecmisSecilen) - 1, len(gecmisSecilen) + 7)
fut_prices = trend_modeli(fut_indices)
fut_dates = [son_tarih] + list(pd.date_range(start=son_tarih + pd.Timedelta(days=1), periods=7, freq='D'))

tahmin_7gun = float(fut_prices[-1])
guncel_son_fiyat = float(fiyatlar[-1])
tahmin_fark_yuzde = ((tahmin_7gun - guncel_son_fiyat) / guncel_son_fiyat) * 100
gunluk_egim = float(p[0])

# İnteraktif Trend & Projeksiyon Grafiği
fig_trend = go.Figure()

# 1. Kapanış Fiyatı
fig_trend.add_trace(go.Scatter(
    x=gecmisSecilen.index, 
    y=gecmisSecilen['Close'], 
    name=f'Kapanış ({secilen_para})',
    line=dict(color='#00b4d8', width=2.5)
))

# 2. SMA 20
fig_trend.add_trace(go.Scatter(
    x=gecmisSecilen.index, 
    y=gecmisSecilen['SMA20'], 
    name='SMA 20 (Kısa Vade)',
    line=dict(color='#f77f00', width=1.5)
))

# 3. SMA 50
fig_trend.add_trace(go.Scatter(
    x=gecmisSecilen.index, 
    y=gecmisSecilen['SMA50'], 
    name='SMA 50 (Orta Vade)',
    line=dict(color='#9d4edd', width=1.5)
))

# 4. Maliyet Çizgisi
fig_trend.add_hline(
    y=secilenMaliyet, 
    line_dash="dash", 
    line_color="#e63946", 
    annotation_text=f"Maliyetim ({secilenMaliyet:.2f} {secilen_para})",
    annotation_position="top left"
)

# 5. 🔮 Gelecek 7 Günlük Regresyon Tahmin Çizgisi
fig_trend.add_trace(go.Scatter(
    x=fut_dates, 
    y=fut_prices, 
    name='🔮 7 Günlük ML Tahmini',
    mode='lines',
    line=dict(color='#c084fc', width=2.5, dash='dash')
))

# 6. Tahmin Güven Bandı (Üst)
fig_trend.add_trace(go.Scatter(
    x=fut_dates,
    y=fut_prices + std_hata,
    name='Tahmin Üst Sınır',
    mode='lines',
    line=dict(color='rgba(0,0,0,0)', width=0),
    showlegend=False,
    hoverinfo='skip'
))

# 7. Tahmin Güven Bandı (Alt)
fig_trend.add_trace(go.Scatter(
    x=fut_dates,
    y=fut_prices - std_hata,
    name='Güven Aralığı',
    mode='lines',
    fill='tonexty',
    fillcolor='rgba(192, 132, 252, 0.15)',
    line=dict(color='rgba(0,0,0,0)', width=0),
    hoverinfo='skip'
))

fig_trend.update_layout(
    title=f"📈 {secilen_ikon} {secilen} - Canlı Fiyat & Gelecek 7 Günlük Projeksiyon",
    xaxis_title="Tarih",
    yaxis_title=f"Fiyat ({secilen_para})",
    hovermode="x unified",
    height=480,
    margin=dict(t=40, b=20, l=20, r=20)
)
st.plotly_chart(fig_trend, use_container_width=True)

# 🔮 Akakçe / Cimri Tarzı Makine Öğrenmesi Tahmin Kartı
st.markdown("#### 🔮 Makine Öğrenmesi Fiyat Projeksiyonu (Sonraki 7 Gün)")
col_ml1, col_ml2, col_ml3 = st.columns(3)

with col_ml1:
    st.metric(
        label="7 Gün Sonraki Model Hedefi",
        value=f"{tahmin_7gun:,.2f} {secilen_para}",
        delta=f"%{tahmin_fark_yuzde:+.2f} Beklenen Yön"
    )

with col_ml2:
    st.metric(
        label="Model Güven Bandı",
        value=f"±{std_hata:.2f} {secilen_para}",
        help="Olası dalgalanma payı / Standart hata aralığı"
    )

with col_ml3:
    egim_yorum = "Yükseliş Eğilimi 🚀" if gunluk_egim > 0 else "Düzeltme / Düşüş Eğilimi 📉"
    st.metric(
        label="Günlük Trend İvmesi (Eğim)",
        value=f"{gunluk_egim:+.2f} {secilen_para}/Gün",
        delta=egim_yorum
    )

if gunluk_egim > 0:
    st.info(f"💡 **Model Yorumu:** Mevcut regresyon eğimi ve momentum pozitif bölgede. Varlık önümüzdeki 7 günde **{tahmin_7gun:.2f} {secilen_para}** bandına doğru hareket etme eğiliminde.")
else:
    st.warning(f"⚠️ **Model Yorumu:** Son dönem fiyat eğiliminde kâr satışı / düzeltme baskısı hakim. Kısa vadede **{tahmin_7gun:.2f} {secilen_para}** seviyelerine doğru dengelenme izlenebilir.")

# 3'lü İndikatör Sinyal Rozetleri
c_ind1, c_ind2, c_ind3 = st.columns(3)

with c_ind1:
    if guncel_rsi > 70:
        st.warning(f"⚠️ **RSI: {guncel_rsi:.1f}**\nAşırı Alım (Düzeltme Riski)")
    elif guncel_rsi < 30:
        st.success(f"💎 **RSI: {guncel_rsi:.1f}**\nAşırı Satım (Dip Fırsatı)")
    else:
        st.info(f"⚖️ **RSI: {guncel_rsi:.1f}**\nNötr Bölge")

with c_ind2:
    if macd_al:
        st.success(f"🟢 **MACD: {guncel_macd:.2f}**\nBoğa Gücü (Alıcılar Üstün)")
    else:
        st.error(f"🔴 **MACD: {guncel_macd:.2f}**\nAyı Baskısı (Satıcılar Üstün)")

with c_ind3:
    if golden_cross:
        st.success(f"🏆 **Trend:** Altın Kesişim\nSMA 20 > SMA 50 (Yükseliş Trendi)")
    else:
        st.error(f"💀 **Trend:** Düşüş Eğilimi\nSMA 20 < SMA 50 (Satış Baskısı)")

# İnteraktif RSI Grafiği
fig_rsi = go.Figure()
fig_rsi.add_trace(go.Scatter(x=gecmisSecilen.index, y=gecmisSecilen['RSI'], name='RSI (14)', line=dict(color='#a855f7', width=2)))
fig_rsi.add_hline(y=70, line_dash="dash", line_color="#ef4444", annotation_text="Aşırı Alım (70)")
fig_rsi.add_hline(y=30, line_dash="dash", line_color="#22c55e", annotation_text="Aşırı Satım (30)")
fig_rsi.update_layout(title="RSI (Göreceli Güç Endeksi) - Son 6 Ay", yaxis_range=[0, 100], height=220, margin=dict(t=30, b=20, l=20, r=20))
st.plotly_chart(fig_rsi, use_container_width=True)

# İnteraktif MACD Grafiği
fig_macd = go.Figure()
renkler = ['#10b981' if val >= 0 else '#ef4444' for val in gecmisSecilen['Hist']]
fig_macd.add_trace(go.Bar(
    x=gecmisSecilen.index,
    y=gecmisSecilen['Hist'],
    name='Histogram',
    marker_color=renkler,
    opacity=0.6
))
fig_macd.add_trace(go.Scatter(
    x=gecmisSecilen.index,
    y=gecmisSecilen['MACD'],
    name='MACD (12,26)',
    line=dict(color='#2563eb', width=2)
))
fig_macd.add_trace(go.Scatter(
    x=gecmisSecilen.index,
    y=gecmisSecilen['Signal'],
    name='Sinyal (9)',
    line=dict(color='#f59e0b', width=1.5, dash='dot')
))
fig_macd.update_layout(
    title=f"📊 {secilen} - MACD & Sinyal Kesişim Grafiği",
    height=240,
    margin=dict(t=30, b=20, l=20, r=20),
    hovermode="x unified"
)
st.plotly_chart(fig_macd, use_container_width=True)

# 🧪 Mini Strateji Backtest Testi
with st.expander(f"🧪 Strateji Testi: {secilen} için MACD Al-Sat Kârlı mıydı?"):
    try:
        df_sim = gecmisSecilen.copy()
        df_sim['Pozisyon'] = (df_sim['MACD'] > df_sim['Signal']).astype(int).shift(1)
        df_sim['Gunluk_Getiri'] = df_sim['Close'].pct_change()
        df_sim['Strateji_Getiri'] = df_sim['Gunluk_Getiri'] * df_sim['Pozisyon']

        getiri_bh = ((1 + df_sim['Gunluk_Getiri'].dropna()).prod() - 1) * 100
        getiri_strat = ((1 + df_sim['Strateji_Getiri'].dropna()).prod() - 1) * 100

        col_sim1, col_sim2 = st.columns(2)
        with col_sim1:
            st.metric("Alıp Bekleme Getirisi (Buy & Hold)", f"%{getiri_bh:.2f}")
        with col_sim2:
            fark_strat = getiri_strat - getiri_bh
            st.metric("MACD Sinyal Stratejisi Getirisi", f"%{getiri_strat:.2f}", delta=f"%{fark_strat:.2f} Strateji Farkı")
        
        if getiri_strat > getiri_bh:
            st.success("🎯 **Sonuç:** Son 6 ayda MACD kesişimlerini takip etmek varlığı sürekli elde tutmaktan daha kârlı olmuş!")
        else:
            st.info("ℹ️ **Sonuç:** Güçlü trendlerde veya yatay piyasada varlıkta kalıp beklemek (Buy & Hold) daha yüksek getiri sağlamış.")
    except Exception:
        st.caption("Simülasyon için yeterli geçmiş veri hesaplanamadı.")

st.divider()
st.subheader("🤖 Yapay Zeka Portföy Analisti (Google Gemini)")
st.write("Büyük dil modeli çoklu varlık portföyünüzün risk dengesini ve seçili varlığı canlı analiz etsin.")

if st.button("🧠 Portföyümü ve Varlığımı Yorumla"):
    if not gemini_key:
        st.warning("⚠️ Lütfen sol menüden ücretsiz Gemini API anahtarınızı girin! (aistudio.google.com adresinden 10 saniyede alabilirsiniz)")
    else:
        with st.spinner("🤖 Gemini küresel portföyünüzü ve teknik indikatörleri inceliyor..."):
            try:
                from google import genai
                client = genai.Client(api_key=gemini_key)
                
                prompt = f"""
Sen Borsa İstanbul, Amerikan Borsası (Wall Street), Kripto Paralar ve Emtialar konusunda uzman kıdemli bir küresel portföy yöneticisi ve teknik analistsin.
Aşağıda yatırımcının canlı çoklu varlık portföyü ve piyasa verileri yer alıyor:

- Yatırımcı: {user.get('ad_soyad', 'Yatırımcı')}
- Toplam Portföy Değeri: {toplamGuncelDegerTL:,.2f} TL (≈ ${toplamGuncelDegerTL / usd_try:,.2f} USD)
- Toplam Maliyet: {toplamMaliyetTL:,.2f} TL (≈ ${toplamMaliyetTL / usd_try:,.2f} USD)
- Toplam Net Kâr/Zarar: {toplamKarTL:+,.2f} TL (%{toplamKarYuzde:+.2f})
- Anlık Dolar Kuru: 1 USD = {usd_try:.2f} TL
- Portföy Varlıkları: {list(portfoy.keys())}
- Varlık Sınıfı Dağılımı: {kategoriDegerler}
- En Çok Kazandıran: {enIyiVarlik} (%{enYuksekKar:+.2f})
- En Çok Kaybettiren: {enKotuVarlik} (%{enDusukKar:+.2f})

İncelenen Seçili Varlık: {secilen_ikon} {secilen} ({secilen_kat})
- Güncel Fiyat: {guncel_son_fiyat:,.2f} {secilen_para} (Alış Maliyeti: {secilenMaliyet:,.2f} {secilen_para})
- 14 Günlük RSI: {guncel_rsi:.1f}
- SMA 20: {guncel_sma20:,.2f} {secilen_para}
- SMA 50: {guncel_sma50:,.2f} {secilen_para}
- MACD Durumu: {guncel_macd:.2f} (Sinyal: {guncel_signal:.2f} | {'🟢 Boğa Alım Bölgesi' if macd_al else '🔴 Ayı Satım Baskısı'})
- Trend Durumu: {'🏆 Altın Kesişim (Golden Cross - Yükseliş Trendi)' if golden_cross else '💀 SMA20 < SMA50 (Düşüş Eğilimi)'}
- Makine Öğrenmesi 7 Günlük Model Hedefi: {tahmin_7gun:,.2f} {secilen_para} (%{tahmin_fark_yuzde:+.2f} Beklenen Yön, Eğim: {gunluk_egim:+.2f})

Lütfen şu 3 başlık altında net, profesyonel, samimi ve Türkçe bir analiz sun:
1. 📊 **Küresel Portföy Sağlık & Risk Değerlendirmesi:** (BIST, ABD, Kripto ve Altın çeşitlendirmesi dengeli mi? Dolar/TL riskine karşı nasıl konumlanmış?)
2. 🔍 **{secilen} Teknik & Tahmin Analizi:** (RSI, MACD ve Regresyon tahmin modeli ne söylüyor?)
3. 💡 **Stratejik Öneriler:** (Kısa ve orta vadede varlık dağılımında nelere dikkat edilmeli?)

(Yatırım tavsiyesi olmadığını belirten kısa bir not ekle).
"""
                modeller = []
                try:
                    for m in client.models.list():
                        m_name = getattr(m, 'name', '')
                        if "gemini" in m_name.lower():
                            modeller.append(m_name)
                except Exception:
                    pass

                if not modeller:
                    modeller = ["gemini-3.8-flash", "models/gemini-3.8-flash"]

                analiz_tamamlandi = False
                son_hata = ""
                
                for model_adi in modeller:
                    try:
                        cevap = client.models.generate_content(
                            model=model_adi,
                            contents=prompt
                        )
                        st.markdown(cevap.text)
                        analiz_tamamlandi = True
                        break
                    except Exception as err:
                        son_hata = f"{model_adi} -> {err}"
                        continue
                
                if not analiz_tamamlandi:
                    st.error(f"Yapay zeka analizi alınamadı. Hata detayı: {son_hata}")
            except Exception as e:
                st.error(f"Yapay zeka analizi sırasında bir hata oluştu: {e}")