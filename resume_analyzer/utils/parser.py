"""Resume text extraction (PDF / DOCX) + personal info parsing."""
from __future__ import annotations

import io
import re
from typing import Dict, Optional

import pdfplumber
from docx import Document


# ---------- Text extraction ----------

def extract_text_from_pdf(file_bytes: bytes) -> str:
    """Extract text from a PDF byte stream using pdfplumber."""
    text_parts: list[str] = []
    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text() or ""
            text_parts.append(page_text)
    return "\n".join(text_parts).strip()


def extract_text_from_docx(file_bytes: bytes) -> str:
    """Extract text from a DOCX byte stream using python-docx."""
    doc = Document(io.BytesIO(file_bytes))
    return "\n".join(p.text for p in doc.paragraphs).strip()


def extract_text(filename: str, file_bytes: bytes) -> str:
    """Dispatch to the correct extractor based on file extension."""
    name = filename.lower()
    if name.endswith(".pdf"):
        return extract_text_from_pdf(file_bytes)
    if name.endswith(".docx"):
        return extract_text_from_docx(file_bytes)
    raise ValueError("Unsupported file type. Please upload a PDF or DOCX file.")


# ---------- Personal info regex ----------

EMAIL_RE = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")
PHONE_RE = re.compile(r"(\+?\d[\d\s\-\(\)]{7,}\d)")
LINKEDIN_RE = re.compile(r"(https?://)?(www\.)?linkedin\.com/[A-Za-z0-9_\-/]+", re.I)
GITHUB_RE = re.compile(r"(https?://)?(www\.)?github\.com/[A-Za-z0-9_\-/]+", re.I)


def _first(pattern: re.Pattern, text: str) -> Optional[str]:
    m = pattern.search(text)
    return m.group(0) if m else None


def guess_name(text: str) -> Optional[str]:
    """Simple heuristic: first non-empty line with 2-4 capitalized words."""
    for line in text.splitlines():
        line = line.strip()
        if not line or "@" in line or any(ch.isdigit() for ch in line):
            continue
        words = line.split()
        if 2 <= len(words) <= 4 and sum(w[0].isupper() for w in words if w) >= 2:
            return line
    return None


def extract_personal_info(text: str) -> Dict[str, Optional[str]]:
    """Extract name, email, phone, linkedin, github from resume text."""
    return {
        "name": guess_name(text),
        "email": _first(EMAIL_RE, text),
        "phone": _first(PHONE_RE, text),
        "linkedin": _first(LINKEDIN_RE, text),
        "github": _first(GITHUB_RE, text),
    }
