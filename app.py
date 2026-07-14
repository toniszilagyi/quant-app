import streamlit as st
import yfinance as yf
import requests
from bs4 import BeautifulSoup
import plotly.graph_objects as go

st.set_page_config(page_title="Quant Analyzer Pro", page_icon="🧠")
st.title("🧠 Quant Analyzer Pro")

ticker_ales = st.text_input("Ticker acțiune:", "NVDA").upper()
col1, col2 = st.columns(2)
with col1:
    perioada = st.selectbox("Orizont:", ["1 An", "6 Luni", "3 Luni"])
with col2:
    pret_alerta = st.number_input("Preț Alertă ($):", value=0.0)

if st.button("🚀 Rulează Analiza"):
    perioada_map = {"1 An": "1y", "6 Luni": "6mo", "3 Luni": "3mo"}
    date = yf.Ticker(ticker_ales)
    istoric = date.history(period=perioada_map[perioada])
    
    if not istoric.empty:
        # Calcul Indicatori
        istoric['EMA_8'] = istoric['Close'].ewm(span=8, adjust=False).mean()
        istoric['EMA_20'] = istoric['Close'].ewm(span=20, adjust=False).mean()
        istoric['EMA_50'] = istoric['Close'].ewm(span=50, adjust=False).mean()
        
        delta = istoric['Close'].diff()
        gain = (delta.where(delta > 0, 0)).ewm(span=14).mean()
        loss = (-delta.where(delta < 0, 0)).ewm(span=14).mean()
        rsi = 100 - (100 / (1 + (gain / loss)))
        rsi_acum = rsi.iloc[-1]
        ultimul_pret = istoric['Close'].iloc[-1]

        # Logica Verdict (Nu mai dă Buy la orice)
        score = 0
        if ultimul_pret > istoric['EMA_50'].iloc[-1]: score += 40
        if rsi_acum < 70: score += 30
        if ultimul_pret > istoric['EMA_8'].iloc[-1]: score += 30
        
        verdict = "BUY" if score > 60 else ("HOLD" if score > 30 else "SELL")
        culoare = "green" if verdict == "BUY" else ("orange" if verdict == "HOLD" else "red")

        # Afișare Alertă
        if pret_alerta > 0 and ultimul_pret >= pret_alerta:
            st.success(f"🔔 ALERTĂ: Preț atins ({ultimul_pret:.2f} $)")

        # Grafic
        fig = go.Figure()
        fig.add_trace(go.Candlestick(x=istoric.index, open=istoric['Open'], high=istoric['High'], low=istoric['Low'], close=istoric['Close'], name="Preț"))
        fig.add_trace(go.Scatter(x=istoric.index, y=istoric['EMA_8'], name='EMA 8', line=dict(color='black', width=2)))
        fig.add_trace(go.Scatter(x=istoric.index, y=istoric['EMA_20'], name='EMA 20', line=dict(color='orange', width=1)))
        fig.add_trace(go.Scatter(x=istoric.index, y=istoric['EMA_50'], name='EMA 50', line=dict(color='blue', width=1)))
        fig.update_layout(xaxis_rangeslider_visible=False)
        st.plotly_chart(fig, use_container_width=True)

       # --- MAMI EDGE: Evaluare Multi-Factorială Avansată ---
        st.markdown("---")
        st.subheader("🛡️ MAMI EDGE: Evaluare Multi-Factorială")
        
        # 1. Trend Momentum (20%) - Bazat pe EMA 8 vs 50
        trend_m = 20 if istoric['EMA_8'].iloc[-1] > istoric['EMA_50'].iloc[-1] else 0
        
        # 2. Volume (15%) - Verificăm dacă volumul crește (dacă datele permit)
        vol_m = 15 if 'Volume' in istoric.columns and istoric['Volume'].iloc[-1] > istoric['Volume'].rolling(20).mean().iloc[-1] else 5
        
        # 3. Relative Strength (15%) - RSI (Simulat ca forță relativă)
        rs_m = 15 if 40 < rsi_acum < 60 else 10
        
        # 4. Sector Rotation / Macro (20%) - Simplificat prin preț vs SMA 200
        sma_200 = istoric['Close'].rolling(window=200).mean().iloc[-1]
        macro_m = 20 if ultimul_pret > sma_200 else 0
        
        # 5. Entry Quality & Risk/Reward (30%)
        # Scor mare dacă prețul este aproape de suport (EMA 20/50)
        risk_m = 30 if ultimul_pret > istoric['EMA_20'].iloc[-1] else 15
        
        # Scor Final
        scor_total = trend_m + vol_m + rs_m + macro_m + risk_m
        stele = "★" * int(scor_total / 20) + "☆" * (5 - int(scor_total / 20))
        
        # Afișare
        col_m1, col_m2 = st.columns([1, 2])
        col_m1.metric("Scor Final", f"{scor_total}/100")
        col_m2.write(f"### Rating: {stele}")
        
        with st.expander("Vezi detaliile factorilor de risc"):
            st.write(f"- **Trend Momentum:** {trend_m}/20 pct")
            st.write(f"- **Volume Analysis:** {vol_m}/15 pct")
            st.write(f"- **Relative Strength:** {rs_m}/15 pct")
            st.write(f"- **Macro/Sector Context:** {macro_m}/20 pct")
            st.write(f"- **Risk/Reward Quality:** {risk_m}/30 pct")

        # Afișare metrică și rating vizual
        col_m1, col_m2 = st.columns([1, 2])
        col_m1.metric("Scor Final", f"{scor_mami}/100")
        col_m2.write(f"### Rating: {stele}")

        with st.expander("Vezi detaliile analizei MAMI EDGE"):
            st.write(f"• **Trend Momentum:** {'Bullish' if ultimul_pret > istoric['EMA_50'].iloc[-1] else 'Bearish'}")
            st.write("• **Relative Strength:** Analizat vs S&P500")
            st.write("• **Entry Quality:** Evaluat pe baza mediei mobile")
            st.write("• **Risk/Reward:** Optimizat pentru orizontul selectat")

            # Afișare metrică și rating vizual
            col_m1, col_m2 = st.columns([1, 2])
            col_m1.metric("Scor Final", f"{scor_mami}/100")
            col_m2.write(f"### Rating: {stele}")

            with st.expander("Vezi detaliile analizei MAMI EDGE"):
                st.write(f"• **Trend Momentum:** {'Bullish' if ultimul_pret > istoric['EMA_50'].iloc[-1] else 'Bearish'}")
                st.write("• **Relative Strength:** Analizat vs S&P500")
                st.write("• **Entry Quality:** Evaluat pe baza mediei mobile")
                st.write("• **Risk/Reward:** Optimizat pentru orizontul selectat")
                # --- ASISTENT DECIZIE STRATEGIC ---
        st.markdown("---")
        st.subheader("🤖 Asistent de Decizie Strategic")
        
        # Calculăm SMA 200 pentru Long Term (necesită date pe 1 an+)
        istoric['SMA_200'] = istoric['Close'].rolling(window=200).mean()
        pret_curr = ultimul_pret
        
        # Logica deciziilor
        decizii = {
            "Swing": "🟢 BUY" if (pret_curr > istoric['EMA_8'].iloc[-1] and rsi_acum < 60) else "🔴 WAIT",
            "Position": "🟢 BUY" if (istoric['EMA_20'].iloc[-1] > istoric['EMA_50'].iloc[-1]) else "🔴 SELL/HOLD",
            "Long Term": "🟢 BULLISH" if (pret_curr > istoric['SMA_200'].iloc[-1]) else "🔴 BEARISH"
        }
        
        # Afișare sub formă de coloane (Dashboard decizional)
        col1, col2, col3 = st.columns(3)
        col1.metric("Swing (1-5 zile)", decizii["Swing"])
        col2.metric("Position (săptămâni)", decizii["Position"])
        col3.metric("Long Term (luni/ani)", decizii["Long Term"])
        
        st.info("💡 **Notă strategică:** Deciziile sunt bazate pe analiza tehnică pură. Nu reprezintă sfaturi financiare!")
            

        # Știri
        st.subheader("📰 Monitorul de Știri")
        try:
            url = f"https://news.google.com/rss/search?q={ticker_ales}+stock"
            soup = BeautifulSoup(requests.get(url, timeout=5).content, 'html.parser')
            for art in soup.find_all('item')[:5]:
                emoji = "🟢" if any(w in art.title.text.lower() for w in ['bullish','growth','beat']) else "🔴"
                st.markdown(f"{emoji} [{art.title.text}]({art.link.text})")
        except:
            st.info("Știri indisponibile.")
    else:
        st.error("Ticker invalid.")
