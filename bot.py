import asyncio
import feedparser
import json
import time
from telegram import Bot
from deep_translator import GoogleTranslator
from telethon import TelegramClient
from telethon.sessions import StringSession

# 🔑 CONFIG (PASTE YOUR VALUES)
TOKEN = "8643374685:AAG0fnjpBlnq2YXTZ17G-etF-Mth39Oj6q0"
CHAT_ID = "@ArmeniaBreakingNews"

api_id = 30831221
api_hash = "fe05ace1afd9eca3c75facf10fb8819a"
SESSION = "1ApWapzMBu5UhmohQM5-aKsIpdcoHwHCIa1-i6k8aUg3r8CA6xWeWbnTZzRklhzKlwjcqNExFThHzUoDT-lMyIBpbMFYx5ajvB3-Tay8ja9VjhI56VYvK2ppzlO7k9ZtOIgeeK7QYnejcpn9tVsX1D8oUO6pEvU3vJIfHc7Np0ov1hwCQOsvyVwSx7MyGi-Vle4blEO2YFtR7D0Wi6t03QWuqDLTxLixxJvb0sqK2Bx4QDqkuhtmsOLBCA9naPPe1k9vhZIkWE8qL8eXxH0maA8rXPZeA-R999ZaBFydRCFKQFtkjSlTwIiEzq2lNPaJNNUj0mwOLTiaGR8jU1XWF30G5-2w034s="

MAX_POSTS = 3

RSS_URLS = [
    "https://www.civilnet.am/feed/",
    "https://hetq.am/en/rss",
    "https://mediamax.am/en/index.rss"
]

TG_CHANNELS = [
    "armenpress",
    "newsarmenia",
    "infocomm",
    "civilnet_am",
    "azatutyun",
    "bagramyan26",
    "armmilitaryportal",
    "armyanin"
]

bot = Bot(token=TOKEN)
tg_client = TelegramClient(StringSession(SESSION), api_id, api_hash)

# Load memory (global duplicates protection)
try:
    with open("sent_all.json", "r") as f:
        sent_all = set(json.load(f))
except:
    sent_all = set()

# 🌍 Translation
def translate(text, lang):
    try:
        return GoogleTranslator(source='auto', target=lang).translate(text)
    except:
        return text

# 🧠 Quality filter
def is_good_text(text):
    if not text or len(text) < 50:
        return False
    if any(x in text.lower() for x in ["subscribe", "реклама"]):
        return False
    return True

# 🧠 Smart scoring
def score_news(text):
    score = 0
    t = text.lower()

    if any(x in t for x in ["war", "attack", "explosion", "strike"]):
        score += 5
    if any(x in t for x in ["president", "minister", "government"]):
        score += 3
    if any(x in t for x in ["russia", "usa", "iran", "turkey"]):
        score += 2
    if len(text) > 200:
        score += 1

    return score

# 🧠 Summary builder
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

# 🏷 Emoji logic
def get_emoji(text):
    return "🚨" if score_news(text) >= 5 else "📰"

async def main():
    posted = 0

    # ===== RSS =====
    for url in RSS_URLS:
        if posted >= MAX_POSTS:
            break

        feed = feedparser.parse(url)

        for entry in feed.entries[:5]:
            if posted >= MAX_POSTS:
                break

            link = entry.link
            title = entry.title

            if link in sent_all:
                continue

            if score_news(title) < 2:
                continue

            summary = make_summary(entry.get("summary", ""))

            ru_title = translate(title, "ru")
            am_title = translate(title, "hy")

            ru_summary = translate(summary, "ru")
            am_summary = translate(summary, "hy")

            emoji = get_emoji(title)

            msg = f"""{emoji} <b>{ru_title}</b>

{ru_summary}

🔗 {link}

——————

{emoji} <b>{am_title}</b>

{am_summary}

🔗 {link}
"""

            await bot.send_message(CHAT_ID, msg, parse_mode="HTML")

            sent_all.add(link)
            posted += 1

    # ===== TELEGRAM =====
    await tg_client.start()

    for channel in TG_CHANNELS:
        if posted >= MAX_POSTS:
            break

        async for message in tg_client.iter_messages(channel, limit=5):
            if posted >= MAX_POSTS:
                break

            if not message.text:
                continue

            unique_id = f"{channel}_{message.id}"

            if unique_id in sent_all:
                continue

            if not is_good_text(message.text):
                continue

            if score_news(message.text) < 2:
                continue

            text = message.text[:400]

            ru = translate(text, "ru")
            am = translate(text, "hy")

            emoji = get_emoji(text)

            msg = f"""{emoji} <b>{ru}</b>

• {ru}

——————

{emoji} <b>{am}</b>

• {am}
"""

            await bot.send_message(CHAT_ID, msg, parse_mode="HTML")

            sent_all.add(unique_id)
            posted += 1

    # Save memory
    with open("sent_all.json", "w") as f:
        json.dump(list(sent_all), f)

# 🔁 Infinite loop
while True:
    asyncio.run(main())
    time.sleep(600)
