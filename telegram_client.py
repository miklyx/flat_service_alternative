import os
from dotenv import load_dotenv

from telethon import TelegramClient, functions, types
from telethon.errors import SessionPasswordNeededError
from telethon.sessions import StringSession

load_dotenv()

API_ID = os.environ.get('PY_API_ID')
API_HASH = os.environ.get('PY_API_HASH')
PHONE_NUMBER = os.environ.get('PY_PHONE_NUMBER')
PY_SESSION = os.environ.get('PY_SESSION')

async def telegram_client():
    client = TelegramClient(StringSession(PY_SESSION), API_ID, API_HASH)
    try:
        await client.start()
        return client
    except SessionPasswordNeededError:
        code = input('Please enter the two-factor authentication code from your Telegram app: ')
        await client(functions.auth.CheckPasswordRequest(code=code))
    except Exception as e:
        print(f'Error: {e}')
