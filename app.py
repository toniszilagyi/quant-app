import streamlit as st
import yfinance as yf
import numpy as np
import pandas as pd
from scipy.stats import norm
import requests
from bs4 import BeautifulSoup
import plotly.graph_objects as go

# Configurare pagină modernă
st.set_page_config(page_title="Quant Analyzer Pro", page_icon="🧠", layout="centered")

# CSS pentru un look profesional
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    h1, h2, h3 { color: #ffffff !important; }
    .stButton>button { background-color: #ff4b4b; color: white; border-radius: 8px; width: 100%; font-weight: bold; }
    .stButton>button:hover { background-color: #ff3333; }
    </style>
""", unsafe_allow_html=True)

st.title("🧠 Quant Analyzer Pro")

# Secțiunea de input
col_input1, col_input2 = st.columns([2, 1])
with col_input1:
    ticker_ales = st.text_input("Ticker acțiune:", "NVDA").upper()
with col_input2:
    perioada = st.selectbox("Orizont:", ["1 An", "6 Luni", "3 Luni"])
    pret_alerta = st.number_input("Preț Alertă ($):", min_value=0.0, value=0.0, step=0.1)

perioada_map = {"1 An": "1y", "6 Luni": "6mo", "3 Luni": "3mo"}

if st.button("🚀 Rulează Analiza Robotului"):
    with st.spinner('Se analizează piața...'):
        date_actiune = yf.Ticker(ticker_ales)
        istoric = date_actiune.history(period=perioada_map[perioada])
        
        if istoric.empty:
            st.error("Ticker invalid sau date indisponibile.")
        else:
            ultimul_pret = istoric['Close'].iloc[-1]
            
            # --- LOGICA ALERTĂ ---
            if pret_alerta > 0:
                if ultimul_pret >= pret_alerta:
                    st.success(f"🔔 ALERTĂ ACTIVATĂ: Prețul actual ({ultimul_pret:.2f} $) a atins/depășit pragul de {pret_alerta:.2f} $!")
                else:
                    st.info(f"ℹ️ Prețul curent ({ultimul_pret:.2f} $) este sub pragul de alertă ({pret_alerta:.2f} $).")

            # --- CALCUL INDICATORI ---
            istoric['Randament_Zilnic'] = istoric['Close'].pct_change()
            volatilitate_zilnica = istoric['Randament_Zilnic'].std()
            media_recenta = istoric['Randament_Zilnic'].tail(20).mean()
            scor_prob = norm.cdf(media_recenta / volatilitate_zilnica) * 100
            
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
            scor_tehnic = ((ultimul_pret > istoric['EMA_20'].iloc[-1]) + (istoric['EMA_20'].iloc[-1] > istoric['EMA_50'].iloc[-1]) + (30 < rsi_acum < 70)) * 33.3
            
            # --- ȘTIRI ---
            url = f"https://news.google.com/rss/search?q={ticker_ales}+stock&hl=en-US&gl=US&ceid=US:en"
            scor_stiri = 50.0
            try:
                raspuns = requests.get(url)
                soup = BeautifulSoup(raspuns.content, 'html.parser')
                articole = soup.find_all('item')[:5]
                stiri_gasite = [art.title.text for art in articole]
                scor_stiri = 65.0 # Simplificat pentru demo
            except:
                stiri_gasite = []

            scor_global = (scor_prob * 0.3) + (scor_tehnic * 0.4) + (scor_stiri * 0.3)
            
            # --- AFIȘARE REZULTATE ---
            st.subheader(f"Verdict Global: {scor_global:.1f}%")
            st.metric("Preț Actual", f"{ultimul_pret:.2f} $")
            
            fig = go.Figure()
            fig.add_trace(go.Candlestick(x=istoric.index, open=istoric['Open'], high=istoric['High'], low=istoric['Low'], close=istoric['Close']))
            fig.update_layout(template="plotly_dark", xaxis_rangeslider_visible=False)
            st.plotly_chart(fig, use_container_width=True)
            
            st.write("Știri recente:", stiri_gasite)
