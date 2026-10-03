import streamlit as st
import yfinance as yf
import pandas as pd
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
import requests
import json, re, datetime

def get_yf_session():
    """Yahoo Finance sorguları için tarayıcı kimlikli güvenli oturum döndürür."""
    s = requests.Session()
    s.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7',
    })
    return s

# --- YARDIMCI VERİ & KUR FONKSİYONLARI ---

@st.cache_data(ttl=300)
def get_usd_try_rate() -> float:
    """Anlık USD/TRY kurunu çeker."""
    try:
        usd = yf.Ticker("USDTRY=X").history(period="2d")
        if not usd.empty:
            return float(usd['Close'].iloc[-1])
    except Exception:
        pass
    return 34.50

def varlik_sinifi_belirle(sembol: str):
    """Sembolün varlık sınıfını, para birimini ve rozetini döndürür."""
    s = sembol.upper().strip()
    if s.endswith(".IS"):
        return "BIST Hissesi", "TRY", "[BIST]"
    elif s == "GRAM_ALTIN" or s.startswith("GC=") or s.startswith("SI="):
        para = "TRY" if s == "GRAM_ALTIN" else "USD"
        return "Emtia & Maden", para, "[EMTİA]"
    elif s.endswith("-USD") or s.endswith("-TRY") or s in ["BTC", "ETH", "SOL", "AVAX", "DOGE", "XRP"]:
        return "Kripto Varlık", "USD", "[KRİPTO]"
    elif "USDTRY" in s or "EURTRY" in s:
        return "Nakit & Döviz", "TRY", "[DÖVİZ]"
    else:
        return "ABD Borsası", "USD", "[ABD]"

@st.cache_data(ttl=300, show_spinner=False)
def varlik_gecmisi_getir(sembol: str, period="6mo") -> pd.DataFrame:
    """BIST, ABD, Kripto veya Gram Altın geçmiş verisini çeker."""
    s = sembol.upper().strip()
    if s == "GRAM_ALTIN":
        try:
            ons = yf.Ticker("GC=F").history(period=period)['Close']
            usd = yf.Ticker("USDTRY=X").history(period=period)['Close']
            ons.index = pd.to_datetime(ons.index).tz_localize(None).normalize()
            usd.index = pd.to_datetime(usd.index).tz_localize(None).normalize()
            df_merged = pd.concat([ons, usd], axis=1, keys=['ons', 'usd']).sort_index().ffill().dropna()
            gram_series = (df_merged['ons'] / 31.1034768) * df_merged['usd']
            df = pd.DataFrame({'Close': gram_series}).sort_index()
            return df
        except Exception:
            return pd.DataFrame()
    else:
        try:
            hisse = yf.Ticker(s)
            df = hisse.history(period=period)
            if not df.empty:
                df = df.sort_index()
            return df
        except Exception:
            return pd.DataFrame()

@st.cache_data(ttl=600)
def get_live_news(query: str, count: int = 4):
    """Google News RSS feed üzerinden Türkçe canlı finans haberlerini çeker."""
    url = f"https://news.google.com/rss/search?q={urllib.parse.quote(query)}&hl=tr&gl=TR&ceid=TR:tr"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        content = urllib.request.urlopen(req, timeout=4).read()
        root = ET.fromstring(content)
        items = root.findall('./channel/item')[:count]
        news_list = []
        for it in items:
            title = it.find('title').text if it.find('title') is not None else ''
            link = it.find('link').text if it.find('link') is not None else '#'
            pubDate = it.find('pubDate').text if it.find('pubDate') is not None else ''
            parts = title.rsplit(' - ', 1)
            headline = parts[0]
            source = parts[1] if len(parts) > 1 else 'Finans Medyası'
            news_list.append({
                'headline': headline,
                'source': source,
                'link': link,
                'date': pubDate[:16]
            })
        return news_list
    except Exception:
        return []

@st.cache_data(ttl=1800)
def get_company_fundamentals(symbol: str) -> dict:
    """Şirket temel analiz çarpanlarını çeker ve 30 dk önbelleğe alır."""
    if symbol == "GRAM_ALTIN":
        return {}
    try:
        t = None
        info = {}
        try:
            session = get_yf_session()
            t = yf.Ticker(symbol, session=session)
            info = t.info if isinstance(t.info, dict) else {}
        except Exception:
            # Yeni yfinance sürümleri requests.Session kabul etmez; kendi oturumuyla tekrar dene
            t = yf.Ticker(symbol)
            info = t.info if isinstance(t.info, dict) else {}
        fi = getattr(t, 'fast_info', None)
        
        market_cap = info.get("marketCap")
        if not market_cap and fi:
            market_cap = getattr(fi, 'market_cap', None) or (fi.get('marketCap') if hasattr(fi, 'get') else None)
            
        pe = info.get("trailingPE") or info.get("forwardPE")
        pb = info.get("priceToBook")
        div_y = info.get("dividendYield") or info.get("trailingAnnualDividendYield")
        div_r = info.get("dividendRate")
        
        h52 = info.get("fiftyTwoWeekHigh")
        l52 = info.get("fiftyTwoWeekLow")
        if not h52 and fi:
            h52 = getattr(fi, 'year_high', None) or (fi.get('yearHigh') if hasattr(fi, 'get') else None)
        if not l52 and fi:
            l52 = getattr(fi, 'year_low', None) or (fi.get('yearLow') if hasattr(fi, 'get') else None)

        if not info and market_cap is None:
            raise ValueError(f"'{symbol}' verisi alınamadı.")

        sec = info.get("sector")
        sec_str = sec if sec and str(sec).lower() != "none" else "Piyasa Şirketi"

        ind = info.get("industry")
        ind_str = ind if ind and str(ind).lower() != "none" else "Sanayi & Hizmet"

        lname = info.get("longName")
        lname_str = lname if lname and str(lname).lower() != "none" else symbol
            
        return {
            "longName": lname_str,
            "sector": sec_str,
            "industry": ind_str,
            "marketCap": market_cap,
            "trailingPE": pe,
            "priceToBook": pb,
            "dividendYield": div_y,
            "dividendRate": div_r,
            "fiftyTwoWeekHigh": h52,
            "fiftyTwoWeekLow": l52,
        }
    except Exception as e:
        raise e

@st.cache_data(ttl=7200)
def get_ai_news_sentiment(symbol: str, headlines_tuple: tuple, api_key: str) -> dict:
    """Haber başlıklarını Gemini ile analiz edip piyasa duygu skorunu 2 saat önbelleğe alır."""
    if not api_key or not headlines_tuple:
        return {}
    try:
        from google import genai
        import json, re, datetime
        client = genai.Client(api_key=api_key)
        headlines_text = "\n".join([f"- {h}" for h in headlines_tuple[:5]])
        prompt = f"""
Sen Wall Street ve Borsa İstanbul konusunda uzman kurumsal bir Finansal İstihbarat Analistisin.
Varlık: {symbol}
Aşağıdaki son canlı haber başlıklarını analiz et ve piyasanın algısını değerlendir:
{headlines_text}

LÜTFEN SADECE VE SADECE aşağıdaki JSON formatında tek bir JSON objesi üret:
{{
  "skor": "Boğa (Pozitif)" veya "Nötr (Dengeli)" veya "Ayı (Negatif)",
  "yuzde": 75,
  "ozet": "2 cümlelik net, kurumsal piyasa algısı ve haber özeti."
}}
JSON dışında hiçbir ek metin veya açıklama yazma.
"""
        modeller = ["gemini-2.0-flash", "gemini-1.5-flash", "gemini-1.5-pro"]
        try:
            live_models = [m.name for m in client.models.list() if "gemini" in m.name.lower() and "embed" not in m.name.lower()]
            if live_models:
                modeller = live_models
        except Exception:
            pass

        raw_text = ""
        for m_name in modeller:
            try:
                res = client.models.generate_content(model=m_name, contents=prompt)
                if res and res.text:
                    raw_text = res.text.strip()
                    break
            except Exception:
                continue

        if not raw_text:
            return {}

        match = re.search(r'\{.*\}', raw_text, re.DOTALL)
        if match:
            parsed = json.loads(match.group(0))
            parsed["zaman"] = datetime.datetime.now().strftime("%H:%M")
            return parsed
        return {}
    except Exception:
        return {}


