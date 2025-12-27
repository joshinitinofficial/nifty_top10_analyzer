import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

# ---------------------------------
# PAGE CONFIG
# ---------------------------------
st.set_page_config(
    page_title="NIFTY Top 10 Snapshot",
    layout="wide"
)

st.title("📊 NIFTY Top 10 Equal Weight – Live Snapshot")

# ---------------------------------
# USER CONFIG
# ---------------------------------

STOCKS = {
    "RELIANCE": "RELIANCE.NS",
    "TCS": "TCS.NS",
    "HDFCBANK": "HDFCBANK.NS",
    "INFY": "INFY.NS",
    "ICICIBANK": "ICICIBANK.NS",
    "HINDUNILVR": "HINDUNILVR.NS",
    "ITC": "ITC.NS",
    "LT": "LT.NS",
    "SBIN": "SBIN.NS",
    "BHARTIARTL": "BHARTIARTL.NS"
}

LOT_SIZES = {
    "RELIANCE": 100,
    "TCS": 100,
    "HDFCBANK": 100,
    "INFY": 100,
    "ICICIBANK": 100,
    "HINDUNILVR": 100,
    "ITC": 100,
    "LT": 100,
    "SBIN": 100,
    "BHARTIARTL": 100
}

# ---------------------------------
# FUNCTIONS
# ---------------------------------

@st.cache_data(ttl=3600)
def fetch_stock_data(symbol):
    df = yf.download(
        symbol,
        period="max",
        interval="1d",
        auto_adjust=False,
        progress=False
    )
    df.dropna(inplace=True)
    return df


def draw_small_chart(df):
    last_year = df[df.index >= (datetime.today() - timedelta(days=365))]

    fig, ax = plt.subplots(figsize=(3, 1))
    ax.plot(last_year["Close"], linewidth=1)
    ax.axis("off")

    st.pyplot(fig, clear_figure=True)

# ---------------------------------
# TABLE HEADER
# ---------------------------------

headers = st.columns(6)
headers[0].markdown("**Stock**")
headers[1].markdown("**Prev Close**")
headers[2].markdown("**Lot Size**")
headers[3].markdown("**Contract Value (₹)**")
headers[4].markdown("**% Below ATH**")
headers[5].markdown("**1Y Chart**")

st.divider()

# ---------------------------------
# MAIN LOOP
# ---------------------------------

for stock, symbol in STOCKS.items():
    df = fetch_stock_data(symbol)

    prev_close = float(df["Close"].iloc[-1])
    ath = float(df["High"].max())
    pct_below_ath = round(((ath - prev_close) / ath) * 100, 2)

    lot = LOT_SIZES.get(stock, 0)
    contract_value = int(prev_close * lot)

    row = st.columns(6)
    row[0].write(stock)
    row[1].write(round(prev_close, 2))
    row[2].write(lot)
    row[3].write(f"₹ {contract_value:,}")
    row[4].write(f"{pct_below_ath} %")

    with row[5]:
        draw_small_chart(df)

st.caption("Data Source: Yahoo Finance | Timeframe: Daily")
