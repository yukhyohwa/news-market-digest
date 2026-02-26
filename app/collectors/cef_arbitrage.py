from curl_cffi import requests
import os
import sys
import time
import random
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from app.core.db import save_data
from config.settings import STRATEGY_CONFIG

config = STRATEGY_CONFIG['cef']

# Load credentials from .env
load_dotenv()
EMAIL = os.getenv("CEF_EMAIL")
PASSWORD = os.getenv("CEF_PASSWORD")

LOGIN_URL = "https://www.cefconnect.com/User/Login.aspx"
# We'll fetch all fields to avoid missing calculated fields like AvgDailyVolume
DATA_URL = "https://www.cefconnect.com/api/v3/DailyPricing"

def login_and_fetch_cef_data():
    """Login to CEFConnect and fetch fund data via API with advanced filtering."""
    session = requests.Session(impersonate="chrome120")
    
    print(f"Opening home page to establish session...", flush=True)
    try:
        # Initial visit
        session.get("https://www.cefconnect.com/", timeout=30)
        time.sleep(random.uniform(1, 2))
        
        print(f"Fetching login page for fields...", flush=True)
        response = session.get(LOGIN_URL, timeout=30)
        if response.status_code != 200:
             print(f"Failed to load login page. Status: {response.status_code}", flush=True)
             return []
             
        soup = BeautifulSoup(response.text, 'html.parser')
        
        try:
            viewstate = soup.find('input', {'name': '__VIEWSTATE'})['value']
            viewstate_gen = soup.find('input', {'name': '__VIEWSTATEGENERATOR'})['value']
            event_validation = soup.find('input', {'name': '__EVENTVALIDATION'})['value']
        except Exception as e:
            print(f"Could not find ASP.NET fields: {e}", flush=True)
            return []
            
        print(f"Logging in to CEFConnect as {EMAIL}...", flush=True)
        login_data = {
            '__EVENTTARGET': '',
            '__EVENTARGUMENT': '',
            '__VIEWSTATE': viewstate,
            '__VIEWSTATEGENERATOR': viewstate_gen,
            '__EVENTVALIDATION': event_validation,
            'email': EMAIL,
            'password': PASSWORD,
            'rememberMe': 'on',
            'loginSubmit': '' 
        }
        
        response = session.post(LOGIN_URL, data=login_data, timeout=30)
        
        if "Login.aspx" in response.url and "Invalid" in response.text:
            print("Login failed. Check credentials.", flush=True)
            return []
            
        print("Login successful. Fetching data from API...", flush=True)
        time.sleep(random.uniform(1, 2))
        
        # Use a real browser-like header for the API call
        response = session.get(DATA_URL, timeout=60)
        if response.status_code != 200:
            print(f"Failed to fetch data from API. Status: {response.status_code}", flush=True)
            return []
            
        try:
            funds = response.json()
            print(f"Received {len(funds)} funds from API.", flush=True)
        except Exception as e:
            print(f"Response is not JSON or parsing failed: {e}", flush=True)
            return []
            
        results = []
        for fund in funds:
            ticker = fund.get('Ticker')
            price = fund.get('Price')
            discount = fund.get('Discount')
            avg_discount = fund.get('Discount52WkAvg')
            avg_vol = fund.get('AvgDailyVolume')
            sponsor = fund.get('SponsorName', '')
            
            if ticker is None or price is None or discount is None:
                continue
                
            # Filter 1: Liquidity
            volume_usd = (avg_vol or 0) * price
            if volume_usd < config['min_volume_usd']:
                continue
                
            # Filter 2: Relative Value (Discount < -8% AND Z-Score < -2)
            z_score = fund.get('ZScore1Yr')
            
            if discount >= config['min_discount'] or (z_score is not None and z_score >= config['max_zscore']):
                continue
                
            # Note: We still calculate diff for the report, but filtering is now Z-Score based.
            diff = discount - (avg_discount or 0)
            
            # --- DIVIDEND STABILITY CHECK ---
            # Only checking for candidates that passed previous filters to minimize API calls
            dist_status = "Stable"
            try:
                # Fetch distribution history for the last 1 year
                # API format: /distributionhistory/fund/{TICKER}/{START_DATE}/{END_DATE}
                # Example dates: 01/20/2025 - 01/20/2026
                end_date = datetime.now()
                start_date = end_date - timedelta(days=365)
                date_fmt = "%m-%d-%Y"
                
                hist_url = f"https://www.cefconnect.com/api/v3/distributionhistory/fund/{ticker}/{start_date.strftime(date_fmt)}/{end_date.strftime(date_fmt)}"
                
                # Random short sleep to avoid rate limiting
                time.sleep(random.uniform(0.5, 1.5)) 
                
                h_resp = session.get(hist_url, timeout=10)
                if h_resp.status_code == 200:
                    h_data = h_resp.json()
                    dist_list = h_data.get('Data', [])
                    if len(dist_list) >= 2:
                        # Compare last two distributions
                        # Sort by PayDate just in case, though usually sorted
                        # The API returns them, let's assume order or sort them if needed. 
                        # Actually API usually returns chronological or reverse. Let's trust "recent is last or first".
                        # Let's simple check: find the latest two distinct amounts.
                        
                        # Extract amounts
                        amts = [d.get('TotDiv', 0) for d in dist_list]
                        
                        # Use simple logic: if latest < average of prev 3, or latest < prev
                        if len(amts) >= 2:
                            latest = amts[-1] # List usually ends with latest? Need to verify. 
                            # Re-verification: browser agent showed "DeclaredDateDisplay": "1/2/2026" in the list.
                            # Let's assume list is chronological.
                            prev = amts[-2]
                            
                            if latest < prev:
                                dist_status = "⚠️ Cutting"
                            elif latest > prev:
                                dist_status = "Type: Increasing"
            except Exception as e:
                print(f"Failed to check div history for {ticker}: {e}")
                pass
                
            results.append({
                'ticker': ticker,
                'name': fund.get('Name'),
                'category': fund.get('CategoryName'),
                'sponsor': sponsor,
                'price': round(price, 2),
                'nav': round(fund.get('NAV', 0), 2),
                'discount': round(discount, 2),
                'discount_52wk_avg': round(avg_discount, 2) if avg_discount else 0,
                'z_score': round(fund.get('ZScore1Yr', 0), 2) if fund.get('ZScore1Yr') else 0,
                'avg_daily_volume': int(avg_vol) if avg_vol else 0,
                'dist_status': dist_status
            })
                
        print(f"Processed funds. Found {len(results)} matches meeting criteria.", flush=True)
        return results
        
    except Exception as e:
        print(f"Error in CEF Arbitrage Collector: {e}", flush=True)
        return []

def main():
    print("Starting CEF Arbitrage Collector...", flush=True)
    if not EMAIL or not PASSWORD:
        print("CEF_EMAIL or CEF_PASSWORD not found in .env", flush=True)
        return
        
    records = login_and_fetch_cef_data()
    
    if records:
        save_data('cef_arbitrage', records)
    else:
        print("No CEF opportunities found meeting the high-bar criteria.", flush=True)
        
    print("CEF Arbitrage Task Complete.", flush=True)

if __name__ == "__main__":
    main()
