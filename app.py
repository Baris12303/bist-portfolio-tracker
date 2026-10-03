import streamlit as st
import yfinance as yf
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
import requests
import database


from ui.tab_portfoy import render_tab_portfoy
from ui.tab_kesif import render_tab_kesif

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


from services.market_data import get_usd_try_rate, varlik_sinifi_belirle, varlik_gecmisi_getir, get_live_news, get_company_fundamentals, get_ai_news_sentiment
from core.rebalancing import REBALANCE_STRATEJILERI, hesapla_portfoy_rebalancing
from core.alarms import denetle_portfoy_alarmlari, gonder_alarm_epostasi

# --- GİRİŞ YAPILMIŞ KULLANICI AKIŞI ---
user = st.session_state.kullanici
user_email = user["email"]
is_demo = user.get("rol") == "demo"
usd_try = get_usd_try_rate()

# Kullanıcı hedef fiyatları, stop-loss ve akıllı alarm ayarları (Madde 4 & 7)
if "kullanici_hedefleri" not in st.session_state:
    st.session_state.kullanici_hedefleri = {}

if "bildirim_ayarlari" not in st.session_state:
    st.session_state.bildirim_ayarlari = {
        "site_bildirim_aktif": True,
        "eposta_bildirim_aktif": False,
        "eposta_adresi": user_email if "@" in user_email else ""
    }

if "tetiklenen_alarmlar" not in st.session_state:
    st.session_state.tetiklenen_alarmlar = set()

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
    
    # Demo kullanıcıları için mock hedefler ekle
    if not st.session_state.kullanici_hedefleri:
        st.session_state.kullanici_hedefleri = {
            "THYAO.IS": {"hedef": 345.00, "stop": 260.00},
            "NVDA": {"hedef": 140.00, "stop": 105.00},
            "GRAM_ALTIN": {"hedef": 3400.00, "stop": 2850.00}
        }
else:
    portfoy = database.kullanici_portfoyu_getir(user_email)
    
    # Veritabanından hedefleri ve ayarları session'a aktar (Sadece bir kez)
    if "veritabani_yuklendi" not in st.session_state:
        for s, p_data in portfoy.items():
            st.session_state.kullanici_hedefleri[s] = {
                "hedef": p_data.get("hedef", 0.0),
                "stop": p_data.get("stop", 0.0)
            }
        
        ayarlar_db = database.kullanici_ayarlari_getir(user_email)
        if ayarlar_db:
            st.session_state.bildirim_ayarlari = ayarlar_db
            
        st.session_state.veritabani_yuklendi = True

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
    for _oturum_anahtari in (
        "demo_portfoy",
        "kullanici_hedefleri",
        "bildirim_ayarlari",
        "tetiklenen_alarmlar",
        "veritabani_yuklendi",
    ):
        st.session_state.pop(_oturum_anahtari, None)
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

# 3. Akıllı Alarm & İstihbarat Radarı (Madde 7)
st.sidebar.divider()
st.sidebar.markdown("""
<div style="background: rgba(255, 255, 255, 0.02); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 10px; padding: 12px 14px; margin-bottom: 12px;">
    <div style="font-size: 11.5px; font-weight: 600; color: #38bdf8; text-transform: uppercase; letter-spacing: 0.06em;">
        ✦ Akıllı Alarm & İstihbarat
    </div>
    <div style="font-size: 11.5px; color: #94a3b8; margin-top: 5px; line-height: 1.45;">
        Kritik seviyeleri kaçırmayın. Kâr hedefleri, ani geri çekilmeler ve RSI dip fırsatlarında anlık istihbarat alarak servetinizi proaktif koruyun.
    </div>
</div>
""", unsafe_allow_html=True)

b_site = st.sidebar.toggle(
    "Site İçi Bildirimler", 
    value=st.session_state.bildirim_ayarlari.get("site_bildirim_aktif", True),
    help="Terminal içinde kâr hedefi, stop-loss ve RSI dip uyarı kartlarını gösterir."
)
b_eposta = st.sidebar.toggle(
    "E-posta Bildirimleri", 
    value=st.session_state.bildirim_ayarlari.get("eposta_bildirim_aktif", False),
    help="Seviyeler tetiklendiğinde e-posta kutunuza kurumsal istihbarat raporu iletir."
)

yeni_eposta = st.session_state.bildirim_ayarlari.get("eposta_adresi") or user_email
if b_eposta:
    eposta_girdi = st.sidebar.text_input(
        "Bildirim E-postası:",
        value=yeni_eposta,
        placeholder="ornek@alanadi.com"
    )
    yeni_eposta = eposta_girdi.strip()

yeni_ayarlar = {
    "site_bildirim_aktif": b_site,
    "eposta_bildirim_aktif": b_eposta,
    "eposta_adresi": yeni_eposta
}

if yeni_ayarlar != st.session_state.bildirim_ayarlari:
    st.session_state.bildirim_ayarlari = yeni_ayarlar
    if not is_demo:
        database.kullanici_ayarlari_guncelle(user_email, yeni_ayarlar)

col_alarm_btn, col_alarm_clr = st.sidebar.columns(2)
with col_alarm_btn:
    if st.button("Alarmı Test Et", use_container_width=True, help="Örnek bir alarm tetikleyerek bildirim kanalını test eder."):
        ornek_alarm = [{
            "sembol": "TEST.VARLIK",
            "tip": "HEDEF_YAKIN",
            "etiket": "İstihbarat Test Bildirimi",
            "mesaj": "Sistem bağlantısı ve alarm kanalları sorunsuz çalışıyor. Portföyünüz 7/24 izlenmektedir.",
            "seviye": "pozitif",
            "fiyat": 100.0,
            "hedef": 105.0,
            "para": "TL",
            "alarm_id": "TEST_ALARM"
        }]
        if b_eposta and st.session_state.bildirim_ayarlari.get("eposta_adresi"):
            ok, msj = gonder_alarm_epostasi(st.session_state.bildirim_ayarlari["eposta_adresi"], ornek_alarm)
            if ok:
                st.sidebar.success(msj)
            else:
                st.sidebar.error(msj)
        else:
            st.sidebar.info("Site içi alarm kanalı aktif. E-posta testi için yukarıdaki e-posta anahtarını açabilirsiniz.")
with col_alarm_clr:
    if st.button("Alarmları Sıfırla", use_container_width=True, help="Tetiklenen alarmların bildirim hafızasını sıfırlar."):
        st.session_state.tetiklenen_alarmlar = set()
        st.sidebar.caption("Alarm bildirim hafızası temizlendi.")

# 4. Yapay Zeka Anahtarı
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
    render_tab_portfoy(
        portfoy=portfoy,
        user=user,
        user_email=user_email,
        is_demo=is_demo,
        usd_try=usd_try,
        gemini_key=gemini_key,
    )

# ------------------------------------------------------------------------------
# SEKME 2: PİYASA & ŞİRKET KEŞİF TERMİNALİ
# ------------------------------------------------------------------------------
with tab_kesif:
    render_tab_kesif(is_demo=is_demo, gemini_key=gemini_key, user_email=user_email)
