import sqlite3
from pathlib import Path
import pandas as pd
import yfinance as yf

# Resolve database path relative to project root
BASE_DIR = Path(__file__).resolve().parent.parent
DB_FILE = BASE_DIR / "data" / "stocks.db"

# Mapping stock names in transactions to Yahoo Finance ticker symbols on JSE
TICKER_MAP = {
    "Naspers": "NPN.JO",
    "MTN": "MTN.JO",
    "Shoprite": "SHP.JO",
    "Prosus": "PRX.JO",
    "FirstRand": "FSR.JO",
    "Capitec": "CPI.JO",
    "Standard Bank": "SBK.JO",
    "Sasol": "SOL.JO",
    "Vodacom": "VOD.JO",
    "Anglo American": "AGL.JO",
    "Gold Fields": "GFI.JO",
    "Sanlam": "SLM.JO",
    "Discovery": "DSY.JO",
    "Woolworths": "WHL.JO",
    "Remgro": "REM.JO",
    "Impala Platinum": "IMP.JO",
    "Sibanye Stillwater": "SSW.JO",
    "Bidvest": "BVT.JO",
    "Nedbank": "NED.JO",
    "ABSA": "ABG.JO",
}


def fetch_market_prices():
    if not DB_FILE.exists():
        print(f"❌ Error: Database file not found at {DB_FILE}")
        print("Please run 'python scripts/clean_data.py' first to build the database.")
        return

    connection = sqlite3.connect(DB_FILE)

    # Get unique stocks from transactions
    try:
        stocks_df = pd.read_sql("SELECT DISTINCT stock FROM transactions", connection)
    except sqlite3.OperationalError:
        print("❌ Error: 'transactions' table not found in database.")
        print("Please run 'python scripts/clean_data.py' first to ingest transactions.")
        connection.close()
        return

    if stocks_df.empty:
        print("⚠️ No stocks found in the 'transactions' table.")
        connection.close()
        return

    # Build case-insensitive lookup dictionary
    ticker_lookup = {k.lower(): v for k, v in TICKER_MAP.items()}

    market_data = []

    print(f"Fetching live market prices for {len(stocks_df)} stock(s) via Yahoo Finance...\n")

    for stock in stocks_df["stock"]:
        stock_clean = str(stock).strip()
        # Find mapped ticker or construct JSE ticker symbol
        ticker_symbol = ticker_lookup.get(
            stock_clean.lower(),
            f"{stock_clean}.JO" if not stock_clean.upper().endswith(".JO") else stock_clean,
        )

        try:
            ticker = yf.Ticker(ticker_symbol)

            # Get latest closing price (5d period accounts for weekends / market holidays)
            hist = ticker.history(period="5d")

            if not hist.empty:
                current_price = float(hist["Close"].iloc[-1])
                # JSE stock prices on Yahoo Finance are quoted in South African Cents (ZAc); convert to ZAR (Rands)
                if ticker_symbol.endswith(".JO"):
                    current_price = current_price / 100.0

                market_data.append({"stock": stock_clean, "current_price": current_price})
                print(f"✅ Fetched {stock_clean} ({ticker_symbol}): R{current_price:.2f}")
            else:
                print(f"⚠️ No price history returned for {stock_clean} ({ticker_symbol})")

        except Exception as e:
            print(f"❌ Error fetching {stock_clean} ({ticker_symbol}): {e}")

    if market_data:
        market_df = pd.DataFrame(market_data)
        # Save to Database
        market_df.to_sql("market_data", connection, if_exists="replace", index=False)
        print(f"\n✅ Market data saved successfully to database ({DB_FILE})!")
    else:
        print("\n⚠️ No live market prices could be fetched.")

    connection.close()


if __name__ == "__main__":
    fetch_market_prices()