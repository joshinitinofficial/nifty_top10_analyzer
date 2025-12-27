import streamlit as st
import yfinance as yf
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
# CUSTOM CSS (ALIGNMENT + TEXT SIZE)
# ---------------------------------
st.markdown("""
<style>
/* Center everything vertically inside columns */
div[data-testid="column"] {
    display: flex;
    align-items: center;
}

/* Row container */
.row-box {
    height: 90px;
    display: flex;
    align-items: center;
}

/* Text styles */
.stock-text {
    font-size: 18px;
    font-weight: 700;
}

.cell-text {
    font-size: 16px;
}

/* Thin row separator */
.row-separator {
    border-bottom: 1px solid #2a2a2a;
    margin: 6px 0 10px 0;
}
</style>
""", unsafe_allow_html=True)

st.markdown("## 📊 NIFTY Top 10 Equal Weight – Live Snapshot")

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

    fig, ax = plt.subplots(figsize=(2.8, 1.3))
    ax.plot(last_year["Close"], linewidth=1.5)
    ax.margins(x=0)
    ax.axis("off")

    st.pyplot(fig, clear_figure=True)

# ---------------------------------
# TABLE HEADER
# ---------------------------------
headers = st.columns([1.6, 1.3, 1, 1.6, 1.4, 2])
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

    row = st.columns([1.6, 1.3, 1, 1.6, 1.4, 2])

    row[0].markdown(
        f"<div class='row-box stock-text'>{stock}</div>",
        unsafe_allow_html=True
    )
    row[1].markdown(
        f"<div class='row-box cell-text'>{round(prev_close,2)}</div>",
        unsafe_allow_html=True
    )
    row[2].markdown(
        f"<div class='row-box cell-text'>{lot}</div>",
        unsafe_allow_html=True
    )
    row[3].markdown(
        f"<div class='row-box cell-text'>₹ {contract_value:,}</div>",
        unsafe_allow_html=True
    )
    row[4].markdown(
        f"<div class='row-box cell-text'>{pct_below_ath} %</div>",
        unsafe_allow_html=True
    )

    with row[5]:
        draw_small_chart(df)

    # thin separator after each row
    st.markdown("<div class='row-separator'></div>", unsafe_allow_html=True)

st.caption("Data Source: Yahoo Finance | Timeframe: Daily")
