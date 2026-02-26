import requests
import time
import random
from app.core.db import save_data

# Configuration
# URL from browser subagent: https://www.jisilu.cn/data/taoligu/astock_arbitrage_list/
API_URL = "https://www.jisilu.cn/data/taoligu/astock_arbitrage_list/"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "X-Requested-With": "XMLHttpRequest",
    "Referer": "https://www.jisilu.cn/data/taoligu/#cna"
}

def fetch_a_share_arbitrage():
    """Fetch A-share arbitrage data and return filtered list (Price < Cash Option Price)."""
    print(f"Fetching A-share arbitrage data from {API_URL}...")
    
    # Simulate user browsing behavior
    sleep_time = random.uniform(2, 5)
    print(f"Sleeping for {sleep_time:.2f} seconds...")
    time.sleep(sleep_time)
    
    try:
        # Add timestamp to params to prevent caching
        params = {
            '___jsl': f'LST___t={int(time.time() * 1000)}'
        }
        # Request body
        data = {
            'rp': 500, # Fetch up to 500 records
            'page': 1
        }
        
        response = requests.post(API_URL, headers=HEADERS, params=params, data=data)
        
        if response.status_code != 200:
            print(f"Failed to fetch data. Status code: {response.status_code}")
            return []
            
        try:
            json_data = response.json()
        except Exception as e:
            print(f"Failed to decode JSON. Response text preview: {response.text[:200]}")
            return []
            
        rows = json_data.get('rows', [])
        results = []
        
        for row in rows:
            cell = row.get('cell', {})
            try:
                # Extract fields
                # stock_id: code
                # stock_nm: name
                # price: current price
                # choose_price: cash option price / 现金权益价
                # type_cd: type
                # descr: description
                
                stock_id = cell.get('stock_id')
                stock_nm = cell.get('stock_nm')
                price_str = cell.get('price')
                choose_price_str = cell.get('choose_price')
                type_cd = cell.get('type_cd', '')
                descr = cell.get('descr', '')
                
                if not price_str or price_str == '-' or not choose_price_str or choose_price_str == '-':
                    continue
                    
                price = float(price_str)
                choose_price = float(choose_price_str)
                
                # CRITICAL FILTER: Price < Cash Option Price (现价 < 现金权益价)
                if price < choose_price:
                    results.append({
                        'stock_id': stock_id,
                        'stock_name': stock_nm,
                        'price': price,
                        'choose_price': choose_price,
                        'type_cd': type_cd,
                        'descr': descr
                    })
            except (ValueError, TypeError):
                continue
                
        print(f"Found {len(results)} arbitrage opportunities (Price < Cash Option Price).")
        return results
        
    except Exception as e:
        print(f"Error occurred while fetching A-share arbitrage: {e}")
        return []

def main():
    print("Starting A-share Arbitrage Scraper...")
    records = fetch_a_share_arbitrage()
    
    # Save to DB
    if records:
        save_data('stock_arbitrage', records)
    else:
        print("No arbitrage opportunities found to save.")
    
    print("\nA-share Arbitrage Task Complete.")

if __name__ == "__main__":
    main()
