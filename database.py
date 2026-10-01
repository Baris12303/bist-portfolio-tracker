import hashlib
import streamlit as st
from supabase import create_client, Client

def sifre_hashle(parola: str) -> str:
    """Kullanıcı parolasını güvenli SHA-256 algoritmasıyla özetler."""
    return hashlib.sha256(parola.encode('utf-8')).hexdigest()

def veritabanini_baslat():
    """Geriye dönük uyumluluk fonksiyonu."""
    pass

def get_supabase() -> Client:
    """Streamlit Secrets veya yerel ayarlardan Supabase istemcisini başlatır."""
    url = st.secrets.get("SUPABASE_URL", "")
    key = st.secrets.get("SUPABASE_KEY", "")
    if not url or not key:
        return None
    return create_client(url, key)

# --- KULLANICI İŞLEMLERİ (AUTH) ---

def kullanici_kayit_ol(email: str, parola: str, ad_soyad: str):
    """Yeni kullanıcı kaydeder ve başlangıç için örnek hisselerini yükler."""
    sb = get_supabase()
    if not sb:
        return False, "Veritabanı bağlantısı kurulamadı."
    
    email = email.lower().strip()
    
    # E-posta daha önce alınmış mı kontrol et
    mevcut = sb.table("kullanicilar").select("email").eq("email", email).execute()
    if mevcut.data:
        return False, "Bu e-posta adresi ile zaten bir hesap var!"
    
    # Kullanıcıyı ekle
    parola_hash = sifre_hashle(parola)
    sb.table("kullanicilar").insert({
        "email": email,
        "parola_hash": parola_hash,
        "ad_soyad": ad_soyad,
        "rol": "free"
    }).execute()
    
    # Kullanıcıya başlangıçta hazır örnek portföy ata
    kullanici_ornek_portfoy_yukle(email)
    return True, "Kayıt başarılı! Şimdi giriş yapabilirsiniz."

def kullanici_giris_yap(email: str, parola: str):
    """E-posta ve parola kontrolü yapar."""
    sb = get_supabase()
    if not sb:
        return False, "Veritabanı bağlantısı kurulamadı.", None
    
    email = email.lower().strip()
    parola_hash = sifre_hashle(parola)
    
    res = sb.table("kullanicilar").select("*").eq("email", email).eq("parola_hash", parola_hash).execute()
    if res.data:
        kullanici = res.data[0]
        return True, "Giriş başarılı!", {
            "email": kullanici["email"],
            "ad_soyad": kullanici["ad_soyad"],
            "rol": kullanici.get("rol", "free")
        }
    return False, "E-posta veya şifre hatalı!", None

# --- KİŞİYE ÖZEL PORTFÖY İŞLEMLERİ (CRUD) ---

def kullanici_portfoyu_getir(user_email: str) -> dict:
    """Belirtilen kullanıcının buluttaki hisselerini sözlük olarak getirir."""
    sb = get_supabase()
    if not sb or not user_email:
        return {}
    
    res = sb.table("portfoy").select("sembol, maliyet, adet").eq("user_email", user_email.lower().strip()).execute()
    portfoy_dict = {}
    for row in res.data:
        portfoy_dict[row["sembol"]] = {
            "maliyet": float(row["maliyet"]),
            "adet": int(row["adet"])
        }
    return portfoy_dict

def kullanici_hisse_ekle_guncelle(user_email: str, sembol: str, maliyet: float, adet: int):
    """Kullanıcının portföyüne hisse ekler veya günceller."""
    sb = get_supabase()
    if not sb or not user_email:
        return
    
    sb.table("portfoy").upsert({
        "user_email": user_email.lower().strip(),
        "sembol": sembol.upper().strip(),
        "maliyet": maliyet,
        "adet": adet
    }, on_conflict="user_email,sembol").execute()

def kullanici_hisse_sil(user_email: str, sembol: str):
    """Kullanıcının portföyünden seçili hisseyi siler."""
    sb = get_supabase()
    if not sb or not user_email:
        return
    
    sb.table("portfoy").delete().eq("user_email", user_email.lower().strip()).eq("sembol", sembol).execute()

def kullanici_portfoyu_sifirla(user_email: str):
    """Kullanıcının portföyündeki tüm hisseleri siler."""
    sb = get_supabase()
    if not sb or not user_email:
        return
    
    sb.table("portfoy").delete().eq("user_email", user_email.lower().strip()).execute()

def kullanici_ornek_portfoy_yukle(user_email: str):
    """Kullanıcıya örnek demo portföyü yükler."""
    demo = {
        "AKBNK.IS": (62.50, 150),
        "ASELS.IS": (390.00, 40),
        "KCHOL.IS": (195.00, 60),
        "MGROS.IS": (480.00, 25),
        "SAHOL.IS": (91.00, 100),
        "THYAO.IS": (265.00, 50),
        "TUPRS.IS": (360.00, 30),
    }
    for sembol, (maliyet, adet) in demo.items():
        kullanici_hisse_ekle_guncelle(user_email, sembol, maliyet, adet)