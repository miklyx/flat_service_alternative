from fastapi import FastAPI, Query
from refresh_flats import refresh_flats
from get_flats import get_flats
from pydantic import BaseModel

from typing import Annotated

app = FastAPI()

class Flat(BaseModel):
    message_id: int
    url: str
    about: str
    price: str
    size: str
    address: str
    channel_name: str
    added_dttm: str

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "message_id":874097,
                    "url":"https://www.immobilienscout24.de/expose/148809133",
                    "about":"Sehr hell und freundlichj.\n",
                    "price":"1045.0 €\n",
                    "size":"64.0m²\n",
                    "address":"Rosenfelder Straße 27, 10315 Berlin, Friedrichsfelde (Lichtenberg)\n",
                    "channel_name":"berlin_apartment_bot",
                    "added_dttm":"06/02/2024, 09:05:58"
                }
            ]
        }
    }


@app.get("/")
async def root():
    return "Refresh service"

@app.get("/flats", response_model=list[Flat])
async def get_flats_route(count: Annotated[
                                  int, 
                                  Query(
                                      title="Number of flats",
                                      description = "Number of falts in response" , 
                                      gt=0
                                      )
                                      ] = -1 ):
    data = await get_flats(count)
    return data

@app.get("/refresh_flats")
async def refresh_flats_route(max_count=40, count=40):
    await refresh_flats()
    return "Refreshed"

""" @app.get("/items_p/{item_id}")
async def read_user_item(
    item_id: str, needy: str, skip: int = 0, limit: Union[int, None] = None
):
    item = {"item_id": item_id, "needy": needy, "skip": skip, "limit": limit}
    return item

@app.get("/items/{item_id}")
async def read_item(item_id: int):
    return {"item_id": item_id}



@app.get("/models/{model_name}")
async def get_model(model_name: ModelName):
    if model_name is ModelName.alexnet:
        return {"model_name": model_name, "message": "Deep Learning FTW!"}

    if model_name.value == "lenet":
        return {"model_name": model_name, "message": "LeCNN all the images"}

    return {"model_name": model_name, "message": "Have some residuals"}
 """