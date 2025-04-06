import streamlit as st
import yfinance as yf
import plotly.graph_objs as go

st.set_page_config(page_title="📊 Stock Tracker", layout="centered")

st.title("📈 Stock Tracker")

ticker = st.text_input("Enter Stock Ticker (e.g. AAPL, TSLA, MSFT):", value="AAPL").upper()

if ticker:
    stock = yf.Ticker(ticker)
    
    try:
        info = stock.info
        st.subheader(f"{info['longName']} ({ticker})")
        st.write(f"📅 Market Time: {info.get('regularMarketTime')}")
        st.write(f"💰 Current Price: ${info.get('regularMarketPrice')}")
        st.write(f"📈 Market Cap: {info.get('marketCap'):,}")
        st.write(f"💹 P/E Ratio: {info.get('trailingPE')}")
        st.write(f"🔁 Volume: {info.get('volume'):,}")

        hist = stock.history(period="6mo")
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=hist.index, y=hist['Close'], mode='lines', name='Close'))
        fig.update_layout(title="Stock Price (Last 6 Months)", xaxis_title="Date", yaxis_title="Price")
        st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.error("⚠️ Could not fetch data. Check your ticker or try again later.")

