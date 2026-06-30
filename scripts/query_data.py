import sqlite3
import pandas as pd

DB_FILE = "./data/stocks.db"

connection = sqlite3.connect(DB_FILE)

# Portfolio growth
query = """
SELECT date, SUM(net_value) as
daily_value
FROM transactions
Group BY date
ORDER BY date
"""

portfolio_df = pd.read_sql(query, connection)
portfolio_df["cumulative"] = portfolio_df["daily_value"].cumsum()

print(portfolio_df.head())

# Profit per stock
query = """
SELECT stock, SUM(net_value) as
total_profit
FROM transactions
Group BY stock
ORDER BY total_profit DESC
"""

profit_df = pd.read_sql(query, connection)
print(profit_df)