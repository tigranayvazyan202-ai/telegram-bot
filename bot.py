import asyncio
import feedparser
import json
import time
from telegram import Bot
from deep_translator import GoogleTranslator
from telethon import TelegramClient
from telethon.sessions import StringSession

# 🔑 CONFIG (REPLACE THESE)
TOKEN = "8643374685:AAG0fnjpBlnq2YXTZ17G-etF-Mth39Oj6q0"
CHAT_ID = "@ArmeniaBreakingNews"

api_id = 30831221
api_hash = "fe05ace1afd9eca3c75facf10fb8819a"
SESSION = "1ApWapzMBu5UhmohQM5-aKsIpdcoHwHCIa1-i6k8aUg3r8CA6xWeWbnTZzRklhzKlwjcqNExFThHzUoDT-lMyIBpbMFYx5ajvB3-Tay8ja9VjhI56VYvK2ppzlO7k9ZtOIgeeK7QYnejcpn9tVsX1D8oUO6pEvU3vJIfHc7Np0ov1hwCQOsvyVwSx7MyGi-Vle4blEO2YFtR7D0Wi6t03QWuqDLTxLixxJvb0sqK2Bx4QDqkuhtmsOLBCA9naPPe1k9vhZIkWE8qL8eXxH0maA8rXPZeA-R999ZaBFydRCFKQFtkjSlTwIiEzq2lNPaJNNUj0mwOLTiaGR8jU1XWF30G5-2w034s="

RSS_URLS = [
    "https://www.civilnet.am/feed/",
    "https://hetq.am/en/rss",
    "https://mediamax.am/en/index.rss"
]

TG_CHANNELS = [
    "armenpress",
    "infocomm",
    "newsarmenia"
]

bot = Bot(token=TOKEN)
tg_client = TelegramClient(StringSession(SESSION), api_id, api_hash)

# Load sent data
try:
    with open("sent.json", "r") as f:
        sent_links = json.load(f)
except:
    sent_links = []

try:
    with open("tg_sent.json", "r") as f:
        tg_sent = json.load(f)
except:
    tg_sent = []

# 🌍 Translation
def translate(text, lang):
    try:
        return GoogleTranslator(source='auto', target=lang).translate(text)
    except:
        return text

# 🧠 Clean title
def clean_title(title):
    return title.replace(":", " –").strip()

# 🧠 Summary
def make_summary(text):
    if not text:
        return ""

    text = text.replace("<p>", "").replace("</p>", "")
    sentences = text.split(".")
    bullets = []

    for s in sentences[:3]:
        s = s.strip()
        if len(s) > 25:
            bullets.append(f"• {s.capitalize()}")

    return "\n".join(bullets)

# 🏛 Category
def get_category(title):
    t = title.lower()
    if any(x in t for x in ["war", "attack", "army"]):
        return "🔴"
    elif any(x in t for x in ["government", "minister", "president"]):
        return "🏛️"
    elif any(x in t for x in ["economy", "bank", "business"]):
        return "💰"
    else:
        return "📰"

# 🚨 Breaking
def is_breaking(title):
    return any(x in title.lower() for x in ["war", "attack", "explosion", "urgent"])

async def process_rss():
    for url in RSS_URLS:
        feed = feedparser.parse(url)

        for entry in feed.entries[:5]:
            link = entry.link
            title = entry.title

            if link in sent_links:
                continue

            emoji = get_category(title)
            if is_breaking(title):
                emoji = "🚨"

            summary = make_summary(entry.get("summary", ""))

            ru_title = clean_title(translate(title, "ru"))
            am_title = clean_title(translate(title, "hy"))

            ru_summary = translate(summary, "ru")
            am_summary = translate(summary, "hy")

            msg = f"""{emoji} <b>{ru_title}</b>

{ru_summary}

📎 Источник: RSS  
🔗 {link}

——————

{emoji} <b>{am_title}</b>

{am_summary}

📎 Աղբյուր: RSS  
🔗 {link}
"""

            await bot.send_message(CHAT_ID, msg, parse_mode="HTML")
            sent_links.append(link)

async def process_telegram():
    await tg_client.start()

    for channel in TG_CHANNELS:
        async for message in tg_client.iter_messages(channel, limit=5):

            if not message.text:
                continue

            if message.id in tg_sent:
                continue

            text = message.text[:400]

            ru = translate(text, "ru")
            am = translate(text, "hy")

            msg = f"""📰 <b>{ru}</b>

• {ru}

📎 Источник: Telegram

——————

📰 <b>{am}</b>

• {am}

📎 Աղբյուր: Telegram
"""

            await bot.send_message(CHAT_ID, msg, parse_mode="HTML")
            tg_sent.append(message.id)

async def main():
    await process_rss()
    await process_telegram()

    with open("sent.json", "w") as f:
        json.dump(sent_links, f)

    with open("tg_sent.json", "w") as f:
        json.dump(tg_sent, f)

# 🔁 Run forever
while True:
    asyncio.run(main())
    time.sleep(600)
