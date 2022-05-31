import motor.motor_asyncio  # type: ignore

from conf.configs import conf
import asyncio

client = motor.motor_asyncio.AsyncIOMotorClient(conf.mongo_uri)
client.get_io_loop = asyncio.get_event_loop
database = client.fiftyone

plugin_collection = database.get_collection("plugin_collection")


async def add_task(task_data: dict) -> dict:
    item = await plugin_collection.insert_one(task_data)
    new_item = await plugin_collection.find_one({"_id": item.inserted_id})
    return new_item


async def get_task(tid: str) -> dict:
    new_item = await plugin_collection.find_one({"tid": tid})
    return new_item
