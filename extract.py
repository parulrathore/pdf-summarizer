import fitz  # PyMuPDF
import sys

def extract_text_from_pdf(pdf_path: str) -> list[dict]:
    """
    Extracts text from a PDF, page by page.
    Returns a list of {"page": int, "text": str} dicts.
    """
    doc = fitz.open(pdf_path)
    pages = []

    for page_num, page in enumerate(doc, start=1):
        text = page.get_text().strip()
        pages.append({"page": page_num, "text": text})

    doc.close()
    return pages


def is_extraction_poor(pages: list[dict]) -> bool:
    """
    Heuristic: if avg text per page is very low, PDF is likely scanned/image-based
    and needs OCR instead.
    """
    total_chars = sum(len(p["text"]) for p in pages)
    avg_chars_per_page = total_chars / len(pages) if pages else 0
    return avg_chars_per_page < 50  # tune this threshold as you test


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python extract.py <path_to_pdf>")
        sys.exit(1)

    pdf_path = sys.argv[1]
    pages = extract_text_from_pdf(pdf_path)

    print(f"Extracted {len(pages)} pages\n")

    if is_extraction_poor(pages):
        print("⚠️  Extraction looks poor — this PDF may be scanned/image-based. Needs OCR fallback.\n")

    for p in pages[:3]:  # just print first 3 pages so output isn't overwhelming
        print(f"--- Page {p['page']} ({len(p['text'])} chars) ---")
        print(p["text"][:500])  # first 500 chars per page
        print()