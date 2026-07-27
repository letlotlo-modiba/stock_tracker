import yfinance as yf
import sqlite3
import pandas as pd

DB_FILE = "./data/stocks.db"

connection = sqlite3.connect(DB_FILE)

# Get unique stocks from transactions
stocks_df = pd.read_sql("SELECT DISTINCT stock FROM transactions", connection)

market_data = []

for stock in stocks_df["stock"]:
    try:
        ticker_symbol = f"{stock}.JO"
        ticker = yf.Ticker(ticker_symbol)

        # Get latest closing price
        hist = ticker.history(period="1d")

        if not hist.empty:
            current_price = hist["Close"].iloc[-1]
            market_data.append({"stock": stock, "current_price": current_price})
            print(f"Fetched {stock}: {current_price}")

        else:
            print(f"No data for {stock}")

    except Exception as e:
        print(f"Error fetching {stock}: {e}")

# Convert to DataFrame
market_df = pd.DataFrame(market_data)

# Save to Database
market_df.to_sql("market_data", connection, if_exists="replace", index=False)

print("\n Market data saved to database!")

connection.close()