from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
import os



COLLECTION_NAME = "rag_documents"
VECTOR_SIZE = 3072

QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
client = QdrantClient(url=QDRANT_URL)


def create_collection():
    collections = client.get_collections().collections

    existing_collections = [collection.name for collection in collections]

    if COLLECTION_NAME not in existing_collections:
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(
                size=VECTOR_SIZE,
                distance=Distance.COSINE
            )
        )

        print(f"Created collection: {COLLECTION_NAME}")
    else:
        print(f"Collection already exists: {COLLECTION_NAME}")


def upsert_chunk(chunk_id, vector, chunk):
    point = PointStruct(
        id=chunk_id,
        vector=vector,
        payload=chunk
    )

    client.upsert(
        collection_name=COLLECTION_NAME,
        points=[point]
    )

def search(vector: list[float], top_k: int = 3):
    results = client.query_points(
        collection_name=COLLECTION_NAME,
        query=vector,
        limit=top_k,
        with_payload=True
    )

    return results.points