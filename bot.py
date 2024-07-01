import pyrogram
from pyrogram import Client, filters
import re
import asyncio
import aiohttp
from pymongo import MongoClient
import base64

# MongoDB configuration
MONGO_URI = 'mongodb+srv://iamdaxx404:asd@mohio.1uwb6r5.mongodb.net'
client = MongoClient(MONGO_URI)
db = client['mrdaxx_scrapper_db']
cards_collection = db['cards']

def correct_padding(session_string):
    return session_string + "=" * ((4 - len(session_string) % 4) % 4)

# Update the session_string here with the new session string and apply padding
app = pyrogram.Client(
    'mrdaxx_scrapper',
    api_id='27649783',
    api_hash='834fd6015b50b781e0f8a41876ca95c8',
    session_string=correct_padding("BQAaqk4AcZrIU5Xzzw0Z7gJAzLbFsKYaH90txYwLDZYYs0RhYRtKUxojSiTnEFk3gbECN9qJXPqI_JWTbPMIsD1tAcft0uhjc6obuxCBQkOGBVm6bxPKUvpShUnHQKsxxgG_IvFAbtplnQGaUt4bIbjk_sbr8CGwebOEi0xB8SHLhlfLHeivK_RvFrF8Egh5QrJIvTzpsjljHp3-GyVlsWC8ZPLAJyMzCcRChk8yJ2WuKqdRJhND4UyRkiHgDU-QQrm14GdssrlQV9mT8g1ldvD56sfk2ALJS7SW-qENwQPGTTOVHQPBNGiv2MF7YXKrDa78QLYn_UqtAZmSuKxUGsaSeCfJiAAAAABpRCaiAA")
)

BIN_API_URL = 'https://astroboyapi.com/api/bin.php?bin={}'

def filter_cards(text):
    regex = r'\d{15,16}\D*\d{2}\D*\d{2,4}\D*\d{3,4}'
    matches = re.findall(regex, text)
    return matches

async def bin_lookup(bin_number):
    bin_info_url = BIN_API_URL.format(bin_number)
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as session:
        async with session.get(bin_info_url) as response:
            if response.status == 200:
                try:
                    bin_info = await response.json()
                    return bin_info
                except aiohttp.ContentTypeError:
                    return None
            else:
                return None

async def approved(client_instance, message):
    try:
        if re.search(r'(Approved!|Charged|authenticate_successful|𝗔𝗽𝗽𝗿𝗼𝘃𝗲𝗱|APPROVED|New Cards Found By JennaScrapper|ꕥ Extrap [☭]|み RIMURU SCRAPE by|Approved) ✅', message.text):
            filtered_card_info = filter_cards(message.text)
            if not filtered_card_info:
                return

            for card_info in filtered_card_info:
                if cards_collection.find_one({"card_info": card_info}):
                    continue  # Skip if card already exists in the database

                bin_number = card_info[:6]
                bin_info = await bin_lookup(bin_number)
                if bin_info:
                    brand = bin_info.get("brand", "N/A")
                    card_type = bin_info.get("type", "N/A")
                    level = bin_info.get("level", "N/A")
                    bank = bin_info.get("bank", "N/A")
                    country = bin_info.get("country_name", "N/A")
                    country_flag = bin_info.get("country_flag", "")

                    formatted_message = (
                        "┏━━━━━━━⍟\n"
                        "┃𝖡𝖱𝖠𝖨𝖭𝖳𝖱𝖤𝖤 𝖠𝖴𝖳𝖧 𝟓$ ✅\n"
                        "┗━━━━━━━━━━━⊛\n\n"
                        f"𖠁𝖢𝖠𝖱𝖣 ➔ <code>{card_info}</code>\n\n"
                        f"𖠁𝖲𝖳𝖠𝖳𝖴𝖲 ➔ <b>Approved! ✅</b>\n\n"
                        f"𖠁𝖡𝖨𝖭 ➔ <b>{brand}, {card_type}, {level}</b>\n\n"
                        f"𖠁𝖡𝖠𝖭𝖪 ➔ <b>{bank}</b>\n\n"
                        f"𖠁𝖢𝖮𝖴𝖭𝖳𝖱𝖸 ➔ <b>{country}, {country_flag}</b>\n\n"
                        "𖠁𝖢𝖱𝖤𝖠𝖳𝖮𝖱 ➔ <b>๏─𝙂𝘽𝙋─๏</b>"
                    )

                    await client_instance.send_message(chat_id='-1002222638488', text=formatted_message)

                    # Save card info to MongoDB to prevent duplicate sending
                    cards_collection.insert_one({"card_info": card_info})
    except Exception as e:
        print(f"An error occurred: {e}")

@app.on_message(filters.text)
async def astro(client_instance, message):
    if message.text:
        await asyncio.create_task(approved(client_instance, message))

app.run()
