import asyncio
import feedparser
import json
import time
from telegram import Bot
from deep_translator import GoogleTranslator

TOKEN = "8643374685:AAG0fnjpBlnq2YXTZ17G-etF-Mth39Oj6q0"
CHAT_ID = "@ArmeniaBreakingNews"

RSS_URLS = [
    "https://www.civilnet.am/feed/",
    "https://hetq.am/en/rss",
    "https://mediamax.am/en/index.rss"
]

translator = GoogleTranslator(source='auto', target='ru')

# Load sent links
try:
    with open("sent.json", "r") as f:
        sent_links = json.load(f)
except:
    sent_links = []

# 🧠 Detect category
def get_category(title):
    t = title.lower()
    if any(x in t for x in ["war", "military", "attack", "army"]):
        return "🔴"
    elif any(x in t for x in ["government", "minister", "president", "parliament"]):
        return "🏛️"
    elif any(x in t for x in ["economy", "bank", "business", "market"]):
        return "💰"
    elif any(x in t for x in ["russia", "usa", "iran", "turkey", "eu"]):
        return "🌍"
    else:
        return "📰"

# 🧠 Filter important news
def is_important(title):
    keywords = [
        "armenia", "azerbaijan", "karabakh",
        "government", "minister", "military",
        "border", "economy", "security"
    ]
    return any(k in title.lower() for k in keywords)

def translate(text, lang):
    try:
        return GoogleTranslator(source='auto', target=lang).translate(text)
    except:
        return text

async def main():
    bot = Bot(token=TOKEN)

    for url in RSS_URLS:
        feed = feedparser.parse(url)

        for entry in feed.entries[:7]:
            link = entry.link
            title = entry.title

            if link in sent_links:
                continue

            if not is_important(title):
                continue

            emoji = get_category(title)

            # Translate
            title_ru = translate(title, "ru")
            title_am = translate(title, "hy")

            # ✍️ Clean format
            message = f"""{emoji} <b>{title_ru}</b>

• {title_ru}
🔗 {link}

——————

{emoji} <b>{title_am}</b>

• {title_am}
🔗 {link}
"""

            await bot.send_message(
                chat_id=CHAT_ID,
                text=message,
                parse_mode="HTML"
            )

            sent_links.append(link)

    with open("sent.json", "w") as f:
        json.dump(sent_links, f)

while True:
    asyncio.run(main())
    time.sleep(600)
