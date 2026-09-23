from google import genai
from app.config import settings
import math


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


text_a = "How can I protect my network from unauthorized access?"
text_b = "What can I do to secure my network against hackers?"
text_c = "How do I make a chocolate cake?"


vector_a = get_embedding(text_a)
vector_b = get_embedding(text_b)
vector_c = get_embedding(text_c)


similarity_ab = cosine_similarity(vector_a, vector_b)
similarity_ac = cosine_similarity(vector_a, vector_c)


print("Sentence A:")
print(text_a)

print("\nSentence B:")
print(text_b)

print("\nSentence C:")
print(text_c)

print("\nVector dimensions:", len(vector_a))

print("\nSimilarity A ↔ B:", similarity_ab)
print("Similarity A ↔ C:", similarity_ac)