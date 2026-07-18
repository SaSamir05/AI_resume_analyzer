"""ATS (Applicant Tracking System) compatibility checker."""
from __future__ import annotations

import re
from typing import Dict

SECTION_KEYWORDS = {
    "experience": ["experience", "work history", "employment"],
    "education": ["education", "academic"],
    "projects": ["projects", "personal projects"],
    "skills": ["skills", "technical skills"],
    "certifications": ["certifications", "certificate"],
}


def _has_section(text_lower: str, keys: list[str]) -> bool:
    return any(re.search(rf"\b{k}\b", text_lower) for k in keys)


def check_ats(text: str, personal_info: dict) -> Dict:
    """Score resume for ATS friendliness (0-100) + itemized checks."""
    text_lower = text.lower()

    checks = {
        "Has Email": bool(personal_info.get("email")),
        "Has Phone": bool(personal_info.get("phone")),
        "Has LinkedIn": bool(personal_info.get("linkedin")),
        "Experience Section": _has_section(text_lower, SECTION_KEYWORDS["experience"]),
        "Education Section": _has_section(text_lower, SECTION_KEYWORDS["education"]),
        "Projects Section": _has_section(text_lower, SECTION_KEYWORDS["projects"]),
        "Skills Section": _has_section(text_lower, SECTION_KEYWORDS["skills"]),
        "Reasonable Length": 300 <= len(text.split()) <= 1200,
        "No Tables/Images Hints": "image" not in text_lower and "table" not in text_lower,
    }

    passed = sum(1 for v in checks.values() if v)
    score = round(passed / len(checks) * 100)

    # Keyword density (unique words / total words).
    words = re.findall(r"[A-Za-z]{3,}", text_lower)
    unique_ratio = len(set(words)) / max(len(words), 1)
    keyword_density = round(unique_ratio * 100, 2)

    return {
        "score": score,
        "checks": checks,
        "keyword_density": keyword_density,
        "word_count": len(words),
    }
