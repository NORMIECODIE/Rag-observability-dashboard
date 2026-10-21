import pymupdf
from pathlib import Path


def load_pdf(pdf_path):
    pdf = pymupdf.open(pdf_path)

    documents = []

    for page_number, page in enumerate(pdf):
        text = page.get_text()

        # Remove unnecessary whitespace
        text = text.strip()

        # Skip empty pages
        if not text:
            continue

        metadata = {
            "source": Path(pdf_path).name,
            "page": page_number + 1
        }

        document = {
            "text": text,
            "metadata": metadata
        }

        documents.append(document)

    pdf.close()

    return documents


documents = load_pdf("../documents/test.pdf")

print("Total documents created:", len(documents))

for document in documents:
    print("\n--------------------")
    print("Document:")
    print(document)
