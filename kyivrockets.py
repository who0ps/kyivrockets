#!/usr/bin/python3
API_ID = '1234567'
API_HASH = '12345678901234567890123456789012'
BOT_TOKEN = '1234567890:abc'
SESSION_NAME = 'rkts'
SOURCE_CHANNELS = [-1001223955273, -1001641260594] # kpszsu, war_monitor
TARGET_CHANNEL = '@Kyivrockets'
KEYWORDS_GROUP1 = ['бр ', 'кр ', 'балісти', 'крилат', 'ракет', 'швидкісн', 'ціль', 'кинджал', 'циркон']
KEYWORDS_GROUP2 = ['київ', 'столиц', 'києв']
STOP_WORDS = ['попередньо', 'обстріл', 'ліквід', 'напад', 'тримаймо', 'силами', 'рятувальн', 'житлов', 'будин', 'люд', 'будівл',
              'загроз', 'статисти', 'руйнуван', 'загальна', 'перебувал', 'конус', 'план', 'відом', 'бпла', 'базуван', 'існування',
              'атак', 'дорозвідк']

from telethon import TelegramClient, events
from telethon.tl.functions.messages import GetHistoryRequest
import asyncio
import aiohttp
 
client = TelegramClient(SESSION_NAME, API_ID, API_HASH)
processed_ids = set()
 
def message_matches(text):
    text = text.lower()
    has_kw1 = any(kw in text for kw in KEYWORDS_GROUP1)
    has_kw2 = any(kw in text for kw in KEYWORDS_GROUP2)
    has_stop = any(sw in text for sw in STOP_WORDS)
    return has_kw1 and has_kw2 and not has_stop
 
async def send_message_async(text, link, msg_id):
    async with aiohttp.ClientSession() as session:
        payload = {'chat_id': TARGET_CHANNEL, 'text': f"[{text}]({link})", 'parse_mode': 'Markdown', 'disable_web_page_preview': True}
        async with session.post(f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage', json=payload) as resp:
            if resp.status == 200:
                processed_ids.add(msg_id)
 
async def process_message(msg, channel_id, text=None):
    if msg.id in processed_ids:
        return
    text = text or msg.raw_text
    if not message_matches(text):
        return
    link = f"https://t.me/c/{str(channel_id)[4:]}/{msg.id}"
    await send_message_async(text, link, msg.id)
 
@client.on(events.NewMessage(chats=SOURCE_CHANNELS))
async def handler(event):
    await process_message(event, event.chat_id)
 
async def poll_channels():
    while True:
        for channel_id in SOURCE_CHANNELS:
            try:
                entity = await client.get_entity(channel_id)
                history = await client(GetHistoryRequest(peer=entity,limit=5,offset_date=None,offset_id=0,max_id=0,min_id=0,add_offset=0,hash=0))
                for msg in reversed(history.messages):
                    if msg.id not in processed_ids:
                        await process_message(msg, channel_id, msg.message)
            except:
                continue
        await asyncio.sleep(5)
 
async def main():
    await client.start()
    asyncio.create_task(poll_channels())
    await client.run_until_disconnected()
 
asyncio.run(main())
