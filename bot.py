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

def translate(text, lang):
    try:
        return GoogleTranslator(source='auto', target=lang).translate(text)
    except:
        return text

# 🧠 Clean summary generator
def make_summary(text):
    if not text:
        return ""

    text = text.replace("<p>", "").replace("</p>", "")
    text = text.replace("<br>", " ")

    sentences = text.split(".")
    bullets = []

    for s in sentences[:3]:
        s = s.strip()
        if len(s) > 20:
            bullets.append(f"• {s}")

    return "\n".join(bullets)

# 🏛 Category detection
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

# 🧠 Filter important
def is_important(title):
    keywords = [
        "armenia", "azerbaijan", "karabakh",
        "government", "minister", "military",
        "border", "economy", "security"
    ]
    return any(k in title.lower() for k in keywords)

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

            summary = entry.get("summary", "")
            summary_clean = make_summary(summary)

            # Translate everything
            title_ru = translate(title, "ru")
            title_am = translate(title, "hy")

            summary_ru = translate(summary_clean, "ru")
            summary_am = translate(summary_clean, "hy")

            message = f"""{emoji} <b>{title_ru}</b>

{summary_ru}
🔗 {link}

——————

{emoji} <b>{title_am}</b>

{summary_am}
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
