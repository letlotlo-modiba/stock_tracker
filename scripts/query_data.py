import sqlite3
from pathlib import Path
import pandas as pd

# Resolve database path relative to project root
BASE_DIR = Path(__file__).resolve().parent.parent
DB_FILE = BASE_DIR / "data" / "stocks.db"


def run_queries():
    if not DB_FILE.exists():
        print(f"❌ Error: Database file not found at {DB_FILE}")
        print("Please run 'python scripts/clean_data.py' first.")
        return

    connection = sqlite3.connect(DB_FILE)

    try:
        # Check if transactions table exists
        cursor = connection.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='transactions';")
        if not cursor.fetchone():
            print("❌ Error: 'transactions' table not found in database.")
            print("Please run 'python scripts/clean_data.py' first.")
            connection.close()
            return

        print("=" * 55)
        print("  📊 STOCK TRACKER SQL ANALYTICS SUMMARY")
        print("=" * 55)

        # 1. Portfolio Growth Over Time
        growth_query = """
        SELECT
            date,
            SUM(net_value) AS daily_net_investment
        FROM transactions
        GROUP BY date
        ORDER BY date
        """
        portfolio_df = pd.read_sql(growth_query, connection)
        portfolio_df["cumulative_investment"] = portfolio_df["daily_net_investment"].cumsum()

        print("\n📈 [1] Portfolio Growth (Recent 10 Dates):")
        print("-" * 55)
        print(portfolio_df.tail(10).to_string(index=False))

        # 2. Net Cash Flow & Profit Per Stock
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

        print("\n💰 [2] Transaction Breakdown Per Stock (ZAR):")
        print("-" * 55)
        print(profit_df.to_string(index=False))

        # 3. Market Data (if available)
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='market_data';")
        if cursor.fetchone():
            market_query = "SELECT stock, current_price FROM market_data"
            market_df = pd.read_sql(market_query, connection)
            print("\n🌍 [3] Latest Market Prices (ZAR):")
            print("-" * 55)
            print(market_df.to_string(index=False))

        print("\n" + "=" * 55)

    except Exception as e:
        print(f"❌ Error executing queries: {e}")
    finally:
        connection.close()


if __name__ == "__main__":
    run_queries()
