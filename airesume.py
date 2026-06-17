"""
AI Resume Builder — Streamlit App (Port 8503)
Improve existing resumes or generate new ones from scratch.
Powered by Google Gemini (new google-genai SDK)
"""

import os
import streamlit as st
from google import genai
from dotenv import load_dotenv
from pypdf import PdfReader
from docx import Document
import tempfile

load_dotenv()

# =========================
# PAGE CONFIG
# =========================

st.set_page_config(
    page_title="AI Resume Builder",
    page_icon="✨",
    layout="wide"
)

# =========================
# GEMINI SETUP
# =========================

API_KEY = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")

if not API_KEY:
    st.error("⚠️ GEMINI_API_KEY not found. Add it to your `.env` file.")
    st.stop()

client = genai.Client(api_key=API_KEY)
MODEL_NAME = "gemini-2.0-flash"

# =========================
# TEXT EXTRACTION
# =========================

def extract_text(uploaded_file) -> str:
    name = uploaded_file.name.lower()
    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(name)[1]) as tmp:
        tmp.write(uploaded_file.read())
        tmp_path = tmp.name

    try:
        if name.endswith(".pdf"):
            reader = PdfReader(tmp_path)
            return "\n".join(p.extract_text() or "" for p in reader.pages).strip()
        elif name.endswith(".docx"):
            doc = Document(tmp_path)
            return "\n".join(p.text for p in doc.paragraphs).strip()
        elif name.endswith(".txt"):
            with open(tmp_path, "r", encoding="utf-8") as f:
                return f.read()
        else:
            raise ValueError(f"Unsupported: {name}")
    finally:
        os.unlink(tmp_path)

# =========================
# HEADER
# =========================

st.title("✨ AI Resume Builder")
st.caption("Improve your existing resume or generate one from scratch")

# =========================
# TABS
# =========================

tab1, tab2 = st.tabs(["📝 Improve Existing Resume", "🆕 Generate From Scratch"])

# --- Tab 1: Improve ---
with tab1:
    st.subheader("Upload your resume to get an AI-improved version")

    uploaded = st.file_uploader(
        "Upload resume (PDF, DOCX, or TXT)",
        type=["pdf", "docx", "txt"],
        key="improve_upload"
    )

    if uploaded:
        try:
            resume_text = extract_text(uploaded)
            st.success(f"✅ Extracted {len(resume_text):,} characters")
        except Exception as e:
            st.error(f"❌ {e}")
            st.stop()

        if st.button("✨ Improve Resume", type="primary", key="improve_btn"):
            with st.spinner("🤖 Rewriting your resume with Gemini..."):
                prompt = f"""You are a world-class professional resume writer.

Rewrite and significantly improve the following resume while keeping all factual
information accurate. Apply these best practices:

1. **Strong Action Verbs**: Start every bullet with a powerful action verb.
2. **Quantify Achievements**: Add metrics wherever possible.
3. **Concise & Impactful**: Every word should earn its place.
4. **ATS-Friendly Format**: Use standard section headings.
5. **Modern Structure**: Clean, professional layout.
6. **Compelling Summary**: Write a strong professional summary.

Return ONLY the improved resume text — no commentary.

--- ORIGINAL RESUME ---
{resume_text}
---"""
                response = client.models.generate_content(model=MODEL_NAME, contents=prompt)

                st.markdown("---")
                st.subheader("📝 Your Improved Resume")
                st.markdown(response.text)

                st.download_button(
                    "📥 Download as Text",
                    data=response.text,
                    file_name="improved_resume.txt",
                    mime="text/plain"
                )
    else:
        st.info("👆 Upload your current resume to get started.")

# --- Tab 2: Generate ---
with tab2:
    st.subheader("Fill in your details and AI will create a polished resume")

    col1, col2 = st.columns(2)

    with col1:
        name = st.text_input("👤 Full Name", placeholder="John Doe")
        email = st.text_input("📧 Email", placeholder="john@example.com")
        phone = st.text_input("📱 Phone", placeholder="+1 (555) 123-4567")

    with col2:
        education = st.text_area(
            "🎓 Education",
            placeholder="e.g., B.S. Computer Science, MIT, 2022",
            height=100
        )
        skills = st.text_area(
            "🛠️ Skills",
            placeholder="e.g., Python, JavaScript, Machine Learning, AWS...",
            height=100
        )

    summary = st.text_area(
        "📝 Professional Summary",
        placeholder="A few sentences about yourself and your career goals...",
        height=100
    )

    experience = st.text_area(
        "💼 Work Experience",
        placeholder="Company, role, dates, key achievements (one per line or separated by semicolons)...",
        height=200
    )

    if st.button("🆕 Generate Resume", type="primary", key="generate_btn"):
        if not name or not experience:
            st.warning("⚠️ Please fill in at least your name and work experience.")
        else:
            with st.spinner("🤖 Generating your resume with Gemini..."):
                prompt = f"""You are a world-class professional resume writer.

Using ONLY the information below, create a polished, ATS-friendly resume.
Use strong action verbs, quantify achievements, and structure with clear headings.
Return ONLY the resume text — no commentary.

**Name:** {name}
**Email:** {email}
**Phone:** {phone}
**Summary:** {summary}
**Experience:** {experience}
**Education:** {education}
**Skills:** {skills}
"""
                response = client.models.generate_content(model=MODEL_NAME, contents=prompt)

                st.markdown("---")
                st.subheader("🆕 Your Generated Resume")
                st.markdown(response.text)

                st.download_button(
                    "📥 Download as Text",
                    data=response.text,
                    file_name="generated_resume.txt",
                    mime="text/plain"
                )