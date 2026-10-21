import uuid


def chunk_text(
    text: str,
    document: str,
    page: int,
    chunk_size: int = 200,
    overlap: int = 0
):
    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than 0")

    if overlap < 0:
        raise ValueError("overlap cannot be negative")

    if overlap >= chunk_size:
        raise ValueError("overlap must be smaller than chunk_size")

    chunks = []

    start = 0

    while start < len(text):
        end = start + chunk_size

        chunk = text[start:end]

        chunks.append({
            "chunk_id": str(uuid.uuid4()),
            "document": document,
            "page": page,
            "text": chunk
        })

        start = end - overlap

    return chunks