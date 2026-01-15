# src/utils/file_utils.py
import fitz  # PyMuPDF
import re

def extract_text_from_pdf(pdf_path):
    text = ""
    try:
        doc = fitz.open(pdf_path)
        for page in doc:
            text += page.get_text()
        doc.close()
    except Exception as e:
        print(f"[ERROR] PDF Read failed: {e}")
    return text

def clean_resume_text(text):
    # Remove boilerplate
    text = re.sub(r'(?i)references\s+available\s+upon\s+request', '', text)
    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def get_bullet_points(text):
    """Splits text into a list of potential bullet points/sentences."""
    # Split by common bullet characters, newlines, or sentence endings
    segments = re.split(r'[\n•·*]|\. ', text)
    return [s.strip() for s in segments if len(s.strip()) > 15]


def structural_split(text):
    """
    Replaces Markdown-style headers and list markers with newlines
    to prevent 'one long string' issues.
    """
    # 1. Replace headers (###, ##, #) with a newline
    # We look for # at the start of a line or after existing whitespace
    text = re.sub(r'#+\s*', '\n', text)

    # 2. Replace bullet points (-) with a newline
    text = re.sub(r'\s*-\s+', '\n', text)

    # 3. Clean up multiple consecutive newlines
    text = re.sub(r'\n+', '\n', text).strip()

    return text