# 📈 Stock Tracker

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/)
[![Framework](https://img.shields.io/badge/framework-Streamlit-red.svg)](https://streamlit.io/)
[![Data Pipeline](https://img.shields.io/badge/data-Pandas%20%7C%20SQLite-green.svg)](https://pandas.pydata.org/)
[![Visualizations](https://img.shields.io/badge/charts-Plotly-purple.svg)](https://plotly.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**Stock Tracker** is a Python-based financial portfolio tracking and analytics application designed to clean, ingest, analyze, and visualize stock investments — with dedicated support for Johannesburg Stock Exchange (JSE) securities quoted in South African Rand (ZAR).

---

## 📑 Table of Contents

- [About the Project](#-about-the-project)
- [Key Features](#-key-features)
- [Project Architecture](#-project-architecture)
- [Database Schema](#-database-schema)
- [Prerequisites](#-prerequisites)
- [Installation](#-installation)
- [How to Add Your Own Data](#-how-to-add-your-own-data)
- [Usage Workflow](#-usage-workflow)
  - [1. Clean Data & Ingest into Database](#1-clean-data--ingest-into-database)
  - [2. Fetch Live Market Prices](#2-fetch-live-market-prices)
  - [3. Run Terminal Analytics](#3-run-terminal-analytics)
  - [4. Launch Interactive Web Dashboard](#4-launch-interactive-web-dashboard)
- [Dashboard Capabilities](#-dashboard-capabilities)
- [Current Status & Roadmap](#-current-status--roadmap)
- [Troubleshooting & FAQ](#-troubleshooting--faq)
- [License](#-license)

---

## 🚀 About the Project

Managing personal stock portfolios across multiple trade statements and monthly CSV exports (such as EasyEquities, brokers, or trading journals) is often fragmented, manual, and error-prone.

**Stock Tracker** solves this by delivering an end-to-end data pipeline:
1. **Aggregates and standardizes** raw monthly transaction CSV statements.
2. **Cleans, validates, and normalizes** trade logs, calculating net cash invested and trade totals.
3. **Persists data locally** in a structured, zero-configuration SQLite database (`data/stocks.db`).
4. **Fetches live market valuations** via Yahoo Finance (`yfinance`), automatically converting JSE cent quotations (`ZAc`) into Rands (`ZAR`).
5. **Renders an interactive dashboard** via Streamlit and Plotly for real-time portfolio performance, asset allocation, and historical trend analytics.

---

## ✨ Key Features

- 📂 **Automated Data Cleaning Pipeline**: Consolidates multiple CSVs, strips whitespace, parses date formats, handles case normalization, and computes signed net transaction values (`BUY` vs. `SELL`).
- 🗄️ **Embedded SQLite Database**: Automatically initializes and manages tables (`transactions` and `market_data`) with no external database server needed.
- 🌍 **Live JSE Market Synchronization**: Direct integration with Yahoo Finance for real-time closing prices across JSE equities (e.g. `NPN.JO`, `MTN.JO`, `SHP.JO`, `CPI.JO`, `PRX.JO`).
- 📊 **Interactive Web Dashboard**:
  - **KPI Cards**: Total Purchases, Net Capital Invested, Live Portfolio Market Value, and Unrealized Profit / ROI %.
  - **Interactive Visualizations**: Cumulative portfolio growth over time, daily net capital flow (buys vs. sells), capital allocation per stock, and portfolio distribution pie chart.
  - **Dynamic Filters**: Real-time filtering by customizable date ranges and individual stock selections.
  - **Data Inspection**: Expandable tabs to examine filtered raw transactions and active stock holdings.
- 📓 **Exploratory Data Analysis**: Includes a Jupyter Notebook (`notebook/analysis.ipynb`) for deep-dive exploratory data analysis.

---

## 🧱 Project Architecture

```
stock_tracker/
├── app.py                  # Root Streamlit dashboard entrypoint
├── dashboard/
│   └── app.py              # Streamlit dashboard & Plotly charts
├── data/
│   ├── raw/                # Raw transaction CSV files (EasyEquities statement drops)
│   ├── processed/          # Cleaned, consolidated dataset (cleaned_data.csv)
│   └── stocks.db           # SQLite database storing transactions & market prices
├── notebook/
│   └── analysis.ipynb      # Jupyter Notebook for exploratory analysis
├── scripts/
│   ├── clean_data.py       # Data cleaning, normalization & SQLite ingestion
│   ├── fetch_market_data.py# Fetches real-time closing prices via yfinance
│   └── query_data.py       # CLI SQL analytical summaries & reports
├── .gitignore              # Git ignore rules for environments & caches
├── requirements.txt        # Project dependencies
├── LICENSE                 # MIT License
└── README.md               # Project documentation
```

---

## 🗃️ Database Schema

The SQLite database (`data/stocks.db`) is automatically initialized upon running `scripts/clean_data.py`. It consists of two relational tables:

### 1. `transactions` Table
| Column | Type | Description |
| :--- | :--- | :--- |
| `date` | `TEXT` / `DATETIME` | Date of execution (`YYYY-MM-DD`) |
| `stock` | `TEXT` | Stock name or ticker symbol (e.g. `Naspers`, `MTN`) |
| `transaction_type` | `TEXT` | `BUY` or `SELL` |
| `price` | `REAL` | Execution price per share in ZAR |
| `quantity` | `REAL` | Number of shares transacted |
| `total_value` | `REAL` | Total transaction amount (`price * quantity`) |
| `net_value` | `REAL` | Signed cashflow (`+total_value` for BUY, `-total_value` for SELL) |

### 2. `market_data` Table
| Column | Type | Description |
| :--- | :--- | :--- |
| `stock` | `TEXT` | Stock identifier matching `transactions.stock` |
| `current_price` | `REAL` | Latest market price in ZAR (converted from cents if JSE) |

---

## ⚙️ Prerequisites

- **Python 3.8+** (Python 3.10, 3.11, and 3.12 fully supported)
- **pip** package manager
- Active internet connection (for fetching live stock prices from Yahoo Finance)

---

## 📦 Installation

Clone the repository and set up a Python virtual environment:

```bash
# 1. Clone the repository
git clone https://github.com/your-username/stock_tracker.git
cd stock_tracker

# 2. Create a virtual environment
python3 -m venv .venv

# 3. Activate the virtual environment
# On Linux/macOS:
source .venv/bin/activate

# On Windows (Command Prompt / PowerShell):
.venv\Scripts\activate

# 4. Install all dependencies
pip install -r requirements.txt
```

---

## 📥 How to Add Your Own Data

You can add your own trade data from brokers such as **EasyEquities** or custom trade logs.

### 1. Where to Place CSV Files
Drop your raw CSV transaction files directly into the `data/raw/` directory:
```
data/raw/
├── jan_mock.csv
├── feb_mock.csv
└── my_easyequities_statement.csv
```

### 2. Required CSV Format
Files must include the following column headers (case-insensitive and tolerant to common aliases):

| Required Header | Accepted Aliases | Example Value | Description |
| :--- | :--- | :--- | :--- |
| `date` | `Date`, `Transaction Date` | `2024-01-15` | Date of trade |
| `stock` | `Stock`, `Share`, `Share / ETF`, `Ticker` | `Shoprite` | Name or symbol of stock |
| `transaction_type` | `Transaction Type`, `Action`, `Type` | `BUY` or `SELL` | Trade action |
| `price` | `Price`, `Execution Price` | `265.50` | Share price in ZAR |
| `quantity` | `Quantity`, `Shares`, `Qty` | `10` | Quantity of shares traded |
| `total_value` | `Total Value`, `Amount`, `Total` | `2655.00` | *(Optional)* Calculated as `price * quantity` if omitted |

#### Sample CSV Snippet (`data/raw/sample_trades.csv`):
```csv
date,stock,transaction_type,price,quantity,total_value
2024-01-02,Naspers,BUY,3200,1,3200
2024-01-03,MTN,BUY,120,5,600
2024-01-04,Shoprite,BUY,250,2,500
2024-01-06,MTN,SELL,125,2,250
```

---

## 🔄 Usage Workflow

Run the pipeline using the following step-by-step commands:

### 1. Clean Data & Ingest into Database
Parses and standardizes all CSV files in `data/raw/`, cleans fields, generates `data/processed/cleaned_data.csv`, and writes records to `data/stocks.db`:
```bash
python scripts/clean_data.py
```
*Output: `Cleaned data saved to data/processed/cleaned_data.csv and SQLite database!`*

### 2. Fetch Live Market Prices
Connects to Yahoo Finance (`yfinance`) to fetch current closing market prices for all unique stocks in your portfolio:
```bash
python scripts/fetch_market_data.py
```
*Output: Automatically maps stocks to JSE tickers (e.g. `Naspers` -> `NPN.JO`), converts ZAc cents to ZAR Rands, and populates the `market_data` table.*

### 3. Run Terminal Analytics
Run quick SQL aggregations directly from the command line:
```bash
python scripts/query_data.py
```
*Generates summary reports for:*
- Portfolio cumulative growth over recent dates
- Total bought, total sold, and net cash invested per stock
- Current market valuations

### 4. Launch Interactive Web Dashboard
Start the Streamlit analytics dashboard:
```bash
streamlit run app.py
```
*(Alternatively: `streamlit run dashboard/app.py`)*

Open your browser at **`http://localhost:8501`** to interact with the dashboard.

---

## 📊 Dashboard Capabilities

| Feature | Description |
| :--- | :--- |
| 🎛️ **Sidebar Date Range Filter** | Dynamically zoom into any historical timeframe |
| 🏷️ **Multi-Stock Filter** | Isolate specific securities to analyze focused performance |
| 💳 **KPI Metrics** | High-level summary of total capital invested, realized sales, market value, and unrealized profit |
| 📈 **Portfolio Growth Chart** | Interactive Plotly line graph of cumulative investment trajectory |
| 📊 **Daily Cash Flow** | Bar chart highlighting net daily inflows (purchases) vs outflows (sales) |
| 💰 **Capital Allocated per Stock** | Visual ranking of total capital exposure per equity |
| 🥧 **Asset Allocation Breakdown** | Donut chart displaying live portfolio distribution by holding value |
| 🏆 **Automated Insights Banner** | Highlights the top-performing asset and current unrealized return |
| 📄 **Data Inspector** | Expandable data table view of filtered transactions and live market holdings |

---

## 🛣️ Current Status & Roadmap

### ✅ Completed
- [x] Multi-CSV ingestion pipeline with date & column normalization
- [x] Fault-tolerant data cleaning (handles missing totals, varying column headers)
- [x] Embedded SQLite database integration (`data/stocks.db`)
- [x] Live market price synchronization via Yahoo Finance (`yfinance`)
- [x] JSE currency conversion (`ZAc` cents to `ZAR` Rands)
- [x] Interactive web dashboard with Streamlit and Plotly
- [x] Dynamic filtering by date range and stock selection
- [x] Asset allocation distribution chart and top-performer highlights
- [x] Command-line SQL analytical query script
- [x] Comprehensive exploratory data analysis notebook (`notebook/analysis.ipynb`)
- [x] Dependency management (`requirements.txt`) and `.gitignore` configuration

### 🚧 In Progress
- [ ] Automated daily market price sync via background cron or scheduled tasks
- [ ] Dividend tracking and dividend reinvestment yield calculations
- [ ] Multi-currency support (e.g. USD and GBP alongside ZAR)

### 🔮 Future Plans
- [ ] Benchmark comparison against the FTSE/JSE Top 40 Index (`^J200`)
- [ ] REST API backend powered by FastAPI
- [ ] Docker containerization for one-click deployment
- [ ] Automated weekly portfolio summary email alerts

---

## ❓ Troubleshooting & FAQ

<details>
<summary><b>1. Error: "No such table: transactions" or "stocks.db not found"</b></summary>
Run the data cleaning script first to initialize the database:
```bash
python scripts/clean_data.py
```
Ensure you have at least one valid `.csv` file in `data/raw/`.
</details>

<details>
<summary><b>2. Live prices are showing as 0 or not displaying</b></summary>
Ensure you have run the market data fetcher:
```bash
python scripts/fetch_market_data.py
```
Check that your machine has internet access so `yfinance` can query Yahoo Finance.
</details>

<details>
<summary><b>3. How do I map a new JSE stock ticker?</b></summary>
Open `scripts/fetch_market_data.py` and add your stock name and corresponding Yahoo Finance ticker to the `TICKER_MAP` dictionary (e.g. `"Capitec": "CPI.JO"`).
</details>

---

## 📄 License

This project is open-source and licensed under the [MIT License](LICENSE).