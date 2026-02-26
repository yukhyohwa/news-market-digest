import requests
import time
import random
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from app.core.db import save_data
from config.settings import STRATEGY_CONFIG

config = STRATEGY_CONFIG['spac']

# Configuration
URL = "https://stockanalysis.com/list/spac-stocks/"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def fetch_spac_arbitrage():
    """Fetch SPAC stocks from stockanalysis.com and calculate arbitrage yield."""
    print(f"Fetching SPAC stocks data from {URL}...")
    
    # Simulate user browsing behavior
    sleep_time = random.uniform(1, 3)
    time.sleep(sleep_time)
    
    try:
        response = requests.get(URL, headers=HEADERS, timeout=15)
        if response.status_code != 200:
            print(f"Failed to fetch data. Status code: {response.status_code}")
            return []
            
        soup = BeautifulSoup(response.text, 'html.parser')
        table = soup.find('table')
        if not table:
            print("No table found on page.")
            # Check if it's a mobile layout or something else
            return []
            
        rows = table.find_all('tr')
        if not rows:
            print("No rows found in table.")
            return []
            
        results = []
        today = datetime.now()
        
        # Determine column indexes
        header_cells = rows[0].find_all(['th', 'td'])
        cols = [th.text.strip() for th in header_cells]
        
        sym_idx = -1
        name_idx = -1
        price_idx = -1
        ipo_idx = -1
        
        for i, col in enumerate(cols):
            if 'Symbol' == col or 'Symbol' in col: sym_idx = i
            elif 'Name' in col: name_idx = i
            elif 'Price' in col: price_idx = i
            elif 'IPO Date' in col: ipo_idx = i
            
        if sym_idx == -1 or price_idx == -1 or ipo_idx == -1:
            print(f"Could not find required columns. Headers: {cols}")
            # Fallback to common indexes if layout is standard but names differ
            # Based on testing: 0:No, 1:Symbol, 2:Name, 3:Price, 5:IPO Date
            sym_idx = 1
            name_idx = 2
            price_idx = 3
            ipo_idx = 5
            print(f"Using fallback indexes: Sym={sym_idx}, Name={name_idx}, Price={price_idx}, IPO={ipo_idx}")
            
        processed_count = 0
        for row in rows[1:]:
            cells = row.find_all(['td', 'th'])
            if len(cells) <= max(sym_idx, price_idx, ipo_idx):
                continue
                
            symbol = cells[sym_idx].text.strip()
            name = cells[name_idx].text.strip() if name_idx != -1 else ""
            price_str = cells[price_idx].text.strip().replace(',', '').replace('$', '')
            ipo_date_str = cells[ipo_idx].text.strip()
            
            if not price_str or price_str == '-' or not ipo_date_str or ipo_date_str == '-':
                continue
                
            try:
                price = float(price_str)
                
                # Parse IPO Date (e.g., "May 14, 2021")
                # Handle possible formats
                ipo_date = None
                for fmt in ('%b %d, %Y', '%Y-%m-%d', '%m/%d/%Y'):
                    try:
                        ipo_date = datetime.strptime(ipo_date_str, fmt)
                        break
                    except ValueError:
                        continue
                
                if not ipo_date:
                    continue
                
                # Default NAV = 10.00
                nav = 10.00
                
                # Remaining Days based on 18 months lifecycle (548 days approx)
                expiration_date = ipo_date + timedelta(days=548)
                remaining_days = (expiration_date - today).days
                
                if remaining_days <= 0:
                    continue
                
                # Formula: ((NAV - Price) / Price) * (365 / Remaining Days)
                yield_val = ((nav - price) / price) * (365 / remaining_days)
                
                # FILTERS: Configurable Price Range AND Yield
                if config['min_price'] <= price <= config['max_price'] and yield_val > config['min_yield']:
                    results.append({
                        'symbol': symbol,
                        'name': name,
                        'ipo_date': ipo_date_str,
                        'price': price,
                        'nav': nav,
                        'yield': round(yield_val * 100, 2),
                        'remaining_days': int(remaining_days)
                    })
                processed_count += 1
            except (ValueError, ZeroDivisionError, TypeError):
                continue
                
        print(f"Processed {processed_count} stocks. Found {len(results)} arbitrage opportunities.")
        return results
        
    except Exception as e:
        print(f"Error occurred while fetching SPAC arbitrage: {e}")
        return []

def main():
    print("Starting SPAC Arbitrage Collector...")
    records = fetch_spac_arbitrage()
    
    if records:
        save_data('spac_arbitrage', records)
    else:
        print("No arbitrage opportunities found.")
        
    print("SPAC Arbitrage Task Complete.")

if __name__ == "__main__":
    main()
