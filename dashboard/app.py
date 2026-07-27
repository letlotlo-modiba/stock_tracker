import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px

# --- CONFIG ---
DB_FILE = "./data/stocks.db"

st.set_page_config(page_title="Stock Portfolio Dashboard", layout="wide")

st.title("Stock Portfolio Dashboard")

# --- LOAD DATA ---
@st.cache_data
def load_data():
    conn = sqlite3.connect(DB_FILE)
    
    portfolio_query = """
    SELECT date, SUM(net_value) as daily_value
    FROM transactions
    GROUP BY date
    ORDER BY date
    """
    
    portfolio_df = pd.read_sql(portfolio_query, conn)
    portfolio_df["date"] = pd.to_datetime(portfolio_df["date"])
    portfolio_df["cumulative"] = portfolio_df["daily_value"].cumsum()
    
    profit_query = """
    SELECT stock, SUM(net_value) as total_profit
    FROM transactions
    GROUP BY stock
    ORDER BY total_profit DESC
    """
    
    profit_df = pd.read_sql(profit_query, conn)
    
    conn.close()
    return portfolio_df, profit_df

portfolio_df, profit_df = load_data()

# --- SIDEBAR FILTERS ---
st.sidebar.header("Filters")

start_date = st.sidebar.date_input(
    "Start Date", 
    value=portfolio_df["date"].min()
)

end_date = st.sidebar.date_input(
    "End Date", 
    value=portfolio_df["date"].max()
)

# Filter data
filtered_df = portfolio_df[
    (portfolio_df["date"] >= pd.to_datetime(start_date)) &
    (portfolio_df["date"] <= pd.to_datetime(end_date))
]

# --- METRICS ---
total_profit = filtered_df["cumulative"].iloc[-1]
total_investment = filtered_df["daily_value"][filtered_df["daily_value"] > 0].sum()
best_stock = profit_df.iloc[0]["stock"]

col1, col2, col3 = st.columns(3)

col1.metric("💰 Total Investment", f"R{total_investment:,.2f}")
col2.metric("📈 Total Profit", f"R{total_profit:,.2f}")
col3.metric("🏆 Best Stock", best_stock)

# --- PORTFOLIO GROWTH CHART ---
st.subheader("📈 Portfolio Growth")

fig = px.line(
    filtered_df,
    x="date",
    y="cumulative",
    title="Portfolio Value Over Time"
)

st.plotly_chart(fig, use_container_width=True)

# --- DAILY PERFORMANCE ---
st.subheader("📊 Daily Profit / Loss")

fig2 = px.bar(
    filtered_df,
    x="date",
    y="daily_value",
    title="Daily Gains and Losses"
)

st.plotly_chart(fig2, use_container_width=True)

# --- PROFIT PER STOCK ---
st.subheader("📊 Profit per Stock")

fig3 = px.bar(
    profit_df,
    x="stock",
    y="total_profit",
    title="Stock Performance"
)

st.plotly_chart(fig3, use_container_width=True)