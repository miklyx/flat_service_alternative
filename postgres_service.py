import asyncpg


import asyncio
import os
import redis
import json
from dotenv import load_dotenv


load_dotenv()

DATABASE_URL = os.environ.get("FLATS_ACCU_PG")
CHANNEL_USERNAME = os.environ.get("PY_CHANNEL_USERNAME")
EXTRA_CHANNEL_USERNAME = os.environ.get("PY_CHANNEL_USERNAME_EXTRA")


async def insert_into_postgres(db_connection, flat):
    #print(flat)
    #print(flat.message_id)
    await insert_message(
        db_connection,
        flat["message_id"],
        "",
        flat["url"],
        flat["about"],
        flat["price"],
        flat["size"],
        "",
        flat["address"],
        flat["channel_name"],
        "",
        "",
        "",
        "",
        flat["added_dttm"],
    )


async def init_pg():
    db_connection = await asyncpg.connect(DATABASE_URL)

    try:
        print("creating tables")
        #await create_table_messages24(db_connection)
        #await create_table_last24(db_connection)
        print("populating tables")
        #await init_last_message(db_connection, CHANNEL_USERNAME)
        #await init_last_message(db_connection, EXTRA_CHANNEL_USERNAME)
        return db_connection
    except Exception as e:
        print(f"Error: {e}")


async def create_table_messages24(connection):
    query = """
    CREATE TABLE IF NOT EXISTS messages24 (
      
      id int8 NULL,
      image text NULL,
      url text NULL,
      title text NULL,
      price text NULL,
      "size" text NULL,
      rooms text NULL,
      address text NULL,
      crawler text NULL,
      "from" text NULL,
      "to" text NULL,
      images text NULL,
      total_price text NULL,
      added_dttm text NULL
    );
    """
    await connection.execute(query)


async def create_table_last24(connection):
    query = """
    CREATE TABLE IF NOT EXISTS last_message24 (
        id serial PRIMARY KEY,
        message_id bigint,
        channel text
    );
    """
    await connection.execute(query)


async def insert_message(
    connection,
    id,
    img,
    url,
    title,
    prc,
    sz,
    rm,
    addr,
    crw,
    fr,
    to,
    imgs,
    totprc,
    add_dt,
):
    query = """
      INSERT INTO messages24 (
      
      id,
      image,
      url,
      title,
      price,
      "size",
      rooms,
      address,
      crawler,
      "from",
      "to",
      images,
      total_price,
      added_dttm
    ) VALUES (
      $1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$11,$12,$13,$14);
    """
    try: 
        await connection.execute(
            query, id, img, url, title, prc, sz, rm, addr, crw, fr, to, imgs, totprc, add_dt
        )
        print(f"Inserted message with id {id}")
    except Exception as e:
        print(f"Error inserting message with id {id}: {e}")
        raise e


async def get_last_message_id(connection, channel):
    query = "SELECT max(message_id) FROM last_message24 where channel=$1;"
    result = await connection.fetchval(query, channel)
    # result = await connection.execute(query, channel)
    return result if result is not None else 0


async def update_last_message_id(connection, message_id, channel):
    query = """
        UPDATE last_message24
        SET message_id = $1
        where channel = $2;
    """
    print(f"Updating last message id to {message_id} with type {type(message_id)} for channel {channel}")
    await connection.execute(query, message_id, channel)


async def init_last_message(connection, channel):
    query = """
      INSERT INTO last_message24
      (message_id, channel)
      VALUES 
      (1, $1)
    """
    await connection.execute(query, channel)