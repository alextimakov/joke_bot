import app.config as config
import pymongo
from enum import Enum

client = pymongo.MongoClient(config.db_url)
db = client[config.db_name]


def select_one(collection, column, **conditions):
    for condition, cond_value in conditions.items():
        cursor = db[collection].find(
            filter={"$and": [{condition: cond_value}, {column: {"$exists": True, "$ne": None}}]},
            projection={column: 1})
    for record in cursor:
        return record[column]


def select_many(collection, column, **conditions):
    if not conditions.items():
        cursor = db[collection].find(filter={column: {"$exists": True, "$ne": None}},
                                     projection={column: 1})
    else:
        for condition, cond_value in conditions.items():
            cursor = db[collection].find(
                filter={"$and": [{condition: cond_value}, {column: {"$exists": True, "$ne": None}}]},
                projection={column: 1})
    result = []
    for record in cursor:
        result.extend([record[column]])
    return result


def update_one(collection, condition, cond_value, **values):
    for column, column_value in values.items():
        db[collection].update_one({condition: cond_value}, {"$set": {column: column_value}})


def insert(collection, **values):
    db[collection].insert_one(values)


def remove_one(collection, column, condition, cond_value):
    db[collection].update({condition: cond_value}, {"$unset": {column: 1}})


class States(Enum):
    START = "0"
    MENU = "1"
    SET_STATE = "2"
    NEWS = "3"
    ATTACH = "4"
    NO_ATTACH = "5"
    NEWS_TYPE = "6"
