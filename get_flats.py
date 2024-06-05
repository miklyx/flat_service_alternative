from database_service import get_from_redis, init_redis
import json


def remove_backslashes(data):
    return data.replace("\\", "")


async def get_flats(count=-1):
    redis = await init_redis()
    sorted_set_key = "flats_sorted_set"
    try:
        res = await get_from_redis(redis, sorted_set_key, count)
        data = json.dumps(res)
        result = json.loads(data)
        return result
    except Exception as e:
        print(f"Error: {e}")
