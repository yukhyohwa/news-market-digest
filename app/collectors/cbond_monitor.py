import requests
import time
import random
from datetime import datetime
from app.core.db import save_data
from config.settings import STRATEGY_CONFIG

# Configuration
CONFIG = STRATEGY_CONFIG.get('cbond', {
    'max_dblow': 195.0,
    'max_putback_price': 103.0,
    'max_putback_years': 2.0
})

# API for All Convertible Bonds (Comprehensive data)
URL = "https://datacenter-web.eastmoney.com/api/data/v1/get"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Referer": "https://data.eastmoney.com/"
}

def fetch_cbond_data():
    """Fetch all convertible bond data from Eastmoney (Real-time Market)."""
    print(f"Fetching Convertible Bond Market Data from Eastmoney...")
    
    # Simulate user behavior
    time.sleep(random.uniform(2, 4))
    
    params = {
        'reportName': 'RPT_VALUE_ANALYSIS_CB', # Comprehensive analysis report
        'columns': 'ALL',
        'sortColumns': 'PUBLIC_START_DATE',
        'sortTypes': '-1',
        'pageSize': 1000,  # Fetch all (usually ~500-600 active)
        'pageNumber': 1,
        'source': 'WEB',
        'client': 'WEB'
    }
    
    try:
        response = requests.get(URL, headers=HEADERS, params=params)
        
        if response.status_code != 200:
            print(f"Failed to fetch data. Status: {response.status_code}")
            return []
            
        data = response.json()
        if not data.get('result') or not data['result'].get('data'):
            print("No data found.")
            return []
            
        return data['result']['data']
        
    except Exception as e:
        print(f"Error fetching data from Eastmoney: {e}")
        return []


def process_cbond_data(rows):
    """Process and filter bonds based on Double Low and Put-back criteria."""
    double_low_results = []
    putback_results = []
    
    max_dblow = CONFIG.get('max_dblow', 195.0)
    max_pb_price = CONFIG.get('max_putback_price', 103.0)
    max_pb_years = CONFIG.get('max_putback_years', 2.0)
    
    for item in rows:
        try:
            bond_id = item.get('SECURITY_CODE')
            bond_nm = item.get('SECURITY_NAME_ABBR')
            price = item.get('CURRENT_BOND_PRICE')
            
            if price is None or price == '-':
                continue
            price = float(price)
            
            # Premium Rate (CONVERT_PREMIUM_RATE)
            premium_rt = item.get('CONVERT_PREMIUM_RATE')
            premium_rt = float(premium_rt) if premium_rt is not None and premium_rt != '-' else 999.0
            
            # Double Low (Price + Premium_RT)
            # EM API doesn't provide dblow, we calculate it
            dblow = price + premium_rt
                
            year_left = item.get('REMAIN_YEAR')
            year_left = float(year_left) if year_left is not None and year_left != '-' else 99.0
            
            put_dt = item.get('PUTBACK_DATE', '-') # Put-back date
            
            # 1. Double Low Monitoring
            if dblow < max_dblow and price < 130:
                double_low_results.append({
                    'bond_id': bond_id,
                    'bond_name': bond_nm,
                    'price': price,
                    'premium_rate': premium_rt,
                    'dblow': dblow,
                    'year_left': year_left,
                    'type': 'Double Low'
                })
                
            # 2. Put-back Monitoring
            is_near_putback = False
            if put_dt and put_dt != '-':
                try:
                    put_date = datetime.strptime(str(put_dt).split(' ')[0], '%Y-%m-%d')
                    days_to_put = (put_date - datetime.now()).days
                    if 0 < days_to_put < max_pb_years * 365:
                        is_near_putback = True
                except:
                    if year_left < max_pb_years:
                        is_near_putback = True
            elif year_left < max_pb_years:
                is_near_putback = True
                
            if price < max_pb_price and is_near_putback:
                putback_results.append({
                    'bond_id': bond_id,
                    'bond_name': bond_nm,
                    'price': price,
                    'premium_rate': premium_rt,
                    'dblow': dblow,
                    'put_dt': str(put_dt).split(' ')[0] if put_dt else '-',
                    'year_left': year_left,
                    'type': 'Put-back Opportunity'
                })
                
        except (ValueError, TypeError) as e:
            # print(f"Error processing bond {item.get('SECURITY_CODE')}: {e}")
            continue

            
    print(f"Found {len(double_low_results)} Double Low bonds.")
    print(f"Found {len(putback_results)} Put-back opportunities.")
    
    return double_low_results, putback_results

def main():
    print("Starting Convertible Bond Monitor...")
    raw_rows = fetch_cbond_data()
    if not raw_rows:
        print("No data fetched.")
        return
        
    low_db, putback = process_cbond_data(raw_rows)
    
    # Save results to DB
    if low_db:
        save_data('cbond_double_low', low_db)
    if putback:
        save_data('cbond_putback', putback)
        
    print("Convertible Bond Task Complete.")

if __name__ == "__main__":
    main()
