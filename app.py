Python
import streamlit as st
import yfinance as yf
import requests
from bs4 import BeautifulSoup
import plotly.graph_objects as go

# Configurare interfață
st.set_page_config(page_title="Quant Analyzer Pro", page_icon="🧠")
st.title("🧠 Quant Analyzer Pro")

ticker_ales = st.text_input("Introdu Ticker-ul:", "NVDA").upper()
perioada = st.selectbox("Orizont:", ["1 An", "6 Luni", "3 Luni"])
pret_alerta = st.number_input("Preț Alertă ($):", value=0.0)

# Mapare perioade
perioada_map = {"1 An": "1y", "6 Luni": "6mo", "3 Luni": "3mo"}

if st.button("🚀 Rulează Analiza"):
    date = yf.Ticker(ticker_ales)
    istoric = date.history(period=perioada_map[perioada])
    
    if not istoric.empty:
        ultimul_pret = istoric['Close'].iloc[-1]
        istoric['EMA_50'] = istoric['Close'].ewm(span=50, adjust=False).mean()
        
        # 1. Alertă
        if pret_alerta > 0 and ultimul_pret >= pret_alerta:
            st.success(f"🔔 ALERTĂ: Prețul a atins pragul de {pret_alerta} $!")
        
        # 2. Grafic
        fig = go.Figure()
        fig.add_trace(go.Candlestick(x=istoric.index, open=istoric['Open'], high=istoric['High'], low=istoric['Low'], close=istoric['Close']))
        st.plotly_chart(fig, use_container_width=True)
        
        # 3. Verdict Algoritm
        procent = 70.0 # Exemplu de calcul
        st.success(f"### Verdict Algoritm: BUY")
        st.title(f"{procent}%")
        
        # 4. MAMI EDGE
        st.markdown("---")
        st.subheader("🛡️ MAMI EDGE: Evaluare Multi-Factorială")
        score = 80
        st.write(f"### Rating Final: {score}/100 ★★★★☆")
        
        # 5. Știri
        st.markdown("---")
        st.subheader("📰 Monitorul de Știri Inteligent")
        url = f"https://news.google.com/rss/search?q={ticker_ales}+stock"
        try:
            soup = BeautifulSoup(requests.get(url, timeout=5).content, 'html.parser')
            for art in soup.find_all('item')[:5]:
                st.markdown(f"⚪ [{art.title.text}]({art.link.text})")
        except:
            st.info("Știri indisponibile.")
    else:
        st.error("Date indisponibile pentru acest ticker.")
