import sqlite3

DB_NAME = "portfolio.db"

def veritabanini_baslat():
    """Eğer yoksa veritabanı dosyasını ve portfoy tablosunu oluşturur."""
    baglanti = sqlite3.connect(DB_NAME)
    imlec = baglanti.cursor()
    imlec.execute("""
        CREATE TABLE IF NOT EXISTS portfoy (
            sembol TEXT PRIMARY KEY,
            maliyet REAL,
            adet INTEGER
        )
    """)
    baglanti.commit()
    baglanti.close()

def portfoyu_getir():
    """Veritabanındaki tüm hisseleri bir sözlük (dict) olarak döndürür."""
    baglanti = sqlite3.connect(DB_NAME)
    imlec = baglanti.cursor()
    imlec.execute("SELECT sembol, maliyet, adet FROM portfoy")
    satirlar = imlec.fetchall()
    baglanti.close()
    
    # Koddaki mevcut yapımıza uygun dict formatına dönüştürüyoruz
    portfoy_dict = {}
    for sembol, maliyet, adet in satirlar:
        portfoy_dict[sembol] = {"maliyet": maliyet, "adet": adet}
    return portfoy_dict

def hisse_ekle_veya_guncelle(sembol, maliyet, adet):
    """Yeni bir hisse ekler ya da var olanın maliyet/adedini günceller."""
    baglanti = sqlite3.connect(DB_NAME)
    imlec = baglanti.cursor()
    imlec.execute("""
        INSERT OR REPLACE INTO portfoy (sembol, maliyet, adet)
        VALUES (?, ?, ?)
    """, (sembol, maliyet, adet))
    baglanti.commit()
    baglanti.close()

def hisse_sil(sembol):
    """Veritabanından seçilen hisseyi siler."""
    baglanti = sqlite3.connect(DB_NAME)
    imlec = baglanti.cursor()
    imlec.execute("DELETE FROM portfoy WHERE sembol = ?", (sembol,))
    baglanti.commit()
    baglanti.close()