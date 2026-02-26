import yfinance as yf
from app.core.db import save_data

# Configuration
# Yahoo Finance Tickers
# Shanghai Composite: 000001.SS
# S&P 500: ^GSPC
# Nikkei 225: ^N225
# NASDAQ 100: ^NDX
TICKERS = {
    '000001.SS': {'name': 'Shanghai Composite', 'symbol_short': '000001'},
    '^GSPC': {'name': 'S&P 500', 'symbol_short': 'SPX'},
    '^N225': {'name': 'Nikkei 225', 'symbol_short': 'N225'},
    '^NDX': {'name': 'NASDAQ 100', 'symbol_short': 'NDX'}
}

def fetch_market_indices():
    print("Fetching Market Indices from Yahoo Finance...")
    results = []

    try:
        for ticker_symbol, info in TICKERS.items():
            ticker = yf.Ticker(ticker_symbol)
            
            # fast_info provides real-time/delayed latest price and previous close
            # Note: For some indices fast_info might be missing,fallback to history if needed
            price = ticker.fast_info.last_price
            prev_close = ticker.fast_info.previous_close
            
            if price is None:
                # Fallback to history (1 day) if fast_info fails
                hist = ticker.history(period="1d")
                if not hist.empty:
                    price = hist['Close'].iloc[-1]
                    # Attempt to get prev close from info or calculate? 
                    # history includes Open/High/Low/Close. 
                    # If market is open, 'Close' might be current.
                    # We can try period='5d' to get previous close
                    hist5 = ticker.history(period="5d")
                    if len(hist5) >= 2:
                        prev_close = hist5['Close'].iloc[-2]
                    else:
                        prev_close = price # Fallback
                else:
                    print(f"Warning: No data for {ticker_symbol}")
                    continue
            
             # Handle cases where prev_close might still be None or 0
            if not prev_close:
                 prev_close = price

            change = price - prev_close
            change_pct = (change / prev_close) * 100 if prev_close else 0.0
            
            record = {
                'symbol': info['symbol_short'], # Keep original short symbols for consistency
                'name': info['name'],
                'price': round(float(price), 2),
                'change': round(float(change), 2),
                'change_pct': round(float(change_pct), 2),
                'prev_close': round(float(prev_close), 2)
            }
            results.append(record)
            print(f"Fetched {info['name']} ({ticker_symbol}): Price={price:.2f}, PrevClose={prev_close:.2f}")

    except Exception as e:
        print(f"Error fetching indices: {e}")
        return []

    return results

def main():
    data = fetch_market_indices()
    if data:
        print(f"Found {len(data)} indices.")
        save_data('market_indices', data)
        print("Market Indices Task Complete.")
    else:
        print("No market index data found.")

if __name__ == "__main__":
    main()
