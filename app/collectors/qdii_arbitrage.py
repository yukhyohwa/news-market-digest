import requests
import time
import random
from app.core.db import save_data
from config.settings import STRATEGY_CONFIG

config = STRATEGY_CONFIG.get('qdii', {
    'min_premium_rate': 2.0,
    'min_fund_share': 100000,
    'min_turnover': 10000
})

# Configuration
URLS = {
    'Asia': 'https://www.jisilu.cn/data/qdii/qdii_list/A',
    'Europe/America': 'https://www.jisilu.cn/data/qdii/qdii_list/E',
    'Commodities': 'https://www.jisilu.cn/data/qdii/qdii_list/C'
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "X-Requested-With": "XMLHttpRequest",
    "Referer": "https://www.jisilu.cn/data/qdii/"
}

# Thresholds from settings
PREMIUM_THRESHOLD = config.get('min_premium_rate', 2.0)
MIN_AMOUNT_THRESHOLD = config.get('min_fund_share', 100000) / 10000.0  # Convert to 'Wan'
MIN_VOLUME_THRESHOLD = config.get('min_turnover', 10000) / 10000.0    # Convert to 'Wan'

def fetch_qdii_data(market_name, url):
    """Fetch QDII data from the given URL and return filtered list."""
    print(f"Fetching {market_name} QDII data from {url}...")
    
    # Simulate user browsing behavior with random sleep
    sleep_time = random.uniform(2, 5)
    print(f"Sleeping for {sleep_time:.2f} seconds...")
    time.sleep(sleep_time)
    
    try:
        params = {
            'rp': 500,
            'only_lof': 'y',
            'only_etf': 'n',  # Exclude EOF/ETF as retail investors can't easily arbitrate them
            '___jsl': f'LST___t={int(time.time() * 1000)}'
        }
        
        response = requests.get(url, headers=HEADERS, params=params)
        
        if response.status_code != 200:
            print(f"Failed to fetch data. Status code: {response.status_code}")
            return []
            
        try:
            data = response.json()
        except Exception as e:
            print(f"Failed to decode JSON: {e}")
            return []
            
        rows = data.get('rows', [])
        results = []
        
        for row in rows:
            cell = row.get('cell', {})
            try:
                fund_id = cell.get('fund_id')
                fund_name = cell.get('fund_nm')
                
                # Skip ETF funds explicitly if they still appear in the list
                if 'ETF' in fund_name.upper():
                    continue

                # Premium rates
                discount_rt_str = str(cell.get('discount_rt', '0')).replace('%', '')
                discount_rt2_str = str(cell.get('discount_rt2', '0')).replace('%', '')
                
                # Handle 'buy' or '-' values in premium rates
                premium_rate = 0.0
                if discount_rt_str not in ('buy', '-', ''):
                    premium_rate = float(discount_rt_str)
                
                realtime_premium_rate = 0.0
                if discount_rt2_str not in ('buy', '-', ''):
                    realtime_premium_rate = float(discount_rt2_str)
                
                # Liquidity/Size Filter
                amount = float(cell.get('amount', 0) or 0)
                volume = float(cell.get('volume', 0) or 0)
                
                is_liquid = (amount > MIN_AMOUNT_THRESHOLD) or (volume > MIN_VOLUME_THRESHOLD)
                
                # Use max of T-1 and Realtime premium for filtering
                max_premium = max(premium_rate, realtime_premium_rate)
                
                apply_status = cell.get('apply_status', '')
                
                # Filter: Premium > Threshold AND Liquid AND Not Suspended
                if max_premium > PREMIUM_THRESHOLD and is_liquid and apply_status != '暂停申购':
                    # Clean up estimate values
                    est_val = cell.get('estimate_value', '-')
                    est_val2 = cell.get('estimate_value2', '-')
                    
                    fund_info = {
                        'fund_id': fund_id,
                        'fund_name': fund_name,
                        'price': float(cell.get('price', 0) or 0),
                        'premium_rate': premium_rate,
                        'estimate_value': float(est_val) if est_val not in ('buy', '-', '') else None,
                        'realtime_premium_rate': realtime_premium_rate,
                        'realtime_estimate_value': float(est_val2) if est_val2 not in ('buy', '-', '') else None,
                        'volume': volume,
                        'amount': amount,
                        'index_name': cell.get('index_nm'),
                        'apply_status': cell.get('apply_status'),
                        'market_type': market_name
                    }
                    results.append(fund_info)
            except (ValueError, TypeError) as e:
                # print(f"Error parsing row for {cell.get('fund_id')}: {e}")
                continue
                
        print(f"Found {len(results)} QDII funds in {market_name} with premium > {PREMIUM_THRESHOLD}%")
        return results
        
    except Exception as e:
        print(f"Error occurred while fetching {market_name}: {e}")
        return []

def main():
    print("Starting Jisilu QDII Arbitrage Scraper...")
    
    all_records = []
    for market, url in URLS.items():
        records = fetch_qdii_data(market, url)
        all_records.extend(records)
    
    if all_records:
        # Save to centralized DB
        save_data('qdii_arbitrage', all_records)
        print(f"Total {len(all_records)} QDII records saved.")
    else:
        print("No QDII arbitrage opportunities found.")
    
    print("\nQDII Task Complete.")

if __name__ == "__main__":
    main()
