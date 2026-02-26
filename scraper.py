import requests
from bs4 import BeautifulSoup
import re
import time
import random
from urllib.parse import quote_plus, urljoin
from datetime import datetime

HEADERS_LIST = [
    {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
    },
    {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Connection": "keep-alive",
    }
]

# ─── Signal keyword patterns ───────────────────────────────────────────────────
SIGNAL_PATTERNS = {
    "🚀 New Product Launch": {
        "keywords": ["launch", "launches", "launched", "new product", "unveil", "unveils",
                     "announces", "introduces", "release", "released", "debut", "new feature",
                     "new solution", "new platform", "new service", "new offering"],
        "color": "#00ff88",
        "weight": 3
    },
    "💰 Funding & Investment": {
        "keywords": ["funding", "raises", "raised", "investment", "series a", "series b",
                     "series c", "seed round", "venture", "vc", "million", "billion",
                     "capital", "investor", "valuation", "ipo", "goes public", "listed"],
        "color": "#ffcc00",
        "weight": 4
    },
    "📈 Expansion & Growth": {
        "keywords": ["expand", "expansion", "expands", "opens", "new office", "new location",
                     "enters market", "new market", "growth", "scaling", "scale up",
                     "new region", "international", "global expansion", "new headquarters"],
        "color": "#00ccff",
        "weight": 3
    },
    "👥 Hiring Surge": {
        "keywords": ["hiring", "hire", "recruitment", "jobs", "career", "talent",
                     "headcount", "team expansion", "new employees", "workforce",
                     "looking for", "join our team", "we're growing"],
        "color": "#ff6b6b",
        "weight": 2
    },
    "🤝 Partnership & M&A": {
        "keywords": ["partnership", "partner", "acquisition", "acquires", "acquired",
                     "merger", "merges", "collaboration", "collaborate", "deal",
                     "joint venture", "strategic alliance", "teaming up"],
        "color": "#cc88ff",
        "weight": 3
    },
    "⚙️ Technology Adoption": {
        "keywords": ["digital transformation", "ai", "automation", "cloud", "migrates",
                     "adopts", "implements", "deploys", "technology", "innovation",
                     "modernize", "upgrade", "new system", "new platform", "tech stack"],
        "color": "#ff9944",
        "weight": 2
    },
    "🌍 Market Entry": {
        "keywords": ["enters", "launch in", "new country", "new territory", "market entry",
                     "expands to", "now available in", "opens in", "first in"],
        "color": "#44ffcc",
        "weight": 3
    },
    "👤 Leadership Change": {
        "keywords": ["ceo", "appoints", "appointed", "new cto", "new cfo", "new vp",
                     "chief", "executive", "leadership", "president", "director",
                     "joins as", "promoted to", "new hire"],
        "color": "#ff44aa",
        "weight": 2
    },
    "📊 Financial Performance": {
        "keywords": ["revenue", "profit", "earnings", "quarterly", "annual report",
                     "record revenue", "growth rate", "market cap", "results",
                     "beat expectations", "surpassed"],
        "color": "#88ccff",
        "weight": 2
    }
}


def get_headers():
    return random.choice(HEADERS_LIST)


def search_bing(company_name, query_suffix=""):
    """Scrape Bing search results"""
    results = []
    query = f'"{company_name}" {query_suffix}'.strip()
    url = f"https://www.bing.com/news/search?q={quote_plus(query)}&freshness=Month"

    try:
        resp = requests.get(url, headers=get_headers(), timeout=10)
        soup = BeautifulSoup(resp.text, "lxml")

        cards = soup.find_all("div", class_=re.compile(r"news-card|card-with-cluster", re.I))
        if not cards:
            cards = soup.find_all("div", {"data-eventid": True})
        if not cards:
            cards = soup.find_all("div", class_=re.compile(r"t_s|newsitem", re.I))

        for card in cards[:8]:
            title_el = card.find(["a", "h2", "h3"])
            title = title_el.get_text(strip=True) if title_el else ""
            link = title_el.get("href", "") if title_el else ""
            snippet_el = card.find("p") or card.find("div", class_=re.compile(r"snippet|desc", re.I))
            snippet = snippet_el.get_text(strip=True) if snippet_el else ""
            time_el = card.find("span", class_=re.compile(r"time|date|ago", re.I))
            date_str = time_el.get_text(strip=True) if time_el else ""

            if title and len(title) > 10:
                results.append({
                    "title": title,
                    "snippet": snippet,
                    "link": link,
                    "date": date_str,
                    "source": "Bing News"
                })
    except Exception as e:
        print(f"Bing error: {e}")

    return results


def search_google(company_name, query_suffix=""):
    """Scrape Google search results"""
    results = []
    query = f'"{company_name}" {query_suffix}'.strip()
    url = f"https://www.google.com/search?q={quote_plus(query)}&tbm=nws&tbs=qdr:m"

    try:
        resp = requests.get(url, headers=get_headers(), timeout=10)
        soup = BeautifulSoup(resp.text, "lxml")

        articles = soup.find_all("div", class_=re.compile(r"SoaBEf|WlydOe|ftSUBd|nChh6e", re.I))
        if not articles:
            articles = soup.find_all("article")
        if not articles:
            articles = soup.find_all("div", class_=re.compile(r"dbsr|g ", re.I))

        for art in articles[:8]:
            title_el = art.find(["h3", "h4", "a"])
            title = title_el.get_text(strip=True) if title_el else ""
            link_el = art.find("a")
            link = link_el.get("href", "") if link_el else ""
            snippet_el = art.find("div", class_=re.compile(r"Y3v8qd|st|s3v9rd", re.I))
            snippet = snippet_el.get_text(strip=True) if snippet_el else ""
            time_el = art.find(["time", "span"], class_=re.compile(r"time|WG9SHc", re.I))
            date_str = time_el.get_text(strip=True) if time_el else ""

            if title and len(title) > 10:
                results.append({
                    "title": title,
                    "snippet": snippet,
                    "link": link if link.startswith("http") else "",
                    "date": date_str,
                    "source": "Google News"
                })
    except Exception as e:
        print(f"Google error: {e}")

    return results


def search_duckduckgo(company_name, query_suffix=""):
    """Scrape DuckDuckGo search results"""
    results = []
    query = f'"{company_name}" {query_suffix}'.strip()
    url = f"https://html.duckduckgo.com/html/?q={quote_plus(query)}"

    try:
        resp = requests.post(
            "https://html.duckduckgo.com/html/",
            data={"q": query, "b": "", "kl": "us-en"},
            headers=get_headers(),
            timeout=10
        )
        soup = BeautifulSoup(resp.text, "lxml")

        results_divs = soup.find_all("div", class_=re.compile(r"result__body|result ", re.I))

        for div in results_divs[:8]:
            title_el = div.find("a", class_=re.compile(r"result__a", re.I))
            title = title_el.get_text(strip=True) if title_el else ""
            link = title_el.get("href", "") if title_el else ""
            snippet_el = div.find("a", class_=re.compile(r"result__snippet", re.I))
            snippet = snippet_el.get_text(strip=True) if snippet_el else ""

            if title and len(title) > 10:
                results.append({
                    "title": title,
                    "snippet": snippet,
                    "link": link,
                    "date": "",
                    "source": "DuckDuckGo"
                })
    except Exception as e:
        print(f"DDG error: {e}")

    return results


def classify_signals(articles, company_name):
    """Classify articles into buying signal categories"""
    signals = []
    seen_titles = set()

    for article in articles:
        text = (article["title"] + " " + article["snippet"]).lower()
        company_lower = company_name.lower()

        # Skip if company name not even mentioned
        if not any(word in text for word in company_lower.split()):
            continue

        # Skip duplicates
        title_key = article["title"][:50].lower()
        if title_key in seen_titles:
            continue
        seen_titles.add(title_key)

        matched_categories = []
        for category, data in SIGNAL_PATTERNS.items():
            keyword_matches = [kw for kw in data["keywords"] if kw in text]
            if keyword_matches:
                matched_categories.append({
                    "category": category,
                    "color": data["color"],
                    "weight": data["weight"],
                    "matched_keywords": keyword_matches[:3],
                    "score": len(keyword_matches) * data["weight"]
                })

        if matched_categories:
            # Pick best matching category
            best = max(matched_categories, key=lambda x: x["score"])

            # Confidence scoring
            score = best["score"]
            if score >= 8:
                confidence = "High"
                conf_color = "#00ff88"
            elif score >= 4:
                confidence = "Medium"
                conf_color = "#ffcc00"
            else:
                confidence = "Low"
                conf_color = "#ff6b6b"

            signals.append({
                "category": best["category"],
                "color": best["color"],
                "confidence": confidence,
                "conf_color": conf_color,
                "title": article["title"],
                "snippet": article["snippet"][:200] + "..." if len(article["snippet"]) > 200 else article["snippet"],
                "link": article["link"],
                "date": article["date"],
                "source": article["source"],
                "keywords": best["matched_keywords"],
                "score": best["score"]
            })

    # Sort by score
    signals.sort(key=lambda x: x["score"], reverse=True)
    return signals


def compute_readiness_score(signals):
    """0–100 buying readiness score"""
    if not signals:
        return 0

    weights = {"High": 3, "Medium": 2, "Low": 1}
    raw = sum(weights[s["confidence"]] * s["score"] for s in signals)
    normalized = min(100, int((raw / max(raw, 1)) * 100))

    # Category bonus
    cats = set(s["category"] for s in signals)
    bonus = len(cats) * 5
    return min(100, normalized + bonus)


def run_scraper(company_name):
    """Main function to scrape and analyze buying signals"""
    all_articles = []
    queries = [
        "news",
        "funding investment",
        "expansion launch",
        "partnership acquisition",
        "hiring growth"
    ]

    print(f"\n🔍 Scraping buying signals for: {company_name}\n")

    for q in queries:
        # Try multiple search engines
        arts = search_duckduckgo(company_name, q)
        if not arts:
            arts = search_bing(company_name, q)
        if not arts:
            arts = search_google(company_name, q)

        all_articles.extend(arts)
        time.sleep(random.uniform(0.5, 1.2))

    print(f"✅ Total articles scraped: {len(all_articles)}")

    signals = classify_signals(all_articles, company_name)
    score = compute_readiness_score(signals)

    return {
        "company": company_name,
        "signals": signals,
        "total_articles": len(all_articles),
        "readiness_score": score,
        "timestamp": datetime.now().strftime("%d %b %Y, %H:%M")
    }


if __name__ == "__main__":
    import sys
    company = sys.argv[1] if len(sys.argv) > 1 else "Salesforce"
    result = run_scraper(company)
    for s in result["signals"][:10]:
        print(f"\n[{s['confidence']}] {s['category']}")
        print(f"  {s['title']}")
        print(f"  Keywords: {s['keywords']}")
