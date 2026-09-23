from app.rag.embeddings import (
    create_embedding,
    cosine_similarity 
    )

# Vector embeddings for testing
a = create_embedding("Java is a programming language.")

b = create_embedding("Python is a programming language.")

c = create_embedding("I am an engineer.")

print("Embedding length:", len(a))
# Calculate and print cosine similarities
print("Cosine similarity (a, b):", cosine_similarity(a, b))
print("Cosine similarity (a, c):", cosine_similarity(a, c))
print("Cosine similarity (b, c):", cosine_similarity(b, c))