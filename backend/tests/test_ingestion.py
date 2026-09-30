from pathlib import Path

from app.rag.ingestion import ingest
from app.rag.vector_store import qdrant, Collection

PDF_PATH = Path("documents/What is NLP.pdf")

print("Starting ingestion text...")
print("\n" + "-" * 60)

assert PDF_PATH.exists(), f"PDF not found: {PDF_PATH}"

print(f"PDF found: {PDF_PATH}")

print("\n Running ingestion...")

ingest(str(PDF_PATH))

print("\n Checking Qdrant...")

collection_info = qdrant.get_collection(
    collection_name= Collection
)

points_count = collection_info.points_count

print(f"Collection: {Collection}")
print(f"Points: {points_count}")

assert points_count > 0, f"No points found in the collection!"

print("\n" + "=" * 60)
print("INGESTION SUCCESSFUL!")
print("=" * 60 + "\n")
