from google import genai
from app.config import settings
import math


# Create Gemini client
client = genai.Client(api_key=settings.gemini_api_key)


def get_embedding(text):
    result = client.models.embed_content(
        model="gemini-embedding-001",
        contents=text,
    )

    return result.embeddings[0].values


def cosine_similarity(vector_a, vector_b):
    dot_product = sum(a * b for a, b in zip(vector_a, vector_b))

    magnitude_a = math.sqrt(sum(a * a for a in vector_a))
    magnitude_b = math.sqrt(sum(b * b for b in vector_b))

    return dot_product / (magnitude_a * magnitude_b)


# Our small collection of documents
documents = [
    "A firewall helps protect a network by controlling incoming and outgoing network traffic.",
    "Strong passwords should be long, unique, and difficult for attackers to guess.",
    "Network security protects computers and networks from unauthorized access and cyber attacks.",
    "Cloud computing allows users to access computing resources such as storage and servers over the internet.",
    "A chocolate cake can be made using ingredients such as flour, cocoa powder, sugar, eggs, and milk.",
]


# The user's search query
query = "How can I protect my computer from hackers?"


# Create an embedding for the query
query_vector = get_embedding(query)


# Compare the query with every document
results = []

for document in documents:
    document_vector = get_embedding(document)

    similarity = cosine_similarity(query_vector, document_vector)

    results.append((document, similarity))


# Sort from highest similarity to lowest
results.sort(key=lambda x: x[1], reverse=True)


# Display results
print("Query:")
print(query)

print("\nSemantic Search Results:")

for document, similarity in results:
    print(f"\nSimilarity: {similarity:.4f}")
    print(document)