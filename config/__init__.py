import datetime
import logging

from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")
collection = client["logs"]["logs"]


class MongoHandler(logging.Handler):
    def __init__(self, db_uri, db_name, collection_name):
        logging.Handler.__init__(self)
        client = MongoClient(db_uri)
        self.collection = client[db_name][collection_name]

    def emit(self, record):
        log_document = {
            "app_name": record.name,
            "log_level": record.levelname,
            "message": record.msg,
            "timestamp": datetime.datetime.fromtimestamp(record.created).strftime(
                "%Y-%m-%d %H:%M:%S"
            ),
        }
        self.collection.insert_one(log_document)
