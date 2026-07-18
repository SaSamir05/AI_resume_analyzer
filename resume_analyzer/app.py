"""
AI Resume Analyzer — Streamlit app.

Run:
    streamlit run app.py
"""
from __future__ import annotations

import time
from typing import Dict, List

import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from dotenv import load_dotenv

from ai.analyzer import analyze_resume
from utils.ats_checker import check_ats
from utils.parser import extract_personal_info, extract_text
from utils.report_generator import build_report
from utils.scoring import compute_scores
from utils.skill_extractor import (
    ROLE_REQUIREMENTS,
    extract_skills,
    flatten_skills,
    role_gap_analysis,
)

load_dotenv()

# ---------- Page config & theme ----------
st.set_page_config(
    page_title="AI Resume Analyzer",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

CUSTOM_CSS = """
<style>
    .stApp { background: linear-gradient(135deg,#0f172a 0%,#1e293b 100%); color:#e2e8f0; }
    section[data-testid="stSidebar"] { background:#0b1220; }
    h1,h2,h3,h4 { color:#f8fafc !important; }
    .metric-card {
        background:#111a2e; border:1px solid #1e293b; border-radius:14px;
        padding:18px; box-shadow:0 4px 20px rgba(0,0,0,.35);
    }
    .skill-tag {
        display:inline-block; padding:6px 12px; margin:4px;
        border-radius:999px; font-size:13px; font-weight:600;
        background:#1e40af; color:#dbeafe;
    }
    .missing-tag { background:#7f1d1d; color:#fecaca; }
    .found-tag   { background:#065f46; color:#a7f3d0; }
    .stButton>button {
        background:linear-gradient(90deg,#2563eb,#7c3aed);
        color:white; border:none; border-radius:10px; font-weight:600;
    }
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


# ---------- Helpers ----------

CATEGORY_COLORS = {
    "Programming": "#2563eb",
    "AI/ML": "#7c3aed",
    "Web Development": "#0ea5e9",
    "Database": "#f59e0b",
    "Cloud & DevOps": "#10b981",
    "Data": "#ef4444",
}


def render_tags(skills: List[str], css_class: str = "skill-tag", color: str | None = None) -> None:
    style = f'style="background:{color}"' if color else ""
    html = "".join(f'<span class="{css_class}" {style}>{s}</span>' for s in skills)
    st.markdown(html or "<i>None</i>", unsafe_allow_html=True)


def gauge(value: int, title: str) -> go.Figure:
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        title={"text": title, "font": {"color": "#e2e8f0", "size": 18}},
        number={"font": {"color": "#f8fafc", "size": 40}},
        gauge={
            "axis": {"range": [0, 100], "tickcolor": "#64748b"},
            "bar": {"color": "#2563eb"},
            "bgcolor": "#0f172a",
            "steps": [
                {"range": [0, 40], "color": "#7f1d1d"},
                {"range": [40, 70], "color": "#78350f"},
                {"range": [70, 100], "color": "#065f46"},
            ],
        },
    ))
    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", height=280, margin=dict(l=10, r=10, t=40, b=10))
    return fig


# ---------- Sidebar ----------

with st.sidebar:
    st.title("🧠 Resume Analyzer")
    st.caption("AI-powered • ATS-aware")

    page = st.radio("Navigation", ["📤 Upload & Analyze", "ℹ️ About"], label_visibility="collapsed")
    st.divider()
    target_role = st.selectbox(
        "🎯 Target Role", ["-- None --"] + list(ROLE_REQUIREMENTS.keys())
    )
    st.divider()
    st.markdown("**Tips**\n- Use PDF/DOCX\n- Keep to 1-2 pages\n- Add measurable achievements")


# ---------- About page ----------

if page == "ℹ️ About":
    st.header("About")
    st.write("""
This AI Resume Analyzer scans your resume, extracts your skills and personal info,
scores your resume against ATS best practices, compares it against a target role,
and uses OpenAI to provide detailed improvement recommendations.

**Stack:** Python · Streamlit · OpenAI · pdfplumber · python-docx · Plotly · fpdf2
""")
    st.stop()


# ---------- Upload & Analyze ----------

st.title("AI Resume Analyzer")
st.write("Upload a resume to get instant ATS scoring, skill gap analysis, and AI feedback.")

uploaded = st.file_uploader("📄 Upload Resume (PDF or DOCX)", type=["pdf", "docx"])
if not uploaded:
    st.info("Awaiting resume upload…")
    st.stop()

# --- Parse ---
with st.spinner("Extracting text…"):
    try:
        raw_text = extract_text(uploaded.name, uploaded.read())
    except Exception as e:  # noqa: BLE001
        st.error(f"Failed to parse file: {e}")
        st.stop()

if not raw_text.strip():
    st.error("No text could be extracted. The file may be an image-based PDF.")
    st.stop()

personal = extract_personal_info(raw_text)
skills_by_cat = extract_skills(raw_text)
all_skills = flatten_skills(skills_by_cat)
ats = check_ats(raw_text, personal)
scores = compute_scores(raw_text, all_skills, ats["score"])

selected_role = None if target_role.startswith("--") else target_role
gap = role_gap_analysis(all_skills, selected_role) if selected_role else None

# ---------- Top metrics ----------
c1, c2, c3, c4 = st.columns(4)
c1.metric("Overall Score", f"{scores['Total']}/100")
c2.metric("ATS Score", f"{ats['score']}%")
c3.metric("Skills Detected", len(all_skills))
c4.metric("Word Count", ats["word_count"])

st.divider()

# ---------- Personal info ----------
st.subheader("👤 Personal Information")
pcols = st.columns(5)
for col, (label, key) in zip(
    pcols, [("Name", "name"), ("Email", "email"), ("Phone", "phone"),
            ("LinkedIn", "linkedin"), ("GitHub", "github")]
):
    col.markdown(f"**{label}**  \n{personal.get(key) or '—'}")

# ---------- Extracted preview ----------
with st.expander("📖 Extracted Text Preview"):
    st.text(raw_text[:3000] + ("…" if len(raw_text) > 3000 else ""))

# ---------- Skills ----------
st.subheader("🛠️ Extracted Skills")
if not skills_by_cat:
    st.warning("No known skills detected. Consider adding a dedicated Skills section.")
for cat, items in skills_by_cat.items():
    st.markdown(f"**{cat}**")
    render_tags(items, color=CATEGORY_COLORS.get(cat))

# ---------- Scores ----------
st.subheader("📊 Resume Score Breakdown")
gcols = st.columns(3)
gcols[0].plotly_chart(gauge(scores["Total"], "Overall (out of 100)"), use_container_width=True)
gcols[1].plotly_chart(gauge(ats["score"], "ATS Compatibility"), use_container_width=True)

bar_df = pd.DataFrame(
    {"Category": ["Skills", "Experience", "Education", "Projects", "ATS"],
     "Score":    [scores["Skills"], scores["Experience"], scores["Education"],
                  scores["Projects"], scores["ATS"]],
     "Max":      [25, 25, 15, 20, 15]}
)
bar_fig = go.Figure()
bar_fig.add_bar(x=bar_df["Category"], y=bar_df["Max"], name="Max", marker_color="#1e293b")
bar_fig.add_bar(x=bar_df["Category"], y=bar_df["Score"], name="Score", marker_color="#7c3aed")
bar_fig.update_layout(
    barmode="overlay", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    font_color="#e2e8f0", height=320, margin=dict(l=10, r=10, t=30, b=10),
)
gcols[2].plotly_chart(bar_fig, use_container_width=True)

# ---------- Gap analysis ----------
if gap:
    st.subheader(f"🎯 Skill Gap — {selected_role}")
    gc1, gc2, gc3 = st.columns(3)
    with gc1:
        st.markdown("**✅ Found Skills**")
        render_tags(gap["found"], css_class="skill-tag found-tag")
    with gc2:
        st.markdown("**❌ Missing Skills**")
        render_tags(gap["missing"], css_class="skill-tag missing-tag")
    with gc3:
        st.markdown("**📚 Recommended to Learn**")
        render_tags(gap["missing"][:5], css_class="skill-tag missing-tag")

# ---------- ATS ----------
st.subheader("🧾 ATS Analysis")
ac1, ac2 = st.columns([1, 2])
ac1.metric("Compatibility", f"{ats['score']}%")
ac1.metric("Keyword Density", f"{ats['keyword_density']}%")
with ac2:
    check_df = pd.DataFrame(
        [{"Check": k, "Status": "✅ Pass" if v else "❌ Fail"} for k, v in ats["checks"].items()]
    )
    st.dataframe(check_df, hide_index=True, use_container_width=True)

# ---------- AI Feedback ----------
st.subheader("🤖 AI Resume Review")
if st.button("Generate AI Feedback", type="primary"):
    with st.spinner("Consulting AI reviewer…"):
        result = analyze_resume(raw_text, all_skills, selected_role)
    if result.get("error"):
        st.warning(result["error"])
    st.session_state["ai_feedback"] = result["feedback"]

ai_feedback: str = st.session_state.get("ai_feedback", "")
if ai_feedback:
    st.markdown(ai_feedback)

# ---------- Download report ----------
st.divider()
st.subheader("📥 Download Report")
if st.button("Generate PDF Report"):
    with st.spinner("Building PDF…"):
        pdf_bytes = build_report(personal, scores, skills_by_cat, gap, ats, ai_feedback)
        time.sleep(0.3)
    st.download_button(
        "⬇️ Download PDF",
        data=pdf_bytes,
        file_name="resume_analysis_report.pdf",
        mime="application/pdf",
    )
