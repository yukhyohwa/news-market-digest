# News & Market Digest 🚀

![Python](https://img.shields.io/badge/Python-3.x-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Status](https://img.shields.io/badge/Status-Active-brightgreen)

An integrated intelligence tool designed for "Global News Aggregation" and "Financial Arbitrage Monitoring." It provides a comprehensive perspective ranging from macro global insights to micro market opportunities.

## 🌟 Core Features

### Part 1: 📰 RSS News & Global Insights

* **Multi-source Aggregation**: Subscribe to global mainstream media like TechCrunch, NY Times, BBC, Le Figaro, and more.
* **Intelligent Translation**: Automatically translate foreign news into Chinese (supports English, French, and other languages).
* **Keyword Categorization**: Automatically classify news entries (e.g., AI, International) based on a built-in keyword dictionary.
* **Deduplication & Merging**: Identify and merge similar topics to reduce information redundancy.

### Part 2: 💰 Financial Insights & Arbitrage

* **Fund Arbitrage**: Monitor premium/discount rates and subscription status of LOF/IOF and QDII funds.
* **Bond Monitoring**: Scan Chinese Convertible Bonds (Cbond) for "Double Low" opportunities and put-back suggestions.
* **Equity Arbitrage**: Track A-share cash option arbitrage and SPAC yield analysis.
* **Macro Market Data**: Real-time tracking of Forex rates (BOC) and major commodities (Gold, Silver).

---

## 📁 Project Structure

```text
news-market-digest/
├── main.py              # Unified entry point
├── app/               
│   ├── core/            # Core logical components
│   │   ├── fetcher.py         # Multi-threaded RSS feed aggregator
│   │   ├── processor.py       # News cleaning, deduplication, and categorization
│   │   ├── translator.py      # Multi-language translation engine
│   │   ├── renderer.py        # Markdown report generator for news
│   │   ├── db.py              # SQLite database manager for financial data
│   │   ├── arb_reporter.py    # Generator for financial arbitrage analysis
│   │   ├── unified_reporter.py # Coordinator for merged News + Finance reports
│   │   └── mailer.py          # SMTP email delivery service
│   ├── collectors/      # Specialized financial data scrapers
│   │   ├── market_indices.py  # Global market indices tracking
│   │   ├── forex.py           # Real-time exchange rates (BOC)
│   │   ├── commodities.py     # Gold, Silver, and Commodities prices
│   │   ├── cbond_monitor.py   # Convertible Bond analysis (Double Low strategy)
│   │   ├── lof_funds.py       # LOF/IOF premium and discount monitoring
│   │   ├── qdii_arbitrage.py  # QDII fund arbitrage opportunity tracking
│   │   ├── cef_arbitrage.py   # Closed-End Fund (CEF) monitoring
│   │   ├── bond_issuance.py   # New bond issuance alerts
│   │   ├── a_share_arbitrage.py # A-share cash option and stock arbitrage
│   │   └── spac_arbitrage.py  # SPAC yield and opportunity analysis
├── config/            
│   ├── settings.py      # Configuration for RSS feeds, API keys, and email
│   └── categories.json  # Dictionary for news keyword-based categorization
├── data/                # Local database storage (finance_data.db)
├── output/              # Generated intelligence reports (.md)
└── requirements.txt     # Python dependencies
```

## 🛠️ Quick Start

### 1. Installation

```bash
pip install -r requirements.txt
```

### 2. Usage

```bash
# Run full aggregation (News + Finance) and generate report
python main.py

# Run only RSS News part
python main.py --news

# Run only Financial Arbitrage part
python main.py --arb

# Run and send the report via Email
python main.py --mail
```

## 📄 Notes

* Financial analysis data is for reference only and does not constitute investment advice.
* Database is stored in the `data/` directory; Markdown reports are in the `output/` directory.
