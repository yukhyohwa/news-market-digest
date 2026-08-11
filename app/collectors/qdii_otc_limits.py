import time
import requests
from config.settings import STRATEGY_CONFIG
from app.core.db import save_data

def fetch_otc_fund_status(fund_code):
    """
    Fetch the purchase status (SGZT) of an OTC fund using EastMoney Mobile API.
    """
    url = f'https://fundmobapi.eastmoney.com/FundMApi/FundBaseTypeInformation.ashx?FCODE={fund_code}&deviceid=1&plat=Iphone&product=EFund&version=6.0.0'
    headers = {
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X)'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            datas = data.get('Datas', {})
            if datas:
                # 修复可能存在的编码问题，因为requests有时候解析错东财的返回
                short_name = datas.get('SHORTNAME', '')
                try:
                    short_name = short_name.encode('latin1').decode('utf-8')
                except:
                    pass
                
                sgzt = datas.get('SGZT', '未知')
                try:
                    sgzt = sgzt.encode('latin1').decode('utf-8')
                except:
                    pass
                
                return {
                    'fund_id': fund_code,
                    'fund_name': short_name,
                    'nav': float(datas.get('DWJZ', 0)),
                    'apply_status': sgzt
                }
    except Exception as e:
        print(f"[!] Error fetching data for {fund_code}: {e}")
    return None

def main():
    print("\n[+] 正在抓取 OTC QDII 基金申购限额状态...")
    codes = STRATEGY_CONFIG.get('otc_funds', {}).get('codes', [])
    if not codes:
        print("未配置需要监控的 OTC 基金代码。")
        return

    results = []
    for code in codes:
        print(f"  -> Fetching {code}...")
        status_info = fetch_otc_fund_status(code)
        if status_info:
            results.append(status_info)
        time.sleep(1) # Be polite

    if results:
        save_data('fund_otc_limits', results)
        print(f"[OK] 成功抓取 {len(results)} 只 OTC 基金状态。")
    else:
        print("[!] 未抓取到任何 OTC 基金状态数据。")

if __name__ == "__main__":
    main()
