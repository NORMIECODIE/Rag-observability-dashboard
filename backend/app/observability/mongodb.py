
import os
from datetime import datetime, timezone

from pymongo import MongoClient

MONGODB_URL = os.getenv(
    "MONGODB_URL",
    "mongodb://localhost:27017",
)

client = MongoClient(MONGODB_URL)

db = client["rag_observability"]
traces_collection = db["traces"]


def save_trace(trace_data: dict):
    trace_data["created_at"] = datetime.now(timezone.utc)

    result = traces_collection.insert_one(trace_data)

    return str(result.inserted_id)
