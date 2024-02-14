import asyncio
import os
from dotenv import load_dotenv

from database_service import init_redis, insert_into_redis_sorted

from telegram_client import telegram_client
from telegram_service import read_channel

load_dotenv()

CHANNEL_USERNAME = os.environ.get('PY_CHANNEL_USERNAME')

async def refresh_flats(max_count = 40, count = 40):
    client = await telegram_client()
    r = await init_redis()
    set_key = "flats_set"
    sorted_set_key = "flats_sorted_set"
    try:
        lock = asyncio.Lock()
        flats = await read_channel(client, 0, CHANNEL_USERNAME, lock, count)
        for flat in flats:
          await insert_into_redis_sorted(r, sorted_set_key, flat, max_count)
    except Exception as e:
        print(f'Error: {e}')
    return "Okay"

