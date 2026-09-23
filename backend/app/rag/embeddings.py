import numpy as np

from app.llm.client import client

# Embedding function creation using Gemini API
def create_embedding(text: str) -> list[float]:
    response = client.models.embed_content(
        model="gemini-embedding-2",
        contents = text,
    )
    # Extract the embedding vector from the response
    return response.embeddings[0].values

def cosine_similarity(
        a: list[float],
        b: list[float]
) -> float:
    # Convert lists to numpy arrays for vector operations
    a = np.array(a)
    b = np.array(b)

    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)

    # Calculate cosine similarity
    # The cosine similarity is computed as the dot product of the two vectors divided by the product of their magnitudes (norms).
    if norm_a == 0 or norm_b == 0:
        return 0.0

    similarity = np.dot(a, b) / (norm_a * norm_b)

    return float(similarity)