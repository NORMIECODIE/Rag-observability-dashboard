from pathlib import Path
from app.rag.loader import load_pdf

documents_folder = Path("documents")
pdf_files = list(documents_folder.glob("*.pdf"))

print("Available Documents:")

for i, pdf in enumerate(pdf_files, start=1):
    print(f"{i}. {pdf.name}")

# Prompt user to select a document
choice = int(input("Enter the number of the document you want to load: "))
selected_pdf = pdf_files[choice -1]

print(f"\nLoading document: {selected_pdf.name}\n")
pages = load_pdf(str(selected_pdf))

print(f"Total pages with text: {len(pages)} ")

for page in pages:

    print("\n" + "=" * 60)

    print("Document:", page["document"])
    print("Page:", page["page"])

    print("\nText:")
    print(page["text"])