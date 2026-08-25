import os
import yfinance as yf
import matplotlib.pyplot as plt
import pandas as pd
from app.core.db import save_data, OUTPUT_DIR

# Configuration
# Yahoo Finance Tickers
TICKERS = {
    '000001.SS': {'name': 'Shanghai Composite', 'symbol_short': '000001'},
    '^GSPC': {'name': 'S&P 500', 'symbol_short': 'SPX'},
    '^NDX': {'name': 'NASDAQ 100', 'symbol_short': 'NDX'},
    '^FTSE': {'name': 'FTSE 100', 'symbol_short': 'FTSE100'}
}

def fetch_market_indices():
    print("Fetching Market Indices from Yahoo Finance and generating 30-day chart...")
    results = []
    
    # For charting
    history_data = {}

    try:
        for ticker_symbol, info in TICKERS.items():
            ticker = yf.Ticker(ticker_symbol)
            
            # Fetch 1 month history for charting
            hist = ticker.history(period="1mo")
            if not hist.empty:
                # Store closing prices for chart
                history_data[info['name']] = hist['Close']
                
                # Latest info for DB
                price = hist['Close'].iloc[-1]
                if len(hist) >= 2:
                    prev_close = hist['Close'].iloc[-2]
                else:
                    prev_close = price
            else:
                print(f"Warning: No data for {ticker_symbol}")
                continue

            change = price - prev_close
            change_pct = (change / prev_close) * 100 if prev_close else 0.0
            
            record = {
                'symbol': info['symbol_short'],
                'name': info['name'],
                'price': round(float(price), 2),
                'change': round(float(change), 2),
                'change_pct': round(float(change_pct), 2),
                'prev_close': round(float(prev_close), 2)
            }
            results.append(record)
            print(f"Fetched {info['name']} ({ticker_symbol}): Price={price:.2f}, PrevClose={prev_close:.2f}")

        # Generate Chart
        if history_data:
            plt.figure(figsize=(10, 5))
            
            for name, series in history_data.items():
                if len(series) > 0:
                    # Normalize to the first day
                    first_price = series.iloc[0]
                    normalized = (series / first_price - 1) * 100
                    
                    # Plot
                    line, = plt.plot(normalized.index, normalized.values, label=name, marker='.')
                    
                    # Add label at the end
                    last_date = normalized.index[-1]
                    last_val = normalized.iloc[-1]
                    abs_val = series.iloc[-1]
                    
                    plt.annotate(f"{abs_val:.2f}",
                                 xy=(last_date, last_val),
                                 xytext=(5, 0),
                                 textcoords="offset points",
                                 color=line.get_color(),
                                 va='center')
                                 
            plt.title('Global Market Indices - 30 Day Growth Rate (%)')
            plt.ylabel('Growth Rate (%)')
            plt.grid(True, alpha=0.3)
            plt.legend(loc='upper left')
            
            # Format x-axis
            plt.gcf().autofmt_xdate()
            plt.tight_layout()
            
            # Save chart
            from datetime import datetime
            today_str = datetime.now().strftime("%Y-%m-%d")
            images_dir = os.path.join(OUTPUT_DIR, 'images')
            os.makedirs(images_dir, exist_ok=True)
            chart_path = os.path.join(images_dir, f'market_indices_{today_str}.png')
            
            plt.savefig(chart_path, dpi=120)
            plt.close()
            print(f"Chart saved to {chart_path}")

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
