from pdf_ingestion import load_pdf


def recursive_chunk(text, chunk_size=200):

    if len(text) <= chunk_size:
        return [text.strip()]

    # Try paragraph boundaries first
    paragraphs = text.split("\n\n")

    if len(paragraphs) > 1:

        chunks = []
        current_chunk = ""

        for paragraph in paragraphs:

            paragraph = paragraph.strip()

            if not paragraph:
                continue

            if len(current_chunk) + len(paragraph) + 2 <= chunk_size:

                if current_chunk:
                    current_chunk += "\n\n"

                current_chunk += paragraph

            else:

                if current_chunk:
                    chunks.append(current_chunk)

                if len(paragraph) > chunk_size:

                    smaller_chunks = recursive_chunk(
                        paragraph,
                        chunk_size
                    )

                    chunks.extend(smaller_chunks)

                    current_chunk = ""

                else:
                    current_chunk = paragraph

        if current_chunk:
            chunks.append(current_chunk)

        return chunks

    # Try line boundaries
    lines = text.split("\n")

    if len(lines) > 1:

        chunks = []
        current_chunk = ""

        for line in lines:

            line = line.strip()

            if not line:
                continue

            if len(current_chunk) + len(line) + 1 <= chunk_size:

                if current_chunk:
                    current_chunk += "\n"

                current_chunk += line

            else:

                if current_chunk:
                    chunks.append(current_chunk)

                if len(line) > chunk_size:

                    smaller_chunks = recursive_chunk(
                        line,
                        chunk_size
                    )

                    chunks.extend(smaller_chunks)

                    current_chunk = ""

                else:
                    current_chunk = line

        if current_chunk:
            chunks.append(current_chunk)

        return chunks

    # Final fallback: fixed-size splitting
    chunks = []

    start = 0

    while start < len(text):

        end = start + chunk_size

        chunks.append(text[start:end])

        start = end

    return chunks


# Load the PDF using Day 5 ingestion
documents = load_pdf("../documents/test.pdf")

print("Total page documents:", len(documents))


# Store all recursive chunks
all_chunks = []

chunk_id = 0


# Process each page
for document in documents:

    text = document["text"]
    metadata = document["metadata"]

    chunks = recursive_chunk(
        text,
        chunk_size=200
    )

    for chunk_text in chunks:

        chunk_document = {
            "text": chunk_text,
            "metadata": {
                "source": metadata["source"],
                "page": metadata["page"],
                "chunk_id": chunk_id
            }
        }

        all_chunks.append(chunk_document)

        chunk_id += 1


# Display results
print("\nTotal recursive chunks:", len(all_chunks))


for chunk in all_chunks:

    print("\n==============================")

    print("Chunk ID:", chunk["metadata"]["chunk_id"])
    print("Source:", chunk["metadata"]["source"])
    print("Page:", chunk["metadata"]["page"])
    print("Characters:", len(chunk["text"]))

    print("Text:")
    print(chunk["text"])