import uuid 


def recursive_split(
        text: str,
        chunk_size: int,
        separators: list[str]
) -> list[str]:

    if len(text) <= chunk_size:
        return [text.strip()]

    if not separators:
        return [
            text[i:i + chunk_size].strip()
            for i in range(0, len(text), chunk_size)
        ]

    separator = separators[0]

    parts = text.split(separator)

    chunks = []
    current = ""

    for part in parts:

        part = part.strip()

        if not part:
            continue

        if current:
            candidate = current + separator + part
        else:
            candidate = part

        if len(candidate) <= chunk_size:

            current = candidate

        else:

            if current:
                chunks.append(current.strip())

            if len(part) > chunk_size:

               smaller_chunks = recursive_split(
                   part,
                   chunk_size,
                   separators[1:]
               )

               chunks.extend(smaller_chunks)

               current = ""

            else:

                current = part

    if current:

        chunks.append(current.strip())

    return chunks



def create_overlap_chunks(
        chunks: list[str],
        overlap: int,
        chunk_size: int
) -> list[str]:

        if not chunks:
            return []

        if overlap <= 0:
            return chunks


        result = []

        for i, chunk in enumerate(chunks):

             if i == 0:
                 result.append(chunk)
                 continue
             previous = chunks[i - 1]

             overlap_text = previous[-overlap:]

             available_space = chunk_size - len(overlap_text) -1

             if available_space > 0:

                 chunk = chunk[:available_space]


                 combined = overlap_text + " " + chunk

             else:

                combined = chunk[:chunk_size]

             result.append(combined.strip())

        return result 
             

def chunk_text(
        text: str,
        document: str,
        page: int,
        chunk_size: int = 500,
        overlap: int = 100
) -> list[dict]:

    separators = [
        "\n\n",
        "\n",
        ".",
        ""
    ]

    pieces = recursive_split(
        text= text,
        chunk_size = chunk_size,
        separators = separators
    )

    pieces = create_overlap_chunks(
        chunks = pieces,
        overlap = overlap,
        chunk_size = chunk_size
    )


    chunks = []


    for piece in pieces:

        chunks.append(
            {
                "chunk_id": str(uuid.uuid4()),
                "document_id": document,
                "page": page,
                "text": piece
            }
        )

    return chunks
