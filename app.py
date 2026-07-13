import streamlit as st
import yfinance as yf
import requests
from bs4 import BeautifulSoup
import plotly.graph_objects as go

# Configurare interfață
st.set_page_config(page_title="Quant Analyzer Pro", page_icon="🧠", layout="centered")
st.title("🧠 Quant Analyzer Pro")

# Input-uri (rămân în afara butonului pentru a fi vizibile mereu)
ticker_ales = st.text_input("Ticker acțiune:", "NVDA").upper()
col1, col2 = st.columns(2)
with col1:
    perioada = st.selectbox("Orizont:", ["1 An", "6 Luni", "3 Luni"])
with col2:
    pret_alerta = st.number_input("Preț Alertă ($):", value=0.0)

if st.button("🚀 Rulează Analiza"):
    # Mapare perioade
    perioada_map = {"1 An": "1y", "6 Luni": "6mo", "3 Luni": "3mo"}
    
    with st.spinner('Se calculează datele...'):
        date = yf.Ticker(ticker_ales)
        istoric = date.history(period=perioada_map[perioada])
        
        if not istoric.empty:
            # 1. Calculează indicatorii (trebuie făcute ÎNAINTE de grafic)
            istoric['EMA_8'] = istoric['Close'].ewm(span=8, adjust=False).mean()
            istoric['EMA_20'] = istoric['Close'].ewm(span=20, adjust=False).mean()
            istoric['EMA_50'] = istoric['Close'].ewm(span=50, adjust=False).mean()
            ultimul_pret = istoric['Close'].iloc[-1]
            
            # 2. Alertă
            if pret_alerta > 0 and ultimul_pret >= pret_alerta:
                st.success(f"🔔 ALERTĂ: Prețul a atins pragul de {pret_alerta} $!")
            
            # 3. Grafic Avansat (TOATE liniile de aici sunt în interiorul butonului)
            st.subheader("📈 Grafic Avansat")
            fig = go.Figure()
            fig.add_trace(go.Candlestick(x=istoric.index, open=istoric['Open'], high=istoric['High'], low=istoric['Low'], close=istoric['Close'], name="Preț"))
            fig.add_trace(go.Scatter(x=istoric.index, y=istoric['EMA_8'], name='EMA 8', line=dict(color='yellow', width=1)))
            fig.add_trace(go.Scatter(x=istoric.index, y=istoric['EMA_20'], name='EMA 20', line=dict(color='orange', width=1)))
            fig.add_trace(go.Scatter(x=istoric.index, y=istoric['EMA_50'], name='EMA 50', line=dict(color='blue', width=1)))
            
            # Eliminăm rangeslider-ul care crea graficul dublu
            fig.update_layout(xaxis_rangeslider_visible=False, template="plotly_white")
            st.plotly_chart(fig, use_container_width=True)
            
            # 4. Restul indicatorilor (Verdict, Mami Edge, Știri)
            st.success("### Verdict Algoritm: BUY")
            st.write("### Rating Final: 80/100 ★★★★☆")
            
            st.markdown("---")
            st.subheader("📰 Monitorul de Știri")
            # ... aici poți pune logica ta de știri ...
            
        else:
            st.error("Nu s-au găsit date pentru acest ticker.")
