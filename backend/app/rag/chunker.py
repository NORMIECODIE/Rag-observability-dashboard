
import uuid


def chunk_text(
    text: str,
    document: str,
    page: int,
    chunk_size: int = 500,
    overlap: int = 100,
) -> list[dict]:
    """Split text into bounded, overlapping chunks."""

    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than 0")

    if overlap < 0 or overlap >= chunk_size:
        raise ValueError("overlap must be >= 0 and less than chunk_size")

    text = " ".join(text.split())

    if not text:
        return []

    chunks = []
    start = 0

    while start < len(text):
        end = min(start + chunk_size, len(text))

        # Prefer ending at a word boundary when more text remains.
        if end < len(text):
            boundary = text.rfind(" ", start, end)
            if boundary > start:
                end = boundary

        piece = text[start:end].strip()

        if piece:
            chunks.append({
                "chunk_id": str(uuid.uuid4()),
                "document_id": document,
                "page": page,
                "text": piece,
            })

        if end >= len(text):
            break

        # Move forward while retaining the requested overlap.
        next_start = max(start + 1, end - overlap)

        # Start at a word boundary if possible.
        boundary = text.find(" ", next_start, end)
        if boundary != -1:
            next_start = boundary + 1

        start = next_start

    return chunks
