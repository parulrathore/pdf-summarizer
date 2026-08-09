import fitz  # PyMuPDF
import sys
from pdf2image import convert_from_path
import pytesseract


def extract_text_native(pdf_path: str) -> list[dict]:
    """Extract text using PyMuPDF (fast, works for text-based PDFs)."""
    doc = fitz.open(pdf_path)
    pages = []
    for page_num, page in enumerate(doc, start=1):
        text = page.get_text().strip()
        pages.append({"page": page_num, "text": text})
    doc.close()
    return pages


def extract_text_ocr(pdf_path: str) -> list[dict]:
    """Fallback: convert pages to images and OCR them with Tesseract."""
    images = convert_from_path(pdf_path)
    pages = []
    for page_num, image in enumerate(images, start=1):
        text = pytesseract.image_to_string(image).strip()
        pages.append({"page": page_num, "text": text})
    return pages


def is_extraction_poor(pages: list[dict]) -> bool:
    total_chars = sum(len(p["text"]) for p in pages)
    avg_chars_per_page = total_chars / len(pages) if pages else 0
    return avg_chars_per_page < 50


def extract_text_from_pdf(pdf_path: str) -> list[dict]:
    """
    Tries native text extraction first. Falls back to OCR if the result
    looks poor (e.g. scanned/image-based PDF).
    """
    pages = extract_text_native(pdf_path)

    if is_extraction_poor(pages):
        print("Native extraction looks poor — falling back to OCR...")
        pages = extract_text_ocr(pdf_path)

    return pages


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python extract.py <path_to_pdf>")
        sys.exit(1)

    pdf_path = sys.argv[1]
    pages = extract_text_from_pdf(pdf_path)

    print(f"Extracted {len(pages)} pages\n")

    for p in pages[:3]:
        print(f"--- Page {p['page']} ({len(p['text'])} chars) ---")
        print(p["text"][:500])
        print()