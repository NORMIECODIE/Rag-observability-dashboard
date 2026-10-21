from datetime import datetime

from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017")

db = client["rag_observability"]

traces_collection = db["traces"]


def save_trace(trace_data: dict):
    trace_data["created_at"] = datetime.utcnow()

    result = traces_collection.insert_one(trace_data)

    return str(result.inserted_id)