
from app.rag.vector_store import client, COLLECTION_NAME


result = client.scroll(
    collection_name=COLLECTION_NAME,
    limit=1,
    with_payload=True,
    with_vectors=False,
)

points = result[0]

if points:
    print("Retrieved point:")
    print("ID:", points[0].id)
    print("Payload:", points[0].payload)
else:
    print("No points found in the collection.")
