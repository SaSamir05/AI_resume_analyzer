"""Generate a downloadable PDF report of the resume analysis."""
from __future__ import annotations

from io import BytesIO
from typing import Dict, List

from fpdf import FPDF


class ReportPDF(FPDF):
    def header(self) -> None:
        self.set_font("Helvetica", "B", 16)
        self.set_text_color(30, 30, 30)
        self.cell(0, 10, "AI Resume Analyzer Report", ln=True, align="C")
        self.ln(2)

    def section(self, title: str) -> None:
        self.set_font("Helvetica", "B", 13)
        self.set_text_color(20, 90, 200)
        self.cell(0, 8, title, ln=True)
        self.set_draw_color(20, 90, 200)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(3)
        self.set_text_color(30, 30, 30)

    def body(self, text: str) -> None:
        self.set_font("Helvetica", "", 11)
        # fpdf2 handles latin-1 by default; strip non-encodable chars safely.
        safe = text.encode("latin-1", "replace").decode("latin-1")
        self.multi_cell(0, 6, safe)
        self.ln(2)


def build_report(
    personal: Dict,
    scores: Dict[str, int],
    skills: Dict[str, List[str]],
    gap: Dict[str, List[str]] | None,
    ats: Dict,
    ai_feedback: str,
) -> bytes:
    pdf = ReportPDF()
    pdf.add_page()

    # Personal
    pdf.section("Personal Information")
    for k, v in personal.items():
        pdf.body(f"{k.title()}: {v or '-'}")

    # Scores
    pdf.section("Resume Score")
    for k, v in scores.items():
        pdf.body(f"{k}: {v}")

    # Skills
    pdf.section("Extracted Skills")
    if not skills:
        pdf.body("No skills detected.")
    for cat, items in skills.items():
        pdf.body(f"{cat}: {', '.join(items)}")

    # Gap analysis
    if gap:
        pdf.section("Target Role Gap Analysis")
        pdf.body(f"Required: {', '.join(gap['required']) or '-'}")
        pdf.body(f"Found: {', '.join(gap['found']) or '-'}")
        pdf.body(f"Missing: {', '.join(gap['missing']) or '-'}")

    # ATS
    pdf.section("ATS Analysis")
    pdf.body(f"ATS Compatibility: {ats['score']}%")
    pdf.body(f"Keyword Density: {ats['keyword_density']}%")
    pdf.body(f"Word Count: {ats['word_count']}")
    for check, ok in ats["checks"].items():
        pdf.body(f"  - {check}: {'OK' if ok else 'MISSING'}")

    # AI feedback
    pdf.section("AI Feedback")
    pdf.body(ai_feedback or "No AI feedback available.")

    buf = BytesIO()
    pdf.output(buf)
    return buf.getvalue()
