import sys 


from app.rag.loader import load_pdf
from app.rag.chunker import chunk_text
from app.rag.embeddings import create_embedding
from app.rag.vector_store import create_collection, upsert_chunk

def ingest(pdf_path: str):

    print("Loading PDF....")

    pages = load_pdf(pdf_path)


    print("Creating chunks....")

    all_chunks = []

    for p in pages:

        all_chunks += chunk_text(
            p["text"],
            p["document"],
            p["page"]
        )

    print("Generating embeddings + Uploading to Qdrant....")

    create_collection()


    for c in all_chunks:

        vector = create_embedding(c["text"])

        upsert_chunk(
            c["chunk_id"],
            vector,
            c
        )


    print(f"Successfully indexed {len(all_chunks)} chunks.")


if __name__ == "__main__":

    ingest(sys.argv[1])