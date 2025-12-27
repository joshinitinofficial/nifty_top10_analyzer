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

# ---------------------------------
# CUSTOM CSS
# ---------------------------------
st.markdown("""
<style>
div[data-testid="column"] {
    display: flex;
    align-items: center;
}

.row-box {
    height: 75px;
    display: flex;
    align-items: center;
}

.stock-text {
    font-size: 18px;
    font-weight: 700;
}

.ltp-text {
    font-size: 16px;
    color: #4da6ff;   /* sky blue */
    font-weight: 600;
}

.lot-text {
    font-size: 16px;
}

.contract-text {
    font-size: 16px;
    color: #2ecc71;   /* green */
    font-weight: 600;
}

.ath-text {
    font-size: 16px;
    color: #ff6b6b;   /* light red */
    font-weight: 600;
}

.row-separator {
    border-bottom: 1px solid #2a2a2a;
    margin: 6px 0 10px 0;
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<h2 style='text-align: center; margin-top: 10px;'>
📊 NIFTY Top 10 Equal Weight – Live Snapshot
</h2>
""", unsafe_allow_html=True)


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
    "RELIANCE": 500,
    "TCS": 175,
    "HDFCBANK": 550,
    "INFY": 400,
    "ICICIBANK": 700,
    "HINDUNILVR": 300,
    "ITC": 1600,
    "LT": 175,
    "SBIN": 750,
    "BHARTIARTL": 475
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

    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    df = df.dropna()
    return df


def draw_small_chart(df):
    last_year = df[df.index >= (datetime.today() - timedelta(days=365))]

    fig, ax = plt.subplots(figsize=(1.4, 0.6))  # 🔽 50% smaller
    ax.plot(last_year["Close"], linewidth=1.2)
    ax.margins(x=0)
    ax.axis("off")

    st.pyplot(fig, clear_figure=True)

# ---------------------------------
# TABLE HEADER
# ---------------------------------
headers = st.columns([1.6, 1.3, 1, 1.6, 1.4, 1.4])
headers[0].markdown("**Stock**")
headers[1].markdown("**LTP**")
headers[2].markdown("**Lot Size**")
headers[3].markdown("**Contract Value (₹)**")
headers[4].markdown("**% Below ATH**")
headers[5].markdown("**Chart**")

st.divider()

# ---------------------------------
# MAIN LOOP
# ---------------------------------
for stock, symbol in STOCKS.items():
    df = fetch_stock_data(symbol)

    if df.empty or not all(col in df.columns for col in ["Close", "High"]):
        row = st.columns([1.6, 1.3, 1, 1.6, 1.4, 1.4])
        row[0].markdown(f"<div class='row-box stock-text'>{stock}</div>", unsafe_allow_html=True)
        row[1].markdown("<div class='row-box'>N/A</div>", unsafe_allow_html=True)
        row[2].markdown(f"<div class='row-box'>{LOT_SIZES.get(stock,0)}</div>", unsafe_allow_html=True)
        row[3].markdown("<div class='row-box'>N/A</div>", unsafe_allow_html=True)
        row[4].markdown("<div class='row-box'>Data unavailable</div>", unsafe_allow_html=True)
        row[5].markdown("<div class='row-box'>—</div>", unsafe_allow_html=True)
        st.markdown("<div class='row-separator'></div>", unsafe_allow_html=True)
        continue

    prev_close = float(df["Close"].iloc[-1])
    ath = float(df["High"].max())
    pct_below_ath = round(((ath - prev_close) / ath) * 100, 2)

    lot = LOT_SIZES.get(stock, 0)
    contract_value = int(prev_close * lot)

    row = st.columns([1.6, 1.3, 1, 1.6, 1.4, 1.4])

    row[0].markdown(f"<div class='row-box stock-text'>{stock}</div>", unsafe_allow_html=True)
    row[1].markdown(f"<div class='row-box ltp-text'>{round(prev_close,2)}</div>", unsafe_allow_html=True)
    row[2].markdown(f"<div class='row-box lot-text'>{lot}</div>", unsafe_allow_html=True)
    row[3].markdown(f"<div class='row-box contract-text'>₹ {contract_value:,}</div>", unsafe_allow_html=True)
    row[4].markdown(f"<div class='row-box ath-text'>{pct_below_ath} %</div>", unsafe_allow_html=True)

    with row[5]:
        draw_small_chart(df)

    st.markdown("<div class='row-separator'></div>", unsafe_allow_html=True)

st.caption("Data Source: Yahoo Finance | Timeframe: Daily")
