import os
import requests
from bs4 import BeautifulSoup
import datetime
import re

# 🔧 Config
VARIANTS = {
    "P1S": "https://uk.store.bambulab.com/products/p1s?id=578772891943051274",
    "P1S + AMS": "https://uk.store.bambulab.com/products/p1s?id=578772891943051270",
    "P1S + AMS PRO": "https://uk.store.bambulab.com/products/p1s?id=583795899161169921",
}
TARGETS = {
    "P1S": 390.0,
    "P1S + AMS": 600.0,
    "P1S + AMS PRO": 800.0,
}

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
HEADERS = {"User-Agent": "Mozilla/5.0"}

def extract_price(html):
    soup = BeautifulSoup(html, "html.parser")
    price_tag = soup.find("span", class_="Price--highlight")

    if not price_tag:
        print("⚠️ Could not find span.Price--highlight")
        return None

    price_text = price_tag.get_text(strip=True)
    match = re.search(r"£([\d,.]+)", price_text)
    if match:
        return float(match.group(1).replace(",", ""))
    else:
        print(f"⚠️ Couldn't parse price from text: {price_text}")
        return None


def fetch_all_prices():
    prices = {}
    for variant, url in VARIANTS.items():
        try:
            resp = requests.get(url, headers=HEADERS, timeout=10)
            resp.raise_for_status()
            price = extract_price(resp.text)
            if price:
                prices[variant] = price
        except Exception as e:
            prices[variant] = None
            print(f"Error fetching {variant}: {e}")
    return prices

def format_telegram_message(prices):
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    lines = [f"🧵 *Bambu Lab UK - P1S Prices* (`{now}`)\n"]
    for variant, price in prices.items():
        if price is None:
            lines.append(f"• *{variant}*: ⚠️ Price not found")
            continue
        alert = " 🔻 _Below target!_" if price < TARGETS[variant] else ""
        lines.append(f"• *{variant}*: £{price:.2f}{alert}")
    return "\n".join(lines)

def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "Markdown"
    }
    resp = requests.post(url, data=payload)
    if not resp.ok:
        print("❌ Telegram send failed:", resp.text)
    else:
        print("✅ Telegram message sent")

if __name__ == "__main__":
    prices = fetch_all_prices()
    message = format_telegram_message(prices)
    send_telegram_message(message)
