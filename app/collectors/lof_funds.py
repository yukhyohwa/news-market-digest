import requests
import time
import random
from app.core.db import save_data
from config.settings import STRATEGY_CONFIG

config = STRATEGY_CONFIG['lof']

# Configuration
STOCK_LOF_URL = "https://www.jisilu.cn/data/lof/stock_lof_list/"
INDEX_LOF_URL = "https://www.jisilu.cn/data/lof/index_lof_list/"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "X-Requested-With": "XMLHttpRequest",
    "Referer": "https://www.jisilu.cn/data/lof/"
}
# Thresholds from settings
PREMIUM_THRESHOLD = config['min_premium_rate']
MIN_AMOUNT_THRESHOLD = config['min_fund_share'] / 10000.0  # Convert to 'Wan'
MIN_VOLUME_THRESHOLD = config['min_turnover'] / 10000.0    # Convert to 'Wan'

def fetch_data(url, fund_type):
    """Fetch data from the given URL and return filtered list."""
    print(f"Fetching {fund_type} data from {url}...")
    
    # Simulate user browsing behavior with random sleep (larger interval as requested)
    sleep_time = random.uniform(3, 8)
    print(f"Sleeping for {sleep_time:.2f} seconds to simulate human behavior...")
    time.sleep(sleep_time)
    
    try:
        # Add timestamp to params to prevent caching
        params = {
            'rp': 500,
            'page': 1,
            '___jsl': f'LST___t={int(time.time() * 1000)}'
        }
        
        response = requests.post(url, headers=HEADERS, data=params)
        
        if response.status_code != 200:
            print(f"Failed to fetch data. Status code: {response.status_code}")
            return []
            
        try:
            data = response.json()
        except Exception as e:
            print(f"Failed to decode JSON. Response text preview: {response.text[:200]}")
            return []
        rows = data.get('rows', [])
        
        results = []
        for row in rows:
            cell = row.get('cell', {})
            try:
                # Extract fields
                discount_rt = cell.get('discount_rt')
                
                # Check for valid discount rate
                if not discount_rt or discount_rt == '-':
                    continue
                    
                # From empirical check: discount_rt in JSON seems to be Premium Rate (positive for premium)
                # Example: Price 2.27, NAV 1.91 -> discount_rt 18.95%
                
                val_str = str(discount_rt).replace('%', '')
                val = float(val_str)
                
                premium_rate = val 
                
                # Liquidity/Size Filter
                # amount: Total Shares in 'Wan' (10,000)
                # volume: Turnover in 'Wan' (10,000) (Based on common Jisilu units)
                amount = float(cell.get('amount', 0))
                volume = float(cell.get('volume', 0)) # Sometimes volume is turnover
                
                is_liquid = (amount > MIN_AMOUNT_THRESHOLD) or (volume > MIN_VOLUME_THRESHOLD)
                
                if premium_rate > PREMIUM_THRESHOLD and is_liquid:
                    fund_info = {
                        'fund_id': cell.get('fund_id'),
                        'fund_name': cell.get('fund_nm'),
                        'price': cell.get('price'),
                        'premium_rate': premium_rate,
                        'amount': amount,
                        'volume': volume,
                        'fund_type': fund_type,
                        'apply_status': cell.get('apply_status', '-')
                    }
                    results.append(fund_info)
            except (ValueError, TypeError):
                continue
                
        print(f"Found {len(results)} {fund_type} funds with premium > {PREMIUM_THRESHOLD}%")
        return results
        
    except Exception as e:
        print(f"Error occurred while fetching {fund_type}: {e}")
        return []

def main():
    print("Starting Jisilu LOF/IOF Scraper...")
    
    # 1. Fetch Stock LOF
    stock_records = fetch_data(STOCK_LOF_URL, "Stock LOF")
    
    # 2. Fetch Index LOF
    # 2. Fetch Index LOF
    index_records = fetch_data(INDEX_LOF_URL, "Index LOF")

    all_records = stock_records + index_records
    
    # Save to centralized DB
    save_data('lof_funds', all_records)
    
    print("\nLOF Task Complete.")

if __name__ == "__main__":
    main()
