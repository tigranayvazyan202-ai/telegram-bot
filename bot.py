import asyncio
import feedparser
import json
import time
from telegram import Bot
from googletrans import Translator

TOKEN = "YOUR_TOKEN_HERE"
CHAT_ID = "@your_channel_username"

RSS_URLS = [
    "https://www.civilnet.am/feed/",
    "https://hetq.am/en/rss",
    "https://mediamax.am/en/index.rss"
]

translator = Translator()

# Load sent links
try:
    with open("sent.json", "r") as f:
        sent_links = json.load(f)
except:
    sent_links = []

def translate_to_ru(text):
    try:
        return translator.translate(text, dest='ru').text
    except:
        return text

def translate_to_am(text):
    try:
        return translator.translate(text, dest='hy').text
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

            # Translate
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