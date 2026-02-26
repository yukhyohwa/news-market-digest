
import requests
from bs4 import BeautifulSoup
import time
import random
import re
from app.core.db import save_data

# Configurations
CURRENCY_MAP = {
    'usd': '美元',
    'eur': '欧元',
    'jpy': '日元',
    'gbp': '英镑'
}
TARGET_CURRENCIES = list(CURRENCY_MAP.values())

def fetch_boc_rates():
    url = "https://www.boc.cn/sourcedb/whpj/"
    print(f"Fetching rates from {url}...")
    
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        resp = requests.get(url, headers=headers)
        resp.encoding = 'utf-8'
        
        soup = BeautifulSoup(resp.text, 'html.parser')
        tables = soup.find_all('table')
        
        target_table = None
        for table in tables:
            text = table.get_text()
            if '货币名称' in text and '现汇买入价' in text:
                target_table = table
                break
        
        if not target_table:
            print("No valid rate table found on BOC page.")
            return []
        
        rows = target_table.find_all('tr')
        if len(rows) < 2:
            return []
            
        # Parse Headers
        header_cols = [t.get_text(strip=True) for t in rows[0].find_all(['th', 'td'])]
        print(f"BOC Headers: {header_cols}")
        
        # Map indices
        idx_currency = -1
        idx_spot_buy = -1
        idx_cash_buy = -1
        idx_spot_sell = -1
        idx_cash_sell = -1
        
        for i, h in enumerate(header_cols):
            if '货币名称' in h: idx_currency = i
            elif '现汇买入价' in h: idx_spot_buy = i
            elif '现钞买入价' in h: idx_cash_buy = i
            elif '现汇卖出价' in h: idx_spot_sell = i
            elif '现钞卖出价' in h: idx_cash_sell = i
            
        if idx_currency == -1:
            print("Currency column not found.")
            return []

        results = []
        
        for row in rows[1:]:
            cols = [t.get_text(strip=True) for t in row.find_all(['td'])]
            if not cols or len(cols) <= idx_currency: continue
            
            currency_name = cols[idx_currency].strip()
            
            if currency_name in TARGET_CURRENCIES:
                # Parse rates
                def parse_rate(val):
                    if not val: return 0.0
                    match = re.search(r'(\d+\.?\d*)', val)
                    if match:
                        try:
                            return float(match.group(1))
                        except:
                            return 0.0
                    return 0.0

                spot_buy = parse_rate(cols[idx_spot_buy]) if idx_spot_buy != -1 else 0.0
                cash_buy = parse_rate(cols[idx_cash_buy]) if idx_cash_buy != -1 else 0.0
                spot_sell = parse_rate(cols[idx_spot_sell]) if idx_spot_sell != -1 else 0.0
                cash_sell = parse_rate(cols[idx_cash_sell]) if idx_cash_sell != -1 else 0.0
                
                # Reverse Map Chinese name to Code for consistency? 
                # Or store Chinese Name. User's previous requirement was USD/Euro/JPY.
                # I'll store the Chinese name as 'currency'.
                
                item = {
                    'currency': currency_name,
                    'bank': '中国银行',
                    'spot_buy': spot_buy,
                    'cash_buy': cash_buy,
                    'spot_sell': spot_sell,
                    'cash_sell': cash_sell
                }
                results.append(item)
                
        return results

    except Exception as e:
        print(f"Error fetching BOC rates: {e}")
        return []

def main():
    print("Starting Forex Rate Checker (BOC)...")
    data = fetch_boc_rates()
    
    if data:
        print(f"Found {len(data)} records.")
        save_data('forex_rates', data)
        print("Forex Task Complete.")
    else:
        print("No data found.")

if __name__ == "__main__":
    main()
