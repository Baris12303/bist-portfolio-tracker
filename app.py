import streamlit as st
import yfinance as yf
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
import database

# Sayfa Başlığı ve Geniş Ekran Düzeni
st.set_page_config(page_title="BIST Portföy & Analiz Terminali", page_icon="📈", layout="wide")

# --- KULLANICI OTURUM KONTROLÜ (SESSION STATE) ---
if "kullanici" not in st.session_state:
    st.session_state.kullanici = None

# Giriş yapılmamışsa Giriş / Kayıt / Demo ekranını göster
if not st.session_state.kullanici:
    st.title("📈 BIST Portföy & Analiz Terminali")
    st.write("Borsa İstanbul yatırımlarınızı canlı verilerle takip edin, teknik göstergelerle ve yapay zekayla analiz edin.")
    
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
                        # Otomatik giriş yaptır
                        _, _, user_data = database.kullanici_giris_yap(kayit_email, kayit_sifre)
                        st.session_state.kullanici = user_data
                        st.success(f"Tebrikler {kayit_ad}! Hesabınız ve örnek BIST portföyünüz oluşturuldu.")
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
                    "AKBNK.IS": {"maliyet": 62.50, "adet": 150},
                    "ASELS.IS": {"maliyet": 390.00, "adet": 40},
                    "KCHOL.IS": {"maliyet": 195.00, "adet": 60},
                    "THYAO.IS": {"maliyet": 265.00, "adet": 50},
                    "TUPRS.IS": {"maliyet": 360.00, "adet": 30},
                }
                st.rerun()
                
    with col_info:
        st.markdown("### 🌟 Terminal Özellikleri")
        st.markdown("""
        - ☁️ **Bulut Tabanlı Kişisel Portföy:** Hisselerinizi ve maliyetlerinizi bulutta (Supabase PostgreSQL) güvenle saklayın.
        - ⚡ **Canlı Borsa İstanbul Verileri:** Yahoo Finance altyapısıyla anlık kâr/zarar ve portföy değeri hesaplama.
        - 📊 **İleri Seviye Teknik Analiz:** SMA 20, SMA 50 hareketli ortalamalar ve 14 günlük RSI osilatörü.
        - 🤖 **Google Gemini Yapay Zeka:** Portföy risk analizi ve hisselerinize özel yapay zeka yorumları.
        - 📱 **Her Yerden Erişim:** Masaüstünden veya telefonunuzdan dilediğiniz an erişim.
        """)
        st.info("💡 **İpucu:** Aile üyeleriniz veya arkadaşlarınız kendi hesaplarını açtığında herkes yalnızca kendi portföyünü görür.")
        
    st.stop()

# --- GİRİŞ YAPILMIŞ KULLANICI AKIŞI ---
user = st.session_state.kullanici
user_email = user["email"]
is_demo = user.get("rol") == "demo"

# Portföy verisini getir
if is_demo:
    if "demo_portfoy" not in st.session_state:
        st.session_state.demo_portfoy = {
            "AKBNK.IS": {"maliyet": 62.50, "adet": 150},
            "ASELS.IS": {"maliyet": 390.00, "adet": 40},
            "KCHOL.IS": {"maliyet": 195.00, "adet": 60},
            "THYAO.IS": {"maliyet": 265.00, "adet": 50},
            "TUPRS.IS": {"maliyet": 360.00, "adet": 30},
        }
    portfoy = st.session_state.demo_portfoy
else:
    portfoy = database.kullanici_portfoyu_getir(user_email)

# --- SOL MENÜ (KULLANICI BİLGİSİ & PORTFÖY YÖNETİMİ) ---
st.sidebar.markdown(f"### 👤 {user.get('ad_soyad', 'Yatırımcı')}")
st.sidebar.caption(f"📧 `{user_email}`")
if is_demo:
    st.sidebar.warning("👀 **Demo Modundasınız**")

if st.sidebar.button("🚪 Çıkış Yap", use_container_width=True):
    st.session_state.kullanici = None
    st.session_state.pop("demo_portfoy", None)
    st.rerun()

st.sidebar.divider()
st.sidebar.header("⚙️ Portföy Yönetimi")

# 1. Hisse Ekleme / Güncelleme Formu
with st.sidebar.form("hisse_ekle_formu"):
    st.subheader("➕ Hisse Ekle / Güncelle")
    yeni_sembol = st.text_input("Hisse Sembolü (örn: FROTO veya FROTO.IS)").upper().strip()
    yeni_maliyet = st.number_input("Alış Maliyeti (TL)", min_value=0.0, step=0.5)
    yeni_adet = st.number_input("Adet (Lot)", min_value=1, step=1)
    
    ekle_butonu = st.form_submit_button("Portföye Kaydet")
    if ekle_butonu and yeni_sembol:
        # Otomatik .IS uzantısı ekle
        if not yeni_sembol.endswith(".IS") and "." not in yeni_sembol:
            yeni_sembol = f"{yeni_sembol}.IS"
            
        if is_demo:
            st.session_state.demo_portfoy[yeni_sembol] = {"maliyet": yeni_maliyet, "adet": yeni_adet}
        else:
            database.kullanici_hisse_ekle_guncelle(user_email, yeni_sembol, yeni_maliyet, yeni_adet)
            
        st.success(f"{yeni_sembol} başarıyla kaydedildi!")
        st.rerun()

# 2. Hisse Silme Formu
if portfoy:
    st.sidebar.divider()
    st.sidebar.subheader("🗑️ Hisse Sil")
    silinecek_hisse = st.sidebar.selectbox("Silmek istediğiniz hisse:", list(portfoy.keys()))
    if st.sidebar.button("Hisseyi Portföyden Çıkar", use_container_width=True):
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
                "AKBNK.IS": {"maliyet": 62.50, "adet": 150},
                "ASELS.IS": {"maliyet": 390.00, "adet": 40},
                "KCHOL.IS": {"maliyet": 195.00, "adet": 60},
                "THYAO.IS": {"maliyet": 265.00, "adet": 50},
                "TUPRS.IS": {"maliyet": 360.00, "adet": 30},
            }
        else:
            database.kullanici_ornek_portfoy_yukle(user_email)
        st.rerun()

# 3. Yapay Zeka Anahtarı (Önce güvenli kasadan okur)
gemini_key = st.secrets.get("GEMINI_API_KEY", "")

# Kasada anahtar yoksa manuel giriş kutusu göster
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
st.title("📈 BIST Portföy Takip & Analiz Paneli")
st.write("Canlı borsa verileriyle portföy kâr/zarar ve teknik analiz durumu.")

if not portfoy:
    st.info("💡 Portföyünüz şu an boş. Sol menüden yeni hisse ekleyebilir veya '📥 Örnek Veri' butonuna tıklayarak hazır hisseleri yükleyebilirsiniz.")
    st.stop()

# Hesaplama değişkenleri
toplamMaliyet = 0
toplamGuncelDeger = 0
enIyiHisse = ""
enYuksekKar = -999999
enKotuHisse = ""
enDusukKar = 999999

tabloVerisi = []
pastaEtiketler = []
pastaDegerler = []

# Portföydeki her hisse için canlı veri çekimi ve kâr hesabı
with st.spinner("⏳ Canlı borsa verileri yükleniyor..."):
    for sembol, bilgi in portfoy.items():
        maliyet = bilgi["maliyet"]
        adet = bilgi["adet"]
        try:
            hisse = yf.Ticker(sembol)
            gecmis = hisse.history(period="6mo")
            if gecmis.empty:
                continue
            guncelFiyat = float(gecmis['Close'].iloc[-1])
        except Exception:
            continue
            
        toplamMaliyet += maliyet * adet
        toplamGuncelDeger += guncelFiyat * adet
        karDurumu = ((guncelFiyat - maliyet) / maliyet) * 100 if maliyet > 0 else 0.0
        
        tabloVerisi.append({
            "Hisse": sembol,
            "Adet": adet,
            "Maliyet (TL)": maliyet,
            "Güncel Fiyat (TL)": round(guncelFiyat, 2),
            "Kâr/Zarar (%)": round(karDurumu, 2),
            "Kâr/Zarar (TL)": round((guncelFiyat - maliyet) * adet, 2)
        })
        pastaEtiketler.append(sembol)
        pastaDegerler.append(guncelFiyat * adet)
        
        if karDurumu > enYuksekKar:
            enYuksekKar = karDurumu
            enIyiHisse = sembol
        if karDurumu < enDusukKar:
            enDusukKar = karDurumu
            enKotuHisse = sembol

toplamKarZararTL = toplamGuncelDeger - toplamMaliyet
toplamKarZararYuzde = ((toplamGuncelDeger - toplamMaliyet) / toplamMaliyet) * 100 if toplamMaliyet > 0 else 0.0

# BIST 100 (XU100) Getirisi Hesaplama
try:
    bist_veri = yf.Ticker("XU100.IS").history(period="6mo")
    bist_getiri = ((bist_veri['Close'].iloc[-1] - bist_veri['Close'].iloc[0]) / bist_veri['Close'].iloc[0]) * 100
except Exception:
    bist_getiri = 0.0

fark = toplamKarZararYuzde - bist_getiri

# 4'lü Özet KPI Kartları
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(label="Toplam Yatırılan Maliyet", value=f"{toplamMaliyet:,.2f} TL")

with col2:
    st.metric(label="Güncel Portföy Değeri", value=f"{toplamGuncelDeger:,.2f} TL")

with col3:
    st.metric(
        label="Toplam Kâr/Zarar",
        value=f"{toplamKarZararTL:,.2f} TL",
        delta=f"%{toplamKarZararYuzde:.2f}"
    )

with col4:
    st.metric(
        label="BIST 100 vs Portföy (6 Ay)",
        value=f"BIST: %{bist_getiri:.1f}",
        delta=f"%{fark:.1f} Fark"
    )

st.divider()
st.subheader("📋 Portföy Detayları")
st.dataframe(tabloVerisi, use_container_width=True)

st.divider()
st.subheader("🥧 Portföy Varlık Dağılımı")

# Modern Donut Grafiği
fig_pasta = px.pie(
    names=pastaEtiketler,
    values=pastaDegerler,
    hole=0.45,
    color_discrete_sequence=px.colors.qualitative.Prism
)
fig_pasta.update_traces(
    textposition='inside', 
    textinfo='percent+label',
    hovertemplate="<b>%{label}</b><br>Toplam Değer: %{value:,.2f} TL<br>Portföy Payı: %{percent}<extra></extra>"
)
fig_pasta.update_layout(margin=dict(t=10, b=10, l=10, r=10), height=380)
st.plotly_chart(fig_pasta, use_container_width=True)

# Şampiyon ve Düşen Hisse Kutuları
if enIyiHisse and enKotuHisse:
    col_iyi, col_kotu = st.columns(2)
    with col_iyi:
        st.success(f"🏆 **En Çok Kazandıran:** {enIyiHisse} (+%{enYuksekKar:.2f})")
    with col_kotu:
        st.error(f"🔻 **En Çok Kaybettiren:** {enKotuHisse} (%{enDusukKar:.2f})")

st.divider()
st.subheader("📊 Hisse Teknik Analiz Grafiği")

secilen = st.selectbox("İncelemek istediğiniz hisseyi seçin:", list(portfoy.keys()))

secilenHisse = yf.Ticker(secilen)
gecmisSecilen = secilenHisse.history(period="6mo")
secilenMaliyet = portfoy[secilen]["maliyet"]

gecmisSecilen['SMA20'] = gecmisSecilen['Close'].rolling(window=20).mean()
gecmisSecilen['SMA50'] = gecmisSecilen['Close'].rolling(window=50).mean()

# 14 Günlük RSI Hesabı
fark_fiyat = gecmisSecilen['Close'].diff()
kazanc = fark_fiyat.where(fark_fiyat > 0, 0.0).rolling(window=14).mean()
kayip = (-fark_fiyat.where(fark_fiyat < 0, 0.0)).rolling(window=14).mean()
rs = kazanc / kayip
gecmisSecilen['RSI'] = 100 - (100 / (1 + rs))

guncel_rsi = gecmisSecilen['RSI'].iloc[-1]

# İnteraktif Finans Grafiği (SMA20 + SMA50 + Maliyet)
fig_trend = go.Figure()

fig_trend.add_trace(go.Scatter(
    x=gecmisSecilen.index, 
    y=gecmisSecilen['Close'], 
    name='Kapanış (TL)',
    line=dict(color='#00b4d8', width=2.5)
))

fig_trend.add_trace(go.Scatter(
    x=gecmisSecilen.index, 
    y=gecmisSecilen['SMA20'], 
    name='SMA 20 (Kısa Vade)',
    line=dict(color='#f77f00', width=1.5)
))

fig_trend.add_trace(go.Scatter(
    x=gecmisSecilen.index, 
    y=gecmisSecilen['SMA50'], 
    name='SMA 50 (Orta Vade)',
    line=dict(color='#9d4edd', width=1.5)
))

fig_trend.add_hline(
    y=secilenMaliyet, 
    line_dash="dash", 
    line_color="#e63946", 
    annotation_text=f"Maliyetim ({secilenMaliyet:.2f} TL)",
    annotation_position="top left"
)

fig_trend.update_layout(
    title=f"📈 {secilen} - Canlı & İnteraktif Trend Grafiği",
    xaxis_title="Tarih",
    yaxis_title="Fiyat (TL)",
    hovermode="x unified",
    height=450,
    margin=dict(t=40, b=20, l=20, r=20)
)
st.plotly_chart(fig_trend, use_container_width=True)

# RSI Durum Rozeti
if guncel_rsi > 70:
    st.warning(f"⚠️ **RSI Değeri: {guncel_rsi:.1f}** — Aşırı Alım Bölgesi (Hisse şişmiş, dikkatli ol)")
elif guncel_rsi < 30:
    st.success(f"💎 **RSI Değeri: {guncel_rsi:.1f}** — Aşırı Satım Bölgesi (Hisse dipte, alım fırsatı olabilir)")
else:
    st.info(f"⚖️ **RSI Değeri: {guncel_rsi:.1f}** — Nötr Bölge")

# İnteraktif RSI Grafiği
fig_rsi = go.Figure()
fig_rsi.add_trace(go.Scatter(x=gecmisSecilen.index, y=gecmisSecilen['RSI'], name='RSI (14)', line=dict(color='#a855f7', width=2)))
fig_rsi.add_hline(y=70, line_dash="dash", line_color="#ef4444", annotation_text="Aşırı Alım (70)")
fig_rsi.add_hline(y=30, line_dash="dash", line_color="#22c55e", annotation_text="Aşırı Satım (30)")
fig_rsi.update_layout(title="RSI (Göreceli Güç Endeksi) - Son 6 Ay", yaxis_range=[0, 100], height=250, margin=dict(t=30, b=20, l=20, r=20))
st.plotly_chart(fig_rsi, use_container_width=True)

st.divider()
st.subheader("🤖 Yapay Zeka Portföy Analisti (Google Gemini)")
st.write("Büyük dil modeli portföyünüzün risk dengesini ve seçili hissenizi canlı analiz etsin.")

if st.button("🧠 Portföyümü ve Hisselerimi Yorumla"):
    if not gemini_key:
        st.warning("⚠️ Lütfen sol menüden ücretsiz Gemini API anahtarınızı girin! (aistudio.google.com adresinden 10 saniyede alabilirsiniz)")
    else:
        with st.spinner("🤖 Gemini portföyünüzü ve teknik indikatörleri inceliyor..."):
            try:
                from google import genai
                client = genai.Client(api_key=gemini_key)
                
                prompt = f"""
Sen Borsa İstanbul (BIST) konusunda uzman kıdemli bir portföy yöneticisi ve teknik analistsin.
Aşağıda yatırımcının canlı portföy ve piyasa verileri yer alıyor:

- Yatırımcı: {user.get('ad_soyad', 'Yatırımcı')}
- Toplam Portföy Değeri: {toplamGuncelDeger:.2f} TL
- Toplam Maliyet: {toplamMaliyet:.2f} TL
- Toplam Net Kâr/Zarar: {toplamKarZararTL:.2f} TL (%{toplamKarZararYuzde:.2f})
- BIST 100 Karşılaştırması: Portföy BIST 100 endeksine göre %{fark:.1f} fark yaptı.
- Portföydeki Hisseler: {list(portfoy.keys())}
- En Çok Kazandıran: {enIyiHisse} (+%{enYuksekKar:.2f})
- En Çok Kaybettiren: {enKotuHisse} (%{enDusukKar:.2f})

İncelenen Seçili Hisse: {secilen}
- Güncel Fiyat: {gecmisSecilen['Close'].iloc[-1]:.2f} TL (Maliyet: {secilenMaliyet:.2f} TL)
- 14 Günlük RSI: {guncel_rsi:.1f}
- SMA 20 (Kısa Vade Trend): {gecmisSecilen['SMA20'].iloc[-1]:.2f} TL
- SMA 50 (Orta Vade Trend): {gecmisSecilen['SMA50'].iloc[-1]:.2f} TL

Lütfen şu 3 başlık altında net, profesyonel, samimi ve Türkçe bir analiz sun:
1. 📊 **Portföy Sağlık & Risk Değerlendirmesi:** (Çeşitlendirme, kâr/zarar dengesi ve BIST100'e göre durumu)
2. 🔍 **{secilen} Teknik Analiz Yorumu:** (Fiyatın SMA20 ve SMA50'ye göre konumu, RSI ne söylüyor?)
3. 💡 **Stratejik Öneriler:** (Kısa ve orta vadede nelere dikkat edilmeli?)

(Yatırım tavsiyesi olmadığını belirten kısa bir not ekle).
"""
                # Hesaba tanımlı uygun modelleri dinamik olarak alıyoruz
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