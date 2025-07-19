import requests
from bs4 import BeautifulSoup
import datetime
import csv
import re

# List of variants with their unique URLs and labels
VARIANTS = {
    "P1S": "https://uk.store.bambulab.com/products/p1s?id=578772891943051274",
    "P1S + AMS": "https://uk.store.bambulab.com/products/p1s?id=578772891943051270",
    "P1S + AMS PRO": "https://uk.store.bambulab.com/products/p1s?id=583795899161169921",
}

TARGETS = {
    "P1S": 450.0,
    "P1S + AMS": 650.0,
    "P1S + AMS PRO": 850.0,
}

CSV_FILE = "p1s_prices_uk.csv"
HEADERS = {"User-Agent": "Mozilla/5.0"}

def extract_price_from_html(html):
    soup = BeautifulSoup(html, "html.parser")
    # Match the highlighted actual price (not strikethrough)
    price_span = soup.find("span", class_="Price--highlight")
    if price_span:
        price_text = price_span.get_text(strip=True)
        match = re.search(r"£([\d,.]+)", price_text)
        if match:
            return float(match.group(1).replace(",", ""))
    return None

def fetch_prices():
    now = datetime.datetime.now().isoformat()
    rows = []

    print(f"\n[{now}] 🔍 Fetching Bambu UK Prices:")
    for variant, url in VARIANTS.items():
        try:
            response = requests.get(url, headers=HEADERS)
            response.raise_for_status()

            price = extract_price_from_html(response.text)
            if price is not None:
                alert = " ✅ BELOW TARGET!" if price < TARGETS[variant] else ""
                print(f" • {variant}: £{price:.2f}{alert}")
                rows.append([now, variant, price])
            else:
                print(f" • {variant}: ⚠️ Price not found")

        except Exception as e:
            print(f" • {variant}: ❌ Error fetching price: {e}")

    # Write results to CSV
    with open(CSV_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerows(rows)

if __name__ == "__main__":
    fetch_prices()
