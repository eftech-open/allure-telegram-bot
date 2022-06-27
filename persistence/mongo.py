import logging
import os

from collections import defaultdict
from telegram.ext import BasePersistence

from dotenv import load_dotenv
from pymongo import MongoClient


load_dotenv()


class MongoPersistence(BasePersistence):
    """
    MongoDB persistence
    """

    def __init__(self,
                 host,
                 database,
                 port,
                 store_user_data=True,
                 store_chat_data=True,
                 store_bot_data=True):
        super().__init__(
            store_user_data=store_user_data,
            store_chat_data=store_chat_data,
            store_bot_data=store_bot_data,
        )

        self.client = MongoClient(host=host, port=int(port))
        self.db = self.client[database]
        logging.debug(f"Connected to '{self.db}' on '{host}'")

    def drop_table(self) -> None:
        self.db["launch_data"].drop()

    def get_user_data(self) -> dict:
        data = defaultdict(dict)
        for item in self.db["user_data"].find():
            data[item["user_id"]] = item["data"]
        return data

    def get_chat_data(self) -> dict:
        data = defaultdict(dict)
        for item in self.db["chat_data"].find():
            data[item["chat_id"]] = item["data"]
        return data

    def get_launch_data(self) -> list:
        data = list()
        for item in self.db["launch_data"].find():
            data.append(item['launch_id'])
        return data

    def get_bot_data(self) -> dict:
        data = {}
        for item in self.db["bot_data"].find():
            data[item["key"]] = item["value"]
        return data

    def get_callback_data(self) -> dict:
        data = {}
        for item in self.db["callback_dat"].find():
            data[item["callback_dat"]] = item["data"]
        return data

    def get_conversations(self, name: str) -> dict:
        data = {}
        for item in self.db[f"conversation.{name}"].find():
            data[tuple(item["conv"])] = item["state"]
        return data

    def update_conversation(self, name, key, new_state):
        self.db[f"conversation.{name}"].update_one({"conv": key}, {"$set": {"state": new_state}}, upsert=True)

    def update_user_data(self, user_id, data):
        self.db["user_data"].update_one({"user_id": user_id}, {"$set": {"data": data}}, upsert=True)

    def update_chat_data(self, chat_id, data):
        self.db["chat_data"].update_one({"chat_id": chat_id}, {"$set": {"data": data}}, upsert=True)

    def update_bot_data(self, data):
        for key, value in data.items():
            self.db["bot_data"].update_one({"key": key}, {"$set": {"value": value}}, upsert=True)

    def update_launch_data(self, data: dict):
        for key, value in data.items():
            self.db["launch_data"].update_one({"launch_id": key}, {"$set": {"launch_id": key}}, upsert=True)
            logging.debug(f"'launch_id': {key} added to 'launch_data'")


mongo_persistence = MongoPersistence(
    host=os.environ.get('MONGO_HOST'),
    port=os.environ.get('MONGO_PORT'),
    database=os.environ.get('MONGO_DATABASE')
)
