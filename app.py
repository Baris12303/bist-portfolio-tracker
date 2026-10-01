import streamlit as st
import yfinance as yf
import matplotlib.pyplot as plt

# Sayfa Başlığı ve Geniş Ekran Düzeni
st.set_page_config(page_title="BIST Portföyüm", page_icon="📈", layout="wide")

portfoy = {
    "AKBNK.IS": {"maliyet": 62.50, "adet": 150},
    "ASELS.IS": {"maliyet": 390.00, "adet": 40},
    "KCHOL.IS": {"maliyet": 195.00, "adet": 60},
    "MGROS.IS": {"maliyet": 480.00, "adet": 25},
    "SAHOL.IS": {"maliyet": 91.00, "adet": 100},
    "THYAO.IS": {"maliyet": 265.00, "adet": 50},
    "TUPRS.IS": {"maliyet": 360.00, "adet": 30},
}

toplamMaliyet = 0
toplamGuncelDeger = 0

enIyiHisse = ""
enYuksekKar = -999999 # Başlangıçta çok küçük bir sayı veriyoruz 

enKotuHisse = ""
enDusukKar = 999999   # Başlangıçta çok büyük bir sayı veriyoruz

tabloVerisi = []

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
    print(f"Hisse Adi: {sembol} | Maliyet: {maliyet} | Güncel Fiyat: {guncelFiyat:.2f} | Kar/Zarar: %{karDurumu:.2f}")
    if karDurumu > enYuksekKar:
        enYuksekKar = karDurumu
        enIyiHisse = sembol
    if karDurumu < enDusukKar:
        enDusukKar = karDurumu
        enKotuHisse = sembol


toplamKarZararTL = toplamGuncelDeger - toplamMaliyet
toplamKarZararYuzde =  ((toplamGuncelDeger - toplamMaliyet)/toplamMaliyet) * 100

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

# 3. Grafiği web için hazırlayıp çizdiriyoruz
fig, ax = plt.subplots(figsize=(10, 4))
ax.plot(gecmisSecilen.index, gecmisSecilen['Close'], label="Kapanış Fiyatı (TL)", color="blue")
ax.plot(gecmisSecilen.index, gecmisSecilen['SMA20'], label="SMA 20 (Kısa Vade)", color="orange")
ax.plot(gecmisSecilen.index, gecmisSecilen['SMA50'], label="SMA 50 (Orta Vade)", color="purple")
ax.axhline(y=secilenMaliyet, color="red", linestyle="--", label="Maliyetim")

ax.set_title(f"{secilen} - Son 6 Aylık Fiyat ve Trend Grafiği")
ax.set_xlabel("Tarih")
ax.set_ylabel("Fiyat (TL)")
ax.grid(True)
ax.legend()

# 4. Grafiği web sayfasına gömüyoruz
st.pyplot(fig)