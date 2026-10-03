import streamlit as st

from services.market_data import varlik_sinifi_belirle

# --- AKILLI PORTFÖY DENGELEME ROBOTU MOTORU (SOLID - SRP) ---

REBALANCE_STRATEJILERI = {
    "Dengeli Dört Ayak (All-Weather)": {
        "BIST Hissesi": 25.0,
        "ABD Borsası": 25.0,
        "Emtia & Maden": 25.0,
        "Kripto Varlık": 25.0,
        "aciklama": "Ray Dalio modeli; ekonomik döngülere karşı risk ve getiriyi 4 ana sütuna eşit (%25) dağıtır."
    },
    "Teknoloji & Büyüme (Agresif)": {
        "BIST Hissesi": 20.0,
        "ABD Borsası": 40.0,
        "Emtia & Maden": 10.0,
        "Kripto Varlık": 30.0,
        "aciklama": "Yüksek risk toleransı; küresel yapay zeka, teknoloji ve kripto yükseliş ivmesine odaklanır."
    },
    "Defansif & Temettü (Muhafazakar)": {
        "BIST Hissesi": 35.0,
        "ABD Borsası": 15.0,
        "Emtia & Maden": 40.0,
        "Kripto Varlık": 10.0,
        "aciklama": "Sermaye koruma ve nakit akışı; kıymetli madenler ve BIST temettü devlerine ağırlık verir."
    },
    "Özel Dağılım (Kişiselleştirilmiş)": {
        "BIST Hissesi": 25.0,
        "ABD Borsası": 25.0,
        "Emtia & Maden": 25.0,
        "Kripto Varlık": 25.0,
        "aciklama": "Kendi yatırım felsefenize göre hedef yüzdeleri serbestçe belirleyin."
    }
}

def hesapla_portfoy_rebalancing(
    kategori_degerler: dict, 
    toplam_deger_tl: float, 
    hedef_oranlar: dict, 
    eklenecek_nakit_tl: float = 0.0, 
    mod: str = "satisli",
    portfoy: dict = None,
    portfoy_fiyatlari_tl: dict = None
) -> dict:
    """
    Portföy hedef ağırlıkları ile mevcut ağırlıklar arasındaki sapmayı (drift)
    ölçer ve hem sınıf hem tekil varlık bazında matematiksel alış/satış reçetesi üretir.
    """
    ana_siniflar = ["BIST Hissesi", "ABD Borsası", "Emtia & Maden", "Kripto Varlık"]
    hedef_toplam = (toplam_deger_tl + eklenecek_nakit_tl) if mod == "tasarruf" else toplam_deger_tl
    
    sinif_analizleri = []
    for kat in ana_siniflar:
        mevcut_deger = float(kategori_degerler.get(kat, 0.0))
        mevcut_oran = (mevcut_deger / toplam_deger_tl * 100.0) if toplam_deger_tl > 0 else 0.0
        hedef_oran = float(hedef_oranlar.get(kat, 0.0))
        hedef_deger = hedef_toplam * (hedef_oran / 100.0)
        
        sapma_yuzde = mevcut_oran - hedef_oran
        fark_tl = hedef_deger - mevcut_deger
        
        durum = "Dengede"
        if sapma_yuzde > 2.0:
            durum = "Aşırı Ağırlık"
        elif sapma_yuzde < -2.0:
            durum = "Düşük Ağırlık"
            
        sinif_analizleri.append({
            "sinif": kat,
            "mevcut_deger": mevcut_deger,
            "mevcut_oran": mevcut_oran,
            "hedef_oran": hedef_oran,
            "hedef_deger": hedef_deger,
            "sapma_yuzde": sapma_yuzde,
            "fark_tl": fark_tl,
            "durum": durum
        })

    # Lot Reçetesini Oluşturma
    recete_emirleri = []
    toplam_alis_tl = 0.0
    toplam_satis_tl = 0.0

    if portfoy and portfoy_fiyatlari_tl:
        sinif_varliklari = {kat: [] for kat in ana_siniflar}
        for sembol, bilgi in portfoy.items():
            k_sinif, _, _ = varlik_sinifi_belirle(sembol)
            if k_sinif in sinif_varliklari:
                fiyat_tl, _ = portfoy_fiyatlari_tl.get(sembol, (0.0, "TL"))
                adet = float(bilgi.get("adet", 0.0))
                guncel_deger = fiyat_tl * adet
                sinif_varliklari[k_sinif].append({
                    "sembol": sembol,
                    "fiyat_tl": fiyat_tl,
                    "adet": adet,
                    "deger_tl": guncel_deger
                })

        if mod == "satisli":
            for sa in sinif_analizleri:
                kat = sa["sinif"]
                fark = sa["fark_tl"]
                varliklar = sinif_varliklari.get(kat, [])
                
                if not varliklar:
                    if fark > 500:
                        recete_emirleri.append({
                            "islem": "AL",
                            "varlik": f"{kat} (Yeni Pozisyon)",
                            "lot_metin": f"+{fark:,.0f} TL",
                            "tutar_tl": fark,
                            "sinif": kat
                        })
                        toplam_alis_tl += fark
                    continue
                    
                kat_toplam_deger = sum(v["deger_tl"] for v in varliklar)
                
                if fark > 0: # Alış
                    for v in varliklar:
                        pay = (v["deger_tl"] / kat_toplam_deger) if kat_toplam_deger > 0 else (1.0 / len(varliklar))
                        varliga_tutar = fark * pay
                        if v["fiyat_tl"] > 0:
                            lot = (varliga_tutar / v["fiyat_tl"])
                            if kat == "Kripto Varlık":
                                lot_str = f"+{lot:.4f}"
                            elif kat == "Emtia & Maden":
                                lot_str = f"+{lot:.2f} Gr"
                            else:
                                lot_int = int(round(lot))
                                lot_str = f"+{lot_int:,} Lot" if lot_int > 0 else None
                                
                            if lot_str and (lot > 0.0001) and (varliga_tutar >= 100.0 or kat == "Kripto Varlık"):
                                recete_emirleri.append({
                                    "islem": "AL",
                                    "varlik": v["sembol"],
                                    "lot_metin": lot_str,
                                    "tutar_tl": varliga_tutar,
                                    "sinif": kat
                                })
                                toplam_alis_tl += varliga_tutar
                elif fark < 0: # Satış
                    satis_hedefi = abs(fark)
                    for v in varliklar:
                        pay = (v["deger_tl"] / kat_toplam_deger) if kat_toplam_deger > 0 else (1.0 / len(varliklar))
                        varliga_satis = satis_hedefi * pay
                        if v["fiyat_tl"] > 0:
                            lot = (varliga_satis / v["fiyat_tl"])
                            if kat == "Kripto Varlık":
                                lot_str = f"-{lot:.4f}"
                            elif kat == "Emtia & Maden":
                                lot_str = f"-{lot:.2f} Gr"
                            else:
                                lot_int = int(round(lot))
                                lot_str = f"-{lot_int:,} Lot" if lot_int > 0 else None
                                
                            if lot_str and (lot > 0.0001) and (varliga_satis >= 100.0 or kat == "Kripto Varlık"):
                                recete_emirleri.append({
                                    "islem": "SAT",
                                    "varlik": v["sembol"],
                                    "lot_metin": lot_str,
                                    "tutar_tl": varliga_satis,
                                    "sinif": kat
                                })
                                toplam_satis_tl += varliga_satis
        else:
            # Mod B: Tasarruf Ekleme (Yalnızca AL, satış yok)
            eksik_siniflar = [sa for sa in sinif_analizleri if sa["fark_tl"] > 0]
            toplam_eksik_tl = sum(sa["fark_tl"] for sa in eksik_siniflar)
            
            if toplam_eksik_tl > 0 and eklenecek_nakit_tl > 0:
                for sa in eksik_siniflar:
                    kat = sa["sinif"]
                    kat_pay = sa["fark_tl"] / toplam_eksik_tl
                    kat_nakit = eklenecek_nakit_tl * kat_pay
                    varliklar = sinif_varliklari.get(kat, [])
                    
                    if not varliklar:
                        recete_emirleri.append({
                            "islem": "AL",
                            "varlik": f"{kat} (Yeni Pozisyon)",
                            "lot_metin": f"+{kat_nakit:,.0f} TL",
                            "tutar_tl": kat_nakit,
                            "sinif": kat
                        })
                        toplam_alis_tl += kat_nakit
                        continue
                        
                    kat_toplam_deger = sum(v["deger_tl"] for v in varliklar)
                    for v in varliklar:
                        pay = (v["deger_tl"] / kat_toplam_deger) if kat_toplam_deger > 0 else (1.0 / len(varliklar))
                        varliga_tutar = kat_nakit * pay
                        if v["fiyat_tl"] > 0 and varliga_tutar > 0:
                            lot = (varliga_tutar / v["fiyat_tl"])
                            if kat == "Kripto Varlık":
                                lot_str = f"+{lot:.4f}"
                            elif kat == "Emtia & Maden":
                                lot_str = f"+{lot:.2f} Gr"
                            else:
                                lot_int = int(round(lot))
                                lot_str = f"+{lot_int:,} Lot" if lot_int > 0 else None
                                
                            if lot_str and (lot > 0.0001) and (varliga_tutar >= 100.0 or kat == "Kripto Varlık"):
                                recete_emirleri.append({
                                    "islem": "AL",
                                    "varlik": v["sembol"],
                                    "lot_metin": lot_str,
                                    "tutar_tl": varliga_tutar,
                                    "sinif": kat
                                })
                                toplam_alis_tl += varliga_tutar

    return {
        "sinif_analizleri": sinif_analizleri,
        "recete_emirleri": recete_emirleri,
        "toplam_alis_tl": toplam_alis_tl,
        "toplam_satis_tl": toplam_satis_tl,
        "hedef_toplam": hedef_toplam
    }

