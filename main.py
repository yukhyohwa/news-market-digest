import os
import time
import argparse

from app.core.db import init_db
from app.core.unified_reporter import generate_unified_report
from app.core.mailer import send_report_email

# Market collectors only
from app.collectors.lof_funds import main as run_jisilu_lof
from app.collectors.a_share_arbitrage import main as run_a_share_arbitrage
from app.collectors.bond_issuance import main as run_bond_issuance
from app.collectors.forex import main as run_forex_rates
from app.collectors.commodities import main as run_commodities
from app.collectors.spac_arbitrage import main as run_spac_arbitrage
from app.collectors.cef_arbitrage import main as run_cef_arbitrage
from app.collectors.qdii_arbitrage import main as run_qdii_arbitrage
from app.collectors.cbond_monitor import main as run_cbond_monitor
from app.collectors.market_indices import main as run_market_indices
from app.collectors.qdii_otc_limits import main as run_otc_limits


def run_market_pipeline():
    """Run market collectors and persist data in market-digest/data only."""
    print("\n>>> Running Market Data Tasks...")
    init_db()
    tasks = [
        ("LOF/IOF", run_jisilu_lof),
        ("Bond Issuance", run_bond_issuance),
        ("A-share Arbitrage", run_a_share_arbitrage),
        ("Forex Rates", run_forex_rates),
        ("Commodities", run_commodities),
        ("SPAC Arbitrage", run_spac_arbitrage),
        ("CEF Arbitrage", run_cef_arbitrage),
        ("QDII Arbitrage", run_qdii_arbitrage),
        ("Cbond Monitor", run_cbond_monitor),
        ("Market Indices", run_market_indices),
        ("QDII OTC Limits", run_otc_limits),
    ]
    for name, task in tasks:
        print(f"  -> Processing {name}...")
        try:
            task()
        except Exception as exc:
            print(f"  !!! Error in {name}: {exc}")


def cleanup_old_images(days=30):
    images_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output", "images")
    if not os.path.exists(images_dir):
        return
    cutoff = time.time() - days * 86400
    deleted = 0
    for filename in os.listdir(images_dir):
        if filename.endswith(".png"):
            path = os.path.join(images_dir, filename)
            if os.stat(path).st_mtime < cutoff:
                try:
                    os.remove(path)
                    deleted += 1
                except OSError as exc:
                    print(f"Failed to delete {filename}: {exc}")
    if deleted:
        print(f"[CLEANUP] Deleted {deleted} old image(s).")


def main():
    parser = argparse.ArgumentParser(description="Market Digest")
    parser.add_argument("--mail", action="store_true", help="Send the market report by email")
    args = parser.parse_args()

    start_time = time.time()
    print("===========================================")
    print("=== Global Market Digest ===")
    print("===========================================")
    run_market_pipeline()
    print("\n>>> Generating Market Report...")
    report_path = generate_unified_report(include_arb=True)
    if report_path:
        print(f"[OK] Report generated: {report_path}")
        if args.mail:
            send_report_email(report_path)
            print("[SUCCESS] Email sent successfully.")
    else:
        print("[FAIL] Failed to generate report.")
    cleanup_old_images()
    print(f"\nTotal Time: {time.time() - start_time:.2f} seconds")


if __name__ == "__main__":
    main()
