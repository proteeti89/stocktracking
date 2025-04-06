import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import requests
from textblob import TextBlob

NEWS_API_KEY = "3bef3981ae4d4f36b00beb6e244a3c1b"


def label_with_tooltip(label: str, tooltip: str) -> str:
    return f"""<span title=\"{tooltip}\" style=\"text-decoration: dotted underline; cursor: help;\">{label}</span>"""

def format_large_number(n):
    if n is None:
        return "N/A"
    elif n >= 1e12:
        return f"{n / 1e12:.2f}T"
    elif n >= 1e9:
        return f"{n / 1e9:.2f}B"
    elif n >= 1e6:
        return f"{n / 1e6:.2f}M"
    else:
        return str(n)

def fetch_news_sentiment(symbol):
    url = f"https://newsapi.org/v2/everything?q={symbol}&sortBy=publishedAt&apiKey={NEWS_API_KEY}&language=en"
    try:
        response = requests.get(url)
        articles = response.json().get("articles", [])[:5]
        sentiments = []

        for article in articles:
            title = article["title"]
            analysis = TextBlob(title)
            sentiments.append((title, analysis.sentiment.polarity))

        return sentiments
    except Exception as e:
        return [("Error fetching news", 0.0)]

def compute_rsi(data, window=14):
    delta = data["Close"].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

st.set_page_config(page_title="📈 Stock Info Tracker", layout="centered")
st.title("📈 Stock Info Tracker")

symbols = st.text_input("Enter stock symbols separated by commas (e.g., AAPL, TSLA, MSFT)")

if symbols:
    symbol_list = [s.strip().upper() for s in symbols.split(",") if s.strip()]

    for symbol in symbol_list:
        st.subheader(f"📊 {symbol}")
        stock = yf.Ticker(symbol)
        data = stock.info

        price = data.get("regularMarketPrice")
        market_cap = format_large_number(data.get("marketCap"))
        pe_ratio = data.get("trailingPE")
        volume = format_large_number(data.get("volume"))
        last_updated = data.get("regularMarketTime")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown(label_with_tooltip("💰 Current Price", "The most recent trading price for the stock."), unsafe_allow_html=True)
            st.write(f"${price:.2f}" if price else "N/A")

            st.markdown(label_with_tooltip("💹 P/E Ratio", "Price-to-Earnings ratio: shows if the stock is over- or under-valued."), unsafe_allow_html=True)
            st.write(pe_ratio if pe_ratio else "N/A")

        with col2:
            st.markdown(label_with_tooltip("📈 Market Cap", "Total value of all outstanding shares."), unsafe_allow_html=True)
            st.write(market_cap)

            st.markdown(label_with_tooltip("🔁 Volume", "Number of shares traded today."), unsafe_allow_html=True)
            st.write(volume)

        # Historical data for indicators
        hist = stock.history(period="6mo")

        # Moving Averages
        hist["MA20"] = hist["Close"].rolling(window=20).mean()
        hist["MA50"] = hist["Close"].rolling(window=50).mean()
        hist["RSI"] = compute_rsi(hist)

        st.markdown("**📉 6-Month Price Chart with Moving Averages**")
        fig, ax = plt.subplots()
        ax.plot(hist.index, hist["Close"], label="Close Price", color="blue")
        ax.plot(hist.index, hist["MA20"], label="20-day MA", linestyle="--", color="orange")
        ax.plot(hist.index, hist["MA50"], label="50-day MA", linestyle="--", color="green")
        ax.set_xlabel("Date")
        ax.set_ylabel("Price ($)")
        ax.legend()
        st.pyplot(fig)

        # RSI Chart
        st.markdown("**📊 RSI (Relative Strength Index)**")
        fig_rsi, ax_rsi = plt.subplots()
        ax_rsi.plot(hist.index, hist["RSI"], label="RSI", color="purple")
        ax_rsi.axhline(70, color='red', linestyle='--', linewidth=1, label='Overbought (70)')
        ax_rsi.axhline(30, color='green', linestyle='--', linewidth=1, label='Oversold (30)')
        ax_rsi.set_ylim(0, 100)
        ax_rsi.set_ylabel("RSI")
        ax_rsi.set_xlabel("Date")
        ax_rsi.legend()
        st.pyplot(fig_rsi)

        # News Sentiment Analysis
        st.markdown("**📰 Recent News Sentiment**")
        sentiments = fetch_news_sentiment(symbol)
        for headline, polarity in sentiments:
            sentiment_label = "🔺 Positive" if polarity > 0 else ("🔻 Negative" if polarity < 0 else "⚪ Neutral")
            st.write(f"{sentiment_label}: {headline}")

    with st.expander("📘 What do these metrics mean?"):
        st.markdown("""
        - **💰 Current Price**: The last trading price of the stock.
        - **📈 Market Cap**: Total market value of all company shares.
        - **💹 P/E Ratio**: Price relative to earnings. Helps compare stock valuations.
        - **🔁 Volume**: Number of shares traded today.
        - **20-day/50-day MA**: Moving Averages smooth out price trends over time.
        - **📊 RSI**: Momentum indicator showing whether a stock may be overbought or oversold.
        - **📰 News Sentiment**: Analyzed from recent article headlines using basic NLP.
        """)
