
import requests
import json
from datetime import datetime, timedelta
from app.core.db import save_data
import time
import random

# API for New Convertible Bonds (Issuance/Listing)
# Returns list with PUBLIC_START_DATE (Subscription) and LISTING_DATE
API_URL = "https://datacenter-web.eastmoney.com/api/data/v1/get"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Referer": "https://data.eastmoney.com/"
}

def fetch_issuance_data():
    print("Fetching Bond Issuance Data...")
    
    # Simulate user behavior
    time.sleep(random.uniform(2, 5))
    
    params = {
        'reportName': 'RPT_BOND_CB_LIST',
        'columns': 'ALL',
        'sortColumns': 'PUBLIC_START_DATE',
        'sortTypes': '-1',
        'pageSize': 100,  # Fetch recent 100
        'pageNumber': 1,
        'source': 'WEB',
        'client': 'WEB'
    }
    
    try:
        response = requests.get(API_URL, headers=HEADERS, params=params)
        
        if response.status_code != 200:
            print(f"Failed to fetch data. Status: {response.status_code}")
            return []
            
        data = response.json()
        if not data.get('result') or not data['result'].get('data'):
            print("No data found.")
            return []
            
        return data['result']['data']
        
    except Exception as e:
        print(f"Error fetching data: {e}")
        return []

def filter_bond_data(data):
    """
    Filter bonds that are available for subscription or listing today or tomorrow.
    """
    results = []
    
    now = datetime.now()
    today_str = now.strftime('%Y-%m-%d')
    tomorrow = now + timedelta(days=1)
    tomorrow_str = tomorrow.strftime('%Y-%m-%d')
    
    print(f"Checking for events on {today_str} and {tomorrow_str}...")
    
    for item in data:
        # Fields: SECURITY_CODE, SECURITY_NAME_ABBR, PUBLIC_START_DATE, LISTING_DATE
        sub_date = item.get('PUBLIC_START_DATE')
        list_date = item.get('LISTING_DATE')
        code = item.get('SECURITY_CODE')
        name = item.get('SECURITY_NAME_ABBR')
        
        event_type = []
        
        # Check Subscription (申购)
        if sub_date:
            sub_d = str(sub_date).split(' ')[0]
            if sub_d == today_str:
                event_type.append(f"Subscription Today ({sub_d})")
            elif sub_d == tomorrow_str:
                event_type.append(f"Subscription Tomorrow ({sub_d})")
        
        # Check Listing (上市)
        if list_date:
            list_d = str(list_date).split(' ')[0]
            if list_d == today_str:
                event_type.append(f"Listing Today ({list_d})")
            elif list_d == tomorrow_str:
                event_type.append(f"Listing Tomorrow ({list_d})")
                
        if event_type:
            bond_info = {
                'bond_code': code,
                'bond_name': name,
                'subscription_date': str(sub_date).split(' ')[0] if sub_date else '-',
                'listing_date': str(list_date).split(' ')[0] if list_date else '-',
                'details': ', '.join(event_type)
            }
            results.append(bond_info)
            
    print(f"Found {len(results)} bond events for today/tomorrow.")
    return results

def main():
    print("Starting Bond Issuance/Listing Checker...")
    raw_data = fetch_issuance_data()
    filtered_data = filter_bond_data(raw_data)
    
    save_data('bond_issuance', filtered_data)
    print("Bond Issuance Task Complete.")

if __name__ == "__main__":
    main()
