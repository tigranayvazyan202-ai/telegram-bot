from telethon import TelegramClient
from telethon.sessions import StringSession
import asyncio
import json
import time
from deep_translator import GoogleTranslator
from telegram import Bot

# 🔑 YOUR DATA (REPLACE THESE)
api_id = 30831221
api_hash = "fe05ace1afd9eca3c75facf10fb8819a"

BOT_TOKEN = "8643374685:AAG0fnjpBlnq2YXTZ17G-etF-Mth39Oj6q0"
CHAT_ID = "@ArmeniaBreakingNews"

# 🔐 SESSION STRING (PASTE YOUR FULL STRING HERE)
SESSION = "1ApWapzMBu5UhmohQM5-aKsIpdcoHwHCIa1-i6k8aUg3r8CA6xWeWbnTZzRklhzKlwjcqNExFThHzUoDT-lMyIBpbMFYx5ajvB3-Tay8ja9VjhI56VYvK2ppzlO7k9ZtOIgeeK7QYnejcpn9tVsX1D8oUO6pEvU3vJIfHc7Np0ov1hwCQOsvyVwSx7MyGi-Vle4blEO2YFtR7D0Wi6t03QWuqDLTxLixxJvb0sqK2Bx4QDqkuhtmsOLBCA9naPPe1k9vhZIkWE8qL8eXxH0maA8rXPZeA-R999ZaBFydRCFKQFtkjSlTwIiEzq2lNPaJNNUj0mwOLTiaGR8jU1XWF30G5-2w034s="

# Channels to read
CHANNELS = [
    "armenpress",
    "infocomm",
    "newsarmenia"
]

client = TelegramClient(StringSession(SESSION), api_id, api_hash)
bot = Bot(token=BOT_TOKEN)

# Load already sent message IDs
try:
    with open("tg_sent.json", "r") as f:
        sent_ids = json.load(f)
except:
    sent_ids = []

# 🌍 Translation
def translate(text, lang):
    try:
        return GoogleTranslator(source='auto', target=lang).translate(text)
    except:
        return text

async def main():
    await client.start()

    for channel in CHANNELS:
        async for message in client.iter_messages(channel, limit=5):

            if not message.text:
                continue

            if message.id in sent_ids:
                continue

            text = message.text[:500]

            # Translate
            ru = translate(text, "ru")
            am = translate(text, "hy")

            final = f"""📰 <b>{ru}</b>

{ru}

——————

📰 <b>{am}</b>

{am}
"""

            await bot.send_message(
                chat_id=CHAT_ID,
                text=final,
                parse_mode="HTML"
            )

            sent_ids.append(message.id)

    # Save sent IDs
    with open("tg_sent.json", "w") as f:
        json.dump(sent_ids, f)

# 🔁 Run forever (every 10 minutes)
while True:
    asyncio.run(main())
    time.sleep(600)
