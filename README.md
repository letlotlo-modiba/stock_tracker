# Stock Tracker

**Stock Tracker** is a Python-based financial portfolio tracking and analytics application designed to clean, ingest, analyze, and visualize stock market investments, with dedicated support for Johannesburg Stock Exchange (JSE) securities quoted in South African Rands (ZAR).

---

## Table of Contents
- [About the Project](#-about-the-project)
- [Key Features](#-key-features)
- [Required Libraries & Toolkits](#-required-libraries--toolkits)
- [Project Architecture](#-project-architecture)
- [Getting Started](#-getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
- [Usage & Pipeline Workflow](#-usage--pipeline-workflow)
  - [1. Data Cleaning & Database Ingestion](#1-data-cleaning--database-ingestion)
  - [2. Fetch Live Market Prices](#2-fetch-live-market-prices)
  - [3. Running SQL Analytical Queries](#3-running-sql-analytical-queries)
  - [4. Launching the Interactive Dashboard](#4-launching-the-interactive-dashboard)
- [License](#-license)

---

## About the Project

Managing personal stock portfolios across multiple trade logs and monthly statements can be challenging. **Stock Tracker** provides an automated data pipeline that:
1. Aggregates raw monthly transaction CSV files (BUYS and SELLS).
2. Calculates net cash flows, cumulative investment growth, and per-stock profits.
3. Automatically fetches live stock market prices via Yahoo Finance.
4. Handles unit conversions (e.g., converting JSE prices quoted in South African Cents `ZAc` into Rands `ZAR`).
5. Displays real-time portfolio performance, asset allocation, and metrics through a web dashboard.

---

## Key Features

- **Automated Data Pipeline**: Scans raw transaction logs (`.csv`), cleans headers, parses dates, and computes transaction net values.
- **SQLite Database Persistence**: Stores transaction records and market data efficiently in a local SQLite database (`stocks.db`).
- **Live Market Price Fetching**: Integrates with Yahoo Finance (`yfinance`) to fetch real-time closing prices for JSE tickers (e.g., `NPN.JO`, `MTN.JO`, `SHP.JO`).
- **Interactive Web Dashboard**: Built with Streamlit and Plotly for visual analytics:
  - **KPI Metrics**: Total Investment, Historical Profit, Live Portfolio Value, Live Profit.
  - **Dynamic Filters**: Filter data by custom date ranges and specific stock selections.
  - **Interactive Charts**: Portfolio growth line charts, daily gain/loss bar charts, stock profit rankings, and asset distribution pie charts.
  - **Data Inspection**: Expandable table view to inspect raw processed datasets.
- **Exploratory Data Analysis**: Includes a Jupyter Notebook (`notebook/analysis.ipynb`) for custom analysis.

---

## Required Libraries & Toolkits

This project relies on the Python 3 ecosystem and the following libraries:

| Library / Toolkit | Version / Type | Purpose |
| :--- | :--- | :--- |
| **Python 3.8+** | Runtime | Core programming language |
| **[Pandas](https://pandas.pydata.org/)** | Library | Data cleaning, manipulation, time-series conversion, and database I/O |
| **[SQLite3](https://docs.python.org/3/library/sqlite3.html)** | Standard Library | Relational database engine for storing transaction logs & market prices |
| **[yfinance](https://github.com/ranaroussi/yfinance)** | Library | Fetches real-time and historical financial market data from Yahoo Finance |
| **[Streamlit](https://streamlit.io/)** | Framework | Powers the interactive web dashboard interface |
| **[Plotly](https://plotly.com/python/)** | Library | Renders dynamic, responsive charts (line, bar, pie) on the dashboard |
| **[Jupyter](https://jupyter.org/)** | Toolkit | Interactive notebook environment for data analysis (`analysis.ipynb`) |

---

## Project Architecture

```
stock_tracker/
├── dashboard/
│   └── app.py              # Streamlit web application & Plotly visualizations
├── data/
│   ├── raw/                # Raw transaction CSV files (e.g., jan_mock.csv, feb_mock.csv)
│   ├── processed/          # Cleaned dataset output (cleaned_data.csv)
│   └── stocks.db           # SQLite database storing 'transactions' & 'market_data' tables
├── notebook/
│   └── analysis.ipynb      # Jupyter notebook for exploratory data analysis
├── scripts/
│   ├── clean_data.py       # Pipeline script to clean CSVs & save to SQLite DB
│   ├── fetch_market_data.py# Script to fetch live market prices via yfinance
│   └── query_data.py       # SQL query script to extract performance summaries
├── LICENSE                 # MIT License
└── README.md               # Project documentation
```

---

## Getting Started

### Prerequisites

Ensure you have **Python 3.8** or higher installed on your system.

### Installation

1. **Clone or navigate to the repository**:
   ```bash
   cd stock_tracker
   ```

2. **Create and activate a virtual environment** *(optional but recommended)*:
   ```bash
   # On Linux/macOS
   python3 -m venv .venv
   source .venv/bin/activate

   # On Windows
   python -m venv .venv
   .venv\Scripts\activate
   ```

3. **Install the required dependencies**:
   ```bash
   pip install pandas yfinance streamlit plotly jupyter
   ```

---

## Usage & Pipeline Workflow

Follow these steps to process your trade data and run the dashboard:

### 1. Data Cleaning & Database Ingestion
Place your raw transaction CSV files inside the `data/raw/` folder, then run:
```bash
python scripts/clean_data.py
```
*This script cleans column names, converts dates and numeric fields, calculates net transaction values, saves `cleaned_data.csv` to `data/processed/`, and populates the `transactions` table in `data/stocks.db`.*

### 2. Fetch Live Market Prices
Fetch the latest stock closing prices from Yahoo Finance:
```bash
python scripts/fetch_market_data.py
```
*This updates the `market_data` table in `data/stocks.db` with live prices (converting JSE prices from cents to Rands).*

### 3. Running SQL Analytical Queries
To run quick SQL summary queries in the terminal:
```bash
python scripts/query_data.py
```

### 4. Launching the Interactive Dashboard
Launch the Streamlit web dashboard:
```bash
streamlit run dashboard/app.py
```
Open your browser at `http://localhost:8501` to view your portfolio analytics.

---

## License

This project is licensed under the [MIT License](LICENSE).