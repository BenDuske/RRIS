import pdfplumber
import pytesseract
from pdf2image import convert_from_path
from typing import Optional

def extract_text_from_pdf(path: str) -> str:
    """
    Extract text from a PDF file.
    - First attempts direct text extraction (pdfplumber)
    - Falls back to OCR (pytesseract) for scanned PDFs
    """

    # Try text-based extraction first
    try:
        with pdfplumber.open(path) as pdf:
            pages = [page.extract_text() for page in pdf.pages]

            # If any page has text, return combined text
            if any(pages):
                return "\n".join(p for p in pages if p)
    except Exception:
        # pdfplumber failed → fall back to OCR
        pass

    # OCR fallback for scanned PDFs
    return ocr_pdf(path)


def ocr_pdf(path: str) -> str:
    """
    Convert PDF pages to images and run OCR.
    Used when the PDF contains no extractable text.
    """

    try:
        images = convert_from_path(path)
    except Exception as e:
        return f"[OCR ERROR] Could not convert PDF to images: {e}"

    text = ""
    for img in images:
        try:
            text += pytesseract.image_to_string(img)
        except Exception as e:
            text += f"[OCR ERROR] {e}\n"

    return text


def ingest_pdf(path: str) -> Optional[str]:
    """
    Main entry point for PDF ingestion.
    Returns clean text or None if the file cannot be processed.
    """

    try:
        text = extract_text_from_pdf(path)
        if not text or len(text.strip()) == 0:
            return None

        # Clean up whitespace
        cleaned = "\n".join(line.strip() for line in text.split("\n") if line.strip())
        return cleaned

    except Exception as e:
        return f"[INGEST ERROR] {e}
