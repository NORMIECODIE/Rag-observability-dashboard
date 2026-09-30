from pymongo import MongoClient

from app.config import settings


# It creates a connection to the MongoDB
client = MongoClient(
    settings.mongodb_url
)

# It connects to the MongoDB
database = client[
    settings.mongodb_database
]

# It stores the traces ( spans , question , answer , status , total latency )
traces_collection = database["traces"]


# Wrap index creation in a try-except block
try:
    # It creates an index on the trace_id column
    traces_collection.create_index(
        "trace_id", 
        unique=True
    )
except Exception as e:
    print(f"Warning: Could not create index on trace_id: {e}")

# It creates an index on the created_at column
traces_collection.create_index(
    "created_at"
)