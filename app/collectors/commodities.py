import os
import yfinance as yf
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime
from app.core.db import save_data, OUTPUT_DIR

def fetch_commodities():
    print("Fetching Commodities from Yahoo Finance and generating 30-day chart...")
    tickers = ['GC=F', 'BZ=F']
    results = []
    
    # For charting
    history_data = {}
    name_map = {
        'GC=F': 'Gold', 
        'BZ=F': 'Brent Crude'
    }

    try:
        for tick in tickers:
            ticker = yf.Ticker(tick)
            
            # Fetch 1 month history for charting
            hist = ticker.history(period="1mo")
            if not hist.empty:
                name = name_map.get(tick, tick)
                history_data[name] = hist['Close']
                
                # Latest info for DB
                price = hist['Close'].iloc[-1]
                if len(hist) >= 2:
                    prev_close = hist['Close'].iloc[-2]
                else:
                    prev_close = price
            else:
                print(f"Warning: No data for {tick}")
                continue

            change = price - prev_close
            change_pct = (change / prev_close) * 100 if prev_close else 0.0
            
            record = {
                'symbol': tick,
                'name': name,
                'price': round(float(price), 2),
                'change': round(float(change), 2),
                'change_pct': round(float(change_pct), 2)
            }
            results.append(record)
            print(f"Fetched {name}: {price:.2f}")
            
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
                                 
            plt.title('Global Commodities - 30 Day Growth Rate (%)')
            plt.ylabel('Growth Rate (%)')
            plt.grid(True, alpha=0.3)
            plt.legend(loc='upper left')
            
            # Format x-axis
            plt.gcf().autofmt_xdate()
            plt.tight_layout()
            
            # Save chart
            today_str = datetime.now().strftime("%Y-%m-%d")
            images_dir = os.path.join(OUTPUT_DIR, 'images')
            os.makedirs(images_dir, exist_ok=True)
            chart_path = os.path.join(images_dir, f'commodities_{today_str}.png')
            
            plt.savefig(chart_path, dpi=120)
            plt.close()
            print(f"Commodities chart saved to {chart_path}")

    except Exception as e:
        print(f"Error fetching commodities: {e}")
        return []

    return results

def main():
    data = fetch_commodities()
    if data:
        print(f"Found {len(data)} commodities.")
        save_data('commodities', data)
        print("Commodities Task Complete.")
    else:
        print("No commodity data found.")

if __name__ == "__main__":
    main()
