import yfinance as yf
import matplotlib.pyplot as plt

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
    print(f"Hisse Adi: {sembol} | Maliyet: {maliyet} | Güncel Fiyat: {guncelFiyat:.2f} | Kar/Zarar: %{karDurumu:.2f}")
    if karDurumu > enYuksekKar:
        enYuksekKar = karDurumu
        enIyiHisse = sembol
    if karDurumu < enDusukKar:
        enDusukKar = karDurumu
        enKotuHisse = sembol


toplamKarZararTL = toplamGuncelDeger - toplamMaliyet
toplamKarZararYuzde =  ((toplamGuncelDeger - toplamMaliyet)/toplamMaliyet) * 100

print(f"En Çok Kazandıran Hisse: {enIyiHisse} (%{enYuksekKar:.2f})")
print(f"En Çok Kaybettiren Hisse: {enKotuHisse} (%{enDusukKar:.2f})")

print(f"Toplam kar/zarar (TL): {toplamKarZararTL:.2f}\nToplam kar/zarar (%): {toplamKarZararYuzde:.2f}")

secilen = input("\nGrafiğini görmek istediğiniz hisse (örn:THYAO.IS): ").upper().strip()
secilenHisse = yf.Ticker(secilen)
secilenMaliyet = portfoy[secilen]["maliyet"]
gecmisSecilenHisse = secilenHisse.history(period="6mo")

gecmisSecilenHisse['SMA20'] = gecmisSecilenHisse['Close'].rolling(window=20).mean()
gecmisSecilenHisse['SMA50'] = gecmisSecilenHisse['Close'].rolling(window=50).mean()

# --- GRAFİK ÇİZME ---
plt.figure(figsize=(10, 5)) # Pencere boyutu (genişlik: 10, yükseklik: 5)
plt.plot(gecmisSecilenHisse.index, gecmisSecilenHisse['Close'], label="Kapanış Fiyatı (TL)", color="blue")
plt.plot(gecmisSecilenHisse.index, gecmisSecilenHisse['SMA20'], color='orange', label='SMA 20 (Trend)')
plt.plot(gecmisSecilenHisse.index, gecmisSecilenHisse['SMA50'], color='purple', label='SMA 50 (Orta Vade)')
plt.axhline(y=secilenMaliyet, color='red', linestyle='--', label='Maliyetim')

plt.title(f"{secilen} - Son 6 Aylık Fiyat Grafiği")
plt.xlabel("Tarih")
plt.ylabel("Fiyat (TL)")
plt.grid(True) # Arkaya ızgara çizgileri ekler
plt.legend()   # Sağ üstteki etiket kutusunu gösterir


print("Grafik açılıyor...")
plt.show() # Pencereyi ekranda açar