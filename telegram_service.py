import os
from dotenv import load_dotenv

load_dotenv()

CHANNEL_USERNAME = os.environ.get('PY_CHANNEL_USERNAME')
EXTRA_CHANNEL_USERNAME = os.environ.get('PY_CHANNEL_USERNAME_EXTRA')

def parse_main_bot(str):
    about = str.split('Price: ')[0]
    last = str.split('Price: ')[1]
    price = last.split('Size: ')[0]
    last = last.split('Size: ')[1]
    size = last.split('Location: ')[0]
    address_full = last.split('Location: ')[1]
    address = address_full.split('https:')[0]
    url = 'https:'+address_full.split('https:')[1]
    return [about, price, size, address, url]

def parse_extra_bot(str):
    arr = str.split('\n')
    about = arr[0]
    price = arr[3].split('Preis: ')[1]
    size = arr[2].split('Größe: ')[1]
    address_full = 'Berlin'
    address = 'Berlin'
    url = arr[5]
    return [about, price, size, address, url]

async def read_channel(client, last_message_id, channel_name, lock, count = 40):
    try:
      async with lock:
        print('getting messages')
        entity = await client.get_entity(channel_name)
        messages = await client.get_messages(entity, limit=count)
        print('checking new')
        new_messages = [message for message in messages if message.id > last_message_id]
        if new_messages:
            last_message_id = new_messages[0].id
            flats = []
            for message in new_messages:
                if channel_name=='berlin_apartment_bot':
                    print('old bot')
                    str=message.raw_text
                    parsed = parse_main_bot(str)
                else :
                    str=message.raw_text
                    parsed = parse_extra_bot(str)
                    print('new bot')
                flat = {
                        "message_id":message.id,
                        "url":parsed[4],
                        "about":parsed[0],
                        "price":parsed[1],
                        "size":parsed[2],
                        "address":parsed[3],
                        "channel_name":channel_name,
                        'added_dttm':message.date.strftime("%d/%m/%Y, %H:%M:%S")
                      }
                flats.append(flat)
            return flats
    except Exception as e:
        print(f'Error reading channel: {e}')

