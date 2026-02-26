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
global-news-market-digest/
├── main.py              # Unified entry point
├── app/               
│   ├── core/            # Logic: Fetchers, Processors, DB, & Unified Reporter
│   ├── collectors/      # Financial scrapers: LOF, QDII, Cbond, CEF, etc.
├── config/            
│   ├── settings.py      # RSS feeds, Email, and Strategy configurations
│   └── categories.json  # News categorization dictionary
├── data/                # SQLite Database (finance_data.db)
├── output/              # Generated Markdown intelligence reports
└── requirements.txt     # Project dependencies
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
