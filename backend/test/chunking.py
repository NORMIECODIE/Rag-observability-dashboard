from backend.test.pdf_ingestion import load_pdf


def fixed_size_chunk(text, chunk_size=500, chunk_overlap=50):

    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than 0")

    if chunk_overlap < 0:
        raise ValueError("chunk_overlap cannot be negative")

    if chunk_overlap >= chunk_size:
        raise ValueError("chunk_overlap must be smaller than chunk_size")

    chunks = []

    start = 0

    while start < len(text):

        end = start + chunk_size

        chunk = text[start:end]

        chunks.append(chunk)

        start = end - chunk_overlap

    return chunks


# Load PDF documents
documents = load_pdf("../documents/test.pdf")

print("Total page documents:", len(documents))


# Store all chunks
all_chunks = []

# Global chunk ID
chunk_id = 0


# Process each page document
for document in documents:

    text = document["text"]
    metadata = document["metadata"]


    CHUNK_SIZE = 200
    CHUNK_OVERLAP = 0

    chunks = fixed_size_chunk(
    text,
    chunk_size=CHUNK_SIZE,
    chunk_overlap=CHUNK_OVERLAP
)

    # Create a document object for every chunk
    for chunk_text in chunks:

        chunk_document = {
            "text": chunk_text,
            "metadata": {
                "source": metadata["source"],
                "page": metadata["page"],
                "chunk_id": chunk_id,
                "chunking_method": "fixed_size"
            }
        }

        all_chunks.append(chunk_document)

        chunk_id += 1


# Display results
print("\nTotal chunks:", len(all_chunks))


for chunk in all_chunks:

    print("\n==============================")
    print("Metadata:", chunk["metadata"])
    print("Characters:", len(chunk["text"]))

    print("Text:")
    print(chunk["text"])
