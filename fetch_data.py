import os
import requests
import pandas as pd
import yfinance as yf

# Create the data/ folder if it does not exist yet
os.makedirs("data", exist_ok=True)

# Read the FRED API key from a local text file and strip extra spaces/newlines
with open("fred_key.txt", "r") as f:
    FRED_API_KEY = f.read().strip()

# List of FRED series IDs and Yahoo Finance tickers to download
FRED_SERIES = ["UNRATE", "CPIAUCSL", "FEDFUNDS", "RRVRUSQ156N", "FGEXPND", "USREC"]
YAHOO_TICKERS = ["SPY", "XLF", "XLK", "XLE", "XLRE"]


def fetch_fred(series_id):
    """Download one economic series from the FRED API and save as data/<SERIES>.csv."""
    url = "https://api.stlouisfed.org/fred/series/observations"
    params = {
        "series_id": series_id,
        "api_key": FRED_API_KEY,
        "file_type": "json",
    }

    response = requests.get(url, params=params, timeout=15)
    response.raise_for_status()  # Raise an error if the request failed (e.g., bad key)

    # Extract the list of observations and keep only date and value
    observations = response.json()["observations"]
    df = pd.DataFrame(observations)[["date", "value"]]

    # FRED marks missing values with "." -> convert those to NaN (real missing numbers)
    df["value"] = pd.to_numeric(df["value"], errors="coerce")

    output_path = f"data/{series_id}.csv"
    df.to_csv(output_path, index=False)
    print(f"Saved {output_path} ({len(df)} rows)")


def fetch_yahoo(ticker):
    """Download daily stock/ETF prices from Yahoo Finance and save as data/<TICKER>.csv."""
    df = yf.download(ticker, start="2000-01-01", progress=False)

    if df.empty:
        raise ValueError("No data returned from Yahoo Finance.")

    # Flatten multi-level column names if yfinance returns tuples like ('Close', 'SPY')
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    # Move the Date index into a regular column and lowercase all column names
    df = df.reset_index()
    df.columns = [str(col).lower() for col in df.columns]

    # Keep only the 6 requested columns in exact order
    cols = ["date", "open", "high", "low", "close", "volume"]
    df = df[cols]

    output_path = f"data/{ticker}.csv"
    df.to_csv(output_path, index=False)
    print(f"Saved {output_path} ({len(df)} rows)")


if __name__ == "__main__":
    # Download all FRED series, catching errors individually so one failure won't stop the rest
    for series in FRED_SERIES:
        try:
            fetch_fred(series)
        except Exception as e:
            print(f"ERROR fetching FRED {series}: {e}")

    # Download all Yahoo Finance tickers
    for ticker in YAHOO_TICKERS:
        try:
            fetch_yahoo(ticker)
        except Exception as e:
            print(f"ERROR fetching Yahoo {ticker}: {e}")