import os
import redis
import json
from dotenv import load_dotenv

load_dotenv()

REDIS_PWD = os.environ.get("REDIS_PWD")
REDIS_HOST = os.environ.get("REDIS_HOST")
CHANNEL_USERNAME = os.environ.get("PY_CHANNEL_USERNAME")
EXTRA_CHANNEL_USERNAME = os.environ.get("PY_CHANNEL_USERNAME_EXTRA")


async def insert_into_redis(redis, list, flat):
    redis.sadd(list, json.dumps(flat))
    if len(redis.smembers(list)) > 20:
        redis.srem(list, redis.spop(list))


async def insert_into_redis_sorted(redis, sorted_set_key, flat, max_count=40):
    redis.zadd(sorted_set_key, {json.dumps(flat): flat["message_id"]})
    if len(redis.zrange(sorted_set_key, 0, -1)) > max_count:
        oldest_element = redis.zrange(sorted_set_key, 0, 0, withscores=True)
        redis.zrem(sorted_set_key, oldest_element[0][0])


async def init_redis():
    redis_connection = redis.Redis(host=REDIS_HOST, port=19093, password=REDIS_PWD)
    return redis_connection


async def get_from_redis(redis, sorted_set_key, count=-1):
    if count:
        index = count - 1
    res = redis.zrange(sorted_set_key, 0, index)
    data = [json.loads(x.decode("utf-8")) for x in res]
    return data
