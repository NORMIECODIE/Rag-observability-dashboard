from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
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


# Document we want to store
text = "Network security protects computers and networks from unauthorized access and cyber attacks."


# Generate embedding
result = gemini.models.embed_content(
    model="gemini-embedding-001",
    contents=text,
)

vector = result.embeddings[0].values


# Store vector + original text in Qdrant
qdrant.upsert(
    collection_name=collection_name,
    points=[
        PointStruct(
            id=1,
            vector=vector,
            payload={
                "text": text
            },
        )
    ],
)


print("Document stored successfully!")

print("\nStored document:")
print(text)

print("\nVector dimensions:")
print(len(vector))

stored = qdrant.retrieve(
    collection_name=collection_name,
    ids=[1],
    with_vectors=False,
)

print("\nRetrieved from Qdrant:")
print(stored)