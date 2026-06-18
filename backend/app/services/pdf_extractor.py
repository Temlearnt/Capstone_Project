# backend/app/services/pdf_extractor.py
import fitz  # PyMuPDF
from io import BytesIO
import logging

logger = logging.getLogger(__name__)

def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    """
    Extract text from PDF bytes using PyMuPDF (fitz)
    PyMuPDF lebih cepat 60-70x dibanding pdfplumber/pdfminer
    """
    try:
        # Buka PDF dari bytes
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        text = ""
        
        # Looping setiap halaman
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            text += page.get_text()
        
        doc.close()
        return text.strip() if text else ""
    
    except Exception as e:
        logger.error(f"Error extracting PDF with PyMuPDF: {e}")
        return ""