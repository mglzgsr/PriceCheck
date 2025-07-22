import os
import requests
from datetime import datetime

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
URL = "https://uk.store.bambulab.com/products/p1s.js"

print("✅ Running version from:", __file__)
print(f"🔗 Fetching from URL: {URL}")

# Friendly labels mapped from Shopify titles
TITLE_MAP = {
    "P1S 3D Printer": "P1S",
    "P1S 3D Printer Combo": "P1S + AMS",
    "P1S 3D Printer Combo AMS PRO": "P1S + AMS PRO"
}

TARGETS = {
    "P1S": 390.0,
    "P1S + AMS": 600.0,
    "P1S + AMS PRO": 800.0
}

def fetch_prices():
    prices = {}
    try:
        resp = requests.get(URL, timeout=10)
        resp.raise_for_status()
        data = resp.json()

        for variant in data['variants']:
            # Combine product title + public_title
            base_title = data['title'].strip()
            variant_title = variant['public_title'] or ""
            full_title = f"{base_title} {variant_title}".strip()

            label = TITLE_MAP.get(full_title)
            if label:
                prices[label] = variant['price'] / 100  # convert to GBP

    except Exception as e:
        print(f"❌ Error fetching prices: {e}")

    return prices

def format_telegram_message(prices):
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    lines = [f"🧵 *Bambu Lab UK - P1S Prices* (`{now}`)\n"]
    for variant in ["P1S", "P1S + AMS", "P1S + AMS PRO"]:
        price = prices.get(variant)
        if price:
            alert = " 🔻 _Below target!_" if price < TARGETS[variant] else ""
            lines.append(f"• *{variant}*: £{price:.2f}{alert}")
        else:
            lines.append(f"• *{variant}*: ⚠️ Price not found")
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
    prices = fetch_prices()
    message = format_telegram_message(prices)
    print("📨 Message Preview:\n", message)
    if "£" in message:
        send_telegram_message(message)
    else:
        print("🚫 Skipped sending — no valid prices extracted")
