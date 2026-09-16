import os
import sqlite3
from pathlib import Path
import pandas as pd

# Define base paths relative to this script so it runs from any directory
BASE_DIR = Path(__file__).resolve().parent.parent
RAW_FOLDER = BASE_DIR / "data" / "raw"
PROCESSED_FILE = BASE_DIR / "data" / "processed" / "cleaned_data.csv"
DB_FILE = BASE_DIR / "data" / "stocks.db"


def clean_and_ingest():
    # Ensure directories exist
    RAW_FOLDER.mkdir(parents=True, exist_ok=True)
    PROCESSED_FILE.parent.mkdir(parents=True, exist_ok=True)
    DB_FILE.parent.mkdir(parents=True, exist_ok=True)

    csv_files = [f for f in os.listdir(RAW_FOLDER) if f.endswith(".csv")]

    if not csv_files:
        print(f"⚠️ No CSV files found in {RAW_FOLDER}")
        print("Please place your transaction CSV files in the data/raw/ directory.")
        return

    all_data = []

    # Loop through all CSV files in the raw folder
    for file in sorted(csv_files):
        print(f"Processing: {file}")
        path = RAW_FOLDER / file

        try:
            df = pd.read_csv(path)
            if df.empty:
                print(f"  Skipping empty file: {file}")
                continue

            # Standardize column headers: lowercase and stripped of whitespace
            df.columns = df.columns.str.strip().str.lower()

            # Optional mapping for common alternative column names
            col_rename = {
                "share": "stock",
                "ticker": "stock",
                "share / etf": "stock",
                "action": "transaction_type",
                "type": "transaction_type",
                "shares": "quantity",
                "amount": "total_value",
                "total": "total_value",
            }
            df = df.rename(columns={k: v for k, v in col_rename.items() if k in df.columns})

            # Verify required columns exist
            required_cols = {"date", "stock", "transaction_type", "price", "quantity"}
            missing_cols = required_cols - set(df.columns)
            if missing_cols:
                print(f"  Warning: {file} is missing required columns: {missing_cols}. Skipping.")
                continue

            # Convert type: date
            df["date"] = pd.to_datetime(df["date"])

            # Clean and standardize transaction_type (BUY / SELL)
            df["transaction_type"] = df["transaction_type"].astype(str).str.strip().str.upper()

            # Clean and convert numeric types
            df["price"] = pd.to_numeric(df["price"], errors="coerce")
            df["quantity"] = pd.to_numeric(df["quantity"], errors="coerce")

            # Calculate total_value if missing or null
            if "total_value" not in df.columns or df["total_value"].isna().all():
                df["total_value"] = df["price"] * df["quantity"]
            else:
                df["total_value"] = pd.to_numeric(df["total_value"], errors="coerce").fillna(
                    df["price"] * df["quantity"]
                )

            # Drop any rows where critical fields could not be parsed
            df = df.dropna(subset=["date", "stock", "price", "quantity", "total_value"])

            # Net value calculation: BUY is positive (cash invested), SELL is negative (cash returned)
            df["net_value"] = df.apply(
                lambda x: x["total_value"] if x["transaction_type"] == "BUY" else -x["total_value"],
                axis=1,
            )

            all_data.append(df)

        except Exception as e:
            print(f"  Error processing {file}: {e}")

    if not all_data:
        print("❌ No valid transaction data found across CSV files.")
        return

    # Combine all individual statements
    final_df = pd.concat(all_data, ignore_index=True)

    # Sort chronologically and remove exact duplicate records
    final_df = final_df.sort_values("date").drop_duplicates()

    # Save cleaned data to CSV
    final_df.to_csv(PROCESSED_FILE, index=False)
    print(f"✅ Cleaned data ({len(final_df)} rows) saved to {PROCESSED_FILE}")

    # Save to SQLite database
    connection = sqlite3.connect(DB_FILE)
    final_df.to_sql("transactions", connection, if_exists="replace", index=False)
    connection.close()

    print(f"✅ Data saved to database: {DB_FILE}")
    print("🚀 Data cleaning & ingestion pipeline completed successfully!")


if __name__ == "__main__":
    clean_and_ingest()