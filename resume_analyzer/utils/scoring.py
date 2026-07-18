"""Resume scoring engine: skills / experience / education / projects / ATS."""
from __future__ import annotations

import re
from typing import Dict, List


def _count_matches(text: str, patterns: List[str]) -> int:
    text_l = text.lower()
    return sum(len(re.findall(p, text_l)) for p in patterns)


def score_skills(all_skills: List[str]) -> int:
    """25 pts: 2 pts per unique skill, capped."""
    return min(25, len(set(all_skills)) * 2)


def score_experience(text: str) -> int:
    """25 pts: based on years/roles keywords."""
    years = _count_matches(text, [r"\b\d+\+?\s*(?:years|yrs)\b"])
    roles = _count_matches(text, [r"\bintern\b", r"\bengineer\b", r"\bdeveloper\b",
                                  r"\banalyst\b", r"\bmanager\b", r"\bconsultant\b"])
    return min(25, years * 5 + roles * 3)


def score_education(text: str) -> int:
    """15 pts: presence of degrees."""
    degrees = _count_matches(text, [r"\bbachelor\b", r"\bmaster\b", r"\bphd\b",
                                    r"\bb\.?tech\b", r"\bm\.?tech\b", r"\bb\.?sc\b",
                                    r"\bm\.?sc\b", r"\bmba\b"])
    return min(15, 8 + degrees * 4)


def score_projects(text: str) -> int:
    """20 pts: number of projects mentioned."""
    projects = _count_matches(text, [r"\bproject\b"])
    return min(20, projects * 4)


def score_ats(ats_score: int) -> int:
    """15 pts scaled from ATS %."""
    return round(ats_score * 0.15)


def compute_scores(text: str, all_skills: List[str], ats_score: int) -> Dict[str, int]:
    """Compute all sub-scores + total. Total is out of 100."""
    scores = {
        "Skills": score_skills(all_skills),
        "Experience": score_experience(text),
        "Education": score_education(text),
        "Projects": score_projects(text),
        "ATS": score_ats(ats_score),
    }
    scores["Total"] = sum(scores.values())
    return scores
