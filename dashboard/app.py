import os
import sqlite3
from pathlib import Path
import pandas as pd
import plotly.express as px
import streamlit as st

# --- CONFIG & PATH RESOLUTION ---
BASE_DIR = Path(__file__).resolve().parent.parent
DB_FILE = BASE_DIR / "data" / "stocks.db"

st.set_page_config(
    page_title="Stock Portfolio Dashboard | JSE Tracker",
    page_icon="📈",
    layout="wide",
)

# --- HEADER ---
st.markdown(
    """
    <div style='text-align: center; padding: 10px 0;'>
        <h1 style='margin-bottom: 0;'>📈 Stock Portfolio Dashboard</h1>
        <p style='color: gray; font-size: 1.1rem;'>Track personal investments, profits, and live JSE valuations in ZAR</p>
    </div>
    """,
    unsafe_allow_html=True,
)


# --- LOAD DATA FUNCTIONS ---
@st.cache_data
def load_transactions_data():
    if not DB_FILE.exists():
        return pd.DataFrame(), pd.DataFrame()

    connection = sqlite3.connect(DB_FILE)
    try:
        # Full transaction details for dynamic filtering by stock and date
        tx_query = """
        SELECT
            date,
            stock,
            transaction_type,
            price,
            quantity,
            total_value,
            net_value
        FROM transactions
        ORDER BY date ASC
        """
        tx_df = pd.read_sql(tx_query, connection)
        if not tx_df.empty:
            tx_df["date"] = pd.to_datetime(tx_df["date"])

        # Lifetime profit/summary per stock
        profit_query = """
        SELECT
            stock,
            SUM(CASE WHEN transaction_type = 'BUY' THEN total_value ELSE 0 END) AS total_bought,
            SUM(CASE WHEN transaction_type = 'SELL' THEN total_value ELSE 0 END) AS total_sold,
            SUM(net_value) AS net_cash_invested
        FROM transactions
        GROUP BY stock
        ORDER BY net_cash_invested DESC
        """
        profit_df = pd.read_sql(profit_query, connection)
        return tx_df, profit_df

    except sqlite3.OperationalError:
        return pd.DataFrame(), pd.DataFrame()
    finally:
        connection.close()


@st.cache_data
def load_live_market_data():
    if not DB_FILE.exists():
        return pd.DataFrame()

    connection = sqlite3.connect(DB_FILE)
    try:
        query = """
        SELECT
            t.date,
            t.stock,
            t.quantity,
            t.price,
            t.transaction_type,
            t.net_value,
            m.current_price
        FROM transactions t
        INNER JOIN market_data m
        ON t.stock = m.stock
        """
        df = pd.read_sql(query, connection)
        if not df.empty:
            df["date"] = pd.to_datetime(df["date"])
        return df
    except sqlite3.OperationalError:
        return pd.DataFrame()
    finally:
        connection.close()


# --- DATA RETRIEVAL ---
tx_df, profit_df = load_transactions_data()
live_df = load_live_market_data()

# --- MISSING DATA GUARD ---
if tx_df.empty:
    st.error("⚠️ **No transaction data found in database.**")
    st.markdown(
        """
        To populate this dashboard with your portfolio data:
        1. Place your trade statement CSV files in `data/raw/`
        2. Run the cleaning and ingestion pipeline:
           ```bash
           python scripts/clean_data.py
           ```
        3. Fetch live closing market prices:
           ```bash
           python scripts/fetch_market_data.py
           ```
        4. Refresh this page to view your analytics.
        """
    )
    st.stop()

# --- SIDEBAR FILTERS ---
st.sidebar.header("🔍 Filter Portfolio")

# Date range selection
min_date = tx_df["date"].min().date()
max_date = tx_df["date"].max().date()

start_date = st.sidebar.date_input("Start Date", value=min_date, min_value=min_date, max_value=max_date)
end_date = st.sidebar.date_input("End Date", value=max_date, min_value=min_date, max_value=max_date)

if start_date > end_date:
    st.sidebar.error("Start Date cannot be after End Date.")
    st.stop()

# Stock multiselect filter
all_stocks = sorted(tx_df["stock"].unique().tolist())
selected_stocks = st.sidebar.multiselect(
    "Select Stocks",
    options=all_stocks,
    default=all_stocks,
)

if not selected_stocks:
    st.warning("Please select at least one stock from the sidebar to view metrics.")
    st.stop()

# --- FILTER DATASETS ---
# Filter transactions by date and selected stocks
filtered_tx = tx_df[
    (tx_df["date"].dt.date >= start_date)
    & (tx_df["date"].dt.date <= end_date)
    & (tx_df["stock"].isin(selected_stocks))
].copy()

# Daily portfolio aggregation
daily_growth = (
    filtered_tx.groupby("date")
    .agg(daily_net_investment=("net_value", "sum"))
    .reset_index()
    .sort_values("date")
)
daily_growth["cumulative_investment"] = daily_growth["daily_net_investment"].cumsum()

# Filter live data
filtered_live = pd.DataFrame()
if not live_df.empty:
    filtered_live = live_df[
        (live_df["date"].dt.date >= start_date)
        & (live_df["date"].dt.date <= end_date)
        & (live_df["stock"].isin(selected_stocks))
    ].copy()

# --- LIVE PORTFOLIO CALCULATIONS ---
if not filtered_live.empty:
    filtered_live["signed_qty"] = filtered_live.apply(
        lambda r: r["quantity"] if r["transaction_type"] == "BUY" else -r["quantity"], axis=1
    )

    # Aggregate holdings per stock
    holdings = (
        filtered_live.groupby("stock")
        .agg(
            quantity=("signed_qty", "sum"),
            net_invested=("net_value", "sum"),
            current_price=("current_price", "first"),
        )
        .reset_index()
    )

    holdings["market_value"] = holdings["quantity"] * holdings["current_price"]
    holdings["unrealized_profit"] = holdings["market_value"] - holdings["net_invested"]

    total_market_val = holdings["market_value"].sum()
    total_unrealized_profit = holdings["unrealized_profit"].sum()
else:
    holdings = pd.DataFrame()
    total_market_val = 0.0
    total_unrealized_profit = 0.0

# Historical metrics in selected window
total_bought = filtered_tx[filtered_tx["transaction_type"] == "BUY"]["total_value"].sum()
total_sold = filtered_tx[filtered_tx["transaction_type"] == "SELL"]["total_value"].sum()
net_invested = daily_growth["cumulative_investment"].iloc[-1] if not daily_growth.empty else 0.0

# --- KPI METRICS CARDS ---
st.markdown("---")
c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Purchases", f"R{total_bought:,.2f}")
c2.metric("Net Capital Invested", f"R{net_invested:,.2f}", delta=f"R{total_sold:,.2f} Realized Sells" if total_sold > 0 else None)
c3.metric("Live Portfolio Value", f"R{total_market_val:,.2f}")
c4.metric(
    "Live Portfolio Profit",
    f"R{total_unrealized_profit:,.2f}",
    delta=f"{(total_unrealized_profit / net_invested * 100):.1f}% ROI" if net_invested > 0 else None,
)

if live_df.empty:
    st.info("💡 **Note**: Live prices are not yet synced. Run `python scripts/fetch_market_data.py` to fetch real-time JSE prices.")

st.markdown("---")

# --- CHARTS ROW 1 ---
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("📈 Portfolio Investment Over Time")
    if not daily_growth.empty:
        fig_line = px.line(
            daily_growth,
            x="date",
            y="cumulative_investment",
            labels={"date": "Date", "cumulative_investment": "Net Invested (ZAR)"},
            title="Cumulative Net Capital Invested",
            markers=True,
        )
        fig_line.update_traces(line_color="#1f77b4")
        st.plotly_chart(fig_line, use_container_width=True)
    else:
        st.info("No transaction records found for the selected date range.")

with col_right:
    st.subheader("📊 Daily Net Cash Flow")
    if not daily_growth.empty:
        fig_bar = px.bar(
            daily_growth,
            x="date",
            y="daily_net_investment",
            labels={"date": "Date", "daily_net_investment": "Daily Net Flow (ZAR)"},
            title="Daily Buys (+) vs Sells (-)",
        )
        fig_bar.update_traces(marker_color="#2ca02c")
        st.plotly_chart(fig_bar, use_container_width=True)
    else:
        st.info("No data available.")

# --- CHARTS ROW 2 ---
col_stock_profit, col_allocation = st.columns(2)

with col_stock_profit:
    st.subheader("💰 Net Capital per Stock")
    stock_net = (
        filtered_tx.groupby("stock")["net_value"]
        .sum()
        .reset_index()
        .sort_values("net_value", ascending=False)
    )
    if not stock_net.empty:
        fig_stocks = px.bar(
            stock_net,
            x="stock",
            y="net_value",
            labels={"stock": "Stock", "net_value": "Net Cash Invested (ZAR)"},
            title="Capital Allocated per Stock",
            color="stock",
        )
        st.plotly_chart(fig_stocks, use_container_width=True)

with col_allocation:
    st.subheader("🥧 Active Portfolio Distribution")
    if not holdings.empty:
        active_holdings = holdings[holdings["quantity"] > 0]
        if not active_holdings.empty:
            fig_pie = px.pie(
                active_holdings,
                names="stock",
                values="market_value",
                title="Current Market Value Allocation",
                hole=0.4,
            )
            st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.info("No active long stock positions currently held.")
    else:
        st.info("Run `python scripts/fetch_market_data.py` to view active asset allocation.")

# --- INSIGHTS BANNER ---
st.subheader("💡 Key Insights")
if not holdings.empty and not holdings[holdings["quantity"] > 0].empty:
    top_performer = holdings.sort_values("unrealized_profit", ascending=False).iloc[0]
    st.success(
        f"🏆 **Top Performing Asset**: **{top_performer['stock']}** with an estimated profit of **R{top_performer['unrealized_profit']:,.2f}** "
        f"across {top_performer['quantity']:,.0f} shares."
    )
elif not filtered_tx.empty:
    largest_holding = stock_net.iloc[0]
    st.info(f"📌 **Largest Capital Allocation**: **{largest_holding['stock']}** with R{largest_holding['net_value']:,.2f} net invested.")

# --- RAW DATA EXPANDER ---
with st.expander("📄 View Detailed Datasets"):
    tab1, tab2 = st.tabs(["Filtered Transactions", "Holdings & Live Market Prices"])
    with tab1:
        st.dataframe(filtered_tx, use_container_width=True)
    with tab2:
        if not holdings.empty:
            st.dataframe(holdings, use_container_width=True)
        else:
            st.write("Market data not yet populated.")