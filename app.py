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
            
            # --- MOTOR DE ȘTIRI AVANSAT (ANALIZĂ DE SENTIMENT PONDERATĂ) ---
            url = f"https://news.google.com/rss/search?q={ticker_ales}+stock&hl=en-US&gl=US&ceid=US:en"
            raspuns = requests.get(url)
            scor_stiri = 50.0
            stiri_gasite = []
            
            if raspuns.status_code == 200:
                soup = BeautifulSoup(raspuns.content, 'html.parser')
                articole = soup.find_all('item')[:10]
                
                # Dicționar ponderat de sentiment financiar
                词典_pozitiv = {
                    'bullish': 3, 'breakout': 3, 'surge': 3, 'soars': 3, 'shatters': 3,
                    'buy': 2, 'growth': 2, 'beat': 2, 'earnings': 1, 'upgraded': 2, 
                    'rally': 2, 'profit': 2, 'higher': 1, 'ai': 1, 'demand': 1, 'leads': 1
                }
                词典_negativ = {
                    'bankruptcy': -4, 'crash': -4, 'investigation': -3, 'fraud': -3,
                    'bearish': -3, 'slump': -3, 'miss': -2, 'drop': -2, 'fall': -2,
                    'sell': -2, 'risk': -1, 'down': -1, 'loss': -1, 'lower': -1, 'cut': -2
                }
                
                scor_total_sentiment = 0
                numar_cuvinte_cheie = 0
                
                for art in articole:
                    titlu = art.title.text
                    titlu_lower = titlu.lower()
                    sentiment_articol = 0
                    
                    for cuvant, pondere in 词典_pozitiv.items():
                        if cuvant in titlu_lower:
                            sentiment_articol += pondere
                            numar_cuvinte_cheie += 1
                    for cuvant, pondere in 词典_negativ.items():
                        if cuvant in titlu_lower:
                            sentiment_articol += pondere
                            numar_cuvinte_cheie += 1
                    
                    scor_total_sentiment += sentiment_articol
                    
                    # Salvăm titlul și un indicator vizual pentru utilizator
                    if sentiment_articol > 0: emoji_stire = "🟢"
                    elif sentiment_articol < 0: emoji_stire = "🔴"
                    else: emoji_stire = "⚪"
                    stiri_gasite.append(f"{emoji_stire} {titlu}")
                
                # Calculăm scorul final de știri pe o scară de la 0 la 100
                if numar_cuvinte_cheie > 0:
                    grosier_scor = 50 + (scor_total_sentiment * 7)
                    scor_stiri = max(0, min(100, grosier_scor))
                else:
                    scor_stiri = 50.0

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
            st.progress(int(scor_stiri), text=f"📰 Motor Sentiment Știri (Ponderat): {scor_stiri:.1f}%")
            
            st.markdown("---")
            st.subheader("📊 Grafic Avansat Candlestick (Fără întreruperi de weekend)")
            
            date_grafic = istoric.tail(90).copy()
            # Transformăm indexul în text formatat pentru a elimina golurile de weekend din Plotly
            date_grafic['Data_Str'] = date_grafic.index.strftime('%Y-%m-%d')
            
            fig = go.Figure()
            
            fig.add_trace(go.Candlestick(
                x=date_grafic['Data_Str'],
                open=date_grafic['Open'],
                high=date_grafic['High'],
                low=date_grafic['Low'],
                close=date_grafic['Close'],
                name='Preț Acțiune'
            ))
            
            fig.add_trace(go.Scatter(x=date_grafic['Data_Str'], y=date_grafic['EMA_20'], mode='lines', name='EMA 20', line=dict(color='orange', width=1.5)))
            fig.add_trace(go.Scatter(x=date_grafic['Data_Str'], y=date_grafic['EMA_50'], mode='lines', name='EMA 50', line=dict(color='blue', width=1.5)))
            
            fig.update_layout(
                margin=dict(l=10, r=10, t=10, b=10),
                xaxis_rangeslider_visible=False,
                template="plotly_white",
                xaxis=dict(type='category', nticks=10), # Forțează Plotly să trateze axa ca pe categorii continue
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )
            st.plotly_chart(fig, use_container_width=True)

            # --- SECȚIUNEA NOUĂ: MONITORUL DE ȘTIRI LIVE ---
            st.markdown("---")
            st.subheader("📰 Monitorul de Știri Inteligent & Impact")
            if stiri_gasite:
                for stire in stiri_gasite:
                    st.markdown(stire)
            else:
                st.info("Nu au fost găsite știri recente care să poată fi evaluate complet.")
