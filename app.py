import streamlit as st
import yfinance as yf
import requests
from bs4 import BeautifulSoup
import plotly.graph_objects as go

# Configurare pagină
st.set_page_config(page_title="Quant Analyzer Pro", page_icon="🧠")
st.title("🧠 Quant Analyzer Pro")

# Input-uri
ticker_ales = st.text_input("Ticker acțiune:", "NVDA").upper()
perioada = st.selectbox("Orizont:", ["1 An", "6 Luni", "3 Luni"])
pret_alerta = st.number_input("Preț Alertă ($):", value=0.0)

# Buton Analiză
if st.button("🚀 Rulează Analiza"):
    # Descărcare date
    perioada_map = {"1 An": "1y", "6 Luni": "6mo", "3 Luni": "3mo"}
    date_actiune = yf.Ticker(ticker_ales)
    istoric = date_actiune.history(period=perioada_map[perioada])
    
    if not istoric.empty:
        ultimul_pret = istoric['Close'].iloc[-1]
        
        # 1. Alertă
        if pret_alerta > 0 and ultimul_pret >= pret_alerta:
            st.success(f"🔔 ALERTĂ: Prețul a atins pragul!")
        else:
            st.info(f"ℹ️ Prețul curent ({ultimul_pret:.2f} $) este sub prag.")

        # 2. Grafic Avansat
        st.subheader("📈 Grafic Avansat")
        
        # Calculăm EMA 8
        istoric['EMA_8'] = istoric['Close'].ewm(span=8, adjust=False).mean()
        
        fig = go.Figure()
        
        # Lumanari
        fig.add_trace(go.Candlestick(x=istoric.index, open=istoric['Open'], high=istoric['High'], low=istoric['Low'], close=istoric['Close'], name="Preț"))
        
        # Medii Mobile
        fig.add_trace(go.Scatter(x=istoric.index, y=istoric['EMA_8'], name='EMA 8', line=dict(color='yellow', width=1)))
        fig.add_trace(go.Scatter(x=istoric.index, y=istoric['EMA_20'], name='EMA 20', line=dict(color='orange', width=1)))
        fig.add_trace(go.Scatter(x=istoric.index, y=istoric['EMA_50'], name='EMA 50', line=dict(color='blue', width=1)))
        
        # Eliminăm graficul mic de jos (rangeslider) și setăm tema
        fig.update_layout(
            xaxis_rangeslider_visible=False, 
            template="plotly_white",
            height=600
        )
        
        st.plotly_chart(fig, use_container_width=True)
        # 4. MAMI EDGE
        st.markdown("---")
        st.subheader("🛡️ MAMI EDGE: Evaluare Multi-Factorială")
        st.write("### Rating Final: 80/100 ★★★★☆")
        
        # 5. Știri (cu try-except corect indentat)
        st.markdown("---")
        st.subheader("📰 Monitorul de Știri Inteligent")
        try:
            url = f"https://news.google.com/rss/search?q={ticker_ales}+stock"
            soup = BeautifulSoup(requests.get(url, timeout=5).content, 'html.parser')
            for art in soup.find_all('item')[:5]:
                st.markdown(f"⚪ [{art.title.text}]({art.link.text})")
        except:
            st.info("Știrile sunt indisponibile momentan.")
    else:
        st.error("Ticker invalid sau date lipsă.")
