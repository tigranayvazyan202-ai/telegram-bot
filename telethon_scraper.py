from telethon import TelegramClient
import asyncio
import json
from deep_translator import GoogleTranslator
from telegram import Bot

# 🔑 YOUR DATA (REPLACE THESE)
api_id = 30831221
api_hash = "fe05ace1afd9eca3c75facf10fb8819a"

BOT_TOKEN = "8643374685:AAG0fnjpBlnq2YXTZ17G-etF-Mth39Oj6q0"
CHAT_ID = "@ArmeniaBreakingNews"

# Channels to read
CHANNELS = [
    "armenpress",
    "infocomm",
    "newsarmenia"
]

client = TelegramClient("session", api_id, api_hash)
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

asyncio.run(main())
