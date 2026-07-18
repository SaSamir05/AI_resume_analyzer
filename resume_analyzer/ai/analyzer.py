"""OpenAI-powered resume review + career recommendation engine."""
from __future__ import annotations

import os
from typing import Dict, List, Optional

from dotenv import load_dotenv

load_dotenv()

_OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")


def _client():
    """Lazily construct the OpenAI client so the app runs even without a key."""
    from openai import OpenAI  # imported lazily to avoid hard dep at import
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key or api_key.startswith("sk-your"):
        return None
    return OpenAI(api_key=api_key)


SYSTEM_PROMPT = (
    "You are a senior technical recruiter and career coach. "
    "Analyse the given resume and produce concise, actionable, structured feedback."
)


def _prompt(resume_text: str, target_role: Optional[str], skills: List[str]) -> str:
    role_line = f"Target role: {target_role}\n" if target_role else ""
    return f"""{role_line}Detected skills: {', '.join(skills) or 'none'}

RESUME:
\"\"\"
{resume_text[:6000]}
\"\"\"

Produce the following sections using markdown headings:
## Strengths
## Weaknesses
## Missing Sections
## Formatting Issues
## ATS Improvements
## Keyword Recommendations
## Resume Summary Suggestion
## Suitable Job Roles
## Learning Roadmap (courses & certifications)
"""


def analyze_resume(
    resume_text: str,
    skills: List[str],
    target_role: Optional[str] = None,
) -> Dict[str, str]:
    """Return {'feedback': str, 'error': Optional[str]}."""
    client = _client()
    if client is None:
        return {
            "feedback": _offline_feedback(skills, target_role),
            "error": "OPENAI_API_KEY not configured — showing offline heuristic feedback.",
        }

    try:
        resp = client.chat.completions.create(
            model=_OPENAI_MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": _prompt(resume_text, target_role, skills)},
            ],
            temperature=0.4,
        )
        return {"feedback": resp.choices[0].message.content or "", "error": None}
    except Exception as e:  # noqa: BLE001
        return {
            "feedback": _offline_feedback(skills, target_role),
            "error": f"OpenAI call failed: {e}",
        }


def _offline_feedback(skills: List[str], target_role: Optional[str]) -> str:
    """Fallback rule-based feedback when no API key is configured."""
    role = target_role or "your target role"
    return f"""## Strengths
- Resume includes {len(skills)} recognisable technical skills.

## Weaknesses
- AI-generated deep review unavailable (add OPENAI_API_KEY to .env).

## Missing Sections
- Ensure Experience, Projects, Education and Skills sections are clearly labelled.

## Formatting Issues
- Prefer single-column layout, standard fonts, avoid tables/images for ATS.

## ATS Improvements
- Include role-specific keywords for {role}.
- Add measurable results (numbers, %, impact).

## Keyword Recommendations
- Mirror keywords from the {role} job description.

## Resume Summary Suggestion
- 3-line summary highlighting years of experience, core stack, and top achievement.

## Suitable Job Roles
- Roles aligned with your detected skills.

## Learning Roadmap
- Follow structured courses on Coursera / Udemy for gaps identified above.
"""
