from qdrant_client import QdrantClient
from google import genai
from app.config import settings


# Connect to Qdrant
qdrant = QdrantClient(
    url="http://localhost:6333"
)


# Connect to Gemini
gemini = genai.Client(
    api_key=settings.gemini_api_key
)


collection_name = "rag_documents"


# User's search question
query = "How can I protect my computer from hackers?"


# Convert the query into an embedding
result = gemini.models.embed_content(
    model="gemini-embedding-001",
    contents=query,
)

query_vector = result.embeddings[0].values


# Search Qdrant
results = qdrant.query_points(
    collection_name=collection_name,
    query=query_vector,
    limit=5,
    with_payload=True,
).points


print("Query:")
print(query)

print("\nSearch Results:")

for result in results:
    print(f"\nSimilarity: {result.score:.4f}")
    print(f"Text: {result.payload['text']}")