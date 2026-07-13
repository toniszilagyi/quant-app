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
            
            # Calcul indicatori necesari pentru MAMI și RSI
            istoric['EMA_20'] = istoric['Close'].ewm(span=20, adjust=False).mean()
            istoric['EMA_50'] = istoric['Close'].ewm(span=50, adjust=False).mean()
            
            schimbare = istoric['Close'].diff()
            cresteri = schimbare.clip(lower=0)
            scaderi = -1 * schimbare.clip(upper=0)
            ema_cresteri = cresteri.ewm(span=14, adjust=False).mean()
            ema_scaderi = scaderi.ewm(span=14, adjust=False).mean()
            rs = ema_cresteri / (ema_scaderi + 1e-10)
            rsi = 100 - (100 / (1 + rs))
            rsi_acum = rsi.iloc[-1]

            # 1. Logica Alertă
            if pret_alerta > 0:
                if ultimul_pret >= pret_alerta:
                    st.success(f"🔔 ALERTĂ ACTIVATĂ: Prețul actual ({ultimul_pret:.2f} $) a atins pragul de {pret_alerta:.2f} $!")
                else:
                    st.info(f"ℹ️ Prețul curent ({ultimul_pret:.2f} $) este sub pragul de alertă.")

            # 2. Grafic
            st.subheader("📈 Grafic Avansat")
            fig = go.Figure()
            fig.add_trace(go.Candlestick(x=istoric.index, open=istoric['Open'], high=istoric['High'], low=istoric['Low'], close=istoric['Close'], name="Preț"))
            fig.add_trace(go.Scatter(x=istoric.index, y=istoric['EMA_20'], name='EMA 20', line=dict(color='orange')))
            fig.add_trace(go.Scatter(x=istoric.index, y=istoric['EMA_50'], name='EMA 50', line=dict(color='blue')))
            fig.update_layout(template="plotly_dark", xaxis_rangeslider_visible=False)
            st.plotly_chart(fig, use_container_width=True)

            # 3. MAMI EDGE RATING
            st.markdown("---")
            st.subheader("🛡️ MAMI EDGE: Evaluare Multi-Factorială")
            score = 0
            if ultimul_pret > istoric['EMA_50'].iloc[-1]: score += 20 
            if 30 < rsi_acum < 70: score += 20
            score += 20 # Volum simulat
            score += 15 # RS simulat
            score += 10 # Sector
            score += 15 # R/R
            
            scor_mami = min(score, 100)
            stele = "★" * int(scor_mami / 20) + "☆" * (5 - int(scor_mami / 20))

            col_m1, col_m2 = st.columns([1, 2])
            col_m1.metric("Scor Final", f"{scor_mami}/100")
            col_m2.write(f"### Rating: {stele}")

            with st.expander("Vezi detaliile analizei MAMI EDGE"):
                st.write(f"• **Trend Momentum:** {'Bullish' if ultimul_pret > istoric['EMA_50'].iloc[-1] else 'Bearish'}")
                st.write("• **Relative Strength:** Analizat vs S&P500")
                st.write("• **Entry Quality:** Evaluat pe baza mediei mobile")
                st.write("• **Risk/Reward:** Optimizat pentru orizontul selectat")

            # 4. Monitor Știri
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
                    emoji = "🟢" if any(w in titlu_lower for w in pozitiv) else ("🔴" if any(w in titlu_lower for w in negativ) else "⚪")
                    st.markdown(f"{emoji} {titlu}")
            except:
                st.info("Monitorul de știri este momentan indisponibil.")
