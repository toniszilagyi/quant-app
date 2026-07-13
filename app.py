import streamlit as st
import yfinance as yf
import numpy as np
import pandas as pd
from scipy.stats import norm
import requests
from bs4 import BeautifulSoup
import plotly.graph_objects as go

st.set_page_config(page_title="Quant Analyzer Pro", page_icon="🧠", layout="centered")

st.title("🧠 Quant Analyzer Pro")
st.markdown("Introdu tickerul unei acțiuni pentru a genera un verdict bazat pe Probabilități, Analiză Tehnică și Știri.")

ticker_ales = st.text_input("Introduceți Ticker-ul (ex: NVDA, TSLA, AAPL, AMD):", "NVDA").upper()

if st.button("🚀 Rulează Analiza Robotului"):
    with st.spinner('Se descarcă datele și se analizează piața...'):
        date_actiune = yf.Ticker(ticker_ales)
        istoric = date_actiune.history(period="1y")
        
        if istoric.empty:
            st.error(f"❌ Ticker-ul [{ticker_ales}] nu a putut fi găsit.")
        else:
            ultimul_pret = istoric['Close'].iloc[-1]
            istoric['Randament_Zilnic'] = istoric['Close'].pct_change()
            volatilitate_zilnica = istoric['Randament_Zilnic'].std()
            media_recenta = istoric['Randament_Zilnic'].tail(20).mean()
            scor_prob = norm.cdf(media_recenta / volatilitate_zilnica) * 100
            
            # Indicatori tehnici
            istoric['EMA_20'] = istoric['Close'].ewm(span=20, adjust=False).mean()
            istoric['EMA_50'] = istoric['Close'].ewm(span=50, adjust=False).mean()
            
            schimbare = istoric['Close'].diff()
            cresteri = schimbare.clip(lower=0)
            scaderi = -1 * schimbare.clip(upper=0)
            ema_cresteri = cresteri.ewm(span=14, adjust=False).mean()
            ema_scaderi = scaderi.ewm(span=14, adjust=False).mean()
            rs = ema_cresteri / (ema_scaderi + 1e-10)
            rsi = 100 - (100 / (1 + rs))
            
            ema20_acum = istoric['EMA_20'].iloc[-1]
            ema50_acum = istoric['EMA_50'].iloc[-1]
            rsi_acum = rsi.iloc[-1]
            
            puncte_tehnice = 0
            if ultimul_pret > ema20_acum: puncte_tehnice += 1
            if ema20_acum > ema50_acum: puncte_tehnice += 1
            if rsi_acum < 70 and rsi_acum > 30: puncte_tehnice += 1
            scor_tehnic = (puncte_tehnice / 3) * 100
            
            # Știri
            url = f"https://news.google.com/rss/search?q={ticker_ales}+stock&hl=en-US&gl=US&ceid=US:en"
            raspuns = requests.get(url)
            scor_stiri = 50.0
            
            if raspuns.status_code == 200:
                soup = BeautifulSoup(raspuns.content, 'html.parser')
                articole = soup.find_all('item')[:8]
                cuvinte_bullish = ['bullish', 'growth', 'buy', 'surge', 'beat', 'earnings', 'upgraded', 'success', 'ai', 'demand', 'rally', 'profit', 'higher']
                cuvinte_bearish = ['bearish', 'sell', 'drop', 'fall', 'miss', 'risk', 'down', 'investigation', 'short', 'loss', 'slump', 'lower', 'inflation', 'cut']
                
                scor_total = 0
                for art in articole:
                    titlu = art.title.text.lower()
                    for cuvant in cuvinte_bullish:
                        if cuvant in titlu: scor_total += 1
                    for cuvant in cuvinte_bearish:
                        if cuvant in titlu: scor_total -= 1
                
                if scor_total > 5: scor_total = 5
                if scor_total < -5: scor_total = -5
                scor_stiri = 50 + (scor_total * 10)

            scor_global = (scor_prob * 0.30) + (scor_tehnic * 0.40) + (scor_stiri * 0.30)
            
            if scor_global >= 75: recomandare, subtext, culoare_box = "🚀 STRONG BUY", "Aliniere perfectă între indicatori!", "#d4edda"
            elif scor_global >= 55: recomandare, subtext, culoare_box = "📈 BUY", "Context general pozitiv. Atenție la risc.", "#d4edda"
            elif scor_global >= 45: recomandare, subtext, culoare_box = "🟡 HOLD", "Indicatori contradictorii. Așteaptă confirmări.", "#fff3cd"
            elif scor_global >= 30: recomandare, subtext, culoare_box = "📉 SELL", "Presiune mare la vânzare.", "#f8d7da"
            else: recomandare, subtext, culoare_box = "💥 STRONG SELL", "Semnale negative masive. Evită.", "#f8d7da"
            
            st.markdown(f'''
            <div style="background-color: {culoare_box}; padding: 20px; border-radius: 10px; border: 1px solid #ccc; text-align: center; margin-bottom: 25px;">
                <h2 style="margin: 0; color: black;">Verdict Final: {recomandare}</h2>
                <p style="margin: 5px 0 0 0; font-size: 16px; color: #333;">{subtext}</p>
                <h1 style="margin: 10px 0 0 0; font-size: 48px; color: black;">{scor_global:.1f}%</h1>
            </div>
            ''', unsafe_allow_html=True)
            
            col1, col2, col3 = st.columns(3)
            col1.metric("💰 Preț Actual", f"{ultimul_pret:.2f} $")
            col2.metric("⏱️ Indicator RSI", f"{rsi_acum:.1f}")
            col3.metric("📊 Volatilitate", f"{volatilitate_zilnica*100:.2f} %")
            
            st.markdown("---")
            st.subheader("Defalcarea scorurilor pe Motoare:")
            st.progress(int(scor_prob), text=f"🔢 Motor Probabilități: {scor_prob:.1f}%")
            st.progress(int(scor_tehnic), text=f"📈 Motor Analiză Tehnică: {scor_tehnic:.1f}%")
            st.progress(int(scor_stiri), text=f"📰 Motor Sentiment Știri: {scor_stiri:.1f}%")
            
            st.markdown("---")
            st.subheader("📊 Grafic Avansat Candlestick (Ultimele 90 de zile)")
            
            # Filtram ultimele 90 de zile pentru un grafic aerisit
            date_grafic = istoric.tail(90)
            
            fig = go.Figure()
            
            # Adaugam lumandarile (Open, High, Low, Close)
            fig.add_trace(go.Candlestick(
                x=date_grafic.index,
                open=date_grafic['Open'],
                high=date_grafic['High'],
                low=date_grafic['Low'],
                close=date_grafic['Close'],
                name='Preț Acțiune'
            ))
            
            # Adaugam liniile EMA pentru strategii tehnice
            fig.add_trace(go.Scatter(x=date_grafic.index, y=date_grafic['EMA_20'], mode='lines', name='EMA 20 (Scurt)', line=dict(color='orange', width=1.5)))
            fig.add_trace(go.Scatter(x=date_grafic.index, y=date_grafic['EMA_50'], mode='lines', name='EMA 50 (Lung)', line=dict(color='blue', width=1.5)))
            
            # Design grafic curat
            fig.update_layout(
                margin=dict(l=10, r=10, t=10, b=10),
                xaxis_rangeslider_visible=False,
                template="plotly_white",
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )
            
            st.plotly_chart(fig, use_container_width=True)
