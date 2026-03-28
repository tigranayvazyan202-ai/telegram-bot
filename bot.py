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

# Load sent links
try:
    with open("sent.json", "r") as f:
        sent_links = json.load(f)
except:
    sent_links = []

def translate_to_ru(text):
    try:
        return GoogleTranslator(source='auto', target='ru').translate(text)
    except:
        return text

def translate_to_am(text):
    try:
        return GoogleTranslator(source='auto', target='hy').translate(text)
    except:
        return text

async def main():
    bot = Bot(token=TOKEN)

    for url in RSS_URLS:
        feed = feedparser.parse(url)

        for entry in feed.entries[:5]:
            link = entry.link

            if link in sent_links:
                continue

            title = entry.title

            title_ru = translate_to_ru(title)
            title_am = translate_to_am(title)

            message = f"""📰 <b>{title_ru}</b>

• {title_ru}
🔗 {link}

——————

📰 <b>{title_am}</b>

• {title_am}
🔗 {link}
"""

            await bot.send_message(
                chat_id=CHAT_ID,
                text=message,
                parse_mode="HTML",
                disable_web_page_preview=False
            )

            sent_links.append(link)

    with open("sent.json", "w") as f:
        json.dump(sent_links, f)

while True:
    asyncio.run(main())
    time.sleep(600)
