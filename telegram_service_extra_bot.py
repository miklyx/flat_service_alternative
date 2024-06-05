import os
from dotenv import load_dotenv
from telethon.tl.types import InputPeerChannel
from telegram_client import telegram_client
from telethon import events
from database_service import insert_into_redis_sorted, init_redis
import json

load_dotenv()

CHANNEL_USERNAME = os.environ.get("PY_CHANNEL_USERNAME")
EXTRA_CHANNEL_USERNAME = os.environ.get("PY_CHANNEL_USERNAME_EXTRA")

event_handlers = {}


def parse_main_bot(str):
    about = str.split("Price: ")[0].replace("\n", "")
    last = str.split("Price: ")[1]
    price = last.split("Size: ")[0].replace("\n", "")
    last = last.split("Size: ")[1]
    size = last.split("Location: ")[0].replace("\n", "")
    address_full = last.split("Location: ")[1]
    address = address_full.split("https:")[0].replace("\n", "")
    url = "https:" + address_full.split("https:")[1]
    return [about, price, size, address, url]


def parse_extra_bot(str):
    arr = str.split("\n")
    about = arr[0]
    price = arr[3].split("Preis: ")[1]
    size = arr[2].split("Größe: ")[1]
    address_full = "Berlin"
    address = "Berlin"
    url = arr[5]
    return [about, price, size, address, url]


async def subscribe_to_extra_channel():
    client = await telegram_client()
    entity = await client.get_entity(EXTRA_CHANNEL_USERNAME)

    if 1 == 1:  # entity.id not in event_handlers:
        event_handlers[entity.id] = True
        print(event_handlers)
        print("subscribed")

        @client.on(events.NewMessage(chats=[entity.id]))
        async def new_message_handler(event):
            parsed = parse_extra_bot(event.message.message)
            print(parsed)
            flat = {
                "message_id": event.message.id,
                "url": parsed[4],
                "about": parsed[0],
                "price": parsed[1],
                "size": parsed[2],
                "address": parsed[3],
                "channel_name": CHANNEL_USERNAME,
                "added_dttm": event.message.date.strftime("%d/%m/%Y, %H:%M:%S"),
            }
            r = await init_redis()
            sorted_set_key = "flats_sorted_set"
            print("Received new message:", flat)
            await insert_into_redis_sorted(r, sorted_set_key, flat, max_count=40)
            r.publish("flats_extra_channel", json.dumps(flat))

        await client.run_until_disconnected()


async def unsubscribe_from_extra_channel():
    client = await telegram_client()
    entity = await client.get_entity(EXTRA_CHANNEL_USERNAME)
    if entity.id in event_handlers:
        client.disconnect()
        event_handlers = {}
        print(event_handlers)
        print("unsubscribed")
