from pathlib import Path
import pymupdf


def load_pdf(pdf_path: str):
    pdf = pymupdf.open(pdf_path)
    pages = []

    for page_number, page in enumerate(pdf):
        text = page.get_text().strip()

        if not text:
            continue

        pages.append({
            "document": Path(pdf_path).name,
            "page": page_number + 1,
            "text": text
        })

    pdf.close()

    return pages