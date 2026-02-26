# 📡 BuySignal — Buying Signals Identifier
> No API. No subscriptions. Pure web scraping.

## What It Does
Enter any company name → scrapes Google, Bing & DuckDuckGo live → detects buying signals:
- 🚀 New Product Launches
- 💰 Funding & Investment Rounds
- 📈 Expansion & Growth
- 👥 Hiring Surges
- 🤝 Partnerships & M&A
- ⚙️ Technology Adoption
- 🌍 Market Entry
- 👤 Leadership Changes
- 📊 Financial Performance

## Setup (One Time)

```bash
pip install requests beautifulsoup4 lxml flask
```

## Run

```bash
cd buying_signals
python server.py
```

Then open your browser at: **http://localhost:5055**

## Files
```
buying_signals/
├── scraper.py    ← Web scraping + signal classification engine
├── server.py     ← Flask web server
├── index.html    ← Beautiful frontend UI
└── README.md
```

## How It Works
1. **scraper.py** builds search queries like `"Freshworks" funding investment`
2. Sends them to DuckDuckGo → Bing → Google (fallback chain)
3. Parses HTML with BeautifulSoup — no API keys needed
4. Matches article text against 80+ buying signal keywords across 9 categories
5. Scores each signal by keyword density + category weight
6. Computes a 0–100 Buying Readiness Score

## CLI Mode (no UI)
```bash
python scraper.py "Salesforce"
python scraper.py "Infosys"
```
