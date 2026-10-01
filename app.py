import streamlit as st
import yfinance as yf
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
import database
database.veritabanini_baslat()

# Sayfa Başlığı ve Geniş Ekran Düzeni
st.set_page_config(page_title="BIST Portföyüm", page_icon="📈", layout="wide")

portfoy = database.portfoyu_getir()

toplamMaliyet = 0
toplamGuncelDeger = 0

enIyiHisse = ""
enYuksekKar = -999999 # Başlangıçta çok küçük bir sayı veriyoruz 

enKotuHisse = ""
enDusukKar = 999999   # Başlangıçta çok büyük bir sayı veriyoruz

tabloVerisi = []
pastaEtiketler = []
pastaDegerler = []

# Son 6 aylık veriyi çekiyoruz (grafikte trendi görmek için)
for sembol, bilgi in portfoy.items():
    maliyet = bilgi["maliyet"]
    adet = bilgi["adet"]
    hisse = yf.Ticker(sembol)
    gecmis = hisse.history(period="6mo")
    guncelFiyat = gecmis['Close'].iloc[-1]
    toplamMaliyet += maliyet * adet
    toplamGuncelDeger += guncelFiyat * adet
    karDurumu = ((guncelFiyat - maliyet) / maliyet) * 100
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
    print(f"Hisse Adi: {sembol} | Maliyet: {maliyet} | Güncel Fiyat: {guncelFiyat:.2f} | Kar/Zarar: %{karDurumu:.2f}")
    if karDurumu > enYuksekKar:
        enYuksekKar = karDurumu
        enIyiHisse = sembol
    if karDurumu < enDusukKar:
        enDusukKar = karDurumu
        enKotuHisse = sembol


toplamKarZararTL = toplamGuncelDeger - toplamMaliyet
toplamKarZararYuzde =  ((toplamGuncelDeger - toplamMaliyet)/toplamMaliyet) * 100

# --- SOL MENÜ (PORTFÖY YÖNETİMİ) ---
st.sidebar.header("⚙️ Portföy Yönetimi")

# 1. Hisse Ekleme / Güncelleme Formu
with st.sidebar.form("hisse_ekle_formu"):
    st.subheader("➕ Hisse Ekle / Güncelle")
    yeni_sembol = st.text_input("Hisse Sembolü (örn: FROTO.IS)").upper().strip()
    yeni_maliyet = st.number_input("Alış Maliyeti (TL)", min_value=0.0, step=0.5)
    yeni_adet = st.number_input("Adet (Lot)", min_value=1, step=1)
    
    ekle_butonu = st.form_submit_button("Portföye Kaydet")
    if ekle_butonu and yeni_sembol:
        database.hisse_ekle_veya_guncelle(yeni_sembol, yeni_maliyet, yeni_adet)
        st.success(f"{yeni_sembol} başarıyla kaydedildi!")
        st.rerun() # Sayfayı anında yenileyip yeni veriyi gösterir

# 2. Hisse Silme Formu
if portfoy:
    st.sidebar.divider()
    st.sidebar.subheader("🗑️ Hisse Sil")
    silinecek_hisse = st.sidebar.selectbox("Silmek istediğiniz hisse:", list(portfoy.keys()))
    if st.sidebar.button("Hisseyi Portföyden Çıkar"):
        database.hisse_sil(silinecek_hisse)
        st.sidebar.warning(f"{silinecek_hisse} silindi!")
        st.rerun()

# Web Sayfasındaki Başlıklarımız
st.title("📈 BIST Portföy Takip & Analiz Paneli")
st.write("Canlı borsa verileriyle portföy kâr/zarar ve teknik analiz durumu.")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(label="Toplam Yatırılan Maliyet", value=f"{toplamMaliyet:.2f} TL")

with col2:
    st.metric(label="Güncel Portföy Değeri", value=f"{toplamGuncelDeger:.2f} TL")

with col3:
    st.metric(
        label="Toplam Kâr/Zarar",
        value=f"{toplamKarZararTL:.2f} TL",
        delta=f"%{toplamKarZararYuzde:.2f}"
    )

st.divider() # Araya şık bir çizgi çeker
st.subheader("📋 Portföy Detayları")
st.dataframe(tabloVerisi, use_container_width=True)

st.divider()
st.subheader("🥧 Portföy Varlık Dağılımı")

# Modern Donut (Ortası delik halka) Grafiği
fig_pasta = px.pie(
    names=pastaEtiketler,
    values=pastaDegerler,
    hole=0.45, # Ortasını delik yaparak modern SaaS görünümü verir
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
col_iyi, col_kotu = st.columns(2)
with col_iyi:
    st.success(f"🏆 **En Çok Kazandıran:** {enIyiHisse} (+%{enYuksekKar:.2f})")
with col_kotu:
    st.error(f"🔻 **En Çok Kaybettiren:** {enKotuHisse} (%{enDusukKar:.2f})")

st.divider()
st.subheader("📊 Hisse Teknik Analiz Grafiği")

# 1. Kullanıcıya açılır menüden hisse seçtiriyoruz
secilen = st.selectbox("İncelemek istediğiniz hisseyi seçin:",list(portfoy.keys()))

# 2. Seçilen hissenin verilerini ve göstergelerini hazırlıyoruz
secilenHisse = yf.Ticker(secilen)
gecmisSecilen = secilenHisse.history(period="6mo")
secilenMaliyet = portfoy[secilen]["maliyet"]

gecmisSecilen['SMA20'] = gecmisSecilen['Close'].rolling(window=20).mean()
gecmisSecilen['SMA50'] = gecmisSecilen['Close'].rolling(window=50).mean()

# Modern İnteraktif Finans Grafiği
fig_trend = go.Figure()

# 1. Kapanış Fiyatı
fig_trend.add_trace(go.Scatter(
    x=gecmisSecilen.index, 
    y=gecmisSecilen['Close'], 
    name='Kapanış (TL)',
    line=dict(color='#00b4d8', width=2.5)
))

# 2. SMA 20 (Trend)
fig_trend.add_trace(go.Scatter(
    x=gecmisSecilen.index, 
    y=gecmisSecilen['SMA20'], 
    name='SMA 20 (Kısa Vade)',
    line=dict(color='#f77f00', width=1.5)
))

# 3. SMA 50 (Orta Vade)
fig_trend.add_trace(go.Scatter(
    x=gecmisSecilen.index, 
    y=gecmisSecilen['SMA50'], 
    name='SMA 50 (Orta Vade)',
    line=dict(color='#9d4edd', width=1.5)
))

# 4. Kırmızı Kesik Maliyet Çizgisi
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
    hovermode="x unified", # Fareyi getirdiğin tarihteki tüm değerleri tek kutuda gösterir
    height=450,
    margin=dict(t=40, b=20, l=20, r=20)
)

st.plotly_chart(fig_trend, use_container_width=True)