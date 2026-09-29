from pymongo import MongoClient

from app.config import settings


client = MongoClient(
    settings.mongodb_url
)


database = client[
    settings.mongodb_database
]


traces_collection = database["traces"]