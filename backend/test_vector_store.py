from app.rag.embeddings import create_embedding
from app.rag.vector_store import (
    create_collection,
    upsert_chunk,   
    search
)

# Create Qdrant collection
create_collection()

# Test documents chunks
chunks = [
    {
        "id": 1,
        "text": "Java is a programming language used to build backend applications."
    },
    {
        "id": 2,
        "text": "Python is a popular programming language used for data science and machine learning."
    },
    {
        "id": 3,
        "text": "JavaScript is a programming language used to build Actractive Websites."
    }
]

# Creating embeddings and store chunks
for chunk in chunks:

    vector = create_embedding(chunk["text"])

    upsert_chunk(
        point_id=chunk["id"],
        vector=vector,
        payload={"text": chunk["text"]}
    )

# Create embedding for the query
question = "What programming language is used for data science?"

query_vector = create_embedding(question)

# Search Qdrants
results = search(vector=query_vector, top_k=3)

# Print results
print("\n Top 3 results:\n")

for result in results:

    print(f"ID: {result.id}, Score: {result.score}, Text: {result.payload['text']}")
    print("-"*60)