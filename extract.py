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
    """Fallback: convert pages to images and OCR them with Tesseract.
    Also captures Tesseract's own confidence score per page."""
    images = convert_from_path(pdf_path)
    pages = []
    for page_num, image in enumerate(images, start=1):
        text = pytesseract.image_to_string(image).strip()

        data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
        confidences = [int(c) for c in data["conf"] if c != "-1"]
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0

        pages.append({"page": page_num, "text": text, "ocr_confidence": avg_confidence})
    return pages


def is_extraction_poor(pages: list[dict]) -> bool:
    total_chars = sum(len(p["text"]) for p in pages)
    avg_chars_per_page = total_chars / len(pages) if pages else 0
    return avg_chars_per_page < 50


def extract_text_from_pdf(pdf_path: str) -> dict:
    """
    Tries native text extraction first. Falls back to OCR if the result
    looks poor. Returns pages + metadata about extraction method/confidence.
    """
    pages = extract_text_native(pdf_path)
    method = "native"
    low_confidence = False

    if is_extraction_poor(pages):
        pages = extract_text_ocr(pdf_path)
        method = "ocr"

        confidences = [p.get("ocr_confidence", 0) for p in pages]
        avg_conf = sum(confidences) / len(confidences) if confidences else 0
        low_confidence = avg_conf < 60

    return {
        "pages": pages,
        "method": method,
        "low_confidence": low_confidence
    }


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python extract.py <path_to_pdf>")
        sys.exit(1)

    pdf_path = sys.argv[1]
    result = extract_text_from_pdf(pdf_path)

    print(f"Method: {result['method']}, Low confidence: {result['low_confidence']}")
    print(f"Extracted {len(result['pages'])} pages\n")

    for p in result["pages"][:3]:
        print(f"--- Page {p['page']} ({len(p['text'])} chars) ---")
        print(p["text"][:500])
        print()