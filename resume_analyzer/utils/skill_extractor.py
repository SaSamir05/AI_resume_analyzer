"""Skill extraction with categorized skill dictionary + target-role gap analysis."""
from __future__ import annotations

import re
from typing import Dict, List

SKILL_CATEGORIES: Dict[str, List[str]] = {
    "Programming": ["Python", "Java", "JavaScript", "TypeScript", "C", "C++", "C#", "Go", "Rust", "Ruby", "PHP"],
    "AI/ML": ["OpenAI API", "Machine Learning", "Deep Learning", "TensorFlow", "PyTorch",
              "Scikit-learn", "NLP", "Computer Vision", "LangChain", "Hugging Face"],
    "Web Development": ["HTML", "CSS", "React", "Next.js", "Vue", "Angular", "Node.js",
                        "Express", "Django", "Flask", "FastAPI", "Tailwind"],
    "Database": ["MySQL", "PostgreSQL", "MongoDB", "SQLite", "Redis", "Oracle", "Firebase"],
    "Cloud & DevOps": ["AWS", "Azure", "GCP", "Docker", "Kubernetes", "Git", "GitHub",
                       "GitLab", "CI/CD", "Jenkins", "Terraform", "Linux"],
    "Data": ["Pandas", "NumPy", "Matplotlib", "Plotly", "Power BI", "Tableau", "Excel", "Spark"],
}

# Skills required for common target roles.
ROLE_REQUIREMENTS: Dict[str, List[str]] = {
    "Python Developer": ["Python", "Django", "Flask", "FastAPI", "PostgreSQL", "Git", "Docker", "AWS"],
    "AI Engineer": ["Python", "Machine Learning", "Deep Learning", "TensorFlow", "PyTorch",
                    "OpenAI API", "LangChain", "NLP", "AWS", "Docker"],
    "Data Scientist": ["Python", "Pandas", "NumPy", "Machine Learning", "Deep Learning",
                       "SQL", "Tableau", "Statistics", "Scikit-learn"],
    "Full Stack Developer": ["JavaScript", "TypeScript", "React", "Node.js", "Express",
                             "MongoDB", "PostgreSQL", "Docker", "Git", "AWS"],
    "Cyber Security Analyst": ["Linux", "Python", "Networking", "SIEM", "Wireshark",
                               "Penetration Testing", "Cryptography", "Firewalls"],
    "Frontend Developer": ["HTML", "CSS", "JavaScript", "TypeScript", "React", "Next.js", "Tailwind", "Git"],
    "Backend Developer": ["Python", "Node.js", "PostgreSQL", "MongoDB", "Docker", "AWS", "Git", "REST APIs"],
    "DevOps Engineer": ["Linux", "Docker", "Kubernetes", "AWS", "Terraform", "CI/CD", "Jenkins", "Git"],
}


def _contains_skill(text_lower: str, skill: str) -> bool:
    """Check if skill appears in text as a whole-word / phrase match."""
    pattern = r"(?<![A-Za-z0-9+#])" + re.escape(skill.lower()) + r"(?![A-Za-z0-9+#])"
    return re.search(pattern, text_lower) is not None


def extract_skills(text: str) -> Dict[str, List[str]]:
    """Return a dict of {category: [found skills]} from resume text."""
    text_lower = text.lower()
    found: Dict[str, List[str]] = {}
    for category, skills in SKILL_CATEGORIES.items():
        matched = [s for s in skills if _contains_skill(text_lower, s)]
        if matched:
            found[category] = matched
    return found


def flatten_skills(found: Dict[str, List[str]]) -> List[str]:
    """Flatten categorized skills into a single list."""
    return [s for skills in found.values() for s in skills]


def role_gap_analysis(resume_skills: List[str], target_role: str) -> Dict[str, List[str]]:
    """Compare resume skills vs target role requirements."""
    required = ROLE_REQUIREMENTS.get(target_role, [])
    resume_lower = {s.lower() for s in resume_skills}
    found = [s for s in required if s.lower() in resume_lower]
    missing = [s for s in required if s.lower() not in resume_lower]
    return {"required": required, "found": found, "missing": missing}
