from fastapi import FastAPI, Query, BackgroundTasks, WebSocket, WebSocketDisconnect
from refresh_flats import refresh_flats
from get_flats import get_flats
from pydantic import BaseModel
from telegram_service import subscribe_to_channel, unsubscribe_from_channel
from telegram_service_extra_bot import (
    subscribe_to_extra_channel,
    unsubscribe_from_extra_channel,
)
from fastapi_utils.tasks import repeat_every


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
                    "message_id": 874097,
                    "url": "https://www.immobilienscout24.de/expose/148809133",
                    "about": "Sehr hell und freundlichj.\n",
                    "price": "1045.0 €\n",
                    "size": "64.0m²\n",
                    "address": "Rosenfelder Straße 27, 10315 Berlin, Friedrichsfelde (Lichtenberg)\n",
                    "channel_name": "berlin_apartment_bot",
                    "added_dttm": "06/02/2024, 09:05:58",
                }
            ]
        }
    }


class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)


manager = ConnectionManager()


@repeat_every(seconds=60 * 15)
async def refresh_flats_15min():
    await refresh_flats()

@app.on_event("startup")
async def startup_event():
    await refresh_flats_15min()


@app.get("/")
async def root():
    return "Refresh service"


@app.head("/health")
async def health_check():
    return "OK"


@app.get("/flats", response_model=list[Flat])
async def get_flats_route(
    count: Annotated[
        int,
        Query(title="Number of flats", description="Number of flats in response", gt=0),
    ] = 0
):  
    data = await get_flats(count)
    return data


@app.get("/refresh_flats")
async def refresh_flats_route(max_count=40, count=40):
    await refresh_flats()
    return "Refreshed"


@app.post("/subscribe")
async def subscribe_to_channel_endpoint(background_tasks: BackgroundTasks):
    background_tasks.add_task(subscribe_to_channel)


@app.post("/unsubscribe")
async def unsubscribe_from_channel_endpoint():
    await unsubscribe_from_channel()


@app.post("/subscribe_extra")
async def subscribe_to_extra_channel_endpoint(background_tasks: BackgroundTasks):
    background_tasks.add_task(subscribe_to_extra_channel)


@app.post("/unsubscribe_extra")
async def unsubscribe_from_extra_channel_endpoint():
    await unsubscribe_from_extra_channel()


@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: int):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.send_personal_message(f"You wrote: {data}", websocket)
            await manager.broadcast(f"Client #{client_id} says: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast(f"Client #{client_id} left the chat")
