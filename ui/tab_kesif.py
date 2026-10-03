import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from services.market_data import varlik_sinifi_belirle, varlik_gecmisi_getir, get_live_news, get_company_fundamentals, get_ai_news_sentiment

def render_tab_kesif(is_demo, gemini_key):
    st.title("Piyasa & Şirket Keşif Terminali")
    st.caption("BIST, NASDAQ, Kripto ve Emtia varlıklarını temel çarpanları, bilançosu ve canlı haberleriyle inceleyin.")

    col_kat, col_hisse, col_arama = st.columns([1.2, 1.3, 1.5])
    with col_kat:
        kesif_kategori = st.selectbox(
            "Piyasa Grubu:",
            [
                "Borsa İstanbul (BIST)",
                "Amerikan Borsası (Wall Street)",
                "Kripto Varlıklar",
                "Emtia & Kıymetli Madenler"
            ],
            key="kesif_kategori_secim"
        )
        
    with col_hisse:
        if "BIST" in kesif_kategori:
            hizli_secenekler = ["THYAO.IS", "ASELS.IS", "FROTO.IS", "TUPRS.IS", "KCHOL.IS", "BIMAS.IS", "EREGL.IS", "SAHOL.IS", "SISE.IS", "GARAN.IS"]
        elif "Wall Street" in kesif_kategori:
            hizli_secenekler = ["NVDA", "AAPL", "TSLA", "MSFT", "AMZN", "GOOGL", "PLTR", "META", "AMD", "COIN"]
        elif "Kripto" in kesif_kategori:
            hizli_secenekler = ["BTC-USD", "ETH-USD", "SOL-USD", "AVAX-USD", "DOGE-USD", "XRP-USD"]
        else:
            hizli_secenekler = ["GRAM_ALTIN", "GC=F", "SI=F"]
            
        secilen_hizli = st.selectbox("Popüler Varlıklar:", hizli_secenekler, key="kesif_hizli_secim")

    with col_arama:
        serbest_arama = st.text_input("Doğrudan Sembol Girişi:", placeholder="Örn: THYAO, MGROS, NVDA, BTC-USD").upper().strip()

    aktif_kesif_sembol = serbest_arama if serbest_arama else secilen_hizli

    # Detay C: BIST (.IS), Kripto (-USD) ve Altın Sembol Otomasyonu
    if serbest_arama:
        s_temiz = serbest_arama.replace(" ", "").replace("_", "")
        if s_temiz in ["ALTIN", "GRAMALTIN", "GA"]:
            aktif_kesif_sembol = "GRAM_ALTIN"
        elif "." not in serbest_arama and "-" not in serbest_arama and len(serbest_arama) >= 2:
            test_df = varlik_gecmisi_getir(serbest_arama, period="5d")
            if test_df.empty:
                test_bist = varlik_gecmisi_getir(serbest_arama + ".IS", period="5d")
                if not test_bist.empty:
                    aktif_kesif_sembol = serbest_arama + ".IS"
                else:
                    test_kripto = varlik_gecmisi_getir(serbest_arama + "-USD", period="5d")
                    if not test_kripto.empty:
                        aktif_kesif_sembol = serbest_arama + "-USD"

    st.divider()

    with st.spinner(f"Veriler aktarılıyor: {aktif_kesif_sembol}..."):
        k_kat, k_para, k_rozet = varlik_sinifi_belirle(aktif_kesif_sembol)
        k_gecmis = varlik_gecmisi_getir(aktif_kesif_sembol, period="1y")
        try:
            k_info = get_company_fundamentals(aktif_kesif_sembol)
        except Exception:
            k_info = {}

    if k_gecmis.empty:
        st.error(f"'{aktif_kesif_sembol}' için veri bulunamadı. Lütfen sembol kodunu kontrol edin.")
    else:
        guncel_kesif_fiyat = float(k_gecmis['Close'].iloc[-1])
        onceki_kesif_fiyat = float(k_gecmis['Close'].iloc[-2]) if len(k_gecmis) > 1 else guncel_kesif_fiyat
        gunluk_degisim_yuzde = ((guncel_kesif_fiyat - onceki_kesif_fiyat) / onceki_kesif_fiyat) * 100

        sirket_uzun_adi = k_info.get("longName") or aktif_kesif_sembol
        sektor = k_info.get("sector")
        if not sektor or str(sektor).lower() == "none":
            sektor = k_kat
        endustri = k_info.get("industry")
        if not endustri or str(endustri).lower() == "none":
            endustri = "Piyasa Varlığı"

        col_header1, col_header2 = st.columns([2.5, 1.5])
        with col_header1:
            st.markdown(f"### {sirket_uzun_adi} (`{aktif_kesif_sembol}`)")
            st.caption(f"Sınıf: {k_kat} | Sektör: {sektor} | Faaliyet: {endustri}")
        with col_header2:
            st.metric(
                label=f"Piyasa Fiyatı ({k_para})",
                value=f"{guncel_kesif_fiyat:,.2f} {k_para}",
                delta=f"{gunluk_degisim_yuzde:+.2f}% (24s)"
            )

        # Detay D: Emtia & Altın Varlıkları İçin Özel Değerleme Paneli
        if aktif_kesif_sembol == "GRAM_ALTIN" or "=F" in aktif_kesif_sembol:
            st.markdown(f"""
            <div style="background: rgba(251, 191, 36, 0.025); border: 1px solid rgba(251, 191, 36, 0.16); border-radius: 12px; padding: 14px 18px; margin: 10px 0 16px 0;">
                <div style="font-size: 13px; font-weight: 600; color: #fbbf24; margin-bottom: 4px;">✦ Kıymetli Maden & Emtia Fiyatlandırma Modeli ({aktif_kesif_sembol})</div>
                <div style="font-size: 12.5px; color: #cbd5e1; line-height: 1.5;">
                    Altın ve değerli madenler şirket bilançosu barındırmaz; F/K (P/E), PD/DD veya Temettü gibi hisse çarpanları bulunmaz.
                    Fiyat oluşumu <b>Küresel ONS (GC=F)</b> ve <b>USD/TRY</b> paritesi üzerinden <code>(ONS / 31.1035) × USD/TRY</code> matematiksel formülüyle anlık hesaplanmaktadır.
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            # 5'li Finansal Bilanço & Değerleme Çarpanları
            m_cap = k_info.get("marketCap")
            if m_cap and not pd.isna(m_cap) and m_cap > 0:
                m_cap_str = f"{m_cap / 1e9:,.2f} Milyar {k_para}"
            else:
                m_cap_str = "—"
                
            pe_ratio = k_info.get("trailingPE")
            pe_str = f"{pe_ratio:.2f}" if (pe_ratio and not pd.isna(pe_ratio)) else "—"
            
            pb_ratio = k_info.get("priceToBook")
            pb_str = f"{pb_ratio:.2f}" if (pb_ratio and not pd.isna(pb_ratio)) else "—"
            
            div_yield = k_info.get("dividendYield")
            div_rate = k_info.get("dividendRate")
            if div_rate and not pd.isna(div_rate) and div_rate > 0:
                div_str = f"{div_rate:.2f} {k_para}"
                if div_yield and not pd.isna(div_yield) and div_yield > 0:
                    y_p = div_yield * 100 if div_yield < 1 else div_yield
                    div_str = f"%{y_p:.2f} ({div_rate:.2f} {k_para})"
            elif div_yield and not pd.isna(div_yield) and div_yield > 0:
                div_pct = div_yield * 100 if div_yield < 1 else div_yield
                div_str = f"%{div_pct:.2f}"
            else:
                div_str = "%0.00"
                
            # 52 Haftalık Zirve / Dip Garantisi (Geçmiş tablodan matematiksel hesaplama yedeği)
            h_52 = k_info.get("fiftyTwoWeekHigh")
            l_52 = k_info.get("fiftyTwoWeekLow")
            if (not h_52 or pd.isna(h_52)) and not k_gecmis.empty:
                h_52 = float(k_gecmis['Close'].max())
            if (not l_52 or pd.isna(l_52)) and not k_gecmis.empty:
                l_52 = float(k_gecmis['Close'].min())
                
            if h_52 and l_52 and not pd.isna(h_52) and not pd.isna(l_52):
                aralik_52_str = f"{l_52:,.2f} - {h_52:,.2f} {k_para}"
                aralik_52_help = f"52 Haftalık En Düşük: {l_52:,.2f} {k_para} | En Yüksek: {h_52:,.2f} {k_para}"
            else:
                aralik_52_str = "—"
                aralik_52_help = "52 haftalık fiyat aralığı hesaplanamadı."

            st.markdown("##### Temel Analiz & Bilanço Göstergeleri")
            c_val1, c_val2, c_val3, c_val4, c_val5 = st.columns(5)
            with c_val1:
                st.metric("Piyasa Değeri", m_cap_str)
            with c_val2:
                st.metric("F/K Oranı (P/E)", pe_str)
            with c_val3:
                st.metric("PD/DD (P/B)", pb_str)
            with c_val4:
                st.metric("Temettü Dağıtımı", div_str)
            with c_val5:
                st.metric("52 Haftalık Aralık", aralik_52_str, help=aralik_52_help)

        # İnteraktif 1 Yıllık Grafik
        k_gecmis = k_gecmis.sort_index()
        fig_kesif_trend = go.Figure()
        fig_kesif_trend.add_trace(go.Scatter(x=k_gecmis.index, y=k_gecmis['Close'], name='Kapanış', line=dict(color='#38bdf8', width=2.5)))
        sma20_k = k_gecmis['Close'].rolling(20).mean()
        sma50_k = k_gecmis['Close'].rolling(50).mean()
        fig_kesif_trend.add_trace(go.Scatter(x=k_gecmis.index, y=sma20_k, name='SMA 20', line=dict(color='#fbbf24', width=1.5)))
        fig_kesif_trend.add_trace(go.Scatter(x=k_gecmis.index, y=sma50_k, name='SMA 50', line=dict(color='#a855f7', width=1.5)))

        fig_kesif_trend.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#94a3b8'),
            xaxis=dict(gridcolor='rgba(255,255,255,0.04)', zerolinecolor='rgba(255,255,255,0.05)'),
            yaxis=dict(gridcolor='rgba(255,255,255,0.04)', zerolinecolor='rgba(255,255,255,0.05)'),
            title=f"{aktif_kesif_sembol} — Son 1 Yıllık Fiyat & Trend Grafiği",
            xaxis_title="Tarih",
            yaxis_title=f"Fiyat ({k_para})",
            hovermode="x unified",
            height=390,
            margin=dict(t=40, b=20, l=20, r=20)
        )
        st.plotly_chart(fig_kesif_trend, use_container_width=True)

        # Canlı Finans Haberleri
        st.divider()
        st.markdown("##### Canlı Piyasa Haberleri & Basın Akışı")
        
        arama_kelimesi = sirket_uzun_adi if sirket_uzun_adi != aktif_kesif_sembol else aktif_kesif_sembol.replace(".IS", "").replace("-USD", "")
        haberler = get_live_news(arama_kelimesi, count=4)

        if not haberler:
            st.caption("Seçilen varlık hakkında güncel haber akışı bulunamadı.")
        else:
            if gemini_key:
                headlines_tuple = tuple(h['headline'] for h in haberler)
                sentiment_data = get_ai_news_sentiment(aktif_kesif_sembol, headlines_tuple, gemini_key)
                if sentiment_data:
                    skor = sentiment_data.get("skor", "Nötr (Dengeli)")
                    yuzde = sentiment_data.get("yuzde", 50)
                    ozet = sentiment_data.get("ozet", "")
                    zaman = sentiment_data.get("zaman", "")
                    
                    is_pos = any(w in skor.lower() for w in ["boğa", "pozitif", "yükseliş"])
                    is_neg = any(w in skor.lower() for w in ["ayı", "negatif", "düşüş"])
                    badge_bg = "rgba(34, 197, 94, 0.12)" if is_pos else ("rgba(239, 68, 68, 0.12)" if is_neg else "rgba(234, 179, 8, 0.12)")
                    badge_color = "#4ade80" if is_pos else ("#f87171" if is_neg else "#facc15")
                    badge_border = "rgba(34, 197, 94, 0.25)" if is_pos else ("rgba(239, 68, 68, 0.25)" if is_neg else "rgba(234, 179, 8, 0.25)")

                    st.markdown(f"""
                    <div style="background: rgba(255, 255, 255, 0.02); border: 1px solid rgba(255, 255, 255, 0.07); border-radius: 12px; padding: 14px 18px; margin-bottom: 16px;">
                        <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 8px;">
                            <span style="font-size: 11px; text-transform: uppercase; letter-spacing: 0.06em; font-weight: 600; color: #64748b;">✦ AI Piyasa Algı Radarı</span>
                            <span style="background: {badge_bg}; color: {badge_color}; border: 1px solid {badge_border}; font-size: 11.5px; font-weight: 600; padding: 2px 10px; border-radius: 20px;">● {skor} (%{yuzde})</span>
                        </div>
                        <div style="font-size: 13.5px; color: #e2e8f0; line-height: 1.5; font-weight: 400; margin-bottom: 8px;">
                            {ozet}
                        </div>
                        <div style="font-size: 11px; color: #475569; letter-spacing: 0.01em;">
                            ✦ Yapay Zeka İstihbaratı • Güncelleme: {zaman} (2 Saatlik Kurumsal Döngü)
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.caption("✦ Yapay zeka piyasa algı radarı için sol menüden Gemini API anahtarınızı tanımlayabilirsiniz.")

            col_hab1, col_hab2 = st.columns(2)
            for idx, hab in enumerate(haberler):
                target_col = col_hab1 if idx % 2 == 0 else col_hab2
                with target_col:
                    st.markdown(f"""
                    <div class="news-card">
                        <span style="color: #38bdf8; font-size: 11px; text-transform: uppercase; letter-spacing: 0.05em; font-weight: 600;">{hab['source']}</span>
                        <span style="color: #475569; font-size: 11px; float: right;">{hab['date']}</span>
                        <div style="font-weight: 500; font-size: 14px; margin-top: 8px; color: #f1f5f9; line-height: 1.4;">{hab['headline']}</div>
                        <div style="margin-top: 10px;">
                            <a href="{hab['link']}" target="_blank" style="color: #64748b; font-size: 12px; text-decoration: none; font-weight: 500;">Haberi Görüntüle ↗</a>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)


        # Portföye Ekleme
        st.divider()
        with st.expander(f"Portföye Ekle: {aktif_kesif_sembol}"):
            st.caption("Bu varlığı doğrudan kişisel portföyünüze ekleyin:")
            col_add1, col_add2, col_add3 = st.columns(3)
            with col_add1:
                hizli_maliyet = st.number_input("Birim Maliyet", value=float(guncel_kesif_fiyat), format="%.2f", key="hizli_maliyet_in")
            with col_add2:
                hizli_adet = st.number_input("Miktar / Lot", min_value=0.0001, value=10.0, step=1.0, format="%.4f", key="hizli_adet_in")
            with col_add3:
                st.write("")
                st.write("")
                if st.button("Portföye Kaydet", type="primary", use_container_width=True, key="hizli_kaydet_btn"):
                    if is_demo:
                        st.session_state.demo_portfoy[aktif_kesif_sembol] = {"maliyet": float(hizli_maliyet), "adet": float(hizli_adet)}
                    else:
                        database.kullanici_hisse_ekle_guncelle(user_email, aktif_kesif_sembol, float(hizli_maliyet), float(hizli_adet))
                    st.success(f"{aktif_kesif_sembol} portföye eklendi.")
                    st.rerun()