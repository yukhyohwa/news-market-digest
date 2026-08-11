
import os
import datetime
from app.core.arb_reporter import fetch_daily_data, fetch_latest_data, format_liq, format_table, get_previous_otc_status
from app.core.processor import truncate_summary
from config.settings import STRATEGY_CONFIG

def generate_unified_report(categorized_news=None, include_arb=True):
    """
    Combines News Summary and Market Arbitrage into a single report.
    """
    today = datetime.datetime.now().strftime('%Y-%m-%d')
    output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "output")
    os.makedirs(output_dir, exist_ok=True)
    
    filename = os.path.join(output_dir, f"Global_Digest_{today}.md")
    
    report_content = f"# Global News & Market Digest Report ({today})\n\n"
    
    # 1. Arbitrage Section (from DB)
    if include_arb:
        report_content += "## 💰 Market Arbitrage & Opportunities\n\n"
        
        # 1. Market Indices (Global)
        report_content += "### 1. Market Indices (Global)\n"
        indices_chart_path = os.path.join(output_dir, 'images', f'market_indices_{today}.png')
        if os.path.exists(indices_chart_path):
            report_content += f"![Market Indices 30-Day Trend](images/market_indices_{today}.png)\n\n"
        else:
            report_content += "*No market index data or chart available.*\n\n"

        # 2. Commodities
        report_content += "### 2. Commodities\n"
        commodities_chart_path = os.path.join(output_dir, 'images', f'commodities_{today}.png')
        if os.path.exists(commodities_chart_path):
            report_content += f"![Commodities 30-Day Trend](images/commodities_{today}.png)\n\n"
        else:
            report_content += "*No commodities chart available.*\n\n"

        # 3. Forex Rates
        report_content += "### 3. Forex Rates\n"
        forex_chart_path = os.path.join(output_dir, 'images', f'forex_rates_{today}.png')
        if os.path.exists(forex_chart_path):
            report_content += f"![Forex Rates 30-Day Trend](images/forex_rates_{today}.png)\n\n"
        else:
            report_content += "*No forex chart available.*\n\n"

        # 4. QDII OTC Fund Limits Monitor
        report_content += "### 4. QDII OTC Fund Limits Monitor\n"
        rows, cols = fetch_daily_data('fund_otc_limits', today)
        if rows:
            display_rows = []
            for r in rows:
                fund_code, fund_name, nav, status = r[1], r[2], r[3], r[4]
                prev_status = get_previous_otc_status(fund_code, today)
                # Only show if status has changed
                if prev_status is None or status != prev_status:
                    display_rows.append([fund_code, fund_name, f"{nav:.4f}", f"{status} (was: {prev_status or 'Unknown'})"])
                    
            if display_rows:
                report_content += format_table(display_rows, ['Fund Code', 'Fund Name', 'NAV', 'Status Change'], ['left', 'left', 'right', 'left']) + "\n\n"
            else:
                report_content += "*No limit changes detected since last week.*\n\n"
        else:
            report_content += "*No OTC Fund status data available today.*\n\n"

        # 5. Bond Issuance
        report_content += "### 5. Bond Issuance & Listing\n"
        rows, cols = fetch_daily_data('bond_issuance', today)
        if rows:
            display_rows = [[r[1], r[2], r[3], r[4], r[5]] for r in rows]
            report_content += format_table(display_rows, ['Code', 'Name', 'Sub Date', 'List Date', 'Details'], ['left', 'left', 'left', 'left', 'left']) + "\n\n"
        else:
            report_content += "*No new bond events for today.*\n\n"

        # 6. Cbond
        report_content += f"### 6. Cbond Double Low (< {STRATEGY_CONFIG['cbond']['max_dblow']})\n"
        rows, cols = fetch_daily_data('cbond_double_low', today)
        if rows:
            display_rows = [[r[1], r[2], f"{r[3]:.2f}", f"{r[4]:.2f}%", f"{r[5]:.2f}", f"{r[6]:.2f}y"] for r in rows]
            report_content += format_table(display_rows, ['Code', 'Name', 'Price', 'Premium', 'LowIndex', 'Rem.Y'], ['left', 'left', 'right', 'right', 'right', 'right']) + "\n\n"
        else:
            report_content += "*No Cbond double-low opportunities today.*\n\n"

        rows, cols = fetch_daily_data('cbond_putback', today)
        report_content += f"### 7. Cbond Put-back Opportunity (< {STRATEGY_CONFIG['cbond']['max_putback_price']})\n"
        if rows:
            display_rows = [[r[1], r[2], f"{r[3]:.2f}", f"{r[4]:.2f}%", r[6] or "-", f"{r[7]:.2f}y"] for r in rows]
            report_content += format_table(display_rows, ['Code', 'Name', 'Price', 'Premium', 'Put Date', 'Rem.Y'], ['left', 'left', 'right', 'right', 'left', 'right']) + "\n\n"
        else:
            report_content += "*No Cbond put-back opportunities found today.*\n\n"

        # 8. LOF/IOF
        report_content += f"### 8. LOF/IOF Funds (|Premium| > {STRATEGY_CONFIG['lof']['min_premium_rate']}%)\n"
        rows, cols = fetch_daily_data('lof_funds', today, "fund_id, fund_name, price, premium_rate, amount, volume, apply_status")
        if rows:
            display_rows = []
            for r in rows:
                status = r[6]
                if status and '开放申购' in status:
                    continue
                details = []
                if r[4] > 0: details.append(f"Amt:{format_liq(r[4])}")
                if r[5] > 0: details.append(f"Vol:{format_liq(r[5])}")
                display_rows.append([r[0], r[1], f"{r[2]:.3f}", f"{r[3]:.2f}%", status or "-", ", ".join(details)])
            if display_rows:
                report_content += format_table(display_rows, ['Code', 'Name', 'Price', 'Premium', 'Status', 'Liquidity'], ['left', 'left', 'right', 'right', 'left', 'left']) + "\n\n"
            else:
                report_content += "*No arbitrage opportunities found today.*\n\n"
        else:
            report_content += "*No arbitrage opportunities found today.*\n\n"

        # 9. QDII
        report_content += f"### 9. QDII Arbitrage (|Premium| > {STRATEGY_CONFIG['qdii']['min_premium_rate']}%)\n"
        rows, cols = fetch_daily_data('qdii_arbitrage', today)
        if rows:
            display_rows = []
            for r in rows:
                fund_name = r[2]
                if 'ETF' in fund_name.upper() or 'EOF' in fund_name.upper(): continue
                status = r[11]
                if status and '开放申购' in status:
                    continue
                details = []
                if r[9] > 0: details.append(f"Amt:{format_liq(r[9])}")
                if r[8] > 0: details.append(f"Vol:{format_liq(r[8])}")
                market = "APAC" if r[12] == "Asia" else r[12]
                display_rows.append([r[1], fund_name, market, f"{r[4]:.2f}%", f"{r[6]:.2f}%" if r[6] is not None else "-", status or "-", ", ".join(details)])
            if display_rows:
                report_content += format_table(display_rows, ['Code', 'Name', 'Market', 'T-1 Prem', 'Realtime', 'Status', 'Liquidity'], ['left', 'left', 'left', 'right', 'right', 'left', 'left']) + "\n\n"
            else:
                report_content += "*No arbitrage opportunities found today.*\n\n"
        else:
            report_content += "*No arbitrage opportunities found today.*\n\n"

        # 10. A-share
        min_a_share_yield = STRATEGY_CONFIG.get('a_share', {}).get('min_annualized_yield', 7.0)
        report_content += f"### 10. A-share Arbitrage (Yield >= {min_a_share_yield}%)\n"
        rows, cols = fetch_daily_data('stock_arbitrage', today)
        if rows:
            display_rows = []
            for r in rows:
                row_dict = dict(zip(cols, r))
                price = row_dict.get('price')
                cash_price = row_dict.get('choose_price')
                yield_pct = row_dict.get('yield_pct')
                type_cd = row_dict.get('type_cd', '-')
                descr = row_dict.get('descr', '')
                
                if price and price > 0:
                    display_rows.append([row_dict.get('stock_id'), row_dict.get('stock_name'), f"{price:.2f}", f"{cash_price:.2f}", f"{yield_pct:.2f}%" if yield_pct is not None else "-", type_cd, descr])
            if display_rows:
                report_content += format_table(display_rows, ['Code', 'Name', 'Price', 'Cash Price', 'Yield', 'Type', 'Description'], ['left', 'left', 'right', 'right', 'right', 'left', 'left']) + "\n\n"
            else:
                report_content += "*No A-share arbitrage opportunities found today.*\n\n"
        else:
            report_content += "*No A-share arbitrage opportunities found today.*\n\n"

        # 11. SPAC
        report_content += "### 11. SPAC Arbitrage\n"
        rows, cols = fetch_daily_data('spac_arbitrage', today)
        if rows:
            display_rows = [[r[1], r[2], r[3], f"{r[4]:.2f}", f"{r[5]:.2f}", f"{r[6]:.2f}%", str(r[7])] for r in rows]
            report_content += format_table(display_rows, ['Symbol', 'Name', 'IPO Date', 'Price', 'NAV', 'Yield', 'Days'], ['left', 'left', 'left', 'right', 'right', 'right', 'right']) + "\n\n"
        else:
            report_content += "*No SPAC arbitrage opportunities found today.*\n\n"

        # 12. CEF
        min_vol_k = STRATEGY_CONFIG['cef']['min_volume_usd'] // 1000
        report_content += f"### 12. CEF Arbitrage (Disc < {STRATEGY_CONFIG['cef']['min_discount']}%, Vol USD >= {min_vol_k:,}K)\n"
        rows, cols = fetch_daily_data('cef_arbitrage', today)
        if rows:
            display_rows = []
            for r in rows:
                ticker, price, discount, avg_disc, zscore = r[1], r[5], r[7], r[8], r[9]
                diff = discount - avg_disc
                vol_usd = (r[10] or 0) * price
                
                # Volume Filter from STRATEGY_CONFIG
                if vol_usd < STRATEGY_CONFIG['cef']['min_volume_usd']:
                    continue
                    
                dist_status = r[11] if len(r) > 11 else ""
                
                # Div Qual Filter
                if dist_status and 'Cutting' in dist_status:
                    continue
                    
                display_rows.append([ticker, r[2], f"{discount:.2f}%", f"{diff:.2f}%", f"{zscore:.2f}", f"${vol_usd/1000:.0f}K", dist_status])
            
            if display_rows:
                report_content += format_table(display_rows, ['Ticker', 'Name', 'Discount', 'Diff', 'Z-Score', 'Vol USD', 'Div Qual'], ['left', 'left', 'right', 'right', 'right', 'right', 'left']) + "\n\n"
            else:
                report_content += "*No CEF arbitrage opportunities meeting the volume criteria found today.*\n\n"
        else:
            report_content += "*No CEF arbitrage opportunities found today.*\n\n"

    # 2. News Section
    if categorized_news:
        report_content += "## 🌏 Global News Summary\n\n"
        all_categories = list(categorized_news.keys())
        
        # Define target order
        target_order = ["Technology", "Economy & Finance", "Politics & International", "Energy & Environment"]
        
        # Build final display order
        categories_order = [c for c in target_order if c in categorized_news]
        # Collect any remaining categories not in target_order
        remaining = [c for c in all_categories if c not in target_order and c != "Others"]
        categories_order.extend(remaining)
        
        if "Others" in all_categories:
            categories_order.append("Others")
        
        for category in categories_order:
            articles = categorized_news.get(category, [])
            if not articles:
                continue
            
            report_content += f"### 📰 {category} ({len(articles)} items)\n\n"
            for article in articles:
                source_line = ", ".join([f"[{s['name']}]({s['link']})" for s in article['sources']])
                report_content += f"#### ● {article['translated_title']} (Source: {source_line})\n"
                if article['translated_summary']:
                    truncated_summary = truncate_summary(article['translated_summary'], word_limit=100)
                    report_content += f"{truncated_summary}\n"
                report_content += "\n"

    # Sources
    report_content += "## 📚 Sources\n"
    report_content += "- **News**: TechCrunch, NY Times, BBC, Le Figaro\n"
    report_content += "- **Market Data**: Yahoo Finance, Bank of China, Jisilu, Eastmoney, StockAnalysis, CEFConnect\n"

    with open(filename, 'w', encoding='utf-8') as f:
        f.write(report_content)
    
    return filename
