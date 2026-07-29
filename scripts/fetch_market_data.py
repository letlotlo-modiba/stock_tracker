import yfinance as yf
import sqlite3
import pandas as pd

DB_FILE = "./data/stocks.db"

# Mapping stock names in transactions to Yahoo Finance ticker symbols on JSE
TICKER_MAP = {
    "Naspers": "NPN.JO",
    "MTN": "MTN.JO",
    "Shoprite": "SHP.JO",
}

connection = sqlite3.connect(DB_FILE)

# Get unique stocks from transactions
stocks_df = pd.read_sql("SELECT DISTINCT stock FROM transactions", connection)

market_data = []

for stock in stocks_df["stock"]:
    ticker_symbol = TICKER_MAP.get(stock, f"{stock}.JO" if not stock.endswith(".JO") else stock)
    try:
        ticker = yf.Ticker(ticker_symbol)

        # Get latest closing price (5d period accounts for weekends/holidays)
        hist = ticker.history(period="5d")

        if not hist.empty:
            current_price = float(hist["Close"].iloc[-1])
            # JSE stock prices on Yahoo Finance are quoted in South African Cents (ZAc); convert to ZAR (Rands)
            if ticker_symbol.endswith(".JO"):
                current_price = current_price / 100.0

            market_data.append({"stock": stock, "current_price": current_price})
            print(f"Fetched {stock} ({ticker_symbol}): R{current_price:.2f}")

        else:
            print(f"No data for {stock} ({ticker_symbol})")

    except Exception as e:
        print(f"Error fetching {stock} ({ticker_symbol}): {e}")

# Convert to DataFrame
market_df = pd.DataFrame(market_data)

# Save to Database
market_df.to_sql("market_data", connection, if_exists="replace", index=False)

print("\n Market data saved to database!")

connection.close()