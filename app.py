import streamlit as st
import yfinance as yf
import requests
from bs4 import BeautifulSoup
import plotly.graph_objects as go

# Configurare
st.set_page_config(page_title="Quant Analyzer Pro", page_icon="🧠", layout="wide")
st.title("🧠 Quant Analyzer Pro")

# --- RADAR PIAȚĂ (Sidebar) ---
st.sidebar.title("📡 Radar Piață")
radar_list = ["NVDA", "AAPL", "TSLA", "AMD", "MSFT"]
for ticker in radar_list:
    try:
        t = yf.Ticker(ticker)
        data = t.history(period="2d")
        pret = data['Close'].iloc[-1]
        change = (data['Close'].pct_change().iloc[-1]) * 100
        st.sidebar.write(f"{'🟢' if change >= 0 else '🔴'} **{ticker}**: {pret:.2f}$ ({change:+.2f}%)")
    except: continue

# --- SCANNER AUTOMAT (Buton Sidebar) ---
st.sidebar.markdown("---")
if st.sidebar.button("🔍 Scanează Oportunități"):
    st.sidebar.write("### ✅ Top Performeri:")
    lista_scan = ["NVDA", "AAPL", "TSLA", "AMD", "MSFT"]
    for ticker in lista_scan:
        try:
            t = yf.Ticker(ticker)
            hist = t.history(period="1mo")
            if not hist.empty and hist['Close'].iloc[-1] > hist['Close'].ewm(span=50).mean().iloc[-1]:
                st.sidebar.write(f"🚀 {ticker}")
        except: continue

# --- INTERFAȚA PRINCIPALĂ ---
ticker_ales = st.text_input("Ticker acțiune:", "NVDA").upper()
if st.button("🚀 Rulează Analiza"):
    date = yf.Ticker(ticker_ales)
    istoric = date.history(period="1y")
    
    if not istoric.empty:
        # Calcul de bază pentru a nu avea erori
        ultimul_pret = istoric['Close'].iloc[-1]
        st.success(f"Analiză completă pentru {ticker_ales} - Preț: {ultimul_pret:.2f}$")
        
        # Grafic
        fig = go.Figure(data=[go.Candlestick(x=istoric.index, open=istoric['Open'], high=istoric['High'], low=istoric['Low'], close=istoric['Close'])])
        st.plotly_chart(fig, use_container_width=True)
        
        # Aici poți adăuga ulterior restul indicatorilor tăi (MAMI, ATR, etc.)
        # Asigură-te doar că sunt aliniați cu 8 spații sub acest 'if'
    else:
        st.error("Ticker invalid sau fără date.")
