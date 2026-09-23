from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct
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


# Documents to store
documents = [
    "A firewall helps protect a network by controlling incoming and outgoing network traffic.",

    "Strong passwords should be long, unique, and difficult for attackers to guess.",

    "Network security protects computers and networks from unauthorized access and cyber attacks.",

    "Cloud computing allows users to access computing resources such as storage and servers over the internet.",

    "A chocolate cake can be made using ingredients such as flour, cocoa powder, sugar, eggs, and milk.",
]


points = []


for index, text in enumerate(documents, start=1):

    # Generate embedding
    result = gemini.models.embed_content(
        model="gemini-embedding-001",
        contents=text,
    )

    vector = result.embeddings[0].values

    # Create Qdrant point
    point = PointStruct(
        id=index,
        vector=vector,
        payload={
            "text": text
        },
    )

    points.append(point)


# Store all vectors in Qdrant
qdrant.upsert(
    collection_name=collection_name,
    points=points,
)


print(f"Successfully indexed {len(points)} documents.")

for point in points:
    print(f"ID {point.id}: {point.payload['text']}")