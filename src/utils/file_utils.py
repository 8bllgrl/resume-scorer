# src/utils/file_utils.py
import fitz  # PyMuPDF
import os
import re


def extract_text_from_pdf(pdf_path):
    """Extracts raw text from a PDF file."""
    text = ""
    try:
        doc = fitz.open(pdf_path)
        for page in doc:
            text += page.get_text()
        doc.close()
    except Exception as e:
        print(f"[ERROR] Could not read PDF {pdf_path}: {e}")
    return text


def clean_resume_text(text):
    """Removes junk, normalizes whitespace, and drops boilerplate."""
    # Remove 'References available upon request' (case insensitive)
    text = re.sub(r'(?i)references\s+available\s+upon\s+request', '', text)

    # Normalize whitespace (replace multiple spaces/newlines with one)
    text = re.sub(r'\s+', ' ', text).strip()

    return text