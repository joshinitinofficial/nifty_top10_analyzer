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
# SESSION STATE (for sorting)
# ---------------------------------
if "sort_col" not in st.session_state:
    st.session_state.sort_col = None
if "sort_dir" not in st.session_state:
    st.session_state.sort_dir = "desc"

# ---------------------------------
# CUSTOM CSS
# ---------------------------------
st.markdown("""
<style>

.block-container {
    padding-top: 2.5rem;
}

.main-title {
    text-align: center;
    margin-bottom: 6px;
    font-size: 28px;
    font-weight: 700;
}

.last-updated {
    text-align: center;
    font-size: 14px;
    color: #b0b0b0;
    margin-bottom: 20px;
}

/* sticky header */
.sticky-header {
    position: sticky;
    top: 70px;
    z-index: 100;
    background-color: #0e1117;
    padding: 8px 0;
}

/* columns */
div[data-testid="column"] {
    display: flex;
    align-items: center;
}

/* rows */
.row-box {
    height: 75px;
    display: flex;
    align-items: center;
}

.stock-text { font-size: 18px; font-weight: 700; }
.ltp-text { font-size: 16px; color: #4da6ff; font-weight: 600; }
.contract-text { font-size: 16px; color: #2ecc71; font-weight: 600; }
.ath-text { font-size: 16px; color: #ff6b6b; font-weight: 600; }

.row-separator {
    border-bottom: 1px solid #2a2a2a;
    margin: 6px 0 10px 0;
}

/* tiny sort button */
.sort-btn button {
    padding: 0 !important;
    font-size: 12px !important;
    color: #ccc !important;
    background: transparent !important;
    border: none !important;
}
.sort-btn button:hover {
    color: white !important;
}

</style>
""", unsafe_allow_html=True)

# ---------------------------------
# TITLE
# ---------------------------------
st.markdown("<div class='main-title'>📊 NIFTY Top 10 Equal Weight – Live Snapshot</div>", unsafe_allow_html=True)

last_updated = datetime.now(timezone.utc).astimezone().strftime("%d %b %Y, %I:%M %p")
st.markdown(f"<div class='last-updated'>Last Updated: {last_updated}</div>", unsafe_allow_html=True)

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
    df = yf.download(symbol, period="max", interval="1d", auto_adjust=False, progress=False)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    return df.dropna()

def draw_small_chart(df):
    last_year = df[df.index >= (datetime.today() - timedelta(days=365))]
    fig, ax = plt.subplots(figsize=(1.4, 0.6))
    ax.plot(last_year["Close"], linewidth=1.2)
    ax.axis("off")
    st.pyplot(fig, clear_figure=True)

# ---------------------------------
# COLLECT DATA
# ---------------------------------
rows = []

for stock, symbol in STOCKS.items():
    df = fetch_stock_data(symbol)
    if df.empty:
        continue

    ltp = float(df["Close"].iloc[-1])
    ath = float(df["High"].max())
    pct_below = round(((ath - ltp) / ath) * 100, 2)
    contract = int(ltp * LOT_SIZES.get(stock, 0))

    rows.append({
        "stock": stock,
        "ltp": round(ltp, 2),
        "lot": LOT_SIZES.get(stock, 0),
        "contract": contract,
        "pct": pct_below,
        "df": df
    })

# ---------------------------------
# SORT LOGIC
# ---------------------------------
if st.session_state.sort_col:
    reverse = st.session_state.sort_dir == "desc"
    rows = sorted(rows, key=lambda x: x[st.session_state.sort_col], reverse=reverse)

# ---------------------------------
# STICKY HEADER WITH TRIANGLES
# ---------------------------------
st.markdown("<div class='sticky-header'>", unsafe_allow_html=True)
h = st.columns([1.6, 1.3, 1, 1.8, 1.6, 1.4])

h[0].markdown("**Stock**")
h[1].markdown("**LTP**")
h[2].markdown("**Lot Size**")

with h[3]:
    st.markdown("**Contract Value (₹)**")
    if st.button("▲▼", key="sort_contract", help="Sort", type="secondary"):
        st.session_state.sort_col = "contract"
        st.session_state.sort_dir = "asc" if st.session_state.sort_dir == "desc" else "desc"

with h[4]:
    st.markdown("**% Below ATH**")
    if st.button("▲▼", key="sort_ath", help="Sort", type="secondary"):
        st.session_state.sort_col = "pct"
        st.session_state.sort_dir = "asc" if st.session_state.sort_dir == "desc" else "desc"

h[5].markdown("**Chart**")
st.markdown("</div>", unsafe_allow_html=True)
st.divider()

# ---------------------------------
# RENDER ROWS
# ---------------------------------
for r in rows:
    c = st.columns([1.6, 1.3, 1, 1.8, 1.6, 1.4])
    c[0].markdown(f"<div class='row-box stock-text'>{r['stock']}</div>", unsafe_allow_html=True)
    c[1].markdown(f"<div class='row-box ltp-text'>{r['ltp']}</div>", unsafe_allow_html=True)
    c[2].markdown(f"<div class='row-box'>{r['lot']}</div>", unsafe_allow_html=True)
    c[3].markdown(f"<div class='row-box contract-text'>₹ {r['contract']:,}</div>", unsafe_allow_html=True)
    c[4].markdown(f"<div class='row-box ath-text'>{r['pct']} %</div>", unsafe_allow_html=True)
    with c[5]:
        draw_small_chart(r["df"])
    st.markdown("<div class='row-separator'></div>", unsafe_allow_html=True)
