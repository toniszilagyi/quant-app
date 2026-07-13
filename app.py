import streamlit as st
import yfinance as yf
import numpy as np
import pandas as pd
from scipy.stats import norm
import requests
from bs4 import BeautifulSoup
import plotly.graph_objects as go

# Configurare pagină
st.set_page_config(page_title="Quant Analyzer Pro", page_icon="🧠", layout="centered")

st.title("🧠 Quant Analyzer Pro")

col_input1, col_input2 = st.columns([2, 1])
with col_input1:
    ticker_ales = st.text_input("Ticker acțiune:", "NVDA").upper()
with col_input2:
    perioada = st.selectbox("Orizont:", ["1 An", "6 Luni", "3 Luni"])
    pret_alerta = st.number_input("Preț Alertă ($):", min_value=0.0, value=0.0, step=0.1)

perioada_map = {"1 An": "1y", "6 Luni": "6mo", "3 Luni": "3mo"}

if st.button("🚀 Rulează Analiza"):
    with st.spinner('Se descarcă datele...'):
        date_actiune = yf.Ticker(ticker_ales)
        istoric = date_actiune.history(period=perioada_map[perioada])
        
        if istoric.empty:
            st.error("Ticker invalid.")
        else:
            ultimul_pret = istoric['Close'].iloc[-1]
            
            # 1. LOGICA ALERTĂ (doar afișare, nu blochează restul)
            if pret_alerta > 0:
                if ultimul_pret >= pret_alerta:
                    st.success(f"🔔 ALERTĂ ACTIVATĂ: Prețul actual ({ultimul_pret:.2f} $) a atins/depășit pragul de {pret_alerta:.2f} $!")
                else:
                    st.info(f"ℹ️ Prețul curent ({ultimul_pret:.2f} $) este sub pragul de alertă ({pret_alerta:.2f} $).")

            # 2. CALCUL INDICATORI (Aici era problema probabil)
            istoric['EMA_20'] = istoric['Close'].ewm(span=20, adjust=False).mean()
            istoric['EMA_50'] = istoric['Close'].ewm(span=50, adjust=False).mean()
            
            # 3. AFIȘARE GRAFIC (Acesta trebuie să fie mereu vizibil)
            st.subheader("📈 Grafic Avansat")
            fig = go.Figure()
            fig.add_trace(go.Candlestick(x=istoric.index, open=istoric['Open'], high=istoric['High'], low=istoric['Low'], close=istoric['Close'], name="Preț"))
            fig.add_trace(go.Scatter(x=istoric.index, y=istoric['EMA_20'], name='EMA 20', line=dict(color='orange')))
            fig.add_trace(go.Scatter(x=istoric.index, y=istoric['EMA_50'], name='EMA 50', line=dict(color='blue')))
            fig.update_layout(template="plotly_dark", xaxis_rangeslider_visible=False)
            st.plotly_chart(fig, use_container_width=True)

            # 4. AFIȘARE ȘTIRI (dacă vrei să le cureți, poți itera așa)
st.markdown("---")
st.subheader("📰 Monitorul de Știri Inteligent & Impact")
pozitiv = ['bullish', 'breakout', 'surge', 'soars', 'buy', 'growth', 'beat', 'upgraded', 'rally', 'profit', 'ai', 'demand']
negativ = ['bankruptcy', 'crash', 'investigation', 'fraud', 'bearish', 'slump', 'miss', 'drop', 'fall', 'sell', 'loss', 'down', 'cut']
url = f"https://news.google.com/rss/search?q={ticker_ales}+stock&hl=en-US&gl=US&ceid=US:en"
try:
    raspuns = requests.get(url, timeout=5)
    soup = BeautifulSoup(raspuns.content, 'html.parser')
    articole = soup.find_all('item')[:10]
    for art in articole:
        titlu = art.title.text
        titlu_lower = titlu.lower()
        if any(word in titlu_lower for word in pozitiv):
            emoji = "🟢"
        elif any(word in titlu_lower for word in negativ):
            emoji = "🔴"
        else:
            emoji = "⚪"
        st.markdown(f"{emoji} {titlu}")
except:
    st.info("Monitorul de știri este momentan indisponibil.")
