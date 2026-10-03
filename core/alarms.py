import streamlit as st
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from services.market_data import varlik_sinifi_belirle

# --- AKILLI ALARM & BİLDİRİM RADARI MOTORU (SOLID - SRP) ---

def denetle_portfoy_alarmlari(
    portfoy: dict,
    portfoy_fiyatlari: dict,
    kullanici_hedefleri: dict,
    rsi_degerleri: dict = None,
    usd_kuru: float = 34.50
) -> list:
    """
    Portföydeki varlıkların kâr alma (Take-Profit), zarar kes (Stop-Loss) ve
    14 günlük RSI dip (aşırı satım) seviyelerini denetleyerek aktif alarmları döndürür.
    """
    if not portfoy or not portfoy_fiyatlari:
        return []
        
    aktif_alarmlar = []
    rsi_degerleri = rsi_degerleri or {}
    
    for sembol, bilgi in portfoy.items():
        if sembol not in portfoy_fiyatlari:
            continue
            
        fiyat_tl, _ = portfoy_fiyatlari[sembol]
        maliyet = float(bilgi.get("maliyet", 0.0))
        _, yerel_para, _ = varlik_sinifi_belirle(sembol)
        yerel_fiyat = (fiyat_tl / usd_kuru) if yerel_para == "USD" and usd_kuru > 0 else fiyat_tl
        
        hedef_bilgi = kullanici_hedefleri.get(sembol, {}) if kullanici_hedefleri else {}
        hedef_fiyat = hedef_bilgi.get("hedef") or hedef_bilgi.get("hedef_fiyat")
        stop_loss = hedef_bilgi.get("stop") or hedef_bilgi.get("stop_loss")
        
        # 1. Kâr Alma (Take-Profit) Denetimi
        if hedef_fiyat and hedef_fiyat > 0:
            if yerel_fiyat >= hedef_fiyat:
                aktif_alarmlar.append({
                    "sembol": sembol,
                    "tip": "HEDEF_ULASILDI",
                    "etiket": "Kâr Hedefine Ulaşıldı",
                    "mesaj": f"{sembol} belirlediğiniz {hedef_fiyat:,.2f} {yerel_para} kâr alma hedefine ulaştı (Piyasa: {yerel_fiyat:,.2f} {yerel_para}).",
                    "seviye": "pozitif",
                    "fiyat": yerel_fiyat,
                    "hedef": hedef_fiyat,
                    "para": yerel_para,
                    "alarm_id": f"{sembol}_HEDEF"
                })
            elif (hedef_fiyat - yerel_fiyat) / hedef_fiyat <= 0.03 and yerel_fiyat < hedef_fiyat:
                yaklasma_yuzde = ((hedef_fiyat - yerel_fiyat) / hedef_fiyat) * 100.0
                aktif_alarmlar.append({
                    "sembol": sembol,
                    "tip": "HEDEF_YAKIN",
                    "etiket": "Kâr Hedefine Yaklaşıyor",
                    "mesaj": f"{sembol} kâr alma hedefine %{yaklasma_yuzde:.1f} yaklaştı (Piyasa: {yerel_fiyat:,.2f} {yerel_para} / Hedef: {hedef_fiyat:,.2f} {yerel_para}).",
                    "seviye": "pozitif",
                    "fiyat": yerel_fiyat,
                    "hedef": hedef_fiyat,
                    "para": yerel_para,
                    "alarm_id": f"{sembol}_HEDEF_YAKIN"
                })

        # 2. Zarar Durdur (Stop-Loss) Denetimi
        if stop_loss and stop_loss > 0:
            if yerel_fiyat <= stop_loss:
                aktif_alarmlar.append({
                    "sembol": sembol,
                    "tip": "STOP_LOSS",
                    "etiket": "Stop-Loss Seviyesi Tetiklendi",
                    "mesaj": f"{sembol} belirlediğiniz {stop_loss:,.2f} {yerel_para} zarar kes seviyesine geriledi (Piyasa: {yerel_fiyat:,.2f} {yerel_para}).",
                    "seviye": "risk",
                    "fiyat": yerel_fiyat,
                    "hedef": stop_loss,
                    "para": yerel_para,
                    "alarm_id": f"{sembol}_STOP_LOSS"
                })
            elif (yerel_fiyat - stop_loss) / stop_loss <= 0.03 and yerel_fiyat > stop_loss:
                risk_yuzde = ((yerel_fiyat - stop_loss) / stop_loss) * 100.0
                aktif_alarmlar.append({
                    "sembol": sembol,
                    "tip": "STOP_YAKIN",
                    "etiket": "Stop Seviyesine Yakın",
                    "mesaj": f"{sembol} zarar kes seviyesine %{risk_yuzde:.1f} yaklaştı (Piyasa: {yerel_fiyat:,.2f} {yerel_para} / Stop: {stop_loss:,.2f} {yerel_para}).",
                    "seviye": "risk",
                    "fiyat": yerel_fiyat,
                    "hedef": stop_loss,
                    "para": yerel_para,
                    "alarm_id": f"{sembol}_STOP_YAKIN"
                })

        # 3. RSI < 30 Dip Fırsatı Denetimi
        rsi_val = rsi_degerleri.get(sembol)
        if rsi_val and rsi_val < 30.0:
            aktif_alarmlar.append({
                "sembol": sembol,
                "tip": "RSI_DIP",
                "etiket": "RSI Dip Alım Fırsatı",
                "mesaj": f"{sembol} 14 günlük RSI göstergesi {rsi_val:.1f} seviyesinde; aşırı satım ve dip alım fırsatı bölgesinde bulunuyor.",
                "seviye": "firsat",
                "fiyat": yerel_fiyat,
                "hedef": 30.0,
                "para": yerel_para,
                "alarm_id": f"{sembol}_RSI_DIP"
            })

    return aktif_alarmlar

def gonder_alarm_epostasi(alici_email: str, alarmlar: list) -> tuple:
    """
    Tetiklenen alarmları kurumsal ve minimalist bir e-posta formatında iletir.
    Streamlit secrets üzerinde SMTP ayarı yoksa güvenli simülasyon modunda çalışır.
    """
    if not alici_email or not alarmlar:
        return False, "Geçerli bir alıcı e-posta adresi veya aktif alarm bulunamadı."
        
    smtp_server = st.secrets.get("SMTP_SERVER", "")
    smtp_port = int(st.secrets.get("SMTP_PORT", 587))
    smtp_user = st.secrets.get("SMTP_USER", "")
    smtp_pass = st.secrets.get("SMTP_PASSWORD", "")
    
    alarm_kartlari_html = ""
    for a in alarmlar:
        renk = "#4ade80" if a["seviye"] == "pozitif" else ("#f87171" if a["seviye"] == "risk" else "#38bdf8")
        alarm_kartlari_html += f"""
        <div style="background: #111827; border-left: 4px solid {renk}; border-radius: 6px; padding: 12px 16px; margin-bottom: 12px;">
            <div style="font-size: 11px; text-transform: uppercase; letter-spacing: 0.05em; color: {renk}; font-weight: 600;">
                ● {a['etiket']} — {a['sembol']}
            </div>
            <div style="font-size: 14px; color: #f3f4f6; margin-top: 6px; line-height: 1.4;">
                {a['mesaj']}
            </div>
        </div>
        """
        
    govde_html = f"""
    <!DOCTYPE html>
    <html>
    <head><meta charset="utf-8"></head>
    <body style="background-color: #080b11; color: #e2e8f0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; padding: 24px;">
        <div style="max-width: 600px; margin: 0 auto; background: #0f172a; border: 1px solid #1e293b; border-radius: 12px; padding: 28px;">
            <div style="font-size: 12px; text-transform: uppercase; letter-spacing: 0.1em; color: #38bdf8; font-weight: 700; margin-bottom: 8px;">
                ✦ Global Servet Terminali
            </div>
            <h2 style="color: #f8fafc; font-size: 20px; font-weight: 600; margin-top: 0; margin-bottom: 16px;">
                Piyasa Alarmı & Kurumsal İstihbarat Raporu
            </h2>
            <p style="font-size: 13.5px; color: #94a3b8; line-height: 1.5; margin-bottom: 20px;">
                Portföyünüzde takip edilen varlıklarda stratejik seviyeler tetiklendi. Güncel piyasa durumu aşağıda özetlenmiştir:
            </p>
            {alarm_kartlari_html}
            <div style="margin-top: 28px; text-align: center;">
                <a href="https://bist-terminal.streamlit.app" style="background: #0284c7; color: #ffffff; text-decoration: none; padding: 12px 24px; border-radius: 8px; font-weight: 600; font-size: 13px; display: inline-block;">
                    Terminale Giriş Yap ve Pozisyonları Yönet ↗
                </a>
            </div>
            <div style="border-top: 1px solid #1e293b; margin-top: 28px; padding-top: 16px; font-size: 11px; color: #475569; text-align: center;">
                Bu bildirim Global Servet Terminali Akıllı Alarm Radarı tarafından otomatik iletilmiştir.
            </div>
        </div>
    </body>
    </html>
    """
    
    if smtp_server and smtp_user and smtp_pass:
        try:
            import smtplib
            from email.mime.text import MIMEText
            from email.mime.multipart import MIMEMultipart
            
            msg = MIMEMultipart("alternative")
            msg["Subject"] = f"Piyasa Alarmı: {len(alarmlar)} Varlık Seviyesi Tetiklendi"
            msg["From"] = smtp_user
            msg["To"] = alici_email
            msg.attach(MIMEText(govde_html, "html", "utf-8"))
            
            with smtplib.SMTP(smtp_server, smtp_port, timeout=8) as server:
                server.starttls()
                server.login(smtp_user, smtp_pass)
                server.sendmail(smtp_user, alici_email, msg.as_string())
                
            return True, f"Bildirim e-postası başarıyla iletildi: {alici_email}"
        except Exception as e:
            return False, f"E-posta gönderiminde hata: {e}"
    else:
        return True, f"Bildirim hazırlandı: {alici_email} (Canlı SMTP tanımlandığında otomatik gönderilir)."

