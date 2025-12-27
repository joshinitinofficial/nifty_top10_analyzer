import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta, timezone

# ---------------------------------
# PAGE CONFIG
# ---------------------------------
st.set_page_config(
    page_title="NIFTY Top 10 Snapshot",
    layout="wide"
)

# ---------------------------------
# CUSTOM CSS (STICKY HEADER + UI)
# ---------------------------------
st.markdown("""
<style>

/* Safe top padding */
.block-container {
    padding-top: 2.5rem;
}

/* Main title */
.main-title {
    text-align: center;
    margin-top: 0px;
    margin-bottom: 6px;
    font-size: 28px;
    font-weight: 700;
}

/* Last updated text */
.last-updated {
    text-align: center;
    font-size: 14px;
    color: #b0b0b0;
    margin-bottom: 22px;
}

/* Sticky table header */
.sticky-header {
    position: sticky;
    top: 70px;
    z-index: 100;
    background-color: #0e1117;
    padding-top: 8px;
    padding-bottom: 8px;
}

/* Column vertical alignment */
div[data-testid="column"] {
    display: flex;
    align-items: center;
}

/* Row layout */
.row-box {
    height: 75px;
    display: flex;
    align-items: center;
}

/* Text styles */
.stock-text {
    font-size: 18px;
    font-weight: 700;
}

.ltp-text {
    font-size: 16px;
    color: #4da6ff;
    font-weight: 600;
}

.lot-text {
    font-size: 16px;
}

.contract-text {
    font-size: 16px;
    color: #2ecc71;
    font-weight: 600;
}

.ath-text {
    font-size: 16px;
    color: #ff6b6b;
    font-weight: 600;
}

/* Row separator */
.row-separator {
    border-bottom: 1px solid #2a2a2a;
    margin: 6px 0 10px 0;
}

</style>
""", unsafe_allow_html=True)

# ---------------------------------
# TITLE + TIMESTAMP
# ---------------------------------
st.markdown("""
<div class="main-title">
📊 NIFTY Top 10 Equal Weight – Live Snapshot
</div>
""", unsafe_allow_html=True)

last_updated = datetime.now(timezone.utc).astimezone().strftime("%d %b %Y, %I:%M %p")
st.markdown(
    f"<div class='last-updated'>Last Updated: {last_updated}</div>",
    unsafe_allow_html=True
)

# ---------------------------------
# SORT CONTROLS
# ---------------------------------
sort_col1, sort_col2 = st.columns([1.5, 1.5])

with sort_col1:
    sort_by = st.selectbox(
        "Sort by",
        options=["None", "Contract Value", "% Below ATH"]
    )

with sort_col2:
    sort_order = st.selectbox(
        "Order",
        options=["Descending", "Ascending"]
    )

st.markdown("<br>", unsafe_allow_html=True)

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

    fig, ax = plt.subplots(figsize=(1.4, 0.6))
    ax.plot(last_year["Close"], linewidth=1.2)
    ax.margins(x=0)
    ax.axis("off")
    st.pyplot(fig, clear_figure=True)

# ---------------------------------
# COLLECT DATA FIRST
# ---------------------------------
rows_data = []

for stock, symbol in STOCKS.items():
    df = fetch_stock_data(symbol)

    if df.empty or not all(col in df.columns for col in ["Close", "High"]):
        continue

    prev_close = float(df["Close"].iloc[-1])
    ath = float(df["High"].max())
    pct_below_ath = round(((ath - prev_close) / ath) * 100, 2)

    lot = LOT_SIZES.get(stock, 0)
    contract_value = int(prev_close * lot)

    rows_data.append({
        "stock": stock,
        "ltp": round(prev_close, 2),
        "lot": lot,
        "contract_value": contract_value,
        "pct_below_ath": pct_below_ath,
        "df": df
    })

# ---------------------------------
# APPLY SORTING
# ---------------------------------
if sort_by != "None":
    reverse = True if sort_order == "Descending" else False

    if sort_by == "Contract Value":
        rows_data = sorted(
            rows_data,
            key=lambda x: x["contract_value"],
            reverse=reverse
        )
    elif sort_by == "% Below ATH":
        rows_data = sorted(
            rows_data,
            key=lambda x: x["pct_below_ath"],
            reverse=reverse
        )

# ---------------------------------
# STICKY HEADER ROW
# ---------------------------------
st.markdown("<div class='sticky-header'>", unsafe_allow_html=True)

headers = st.columns([1.6, 1.3, 1, 1.6, 1.4, 1.4])
headers[0].markdown("**Stock**")
headers[1].markdown("**LTP**")
headers[2].markdown("**Lot Size**")
headers[3].markdown("**Contract Value (₹)**")
headers[4].markdown("**% Below ATH**")
headers[5].markdown("**Chart**")

st.markdown("</div>", unsafe_allow_html=True)
st.divider()

# ---------------------------------
# RENDER ROWS
# ---------------------------------
for row_data in rows_data:
    row = st.columns([1.6, 1.3, 1, 1.6, 1.4, 1.4])

    row[0].markdown(
        f"<div class='row-box stock-text'>{row_data['stock']}</div>",
        unsafe_allow_html=True
    )
    row[1].markdown(
        f"<div class='row-box ltp-text'>{row_data['ltp']}</div>",
        unsafe_allow_html=True
    )
    row[2].markdown(
        f"<div class='row-box lot-text'>{row_data['lot']}</div>",
        unsafe_allow_html=True
    )
    row[3].markdown(
        f"<div class='row-box contract-text'>₹ {row_data['contract_value']:,}</div>",
        unsafe_allow_html=True
    )
    row[4].markdown(
        f"<div class='row-box ath-text'>{row_data['pct_below_ath']} %</div>",
        unsafe_allow_html=True
    )

    with row[5]:
        draw_small_chart(row_data["df"])

    st.markdown("<div class='row-separator'></div>", unsafe_allow_html=True)

st.caption("Data Source: Yahoo Finance | Timeframe: Daily")
