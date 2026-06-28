import pandas as pd

# Load raw data file
df = pd.read_csv("./data/easy_equities_mock.csv")

# Create clean column names
df.columns = df.columns.str.strip().str.lower()

# Convert type: date
df["date"] = pd.to_datetime(df["date"])

# Convert type: numeric
df["price"] = pd.to_numeric(df["price"])
df["quantity"] = pd.to_numeric(df["quantity"])
df["total_value"] = pd.to_numeric(df["total_value"])

# Save cleand data
df.to_csv("./data/cleaned_data.csv", index=False)

print("Data cleaned successfully!")