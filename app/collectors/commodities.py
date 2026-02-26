import yfinance as yf
from app.core.db import save_data

def fetch_commodities():
    print("Fetching Commodities from Yahoo Finance...")
    tickers = ['GC=F', 'SI=F']
    results = []

    try:
        for tick in tickers:
            # Using Ticker to get latest data
            ticker = yf.Ticker(tick)
            
            # fast_info provides real-time/delayed latest price and previous close
            price = ticker.fast_info.last_price
            prev_close = ticker.fast_info.previous_close
            
            if price is None or prev_close is None:
                print(f"Warning: No data for {tick}")
                continue

            change = price - prev_close
            change_pct = (change / prev_close) * 100 if prev_close else 0.0
            
            name_map = {
                'GC=F': 'Gold', 
                'SI=F': 'Silver'
            }
            name = name_map.get(tick, tick)
            
            record = {
                'symbol': tick,
                'name': name,
                'price': round(float(price), 2),
                'change': round(float(change), 2),
                'change_pct': round(float(change_pct), 2)
            }
            results.append(record)
            print(f"Fetched {name}: {price:.2f}")

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
