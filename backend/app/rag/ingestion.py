import sys

from app.rag.loader import load_pdf
from app.rag.chunker import chunk_text
from app.rag.embeddings import create_embedding
from app.rag.vector_store import create_collection, upsert_chunk


def ingest(pdf_path: str):
    print("Loading PDF...")

    pages = load_pdf(pdf_path)

    print(f"Loaded {len(pages)} pages.")

    print("Creating chunks...")

    all_chunks = []

    for page in pages:
        chunks = chunk_text(
            page["text"],
            page["document"],
            page["page"]
        )

        all_chunks.extend(chunks)

    print(f"Created {len(all_chunks)} chunks.")

    print("Generating embeddings + uploading to Qdrant...")

    create_collection()

    for index, chunk in enumerate(all_chunks, start=1):
        print(f"Processing chunk {index}/{len(all_chunks)}...")

        vector = create_embedding(chunk["text"])

        upsert_chunk(
            chunk["chunk_id"],
            vector,
            chunk
        )

    print(f"Successfully indexed {len(all_chunks)} chunks.")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python -m app.rag.ingestion <pdf_path>")
        sys.exit(1)

    ingest(sys.argv[1])