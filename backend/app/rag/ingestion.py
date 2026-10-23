import sys 


from app.rag.loader import load_pdf
from app.rag.chunker import chunk_text
from app.rag.embeddings import create_embedding
from app.rag.vector_store import create_collection, upsert_chunk

# Ingest the PDF into the RAG system
def ingest(
        pdf_path: str,
        chunk_size: int = 500,
        overlap: int = 100
        ):

    print("Loading PDF....")

    pages = load_pdf(pdf_path)


    print("Creating chunks....")

    all_chunks = []

    for p in pages:

        all_chunks += chunk_text(
            p["text"],
            p["document"],
            p["page"],
            chunk_size = chunk_size,
            overlap = overlap
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

    pdf_path = sys.argv[1]

    chunk_size = int(sys.argv[2]) if len(sys.argv) > 2 else 500
    overlap = int(sys.argv[3]) if len(sys.argv) > 3 else 100

    ingest(
        pdf_path,
        chunk_size = chunk_size,
        overlap = overlap
    )