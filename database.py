import hashlib
import streamlit as st
from supabase import create_client, Client

def sifre_hashle(parola: str) -> str:
    """Kullanıcı parolasını güvenli SHA-256 algoritmasıyla özetler."""
    return hashlib.sha256(parola.encode('utf-8')).hexdigest()

def veritabanini_baslat():
    """Geriye dönük uyumluluk fonksiyonu."""
    pass

@st.cache_resource(ttl=3600)
def get_supabase():
    """Streamlit Secrets veya yerel ayarlardan Supabase istemcisini baslatir (onbellekli)."""
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
    
    res = sb.table("portfoy").select("sembol, maliyet, adet, hedef, stop").eq("user_email", user_email.lower().strip()).execute()
    portfoy_dict = {}
    for row in res.data:
        portfoy_dict[row["sembol"]] = {
            "maliyet": float(row["maliyet"]),
            "adet": float(row["adet"]),
            "hedef": float(row.get("hedef") or 0.0),
            "stop": float(row.get("stop") or 0.0)
        }
    return portfoy_dict

def kullanici_hedef_guncelle(user_email: str, sembol: str, hedef: float, stop: float):
    """Kullanıcının portföyündeki bir varlığın hedef fiyat ve stop-loss değerini günceller."""
    sb = get_supabase()
    if not sb or not user_email:
        return
    sb.table("portfoy").update({
        "hedef": hedef,
        "stop": stop
    }).eq("user_email", user_email.lower().strip()).eq("sembol", sembol.upper().strip()).execute()

def kullanici_ayarlari_getir(user_email: str) -> dict:
    """Kullanıcının bildirim ayarlarını getirir."""
    sb = get_supabase()
    if not sb or not user_email:
        return {}
    res = sb.table("kullanicilar").select("bildirim_ayarlari").eq("email", user_email.lower().strip()).execute()
    if res.data and len(res.data) > 0 and res.data[0].get("bildirim_ayarlari"):
        return res.data[0]["bildirim_ayarlari"]
    return {}

def kullanici_ayarlari_guncelle(user_email: str, ayarlar: dict):
    """Kullanıcının bildirim ayarlarını günceller."""
    sb = get_supabase()
    if not sb or not user_email:
        return
    sb.table("kullanicilar").update({
        "bildirim_ayarlari": ayarlar
    }).eq("email", user_email.lower().strip()).execute()

def kullanici_hisse_ekle_guncelle(user_email: str, sembol: str, maliyet: float, adet: float):
    """Kullanıcının portföyüne hisse/varlık ekler veya günceller."""
    sb = get_supabase()
    if not sb or not user_email:
        return
    
    try:
        sb.table("portfoy").upsert({
            "user_email": user_email.lower().strip(),
            "sembol": sembol.upper().strip(),
            "maliyet": maliyet,
            "adet": adet
        }, on_conflict="user_email,sembol").execute()
    except Exception as e:
        # Veritabanında adet integer ise ve kesirli değer geldiyse güvenli fallback
        if "invalid input syntax for type integer" in str(e):
            sb.table("portfoy").upsert({
                "user_email": user_email.lower().strip(),
                "sembol": sembol.upper().strip(),
                "maliyet": maliyet,
                "adet": int(adet) if adet >= 1 else 1
            }, on_conflict="user_email,sembol").execute()
        else:
            raise e

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
    """Kullanıcıya örnek küresel karma demo portföyü yükler (BIST, ABD, Kripto, Altın)."""
    demo = {
        "THYAO.IS": (270.00, 50.0),
        "TUPRS.IS": (165.00, 100.0),
        "AKBNK.IS": (58.00, 300.0),
        "NVDA": (115.00, 12.0),
        "GRAM_ALTIN": (2900.00, 16.0),
        "BTC-USD": (62000.00, 0.02),
    }
    for sembol, (maliyet, adet) in demo.items():
        kullanici_hisse_ekle_guncelle(user_email, sembol, maliyet, adet)