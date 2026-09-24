from app.rag.loader import load_pdf
from app.rag.chunker import chunk_text


pdf_path = "documents/What is NLP.pdf"


pages = load_pdf(pdf_path)

all_chunks = []


for page in pages:

    chunks = chunk_text(
        text= page["text"],
        document= page["document"],
        page= page["page"],
        chunk_size= 500,
        overlap= 100
    )

    all_chunks.extend(chunks)


print(f"Total pages: {len(pages)}")
print(f"Total chunks: {len(all_chunks)}")


for i, chunk in enumerate(all_chunks, start = 1):

    print("\n" + "=" * 70)

    print(f"Chunk {i}")
    print("Chunk ID:", chunk["chunk_id"])
    print("Document:", chunk["document_id"])
    print("Page:", chunk["page"])
    print("Length:", len(chunk["text"]))

    print("\nText:")
    print(chunk["text"])