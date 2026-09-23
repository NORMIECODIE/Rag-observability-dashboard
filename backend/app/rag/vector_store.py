from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct

qdrant = QdrantClient(url="http://localhost:6333")

Collection =  "documents"

def create_collection(dim: int = 3072):
    qdrant.recreate_collection(
        collection_name=Collection,
        vectors_config=VectorParams(size=dim, distance=Distance.COSINE),
    )

def upsert_chunk(
        point_id: int,
        vector: list[float],
        payload: dict
    ):
        qdrant.upsert(
            collection_name=Collection,
            points=[
                PointStruct(
                    id=point_id,
                    vector=vector,
                    payload=payload
                )
            ],
        )
def search(
        vector: list[float],
        top_k: int = 3
    ):
    result = qdrant.query_points(
        collection_name=Collection,
        query=vector,
        limit=top_k,
        with_payload=True
    )
    return result.points    