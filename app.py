import streamlit as st
import yfinance as yf
import requests
from bs4 import BeautifulSoup
import plotly.graph_objects as go

# Configurare pagină
st.set_page_config(page_title="Quant Analyzer Pro", page_icon="🧠", layout="wide")
st.title("🧠 Quant Analyzer Pro")
# --- RADAR PIAȚĂ OPTIMIZAT (Sidebar) ---
st.sidebar.title("📡 Radar Piață")
st.sidebar.write("Top Acțiuni (Volum & Volatilitate)")



# Lista extinsă de urmărit (poți adăuga orice ticker dorești)
radar_list = ["NVDA", "AAPL", "TSLA", "AMD", "MSFT", "GOOGL", "AMZN", "META"]

for ticker in radar_list:
    try:
        t = yf.Ticker(ticker)
        data = t.history(period="2d")
        pret = data['Close'].iloc[-1]
        change = (data['Close'].pct_change().iloc[-1]) * 100
        volum = data['Volume'].iloc[-1] / 1_000_000 # În milioane
        
        color = "🟢" if change >= 0 else "🔴"
        st.sidebar.markdown(f"{color} **{ticker}**")
        st.sidebar.write(f"Price: {pret:.2f}$ | Vol: {volum:.1f}M")
        st.sidebar.write(f"Change: {change:+.2f}%")
        st.sidebar.markdown("---")
    except:
        continue
# Lista simulată de tickere populare pentru radar (poți adăuga ce vrei)
radar_list = ["NVDA", "AAPL", "TSLA", "AMD", "MSFT"]

for ticker in radar_list:
    try:
        t = yf.Ticker(ticker)
        pret = t.history(period="1d")['Close'].iloc[-1]
        change = ((t.history(period="2d")['Close'].pct_change()).iloc[-1]) * 100
        color = "🟢" if change >= 0 else "🔴"
        st.sidebar.write(f"{color} **{ticker}**: {pret:.2f}$ ({change:+.2f}%)")
    except:
        st.sidebar.write(f"⚪ {ticker}: Date indisponibile")

ticker_ales = st.text_input("Ticker acțiune:", "NVDA").upper()
col1, col2 = st.columns(2)
with col1:
    perioada = st.selectbox("Orizont:", ["1 An", "6 Luni", "3 Luni"])
with col2:
    pret_alerta = st.number_input("Preț Alertă ($):", value=0.0)

if st.button("🚀 Rulează Analiza"):
    perioada_map = {"1 An": "1y", "6 Luni": "6mo", "3 Luni": "3mo"}
    date = yf.Ticker(ticker_ales)
    istoric = date.history(period=perioada_map[perioada])
    
    if not istoric.empty:
        # Calcul Indicatori
        istoric['EMA_8'] = istoric['Close'].ewm(span=8, adjust=False).mean()
        istoric['EMA_20'] = istoric['Close'].ewm(span=20, adjust=False).mean()
        istoric['EMA_50'] = istoric['Close'].ewm(span=50, adjust=False).mean()
        istoric['SMA_200'] = istoric['Close'].rolling(window=200).mean()
        
        delta = istoric['Close'].diff()
        gain = (delta.where(delta > 0, 0)).ewm(span=14).mean()
        loss = (-delta.where(delta < 0, 0)).ewm(span=14).mean()
        rsi_acum = (100 - (100 / (1 + (gain / loss)))).iloc[-1]
        ultimul_pret = istoric['Close'].iloc[-1]

        # Grafic
        fig = go.Figure()
        fig.add_trace(go.Candlestick(x=istoric.index, open=istoric['Open'], high=istoric['High'], low=istoric['Low'], close=istoric['Close'], name="Preț"))
        fig.add_trace(go.Scatter(x=istoric.index, y=istoric['EMA_8'], name='EMA 8', line=dict(color='black', width=2)))
        fig.add_trace(go.Scatter(x=istoric.index, y=istoric['EMA_20'], name='EMA 20', line=dict(color='orange', width=1)))
        fig.add_trace(go.Scatter(x=istoric.index, y=istoric['EMA_50'], name='EMA 50', line=dict(color='blue', width=1)))
        fig.update_layout(xaxis_rangeslider_visible=False, height=500)
        st.plotly_chart(fig, use_container_width=True)
      # --- SCANNER DE PIAȚĂ AUTOMAT ---
st.sidebar.markdown("---")
if st.sidebar.button("🔍 Scanează Oportunități"):
    with st.spinner("Se scanează piața..."):
        # Lista de acțiuni de scanat
        lista_scan = ["NVDA", "AAPL", "TSLA", "AMD", "MSFT", "GOOGL", "AMZN", "META", "NFLX", "NVDA"]
        rezultate = []
        
        for ticker in lista_scan:
            try:
                t = yf.Ticker(ticker)
                hist = t.history(period="6mo")
                if not hist.empty:
                    ultimul_pret = hist['Close'].iloc[-1]
                    ema_50 = hist['Close'].ewm(span=50, adjust=False).mean().iloc[-1]
                    
                    # Logica rapidă de scor
                    scor = 0
                    if ultimul_pret > ema_50: scor += 50
                    scor += 30 # Volum simulat
                    scor += 20 # Trend
                    
                    if scor >= 80:
                        rezultate.append({"Ticker": ticker, "Preț": round(ultimul_pret, 2), "Scor MAMI": scor})
            except:
                continue
        
        if rezultate:
            st.sidebar.write("### ✅ Acțiuni cu Scor Mare:")
            st.sidebar.table(rezultate)
        else:
            st.sidebar.write("Nicio oportunitate găsită momentan.")
        # MAMI EDGE - Evaluare Multi-Factorială
        st.markdown("---")
        st.subheader("🛡️ MAMI EDGE: Evaluare Multi-Factorială")
        trend_m = 20 if istoric['EMA_8'].iloc[-1] > istoric['EMA_50'].iloc[-1] else 0
        score = trend_m + 15 + (15 if 40 < rsi_acum < 60 else 10) + (20 if ultimul_pret > istoric['SMA_200'].iloc[-1] else 0) + 30
        scor_final = min(score, 100)
        stele = "★" * int(scor_final / 20) + "☆" * (5 - int(scor_final / 20))
        
        c1, c2 = st.columns([1, 3])
        c1.metric("Scor Final", f"{scor_final}/100")
        c2.write(f"### Rating: {stele}")

        # Asistent Decizie
        st.markdown("---")
        st.subheader("🤖 Asistent de Decizie Strategic")
        cols = st.columns(3)
        cols[0].metric("Swing", "🟢 BUY" if ultimul_pret > istoric['EMA_8'].iloc[-1] else "🔴 WAIT")
        cols[1].metric("Position", "🟢 BUY" if istoric['EMA_20'].iloc[-1] > istoric['EMA_50'].iloc[-1] else "🔴 HOLD")
        cols[2].metric("Long Term", "🟢 BULLISH" if ultimul_pret > istoric['SMA_200'].iloc[-1] else "🔴 BEARISH")
        
        st.info("💡 Deciziile sunt bazate pe analiza tehnică. Nu reprezintă sfaturi financiare!")
        # --- CALCULATR ATR PENTRU MANAGEMENTUL RISCULUI ---
        st.markdown("---")
        st.subheader("🛡️ Managementul Riscului (ATR)")
        
        # Calcul ATR (14 perioade)
        high_low = istoric['High'] - istoric['Low']
        high_close = abs(istoric['High'] - istoric['Close'].shift())
        low_close = abs(istoric['Low'] - istoric['Close'].shift())
        tr = high_low.combine(high_close, max).combine(low_close, max)
        atr = tr.rolling(window=14).mean().iloc[-1]
        
        # Calcul Stop Loss (recomandare 2x ATR)
        stop_loss = ultimul_pret - (2 * atr)
        
        col1, col2 = st.columns(2)
        col1.metric("ATR (Volatilitate)", f"{atr:.2f} $")
        col2.metric("Stop Loss Recomandat", f"{stop_loss:.2f} $")
        
        st.write(f"ℹ️ *Dacă prețul scade sub {stop_loss:.2f} $, volatilitatea curentă indică faptul că trendul a fost invalidat.*")

        # Știri
        st.subheader("📰 Monitorul de Știri")
        try:
            url = f"https://news.google.com/rss/search?q={ticker_ales}+stock"
            soup = BeautifulSoup(requests.get(url, timeout=5).content, 'html.parser')
            for art in soup.find_all('item')[:5]:
                st.markdown(f"⚪ [{art.title.text}]({art.link.text})")
        except:
            st.info("Știri indisponibile.")
    else:
        st.error("Date indisponibile pentru acest Ticker.")
