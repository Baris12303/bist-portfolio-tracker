import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import database
from services.market_data import varlik_sinifi_belirle
from core.rebalancing import REBALANCE_STRATEJILERI, hesapla_portfoy_rebalancing
from core.alarms import denetle_portfoy_alarmlari

def render_tab_portfoy(portfoy, user, user_email, is_demo, usd_try, gemini_key):
    st.title("Kişisel Portföy & Servet Paneli")
    st.caption("Borsa İstanbul, Amerikan Borsaları, Kripto Varlıklar ve Emtia tek ekranda konsolide edilmiştir.")

    if not portfoy:
        st.info("Portföyünüzde henüz kayıtlı varlık bulunmamaktadır. Sol menüden varlık ekleyebilir veya 'Örnek Portföy' butonuna tıklayabilirsiniz.")
    else:
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
        portfoy_fiyatlari_tl = {}
        portfoy_rsi_degerleri = {}

        with st.spinner("Piyasa verileri konsolide ediliyor..."):
            for sembol, bilgi in portfoy.items():
                maliyet = float(bilgi["maliyet"])
                adet = float(bilgi["adet"])
                kategori, para, rozet = varlik_sinifi_belirle(sembol)
                
                gecmis = varlik_gecmisi_getir(sembol, period="6mo")
                if gecmis.empty:
                    continue
                    
                guncelFiyatYerel = float(gecmis['Close'].iloc[-1])
                
                if len(gecmis) >= 15:
                    try:
                        gecmis_sirali = gecmis.sort_index()
                        fark_fiyat = gecmis_sirali['Close'].diff()
                        kazanc = fark_fiyat.where(fark_fiyat > 0, 0.0).rolling(window=14).mean()
                        kayip = (-fark_fiyat.where(fark_fiyat < 0, 0.0)).rolling(window=14).mean()
                        rs = kazanc / kayip
                        rsi_seri = 100 - (100 / (1 + rs))
                        son_rsi = float(rsi_seri.iloc[-1])
                        if not np.isnan(son_rsi):
                            portfoy_rsi_degerleri[sembol] = son_rsi
                    except Exception:
                        pass
                
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
                    
                portfoy_fiyatlari_tl[sembol] = (guncelFiyatTL, para)
                varlikMaliyetToplami = maliyetTL * adet
                varlikGuncelToplami = guncelFiyatTL * adet
                
                toplamMaliyetTL += varlikMaliyetToplami
                toplamGuncelDegerTL += varlikGuncelToplami
                
                karDurumuYuzde = ((guncelFiyatYerel - maliyet) / maliyet) * 100 if maliyet > 0 else 0.0
                karDurumuTL = (guncelFiyatTL - maliyetTL) * adet
                
                tabloVerisi.append({
                    "Varlık": f"{rozet} {sembol}",
                    "Kategori": kategori,
                    "Miktar": adet,
                    "Maliyet": maliyetMetni,
                    "Piyasa Fiyatı": fiyatMetni,
                    "Toplam Değer": f"{varlikGuncelToplami:,.2f} TL",
                    "Net Kâr / Zarar": f"{karDurumuTL:+,.2f} TL",
                    "Getiri (%)": round(karDurumuYuzde, 2)
                })
                
                pastaEtiketler.append(f"{sembol}")
                pastaDegerler.append(varlikGuncelToplami)
                kategoriDegerler[kategori] = kategoriDegerler.get(kategori, 0.0) + varlikGuncelToplami
                
                if karDurumuYuzde > enYuksekKar:
                    enYuksekKar = karDurumuYuzde
                    enIyiVarlik = sembol
                if karDurumuYuzde < enDusukKar:
                    enDusukKar = karDurumuYuzde
                    enKotuVarlik = sembol

        toplamKarTL = toplamGuncelDegerTL - toplamMaliyetTL
        toplamKarYuzde = ((toplamGuncelDegerTL - toplamMaliyetTL) / toplamMaliyetTL) * 100 if toplamMaliyetTL > 0 else 0.0

        try:
            bist_veri = yf.Ticker("XU100.IS").history(period="6mo")
            bist_getiri = ((bist_veri['Close'].iloc[-1] - bist_veri['Close'].iloc[0]) / bist_veri['Close'].iloc[0]) * 100
        except Exception:
            bist_getiri = 0.0

        fark = toplamKarYuzde - bist_getiri

        # 4'lü Üst KPI Kartları
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric(label="Toplam Yatırılan Maliyet", value=f"{toplamMaliyetTL:,.2f} TL", delta=f"${toplamMaliyetTL / usd_try:,.2f} USD", delta_color="off")
        with col2:
            st.metric(label="Konsolide Portföy Değeri", value=f"{toplamGuncelDegerTL:,.2f} TL", delta=f"${toplamGuncelDegerTL / usd_try:,.2f} USD", delta_color="off")
        with col3:
            st.metric(label="Toplam Net Getiri", value=f"{toplamKarTL:+,.2f} TL", delta=f"{toplamKarYuzde:+.2f}%")
        with col4:
            st.metric(label="BIST 100 Karşılaştırması", value=f"Endeks: %{bist_getiri:.1f}", delta=f"{fark:+.1f}% Göreceli Fark")

        # --- MADDE 4 & 7: AKILLI ALARM & İSTİHBARAT RADARI ---
        aktif_alarmlar = denetle_portfoy_alarmlari(
            portfoy, 
            portfoy_fiyatlari_tl, 
            st.session_state.kullanici_hedefleri, 
            portfoy_rsi_degerleri, 
            usd_try
        )

        # E-posta Otomatik Gönderim (Stateful Throttling)
        if st.session_state.bildirim_ayarlari.get("eposta_bildirim_aktif", False) and aktif_alarmlar:
            hedef_eposta = st.session_state.bildirim_ayarlari.get("eposta_adresi") or user_email
            yeni_alarmlar = [a for a in aktif_alarmlar if a["alarm_id"] not in st.session_state.tetiklenen_alarmlar]
            if yeni_alarmlar and hedef_eposta:
                basarili, sonuc_msj = gonder_alarm_epostasi(hedef_eposta, yeni_alarmlar)
                if basarili:
                    for ya in yeni_alarmlar:
                        st.session_state.tetiklenen_alarmlar.add(ya["alarm_id"])
                    st.toast(f"✦ İstihbarat Raporu e-postanıza iletildi: {hedef_eposta}")

        # Site İçi Bildirim Hub'ı (Kullanıcı açtıysa)
        if st.session_state.bildirim_ayarlari.get("site_bildirim_aktif", True) and aktif_alarmlar:
            st.markdown(f"""
            <div style="background: rgba(15, 23, 42, 0.65); border: 1px solid rgba(56, 189, 248, 0.2); border-radius: 12px; padding: 14px 18px; margin: 16px 0;">
                <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 10px;">
                    <span style="font-size: 11.5px; font-weight: 700; color: #38bdf8; text-transform: uppercase; letter-spacing: 0.08em;">
                        ✦ Akıllı Alarm Radarı • {len(aktif_alarmlar)} Seviye Tetiklendi
                    </span>
                    <span style="font-size: 11px; color: #64748b;">
                        Hedef Kâr & Stop-Loss Radarı
                    </span>
                </div>
            """, unsafe_allow_html=True)
            
            sutun_sayisi = min(len(aktif_alarmlar), 3)
            cols_alr = st.columns(sutun_sayisi)
            for idx_a, alr in enumerate(aktif_alarmlar):
                target_col = cols_alr[idx_a % sutun_sayisi]
                with target_col:
                    renk = "#4ade80" if alr["seviye"] == "pozitif" else ("#f87171" if alr["seviye"] == "risk" else "#38bdf8")
                    bg_col = "rgba(34, 197, 94, 0.08)" if alr["seviye"] == "pozitif" else ("rgba(239, 68, 68, 0.08)" if alr["seviye"] == "risk" else "rgba(56, 189, 248, 0.08)")
                    bdr_col = "rgba(34, 197, 94, 0.25)" if alr["seviye"] == "pozitif" else ("rgba(239, 68, 68, 0.25)" if alr["seviye"] == "risk" else "rgba(56, 189, 248, 0.25)")
                    st.markdown(f"""
                    <div style="background: {bg_col}; border: 1px solid {bdr_col}; border-radius: 8px; padding: 10px 12px; margin-bottom: 6px;">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <span style="font-size: 11.5px; font-weight: 700; color: {renk};">● {alr['sembol']}</span>
                            <span style="font-size: 10.5px; color: #94a3b8;">{alr['etiket']}</span>
                        </div>
                        <div style="font-size: 12px; color: #f1f5f9; margin-top: 5px; line-height: 1.35;">
                            {alr['mesaj']}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
            st.markdown("</div>", unsafe_allow_html=True)

        st.divider()
        st.dataframe(tabloVerisi, use_container_width=True)

        st.divider()
        tab_pasta1, tab_pasta2, tab_temettu, tab_dengeleme = st.tabs([
            "Varlık Sınıfı Dağılımı", 
            "Pozisyon Bazında Dağılım", 
            "Temettü & Pasif Gelir Radarı",
            "Akıllı Portföy Dengeleme"
        ])
        
        luxury_colors = ['#38bdf8', '#10b981', '#f59e0b', '#a855f7', '#ec4899', '#64748b']
        
        with tab_pasta1:
            fig_kat = px.pie(names=list(kategoriDegerler.keys()), values=list(kategoriDegerler.values()), hole=0.55, color_discrete_sequence=luxury_colors)
            fig_kat.update_traces(textposition='inside', textinfo='percent+label', hovertemplate="<b>%{label}</b><br>Toplam: %{value:,.2f} TL<br>Pay: %{percent}<extra></extra>")
            fig_kat.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color='#94a3b8'), margin=dict(t=10, b=10, l=10, r=10), height=340)
            st.plotly_chart(fig_kat, use_container_width=True)

        with tab_pasta2:
            fig_pasta = px.pie(names=pastaEtiketler, values=pastaDegerler, hole=0.55, color_discrete_sequence=luxury_colors)
            fig_pasta.update_traces(textposition='inside', textinfo='percent+label', hovertemplate="<b>%{label}</b><br>Toplam: %{value:,.2f} TL<br>Pay: %{percent}<extra></extra>")
            fig_pasta.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color='#94a3b8'), margin=dict(t=10, b=10, l=10, r=10), height=340)
            st.plotly_chart(fig_pasta, use_container_width=True)

        with tab_temettu:
            st.markdown("##### Portföy Temettü & Pasif Gelir Projeksiyonu")
            temettu_satirlari = []
            toplam_yillik_temettu = 0.0

            for sembol, veri in portfoy.items():
                adet = float(veri.get("adet", 1.0))
                try:
                    fund = get_company_fundamentals(sembol)
                except Exception:
                    fund = {}
                div_rate = fund.get("dividendRate")
                div_yield = fund.get("dividendYield")
                
                if sembol in portfoy_fiyatlari_tl:
                    fiyat_tl, p_para = portfoy_fiyatlari_tl[sembol]
                else:
                    _, p_para, _ = varlik_sinifi_belirle(sembol)
                    fiyat_tl = float(veri.get("maliyet", 0.0)) * (usd_try if p_para == "USD" else 1.0)

                # Detay A: dividendRate varsa doğrudan hisse başına net nakit ile hesapla
                hisse_yillik = 0.0
                gosterim_verim = "—"
                if div_rate and not pd.isna(div_rate) and div_rate > 0:
                    rate_tl = div_rate * usd_try if p_para == "USD" else div_rate
                    hisse_yillik = adet * rate_tl
                    toplam_yillik_temettu += hisse_yillik
                    if div_yield and not pd.isna(div_yield) and div_yield > 0:
                        y_val = div_yield * 100 if div_yield < 1 else div_yield
                        gosterim_verim = f"%{y_val:.2f} ({div_rate:.2f} {p_para}/Lot)"
                    else:
                        gosterim_verim = f"{div_rate:.2f} {p_para}/Lot"
                elif div_yield and not pd.isna(div_yield) and div_yield > 0:
                    div_pct = (div_yield / 100) if div_yield > 1 else div_yield
                    hisse_yillik = (adet * fiyat_tl) * div_pct
                    toplam_yillik_temettu += hisse_yillik
                    gosterim_verim = f"%{div_pct * 100:.2f}"

                if hisse_yillik > 0:
                    temettu_satirlari.append({
                        "Varlık": sembol,
                        "Adet": f"{adet:,.2f}",
                        "Fiyat": f"{fiyat_tl:,.2f} TL",
                        "Temettü / Lot": gosterim_verim,
                        "Yıllık Tahmini Gelir": f"{hisse_yillik:,.2f} TL",
                        "_hisse_yillik_num": hisse_yillik,
                        "_fiyat_tl_num": fiyat_tl,
                        "_adet_num": adet
                    })

            col_t1, col_t2, col_t3 = st.columns(3)
            with col_t1:
                st.metric(
                    label="Yıllık Tahmini Pasif Gelir",
                    value=f"{toplam_yillik_temettu:,.2f} TL",
                    help="Portföyünüzdeki hisselerin net nakit dağıtım tutarlarına (dividendRate) göre yıllık nakit akışı tahmini."
                )
            with col_t2:
                aylik_nakit = toplam_yillik_temettu / 12
                st.metric(
                    label="Aylık Ortalama Nakit Akışı",
                    value=f"{aylik_nakit:,.2f} TL / Ay",
                    help="Yıllık temettü gelirinin 12 aya bölünmüş eşdeğer aylık pasif maaş karşılığı."
                )
            with col_t3:
                portfoy_verim = (toplam_yillik_temettu / toplamGuncelDegerTL * 100) if toplamGuncelDegerTL > 0 else 0.0
                st.metric(
                    label="Portföy Temettü Verimi",
                    value=f"%{portfoy_verim:.2f}",
                    help="Toplam konsolide portföy büyüklüğünüze oranla yıllık net temettü verimi."
                )

            if temettu_satirlari:
                df_goster = pd.DataFrame([{k: v for k, v in row.items() if not k.startswith('_')} for row in temettu_satirlari])
                st.dataframe(df_goster, use_container_width=True)
            else:
                st.info("Portföyünüzde şu an temettü dağıtan bir hisse senedi bulunmuyor veya çarpanları sıfır görünüyor.")

            # Detay B: Kullanıcı Hedefi + Sepet Dengesini Bozmadan Hedefe Ulaşma Reçetesi
            st.divider()
            st.markdown("###### Temettü Emekliliği Hedef Simülatörü")
            col_h1, col_h2 = st.columns([1.5, 2.5])
            with col_h1:
                hedef_aylik = st.number_input(
                    "Aylık Hedef Pasif Gelir (TL):",
                    min_value=1000.0,
                    max_value=1000000.0,
                    value=25000.0,
                    step=2500.0,
                    help="Hedeflediğiniz aylık ortalama net pasif temettü geliri."
                )
            with col_h2:
                ilerleme = min(aylik_nakit / hedef_aylik, 1.0) if hedef_aylik > 0 else 0.0
                st.write("")
                st.progress(ilerleme)
                st.caption(f"✦ **Hedef İlerlemesi:** {hedef_aylik:,.0f} TL/Ay Hedefinizin **%{ilerleme*100:.1f}** kadarı mevcut hisselerinizce karşılanıyor.")

            # Hedefe Ulaşma Matematiksel Reçetesi
            if aylik_nakit < hedef_aylik:
                aylik_acik = hedef_aylik - aylik_nakit
                yillik_acik = aylik_acik * 12

                recete_parcalari = []
                if temettu_satirlari and toplam_yillik_temettu > 0:
                    for row in temettu_satirlari:
                        pay = row["_hisse_yillik_num"] / toplam_yillik_temettu
                        hisseye_dusen_yillik = yillik_acik * pay
                        hisse_basina_yillik = row["_hisse_yillik_num"] / row["_adet_num"] if row["_adet_num"] > 0 else 0.0
                        if hisse_basina_yillik > 0:
                            gereken_ek_lot = int(np.ceil(hisseye_dusen_yillik / hisse_basina_yillik))
                            recete_parcalari.append(f"+{gereken_ek_lot:,} lot **{row['Varlık']}**")
                
                recete_str = ", ".join(recete_parcalari) if recete_parcalari else "portföyünüze temettü verimi yüksek hisseler eklenmesi"

                st.markdown(f"""
                <div style="background: rgba(255, 255, 255, 0.015); border: 1px solid rgba(255, 255, 255, 0.06); border-radius: 10px; padding: 12px 16px; margin-top: 10px;">
                    <div style="font-size: 11px; text-transform: uppercase; letter-spacing: 0.05em; font-weight: 600; color: #94a3b8;">✦ Sepet Dengeleme & Hedefe Ulaşma Reçetesi</div>
                    <div style="font-size: 12.5px; color: #cbd5e1; margin-top: 5px; line-height: 1.5;">
                        Aylık <b>{hedef_aylik:,.0f} TL</b> hedefe ulaşmak için yıllık <b>{yillik_acik:,.0f} TL</b> ek nakit akışı gerekiyor.
                        Mevcut hisse dağılım dengenizi koruyarak bu açığı kapatmak için portföyünüze yaklaşık: <b>{recete_str}</b> takviyesi yapılması önerilir.
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.success("Tebrikler! Mevcut portföyünüz belirlediğiniz aylık pasif gelir hedefini fazlasıyla karşılıyor.")

        with tab_dengeleme:
            st.markdown("##### Akıllı Portföy Dengeleme & Rebalance Robotu")
            st.caption("Piyasa dalgalanmalarının bozduğu varlık ağırlıklarını stratejik hedefinize geri döndürmek için otomatik al/sat reçetesi üretir.")

            # 1. Strateji ve Mod Seçimi
            col_strat1, col_strat2 = st.columns([1.5, 1.5])
            with col_strat1:
                secilen_strat_adi = st.selectbox(
                    "Stratejik Dağılım Modeli:",
                    list(REBALANCE_STRATEJILERI.keys()),
                    key="rebalance_strat_secim"
                )
                strat_bilgi = REBALANCE_STRATEJILERI[secilen_strat_adi]
                st.caption(f"✦ **Model Felsefesi:** {strat_bilgi['aciklama']}")

            with col_strat2:
                rebalance_mod = st.radio(
                    "Dengeleme Yaklaşımı:",
                    ["Kâr Satışı ile Dengeleme (Sıfır Nakit)", "Yeni Tasarruf Ekleme (Satışsız)"],
                    horizontal=True,
                    key="rebalance_mod_secim"
                )
                secilen_mod_kodu = "satisli" if "Sıfır Nakit" in rebalance_mod else "tasarruf"
                if secilen_mod_kodu == "satisli":
                    st.caption("✦ Hedefi aşan varlıklardan kâr satışı yapılır; elde edilen nakitle geride kalanlar alınır.")
                else:
                    st.caption("✦ Hiçbir varlık satılmaz; eklenen yeni tasarruf en geride kalan sınıflara paylaştırılır.")

            # Hedef Yüzdelerin Alınması
            hedef_oranlar = {}
            if secilen_strat_adi == "Özel Dağılım (Kişiselleştirilmiş)":
                st.markdown("###### Özel Hedef Yüzdelerinizi Belirleyin (Toplam %100 Olmalıdır):")
                c_oz1, c_oz2, c_oz3, c_oz4 = st.columns(4)
                with c_oz1:
                    h_bist = st.number_input("% Borsa İstanbul", min_value=0.0, max_value=100.0, value=25.0, step=5.0, key="h_bist_in")
                with c_oz2:
                    h_abd = st.number_input("% Amerikan Borsası", min_value=0.0, max_value=100.0, value=25.0, step=5.0, key="h_abd_in")
                with c_oz3:
                    h_altin = st.number_input("% Altın & Emtia", min_value=0.0, max_value=100.0, value=25.0, step=5.0, key="h_altin_in")
                with c_oz4:
                    h_kripto = st.number_input("% Kripto Varlık", min_value=0.0, max_value=100.0, value=25.0, step=5.0, key="h_kripto_in")
                
                toplam_hedef_yuzde = h_bist + h_abd + h_altin + h_kripto
                if abs(toplam_hedef_yuzde - 100.0) > 0.01:
                    st.warning(f"Hedef oranların toplamı %{toplam_hedef_yuzde:.0f}. Kusursuz dengeleme için toplam %100 olmalıdır.")
                hedef_oranlar = {
                    "BIST Hissesi": h_bist,
                    "ABD Borsası": h_abd,
                    "Emtia & Maden": h_altin,
                    "Kripto Varlık": h_kripto
                }
            else:
                hedef_oranlar = {
                    "BIST Hissesi": strat_bilgi["BIST Hissesi"],
                    "ABD Borsası": strat_bilgi["ABD Borsası"],
                    "Emtia & Maden": strat_bilgi["Emtia & Maden"],
                    "Kripto Varlık": strat_bilgi["Kripto Varlık"]
                }

            # Tasarruf Ekleme Miktarı (Mod B ise)
            ek_nakit_tl = 0.0
            if secilen_mod_kodu == "tasarruf":
                col_nakit1, col_nakit2 = st.columns([1.5, 2.5])
                with col_nakit1:
                    ek_nakit_tl = st.number_input(
                        "Portföye Eklenecek Yeni Tasarruf (TL):",
                        min_value=500.0,
                        max_value=10000000.0,
                        value=15000.0,
                        step=2500.0,
                        key="rebalance_ek_nakit_in"
                    )
                with col_nakit2:
                    st.write("")
                    st.info(f"✦ Bu ay eklenecek **{ek_nakit_tl:,.0f} TL**, portföyünüzün hedef dağılımına en uzak varlıklara otomatik paylaştırılacaktır.")

            # Matematiksel Motoru Çalıştır (SRP)
            sonuc = hesapla_portfoy_rebalancing(
                kategori_degerler=kategoriDegerler,
                toplam_deger_tl=toplamGuncelDegerTL,
                hedef_oranlar=hedef_oranlar,
                eklenecek_nakit_tl=ek_nakit_tl,
                mod=secilen_mod_kodu,
                portfoy=portfoy,
                portfoy_fiyatlari_tl=portfoy_fiyatlari_tl
            )

            st.divider()

            # 2. Sapma & Denge Radarı (4 Varlık Sınıfı Kıyas Kartları)
            st.markdown("###### Mevcut Ağırlık vs. Stratejik Hedef Radarı")
            c_rad1, c_rad2, c_rad3, c_rad4 = st.columns(4)
            sutunlar_radar = [c_rad1, c_rad2, c_rad3, c_rad4]

            for idx, sa in enumerate(sonuc["sinif_analizleri"]):
                col_r = sutunlar_radar[idx]
                with col_r:
                    kat_adi = sa["sinif"]
                    mev_pct = sa["mevcut_oran"]
                    hed_pct = sa["hedef_oran"]
                    sapma = sa["sapma_yuzde"]
                    durum = sa["durum"]

                    if durum == "Aşırı Ağırlık":
                        badge_bg = "rgba(239, 68, 68, 0.12)"
                        badge_color = "#f87171"
                        badge_border = "rgba(239, 68, 68, 0.25)"
                        durum_etiket = f"Aşırı Ağırlık (+%{sapma:.1f})"
                    elif durum == "Düşük Ağırlık":
                        badge_bg = "rgba(56, 189, 248, 0.12)"
                        badge_color = "#38bdf8"
                        badge_border = "rgba(56, 189, 248, 0.25)"
                        durum_etiket = f"Düşük Ağırlık (%{sapma:.1f})"
                    else:
                        badge_bg = "rgba(34, 197, 94, 0.12)"
                        badge_color = "#4ade80"
                        badge_border = "rgba(34, 197, 94, 0.25)"
                        durum_etiket = "Dengede"

                    st.markdown(f"""
                    <div style="background: rgba(255, 255, 255, 0.02); border: 1px solid rgba(255, 255, 255, 0.06); border-radius: 12px; padding: 14px 16px; margin-bottom: 8px;">
                        <div style="font-size: 11px; text-transform: uppercase; letter-spacing: 0.05em; font-weight: 600; color: #94a3b8; margin-bottom: 6px;">
                            {kat_adi}
                        </div>
                        <div style="display: flex; align-items: baseline; justify-content: space-between; margin-bottom: 8px;">
                            <span style="font-size: 20px; font-weight: 600; color: #f1f5f9;">%{mev_pct:.1f}</span>
                            <span style="font-size: 12px; color: #64748b;">Hedef: %{hed_pct:.1f}</span>
                        </div>
                        <div style="background: {badge_bg}; color: {badge_color}; border: 1px solid {badge_border}; font-size: 10.5px; font-weight: 600; padding: 3px 8px; border-radius: 12px; text-align: center;">
                            ● {durum_etiket}
                        </div>
                        <div style="font-size: 11px; color: #64748b; margin-top: 8px; text-align: center;">
                            Mevcut: {sa['mevcut_deger']:,.0f} TL
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

            # 3. Akıllı Alış / Satış Reçetesi
            st.divider()
            emirler = sonuc["recete_emirleri"]

            if not emirler:
                st.success("Tebrikler! Portföyünüz seçilen stratejik hedef dağılımıyla tam dengede. Herhangi bir al/sat işlemine gerek yok.")
            else:
                st.markdown("###### Dengeleme İçin Önerilen Lot ve İşlem Reçetesi")
                col_em1, col_em2 = st.columns(2)
                
                satis_emirleri = [e for e in emirler if e["islem"] == "SAT"]
                alis_emirleri = [e for e in emirler if e["islem"] == "AL"]

                with col_em1:
                    st.markdown("""
                    <div style="font-size: 12px; text-transform: uppercase; letter-spacing: 0.05em; font-weight: 600; color: #f87171; margin-bottom: 8px;">
                        ● Kâr Satış Emirleri (Nakit Yarat)
                    </div>
                    """, unsafe_allow_html=True)
                    if not satis_emirleri:
                        st.caption("Bu stratejide herhangi bir satış işlemi önerilmiyor.")
                    else:
                        for se in satis_emirleri:
                            st.markdown(f"""
                            <div style="background: rgba(239, 68, 68, 0.04); border: 1px solid rgba(239, 68, 68, 0.15); border-radius: 10px; padding: 10px 14px; margin-bottom: 8px; display: flex; justify-content: space-between; align-items: center;">
                                <div>
                                    <div style="font-size: 13.5px; font-weight: 600; color: #f1f5f9;">{se['varlik']}</div>
                                    <div style="font-size: 11px; color: #94a3b8;">{se['sinif']}</div>
                                </div>
                                <div style="text-align: right;">
                                    <div style="font-size: 14px; font-weight: 600; color: #f87171;">{se['lot_metin']}</div>
                                    <div style="font-size: 11px; color: #64748b;">≈ {se['tutar_tl']:,.0f} TL</div>
                                </div>
                            </div>
                            """, unsafe_allow_html=True)

                with col_em2:
                    st.markdown("""
                    <div style="font-size: 12px; text-transform: uppercase; letter-spacing: 0.05em; font-weight: 600; color: #4ade80; margin-bottom: 8px;">
                        ● Alım & Takviye Emirleri (Açığı Kapat)
                    </div>
                    """, unsafe_allow_html=True)
                    if not alis_emirleri:
                        st.caption("Bu stratejide herhangi bir ek alım işlemi gerekmiyor.")
                    else:
                        for ae in alis_emirleri:
                            st.markdown(f"""
                            <div style="background: rgba(34, 197, 94, 0.04); border: 1px solid rgba(34, 197, 94, 0.15); border-radius: 10px; padding: 10px 14px; margin-bottom: 8px; display: flex; justify-content: space-between; align-items: center;">
                                <div>
                                    <div style="font-size: 13.5px; font-weight: 600; color: #f1f5f9;">{ae['varlik']}</div>
                                    <div style="font-size: 11px; color: #94a3b8;">{ae['sinif']}</div>
                                </div>
                                <div style="text-align: right;">
                                    <div style="font-size: 14px; font-weight: 600; color: #4ade80;">{ae['lot_metin']}</div>
                                    <div style="font-size: 11px; color: #64748b;">≈ {ae['tutar_tl']:,.0f} TL</div>
                                </div>
                            </div>
                            """, unsafe_allow_html=True)

                ozet_metin = ""
                if secilen_mod_kodu == "satisli":
                    ozet_metin = f"Bu reçete uygulandığında yaklaşık <b>{sonuc['toplam_satis_tl']:,.0f} TL</b> nakit yaratılacak ve bu tutar eksik sınıflara dağıtılarak portföyünüz %100 hedef modeline kavuşacaktır."
                else:
                    ozet_metin = f"Eklediğiniz <b>{ek_nakit_tl:,.0f} TL</b> yeni tasarruf, mevcut varlıklarınız satılmadan doğrudan geride kalan sınıflara paylaştırılmıştır."

                st.markdown(f"""
                <div style="background: rgba(255, 255, 255, 0.015); border: 1px solid rgba(255, 255, 255, 0.06); border-radius: 10px; padding: 12px 16px; margin-top: 12px;">
                    <div style="font-size: 11px; text-transform: uppercase; letter-spacing: 0.05em; font-weight: 600; color: #38bdf8;">✦ Rebalance Sonuç Özeti</div>
                    <div style="font-size: 12.5px; color: #cbd5e1; margin-top: 4px; line-height: 1.5;">
                        {ozet_metin}
                    </div>
                </div>
                """, unsafe_allow_html=True)

        # Öne Çıkan Getiriler
        if enIyiVarlik and enKotuVarlik:
            col_iyi, col_kotu = st.columns(2)
            with col_iyi:
                st.caption(f"En Yüksek Performans: **{enIyiVarlik}** (%{enYuksekKar:+.2f})")
            with col_kotu:
                st.caption(f"En Düşük Performans: **{enKotuVarlik}** (%{enDusukKar:+.2f})")

        st.divider()
        st.subheader("Varlık Analizi & Fiyat Projeksiyonu")

        secilen = st.selectbox("Analiz Edilecek Portföy Varlığı:", list(portfoy.keys()), key="portfoy_secim")
        secilen_kat, secilen_para, secilen_rozet = varlik_sinifi_belirle(secilen)
        gecmisSecilen = varlik_gecmisi_getir(secilen, period="6mo")
        secilenMaliyet = float(portfoy[secilen]["maliyet"])

        if not gecmisSecilen.empty:
            gecmisSecilen = gecmisSecilen.sort_index()
            gecmisSecilen['SMA20'] = gecmisSecilen['Close'].rolling(window=20).mean()
            gecmisSecilen['SMA50'] = gecmisSecilen['Close'].rolling(window=50).mean()

            fark_fiyat = gecmisSecilen['Close'].diff()
            kazanc = fark_fiyat.where(fark_fiyat > 0, 0.0).rolling(window=14).mean()
            kayip = (-fark_fiyat.where(fark_fiyat < 0, 0.0)).rolling(window=14).mean()
            rs = kazanc / kayip
            gecmisSecilen['RSI'] = 100 - (100 / (1 + rs))
            guncel_rsi = float(gecmisSecilen['RSI'].iloc[-1])

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

            # 7 Günlük ML Regresyon Tahmini
            gunler = np.arange(len(gecmisSecilen))
            fiyatlar = gecmisSecilen['Close'].values
            p = np.polyfit(gunler, fiyatlar, deg=1)
            trend_modeli = np.poly1d(p)
            tahmin_gecmis = trend_modeli(gunler)
            std_hata = float(np.std(fiyatlar - tahmin_gecmis))

            son_tarih = gecmisSecilen.index[-1]
            fut_indices = np.arange(len(gecmisSecilen) - 1, len(gecmisSecilen) + 7)
            fut_prices = trend_modeli(fut_indices)
            fut_dates = [son_tarih] + list(pd.date_range(start=son_tarih + pd.Timedelta(days=1), periods=7, freq='D'))

            tahmin_7gun = float(fut_prices[-1])
            guncel_son_fiyat = float(fiyatlar[-1])
            tahmin_fark_yuzde = ((tahmin_7gun - guncel_son_fiyat) / guncel_son_fiyat) * 100
            gunluk_egim = float(p[0])

            # Hedef ve Stop-Loss Seviyeleri (Madde 4)
            hedef_bilgi = st.session_state.kullanici_hedefleri.get(secilen, {})
            hedef_fiyat = float(hedef_bilgi.get("hedef", 0.0) or 0.0)
            stop_loss = float(hedef_bilgi.get("stop", 0.0) or 0.0)

            # İnteraktif Trend Grafiği
            fig_trend = go.Figure()
            fig_trend.add_trace(go.Scatter(x=gecmisSecilen.index, y=gecmisSecilen['Close'], name=f'Kapanış ({secilen_para})', line=dict(color='#38bdf8', width=2.5)))
            fig_trend.add_trace(go.Scatter(x=gecmisSecilen.index, y=gecmisSecilen['SMA20'], name='SMA 20', line=dict(color='#fbbf24', width=1.5)))
            fig_trend.add_trace(go.Scatter(x=gecmisSecilen.index, y=gecmisSecilen['SMA50'], name='SMA 50', line=dict(color='#a855f7', width=1.5)))
            fig_trend.add_hline(y=secilenMaliyet, line_dash="dash", line_color="#f43f5e", annotation_text=f"Maliyet ({secilenMaliyet:.2f} {secilen_para})", annotation_position="top left")

            if hedef_fiyat > 0:
                fig_trend.add_hline(
                    y=hedef_fiyat, 
                    line_dash="dot", 
                    line_color="#4ade80", 
                    annotation_text=f"Kâr Hedefi ({hedef_fiyat:,.2f} {secilen_para})", 
                    annotation_position="top right"
                )

            if stop_loss > 0:
                fig_trend.add_hline(
                    y=stop_loss, 
                    line_dash="dot", 
                    line_color="#f87171", 
                    annotation_text=f"Stop-Loss ({stop_loss:,.2f} {secilen_para})", 
                    annotation_position="bottom right"
                )

            fig_trend.add_trace(go.Scatter(x=fut_dates, y=fut_prices, name='7 Günlük Projeksiyon', mode='lines', line=dict(color='#c084fc', width=2.5, dash='dash')))
            fig_trend.add_trace(go.Scatter(x=fut_dates, y=fut_prices + std_hata, name='Tahmin Üst Sınır', mode='lines', line=dict(color='rgba(0,0,0,0)', width=0), showlegend=False, hoverinfo='skip'))
            fig_trend.add_trace(go.Scatter(x=fut_dates, y=fut_prices - std_hata, name='Güven Aralığı', mode='lines', fill='tonexty', fillcolor='rgba(192, 132, 252, 0.12)', line=dict(color='rgba(0,0,0,0)', width=0), hoverinfo='skip'))

            fig_trend.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#94a3b8'),
                xaxis=dict(gridcolor='rgba(255,255,255,0.04)', zerolinecolor='rgba(255,255,255,0.05)'),
                yaxis=dict(gridcolor='rgba(255,255,255,0.04)', zerolinecolor='rgba(255,255,255,0.05)'),
                title=f"{secilen} — Fiyat Trendi ve 7 Günlük Model Projeksiyonu",
                xaxis_title="Tarih",
                yaxis_title=f"Fiyat ({secilen_para})",
                hovermode="x unified",
                height=450,
                margin=dict(t=40, b=20, l=20, r=20)
            )
            st.plotly_chart(fig_trend, use_container_width=True)

            # Akakçe/Cimri usulü Projeksiyon Kartları
            col_ml1, col_ml2, col_ml3 = st.columns(3)
            with col_ml1:
                st.metric(label="7 Günlük Model Hedefi", value=f"{tahmin_7gun:,.2f} {secilen_para}", delta=f"{tahmin_fark_yuzde:+.2f}%")
            with col_ml2:
                st.metric(label="Model Güven Aralığı", value=f"±{std_hata:.2f} {secilen_para}")
            with col_ml3:
                egim_yorum = "Pozitif İvme" if gunluk_egim > 0 else "Negatif İvme"
                st.metric(label="Günlük Trend Eğimi", value=f"{gunluk_egim:+.2f} {secilen_para}/Gün", delta=egim_yorum)

            # Minimalist Durum Rozetleri
            c_ind1, c_ind2, c_ind3 = st.columns(3)
            with c_ind1:
                if guncel_rsi > 70:
                    st.caption(f"● **RSI {guncel_rsi:.1f}** — Aşırı Alım Bölgesi")
                elif guncel_rsi < 30:
                    st.caption(f"● **RSI {guncel_rsi:.1f}** — Aşırı Satım (Fırsat Bölgesi)")
                else:
                    st.caption(f"● **RSI {guncel_rsi:.1f}** — Nötr Denge")
            with c_ind2:
                if macd_al:
                    st.caption(f"● **MACD {guncel_macd:.2f}** — Pozitif İvme (Alıcı Üstünlüğü)")
                else:
                    st.caption(f"● **MACD {guncel_macd:.2f}** — Negatif İvme (Satıcı Baskısı)")
            with c_ind3:
                if golden_cross:
                    st.caption("● **Trend:** SMA 20 > SMA 50 (Yükseliş Trendi)")
                else:
                    st.caption("● **Trend:** SMA 20 < SMA 50 (Düşüş Eğilimi)")

            # --- HEDEF FİYAT & STOP-LOSS RADARI (MADDE 4) ---
            st.markdown("##### Hedef Fiyat & Stop-Loss Radarı")
            
            col_pan1, col_pan2 = st.columns([1.2, 1])
            with col_pan1:
                with st.form(f"hedef_form_{secilen}"):
                    st.markdown(f"<span style='font-size: 12px; color: #94a3b8;'>{secilen} için kâr alma ve risk seviyelerini tanımlayın:</span>", unsafe_allow_html=True)
                    col_inp1, col_inp2 = st.columns(2)
                    with col_inp1:
                        yeni_hedef = st.number_input(
                            f"Kâr Hedefi ({secilen_para})",
                            min_value=0.0,
                            value=float(hedef_fiyat),
                            step=1.0 if guncel_son_fiyat > 50 else 0.1,
                            format="%.2f",
                            help="Fiyat bu seviyeye ulaştığında kâr alma alarmı tetiklenir."
                        )
                    with col_inp2:
                        yeni_stop = st.number_input(
                            f"Stop-Loss ({secilen_para})",
                            min_value=0.0,
                            value=float(stop_loss),
                            step=1.0 if guncel_son_fiyat > 50 else 0.1,
                            format="%.2f",
                            help="Fiyat bu seviyenin altına gerilediğinde sermaye koruma alarmı tetiklenir."
                        )
                    
                    kaydet_hedef = st.form_submit_button("Hedef Seviyeleri Güncelle", type="primary", use_container_width=True)
                    if kaydet_hedef:
                        st.session_state.kullanici_hedefleri[secilen] = {
                            "hedef": float(yeni_hedef),
                            "stop": float(yeni_stop)
                        }
                        if not is_demo:
                            database.kullanici_hedef_guncelle(user_email, secilen, float(yeni_hedef), float(yeni_stop))
                        
                        # Tetiklenmiş bildirim hafızasını bu varlık için yenile
                        st.session_state.tetiklenen_alarmlar.discard(f"{secilen}_HEDEF")
                        st.session_state.tetiklenen_alarmlar.discard(f"{secilen}_HEDEF_YAKIN")
                        st.session_state.tetiklenen_alarmlar.discard(f"{secilen}_STOP_LOSS")
                        st.session_state.tetiklenen_alarmlar.discard(f"{secilen}_STOP_YAKIN")
                        st.success(f"{secilen} için seviyeler güncellendi.")
                        st.rerun()

                # Hızlı Yüzde Kısayol Butonları
                st.caption("Piyasa Fiyatına Göre Hızlı Hesaplama:")
                col_ks1, col_ks2, col_ks3, col_ks4, col_ks5 = st.columns(5)
                with col_ks1:
                    if st.button("+10%", key=f"btn_p10_{secilen}", use_container_width=True, help="Piyasa fiyatının %10 üstünü hedef olarak kaydeder."):
                        y_h = round(guncel_son_fiyat * 1.10, 2)
                        st.session_state.kullanici_hedefleri[secilen] = {"hedef": y_h, "stop": stop_loss}
                        if not is_demo: database.kullanici_hedef_guncelle(user_email, secilen, y_h, stop_loss)
                        st.rerun()
                with col_ks2:
                    if st.button("+20%", key=f"btn_p20_{secilen}", use_container_width=True, help="Piyasa fiyatının %20 üstünü hedef olarak kaydeder."):
                        y_h = round(guncel_son_fiyat * 1.20, 2)
                        st.session_state.kullanici_hedefleri[secilen] = {"hedef": y_h, "stop": stop_loss}
                        if not is_demo: database.kullanici_hedef_guncelle(user_email, secilen, y_h, stop_loss)
                        st.rerun()
                with col_ks3:
                    if st.button("+30%", key=f"btn_p30_{secilen}", use_container_width=True, help="Piyasa fiyatının %30 üstünü hedef olarak kaydeder."):
                        y_h = round(guncel_son_fiyat * 1.30, 2)
                        st.session_state.kullanici_hedefleri[secilen] = {"hedef": y_h, "stop": stop_loss}
                        if not is_demo: database.kullanici_hedef_guncelle(user_email, secilen, y_h, stop_loss)
                        st.rerun()
                with col_ks4:
                    if st.button("-5%", key=f"btn_m5_{secilen}", use_container_width=True, help="Piyasa fiyatının %5 altını stop-loss olarak kaydeder."):
                        y_s = round(guncel_son_fiyat * 0.95, 2)
                        st.session_state.kullanici_hedefleri[secilen] = {"hedef": hedef_fiyat, "stop": y_s}
                        if not is_demo: database.kullanici_hedef_guncelle(user_email, secilen, hedef_fiyat, y_s)
                        st.rerun()
                with col_ks5:
                    if st.button("-10%", key=f"btn_m10_{secilen}", use_container_width=True, help="Piyasa fiyatının %10 altını stop-loss olarak kaydeder."):
                        y_s = round(guncel_son_fiyat * 0.90, 2)
                        st.session_state.kullanici_hedefleri[secilen] = {"hedef": hedef_fiyat, "stop": y_s}
                        if not is_demo: database.kullanici_hedef_guncelle(user_email, secilen, hedef_fiyat, y_s)
                        st.rerun()

            with col_pan2:
                # Hedef Mesafe ve Güvenlik Marjı Radarı
                hedef_kalan_yuzde = ((hedef_fiyat - guncel_son_fiyat) / guncel_son_fiyat * 100) if (hedef_fiyat > 0 and guncel_son_fiyat > 0) else None
                stop_marj_yuzde = ((guncel_son_fiyat - stop_loss) / guncel_son_fiyat * 100) if (stop_loss > 0 and guncel_son_fiyat > 0) else None

                if hedef_fiyat > 0:
                    if guncel_son_fiyat >= hedef_fiyat:
                        durum_hedef = f"<span style='color: #4ade80; font-weight: 600;'>Kâr Hedefine Ulaşıldı (%{hedef_kalan_yuzde:+.1f})</span>"
                    else:
                        durum_hedef = f"Hedefe Kalan: <b style='color: #4ade80;'>%{hedef_kalan_yuzde:+.1f}</b> ({hedef_fiyat - guncel_son_fiyat:,.2f} {secilen_para})"
                else:
                    durum_hedef = "<span style='color: #64748b;'>Hedef seviyesi henüz tanımlanmadı.</span>"

                if stop_loss > 0:
                    if guncel_son_fiyat <= stop_loss:
                        durum_stop = f"<span style='color: #f87171; font-weight: 600;'>Stop-Loss Seviyesinde / Altında!</span>"
                    else:
                        durum_stop = f"Güvenlik Tamponu: <b style='color: #38bdf8;'>%{stop_marj_yuzde:.1f}</b> ({guncel_son_fiyat - stop_loss:,.2f} {secilen_para})"
                else:
                    durum_stop = "<span style='color: #64748b;'>Stop seviyesi henüz tanımlanmadı.</span>"

                st.markdown(f"""
                <div style="background: rgba(255, 255, 255, 0.02); border: 1px solid rgba(255, 255, 255, 0.07); border-radius: 10px; padding: 14px 16px; height: 100%;">
                    <div style="font-size: 11px; text-transform: uppercase; letter-spacing: 0.06em; font-weight: 600; color: #38bdf8; margin-bottom: 8px;">
                        ✦ Seviye Mesafe Radarı
                    </div>
                    <div style="font-size: 12.5px; color: #cbd5e1; margin-bottom: 12px; line-height: 1.45;">
                        <div style="margin-bottom: 4px;">● <b>Kâr Hedefi:</b> {f'{hedef_fiyat:,.2f} {secilen_para}' if hedef_fiyat > 0 else 'Tanımsız'}</div>
                        <div style="padding-left: 12px; font-size: 11.5px;">{durum_hedef}</div>
                    </div>
                    <div style="border-top: 1px solid rgba(255, 255, 255, 0.05); padding-top: 10px; font-size: 12.5px; color: #cbd5e1; line-height: 1.45;">
                        <div style="margin-bottom: 4px;">● <b>Stop-Loss:</b> {f'{stop_loss:,.2f} {secilen_para}' if stop_loss > 0 else 'Tanımsız'}</div>
                        <div style="padding-left: 12px; font-size: 11.5px;">{durum_stop}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)


            # Strateji Simülasyonu
            with st.expander(f"Strateji Simülasyonu: {secilen} MACD Kesişim Performansı"):
                try:
                    df_sim = gecmisSecilen.copy()
                    df_sim['Pozisyon'] = (df_sim['MACD'] > df_sim['Signal']).astype(int).shift(1)
                    df_sim['Gunluk_Getiri'] = df_sim['Close'].pct_change()
                    df_sim['Strateji_Getiri'] = df_sim['Gunluk_Getiri'] * df_sim['Pozisyon']
                    getiri_bh = ((1 + df_sim['Gunluk_Getiri'].dropna()).prod() - 1) * 100
                    getiri_strat = ((1 + df_sim['Strateji_Getiri'].dropna()).prod() - 1) * 100
                    col_sim1, col_sim2 = st.columns(2)
                    with col_sim1:
                        st.metric("Alıp Bekleme Getirisi", f"%{getiri_bh:.2f}")
                    with col_sim2:
                        fark_strat = getiri_strat - getiri_bh
                        st.metric("MACD Sinyal Stratejisi", f"%{getiri_strat:.2f}", delta=f"{fark_strat:+.2f}%")
                except Exception:
                    st.caption("Geçmiş veri hesaplanamadı.")

            # Seçilen Varlık Canlı Haberleri & AI Algı Radarı
            h_arama = secilen.replace(".IS", "").replace("-USD", "")
            portfoy_haberler = get_live_news(h_arama, count=2)
            if portfoy_haberler:
                st.markdown(f"###### {secilen} — Canlı Haber Akışı & Piyasa Algısı")
                if gemini_key:
                    h_tuple = tuple(h['headline'] for h in portfoy_haberler)
                    s_data = get_ai_news_sentiment(secilen, h_tuple, gemini_key)
                    if s_data:
                        sk = s_data.get("skor", "Nötr (Dengeli)")
                        yz = s_data.get("yuzde", 50)
                        oz = s_data.get("ozet", "")
                        zm = s_data.get("zaman", "")
                        
                        is_p = any(w in sk.lower() for w in ["boğa", "pozitif", "yükseliş"])
                        is_n = any(w in sk.lower() for w in ["ayı", "negatif", "düşüş"])
                        bg = "rgba(34, 197, 94, 0.12)" if is_p else ("rgba(239, 68, 68, 0.12)" if is_n else "rgba(234, 179, 8, 0.12)")
                        clr = "#4ade80" if is_p else ("#f87171" if is_n else "#facc15")
                        bdr = "rgba(34, 197, 94, 0.25)" if is_p else ("rgba(239, 68, 68, 0.25)" if is_n else "rgba(234, 179, 8, 0.25)")

                        st.markdown(f"""
                        <div style="background: rgba(255, 255, 255, 0.02); border: 1px solid rgba(255, 255, 255, 0.07); border-radius: 12px; padding: 12px 16px; margin-bottom: 12px;">
                            <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 6px;">
                                <span style="font-size: 11px; text-transform: uppercase; letter-spacing: 0.06em; font-weight: 600; color: #64748b;">✦ AI Algı Radarı</span>
                                <span style="background: {bg}; color: {clr}; border: 1px solid {bdr}; font-size: 11px; font-weight: 600; padding: 2px 8px; border-radius: 16px;">● {sk} (%{yz})</span>
                            </div>
                            <div style="font-size: 13px; color: #e2e8f0; line-height: 1.4; margin-bottom: 6px;">
                                {oz}
                            </div>
                            <div style="font-size: 10.5px; color: #475569;">
                                ✦ Yapay Zeka Analizi • Güncelleme: {zm} (2 Saatlik Kurumsal Döngü)
                            </div>
                        </div>
                        """, unsafe_allow_html=True)

                col_ph1, col_ph2 = st.columns(2)
                for i_h, hab_item in enumerate(portfoy_haberler):
                    col_target = col_ph1 if i_h == 0 else col_ph2
                    with col_target:
                        st.markdown(f"""
                        <div class="news-card" style="padding: 12px 14px; margin-bottom: 8px;">
                            <span style="color: #38bdf8; font-size: 10.5px; font-weight: 600;">{hab_item['source']}</span>
                            <span style="color: #475569; font-size: 10.5px; float: right;">{hab_item['date']}</span>
                            <div style="font-weight: 500; font-size: 13px; margin-top: 6px; color: #f1f5f9; line-height: 1.3;">{hab_item['headline']}</div>
                            <div style="margin-top: 8px;">
                                <a href="{hab_item['link']}" target="_blank" style="color: #64748b; font-size: 11px; text-decoration: none;">Haberi Oku ↗</a>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)

            # Gemini Analiz Kartı
            st.divider()
            st.subheader("Yapay Zeka Portföy Analisti")
            if st.button("Portföy ve Varlık Analizi Oluştur", key="gemini_portfoy_btn"):
                if not gemini_key:
                    st.warning("Sol menüden Gemini API anahtarınızı tanımlayın.")
                else:
                    with st.spinner("Analiz hazırlanıyor..."):
                        try:
                            from google import genai
                            client = genai.Client(api_key=gemini_key)
                            prompt = f"""
Sen Wall Street ve Borsa İstanbul konusunda uzman kıdemli bir küresel portföy yöneticisisin.
Yatırımcı: {user.get('ad_soyad')}
Toplam Servet: {toplamGuncelDegerTL:,.2f} TL (≈ ${toplamGuncelDegerTL / usd_try:,.2f} USD)
Toplam Maliyet: {toplamMaliyetTL:,.2f} TL
Net Getiri: {toplamKarTL:+,.2f} TL (%{toplamKarYuzde:+.2f})
Dolar Kuru: {usd_try:.2f} TL
Varlıklar: {list(portfoy.keys())}
Dağılım: {kategoriDegerler}
İncelenen Varlık: {secilen} ({secilen_kat}) | Fiyat: {guncel_son_fiyat:,.2f} {secilen_para} | 14G RSI: {guncel_rsi:.1f} | 7 Günlük Model Hedefi: {tahmin_7gun:,.2f} {secilen_para} (%{tahmin_fark_yuzde:+.2f})
Lütfen 3 başlık altında profesyonel, net ve Türkçe bir analiz sun:
1. Küresel Portföy Sağlık & Risk Değerlendirmesi
2. {secilen} Teknik & Projeksiyon Yorumu
3. Kısa & Orta Vade Stratejik Öneriler
(Yatırım tavsiyesi olmadığını belirt).
"""
                            modeller = ["gemini-2.0-flash", "gemini-1.5-flash", "gemini-1.5-pro"]
                            try:
                                live_models = [m.name for m in client.models.list() if "gemini" in m.name.lower() and "embed" not in m.name.lower()]
                                if live_models:
                                    modeller = live_models
                            except Exception:
                                pass
                            for m_name in modeller:
                                try:
                                    res = client.models.generate_content(model=m_name, contents=prompt)
                                    st.markdown(res.text)
                                    break
                                except Exception:
                                    continue
                        except Exception as e:
                            st.error(f"Hata: {e}")


# ------------------------------------------------------------------------------
# SEKME 2: PİYASA & ŞİRKET KEŞİF TERMİNALİ
