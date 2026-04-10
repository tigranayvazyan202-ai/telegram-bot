import asyncio
import feedparser
import json
import time
import hashlib
import re

from telegram import Bot
from deep_translator import GoogleTranslator
from telethon import TelegramClient
from telethon.sessions import StringSession

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# ================= CONFIG =================
TOKEN = "8643374685:AAG0fnjpBlnq2YXTZ17G-etF-Mth39Oj6q0"
CHAT_ID = "@ArmeniaBreakingNews"

api_id = 30831221
api_hash = "fe05ace1afd9eca3c75facf10fb8819a"
SESSION = "1ApWapzMBu5UhmohQM5-aKsIpdcoHwHCIa1-i6k8aUg3r8CA6xWeWbnTZzRklhzKlwjcqNExFThHzUoDT-lMyIBpbMFYx5ajvB3-Tay8ja9VjhI56VYvK2ppzlO7k9ZtOIgeeK7QYnejcpn9tVsX1D8oUO6pEvU3vJIfHc7Np0ov1hwCQOsvyVwSx7MyGi-Vle4blEO2YFtR7D0Wi6t03QWuqDLTxLixxJvb0sqK2Bx4QDqkuhtmsOLBCA9naPPe1k9vhZIkWE8qL8eXxH0maA8rXPZeA-R999ZaBFydRCFKQFtkjSlTwIiEzq2lNPaJNNUj0mwOLTiaGR8jU1XWF30G5-2w034s="

MAX_POSTS = 5

RSS_URLS = [
    "https://www.civilnet.am/feed/",
    "https://hetq.am/en/rss",
    "https://mediamax.am/en/index.rss"
]

TG_CHANNELS = [
    "armenpress",
    "newsarmenia",
    "infocomm",
    "civilnet_am"
]

bot = Bot(token=TOKEN)
tg_client = TelegramClient(StringSession(SESSION), api_id, api_hash)

# ================= LOAD MEMORY =================
def load_data():
    try:
        with open("sent.json", "r") as f:
            return json.load(f)
    except:
        return {"hashes": [], "titles": []}

def save_data(data):
    with open("sent.json", "w") as f:
        json.dump(data, f)

# ================= DEDUP =================
def normalize(text):
    text = text.lower()
    text = re.sub(r"[^\w\s]", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text

def get_hash(text):
    return hashlib.md5(normalize(text).encode()).hexdigest()

def is_similar(new_title, old_titles, threshold=0.85):
    if not old_titles:
        return False

    vect = TfidfVectorizer().fit(old_titles + [new_title])
    tfidf = vect.transform(old_titles + [new_title])
    scores = cosine_similarity(tfidf[-1], tfidf[:-1])[0]

    return any(score > threshold for score in scores)

# ================= TRANSLATION =================
def tr(text, lang):
    try:
        return GoogleTranslator(source='auto', target=lang).translate(text)
    except:
        return text

# ================= CATEGORY =================
def categorize(text):
    t = text.lower()

    if any(k in t for k in ["government","minister","parliament","իշխան"]):
        return "🏛"
    if any(k in t for k in ["military","defense","border","army","բանակ"]):
        return "⚔️"
    if any(k in t for k in ["economy","business","market","տնտես"]):
        return "💰"
    if any(k in t for k in ["education","health","society","հասարակ"]):
        return "👥"
    if any(k in t for k in ["diplomacy","embassy","eu","russia"]):
        return "🌍"
    if any(k in t for k in ["culture","art","museum","film"]):
        return "🎭"

    return "📰"

# ================= FORMAT =================
def build_post(title, text, link=""):
    emoji = categorize(title + " " + text)

    ru_title = tr(title, "ru")
    ru_text = tr(text, "ru")

    am_title = tr(title, "hy")
    am_text = tr(text, "hy")

    return f"""{emoji} <b>{ru_title}</b>
{ru_text}

{emoji} <b>{am_title}</b>
{am_text}

<a href="{link}">Источник</a>
"""

# ================= RSS =================
def fetch_rss():
    articles = []

    for url in RSS_URLS:
        feed = feedparser.parse(url)

        for entry in feed.entries[:5]:
            articles.append({
                "title": entry.title,
                "text": entry.get("summary", ""),
                "link": entry.link
            })

    return articles

# ================= MAIN =================
async def main():
    data = load_data()
    posted = 0

    # ===== RSS =====
    for article in fetch_rss():
        if posted >= MAX_POSTS:
            break

        title = article["title"]
        text = article["text"]

        h = get_hash(title)

        if h in data["hashes"]:
            continue

        if is_similar(title, data["titles"]):
            continue

        post = build_post(title, text, article["link"])

        await bot.send_message(CHAT_ID, post, parse_mode="HTML")

        data["hashes"].append(h)
        data["titles"].append(title)
        save_data(data)

        posted += 1
        await asyncio.sleep(10)

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

            title = message.text[:100]
            text = message.text[:400]

            h = get_hash(title)

            if h in data["hashes"]:
                continue

            if is_similar(title, data["titles"]):
                continue

            post = build_post(title, text)

            await bot.send_message(CHAT_ID, post, parse_mode="HTML")

            data["hashes"].append(h)
            data["titles"].append(title)
            save_data(data)

            posted += 1
            await asyncio.sleep(10)

# 🔁 LOOP
while True:
    asyncio.run(main())
    time.sleep(600)
