import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px

# --- CONFIG ---
DB_FILE = "./data/stocks.db"

st.set_page_config(page_title="Stock Portfolio Dashboard", layout="wide")

# --- HEADER ---
st.markdown("""
    <h1 style='text-align: center;'>Stock Portfolio Dashboard</h1>
    <p style='text-align: center; color: gray;'>Track performance, profits and live portfolio value</p>
""", unsafe_allow_html=True)

# --- LOAD HISTORICAL DATA ---
@st.cache_data
def load_data():
    connection = sqlite3.connect(DB_FILE)
    
    portfolio_query = """
    SELECT date, SUM(net_value) as daily_value
    FROM transactions
    GROUP BY date
    ORDER BY date
    """
    
    portfolio_df = pd.read_sql(portfolio_query, connection)
    portfolio_df["date"] = pd.to_datetime(portfolio_df["date"])
    portfolio_df["cumulative"] = portfolio_df["daily_value"].cumsum()
    
    profit_query = """
    SELECT stock, SUM(net_value) as total_profit
    FROM transactions
    GROUP BY stock
    ORDER BY total_profit DESC
    """
    
    profit_df = pd.read_sql(profit_query, connection)
    
    connection.close()
    return portfolio_df, profit_df

# --- LOAD LIVE DATA ---
@st.cache_data
def load_live_data():
    connection = sqlite3.connect(DB_FILE)

    query = """
    SELECT
        t.stock,
        t.quantity,
        t.price,
        t.transaction_type,
        t.net_value,
        m.current_price
    FROM transactions t
    JOIN market_data m
    ON t.stock = m.stock
    """

    df = pd.read_sql(query, connection)

    connection.close()
    return df

# --- LOAD DATA ---
portfolio_df, profit_df = load_data()
live_df = load_live_data()


# --- SIDEBAR FILTERS ---
st.sidebar.header("Filters")

min_date = portfolio_df["date"].min() if not portfolio_df.empty else pd.to_datetime("today")
max_date = portfolio_df["date"].max() if not portfolio_df.empty else pd.to_datetime("today")

start_date = st.sidebar.date_input("Start Date", value=min_date)
end_date = st.sidebar.date_input("End Date", value=max_date)

# Stock Filter
stocks = st.sidebar.multiselect(
    "Select Stocks", 
    options=profit_df["stock"].unique() if not profit_df.empty else [],
    default=profit_df["stock"].unique() if not profit_df.empty else []
)

# Filter Historical Data
filtered_df = portfolio_df[
    (portfolio_df["date"] >= pd.to_datetime(start_date)) &
    (portfolio_df["date"] <= pd.to_datetime(end_date))
]

# Filter Live Data
filtered_live_df = live_df[live_df["stock"].isin(stocks)].copy()

# --- LIVE CALCULATIONS ---
if not filtered_live_df.empty:
    filtered_live_df["signed_quantity"] = filtered_live_df.apply(
        lambda x: x["quantity"] if x["transaction_type"] == "BUY" else -x["quantity"], axis=1
    )
    filtered_live_df["current_value"] = filtered_live_df["signed_quantity"] * filtered_live_df["current_price"]
    filtered_live_df["profit"] = filtered_live_df["current_value"] - filtered_live_df["net_value"]

    portfolio_value = filtered_live_df["current_value"].sum()
    live_profit = filtered_live_df["profit"].sum()
else:
    portfolio_value = 0.0
    live_profit = 0.0

# --- HISTORICAL METRICS ---
if not filtered_df.empty:
    total_profit = filtered_df["cumulative"].iloc[-1]
    total_investment = filtered_df["daily_value"][filtered_df["daily_value"] > 0].sum()
else:
    total_profit = 0.0
    total_investment = 0.0

best_stock = profit_df.iloc[0]["stock"] if not profit_df.empty else "N/A"

# --- METRICS DISPLAY ---
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Investment", f"R{total_investment:,.2f}")
col2.metric("Historical Profit", f"R{total_profit:,.2f}")
col3.metric("Live Portfolio Value", f"R{portfolio_value:,.2f}")
col4.metric("Live Profit", f"R{live_profit:,.2f}")

# --- PORTFOLIO GROWTH CHART ---
st.subheader("Portfolio Growth")

fig = px.line(
    filtered_df,
    x="date",
    y="cumulative",
    title="Portfolio Value Over Time"
)

st.plotly_chart(fig, use_container_width=True)

# --- DAILY PERFORMANCE ---
st.subheader("Daily Profit / Loss")

fig2 = px.bar(
    filtered_df,
    x="date",
    y="daily_value",
    title="Daily Gains and Losses"
)

st.plotly_chart(fig2, use_container_width=True)

# --- PROFIT PER STOCK ---
st.subheader("Profit per Stock")

filtered_profit_df = profit_df[profit_df["stock"].isin(stocks)] if not profit_df.empty else profit_df

fig3 = px.bar(
    filtered_profit_df,
    x="stock",
    y="total_profit",
    title="Stock Performance"
)

st.plotly_chart(fig3, use_container_width=True)

# --- PORTFOLIO AGGREGATION ---
if not filtered_live_df.empty:
    portfolio = filtered_live_df.groupby("stock").agg({
        "signed_quantity": "sum",
        "net_value": "sum",
        "current_price": "first"
    }).reset_index()

    portfolio.rename(columns={"signed_quantity": "quantity"}, inplace=True)
    portfolio["value"] = portfolio["quantity"] * portfolio["current_price"]
    portfolio["profit"] = portfolio["value"] - portfolio["net_value"]
else:
    portfolio = pd.DataFrame(columns=["stock", "quantity", "net_value", "current_price", "value", "profit"])

# --- PORTFOLIO BREAKDOWN ---
st.subheader("Portfolio Allocation")

portfolio_holding = portfolio[portfolio["quantity"] > 0]
if not portfolio_holding.empty:
    fig4 = px.pie(portfolio_holding, names="stock", values="value", title="Portfolio Distribution")
    st.plotly_chart(fig4, use_container_width=True)
else:
    st.info("No active stock holdings in selected range.")

# --- Insight ---
st.subheader("Insights")

if not portfolio.empty:
    top_stock = portfolio.sort_values("profit", ascending=False).iloc[0]
    st.success(f"Best performing stock: {top_stock['stock']} (R{top_stock['profit']:,.2f})")
    st.info(f"Live portfolio value: R{portfolio_value:,.2f}")

# --- Table view of raw data ---
with st.expander("View Raw Data"):
    st.dataframe(filtered_df)