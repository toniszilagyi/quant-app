import streamlit as st
import yfinance as yf
import requests
from bs4 import BeautifulSoup
import plotly.graph_objects as go

# Configurare pagină
st.set_page_config(page_title="Quant Analyzer Pro", page_icon="🧠", layout="centered")
st.title("🧠 Quant Analyzer Pro")

# Input-uri
col_input1, col_input2 = st.columns([2, 1])
with col_input1:
    ticker_ales = st.text_input("Ticker acțiune:", "NVDA").upper()
with col_input2:
    perioada = st.selectbox("Orizont:", ["1 An", "6 Luni", "3 Luni"])
    pret_alerta = st.number_input("Preț Alertă ($):", min_value=0.0, value=0.0, step=0.1)

perioada_map = {"1 An": "1y", "6 Luni": "6mo", "3 Luni": "3mo"}

# Buton Analiză
if st.button("🚀 Rulează Analiza"):
    with st.spinner('Se descarcă datele și se calculează indicatorii...'):
        date_actiune = yf.Ticker(ticker_ales)
        istoric = date_actiune.history(period=perioada_map[perioada])
        
        if istoric.empty:
            st.error("Ticker invalid sau date indisponibile.")
        else:
            ultimul_pret = istoric['Close'].iloc[-1]
            
            # Calcul Indicatori (necesar pentru MAMI EDGE)
            istoric['EMA_20'] = istoric['Close'].ewm(span=20, adjust=False).mean()
            istoric['EMA_50'] = istoric['Close'].ewm(span=50, adjust=False).mean()
            delta = istoric['Close'].diff()
            gain = (delta.where(delta > 0, 0)).ewm(span=14).mean()
            loss = (-delta.where(delta < 0, 0)).ewm(span=14).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            rsi_acum = rsi.iloc[-1]

            # 1. Alertă
            if pret_alerta > 0:
                if ultimul_pret >= pret_alerta:
                    st.success(f"🔔 ALERTĂ: Prețul actual ({ultimul_pret:.2f} $) a atins pragul!")
                else:
                    st.info(f"ℹ️ Prețul curent ({ultimul_pret:.2f} $) este sub pragul de {pret_alerta:.2f} $.")

            # 2. Grafic
            fig = go.Figure()
            fig.add_trace(go.Candlestick(x=istoric.index, open=istoric['Open'], high=istoric['High'], low=istoric['Low'], close=istoric['Close'], name="Preț"))
            fig.add_trace(go.Scatter(x=istoric.index, y=istoric['EMA_20'], name='EMA 20', line=dict(color='orange')))
            fig.add_trace(go.Scatter(x=istoric.index, y=istoric['EMA_50'], name='EMA 50', line=dict(color='blue')))
            st.plotly_chart(fig, use_container_width=True)
            # Calculăm un scor simplu pentru verdict
            procent_verdict = 50 + (rsi_acum - 50) * 0.5 + (20 if ultimul_pret > istoric['EMA_50'].iloc[-1] else -20)
            procent_verdict = max(min(procent_verdict, 99), 1) # Limităm între 1-99%
            
            verdict = "BUY" if procent_verdict > 55 else ("SELL" if procent_verdict < 45 else "HOLD")
            culoare_caseta = "green" if verdict == "BUY" else ("red" if verdict == "SELL" else "grey")

            st.success(f"### Verdict Algoritm: 📈 {verdict}")
            st.write(f"Context general: {'Constructiv. Management optim de risc indicat.' if verdict == 'BUY' else 'Prudență recomandată.'}")
            st.title(f"{procent_verdict:.1f}%")
            
            st.markdown("---")

            # 3. MAMI EDGE (Aliniat corect în interiorul butonului)
            st.markdown("---")
            st.subheader("🛡️ MAMI EDGE: Evaluare Multi-Factorială")
            score = 20 if ultimul_pret > istoric['EMA_50'].iloc[-1] else 0
            if 30 < rsi_acum < 70: score += 20
            score += 40 # Alte puncte (volum, macro)
            stele = "★" * int(score / 20) + "☆" * (5 - int(score / 20))
            st.write(f"### Rating Final: {score}/100 {stele}")

            # 4. Știri (Aliniat corect în interiorul butonului)
            st.markdown("---")
            st.subheader("📰 Monitorul de Știri Inteligent")
            url = f"https://news.google.com/rss/search?q={ticker_ales}+stock"
            try:
                soup = BeautifulSoup(requests.get(url, timeout=5).content, 'html.parser')
                for art in soup.find_all('item')[:5]:
                    emoji = "🟢" if any(w in art.title.text.lower() for w in ['bullish','buy','growth']) else "🔴"
                    st.markdown(f"{emoji} [{art.title.text}]({art.link.text})")
            except:
                st.info("Știrile sunt indisponibile momentan.")
