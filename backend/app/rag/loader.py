from pathlib import Path
from pypdf import PdfReader

def load_pdf(path: str) -> list[dict]:
    reader = PdfReader(path)

    pages = []

    documment_name = Path(path).name

    for i, page in enumerate(reader.pages):

        text = (page.extract_text() or "").strip()

        if text:
            pages.append(
                {
                    "document": documment_name,
                    "page": i + 1,
                    "text": text
                }
            )
    return pages