import pandas as pd
import os
import sqlite3

RAW_FOLDER = "./data/raw"
PROCESSSED_FILE = "./data/processed/cleaned_data.csv"
DB_FILE = "data/stocks.db"

all_data = []

# Loop all data files 
for file in os.listdir(RAW_FOLDER):
    if file.endswith(".csv"): 
        print("Processing:", file)

        path = os.path.join(RAW_FOLDER, file)
        df = pd.read_csv(path)

    # Create clean column names
    df.columns = df.columns.str.strip().str.lower()

    # Convert type: date
    df["date"] = pd.to_datetime(df["date"])

    # Convert type: numeric
    df["price"] = pd.to_numeric(df["price"])
    df["quantity"] = pd.to_numeric(df["quantity"])
    df["total_value"] = pd.to_numeric(df["total_value"])

    # Net value calculation
    df["net_value"] = df.apply(lambda x: x["total_value"] if x["transaction_type"] == "BUY" else -x["total_value"], axis=1)

    # Add all the data to list
    all_data.append(df)

# Combine the data
final_df = pd.concat(all_data, ignore_index=True)
final_df = final_df.sort_values("date").drop_duplicates()

# Save cleand data
final_df.to_csv(PROCESSSED_FILE, index=False)

# Save to database
connection = sqlite3.connect(DB_FILE)
final_df.to_sql("transactions", connection, if_exists="replace", index=False)
connection.close()

print("Data saved to database!")

print("Pipeline completed!")