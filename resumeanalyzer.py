"""
Resume Analyzer — Streamlit App (Port 8502)
Score resumes, find weaknesses, and tailor to job descriptions.
Powered by Google Gemini (new google-genai SDK)
"""

import os
import streamlit as st
from google import genai
from google.genai import errors
from dotenv import load_dotenv
from pypdf import PdfReader
from docx import Document
import tempfile

load_dotenv()

# =========================
# PAGE CONFIG
# =========================

st.set_page_config(
    page_title="Resume Analyzer",
    page_icon="📊",
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

def call_gemini(prompt: str) -> str:
    """Helper function to call Gemini API with error handling."""
    try:
        response = client.models.generate_content(model=MODEL_NAME, contents=prompt)
        return response.text
    except errors.APIError as e:
        if e.code == 429:
            st.error(
                "⚠️ **Gemini API Quota Exceeded (429 Resource Exhausted)**\n\n"
                "You have exceeded your Gemini API free tier rate limit or daily quota.\n\n"
                "**How to resolve this:**\n"
                "- **Wait a bit:** The free tier allows 15 requests per minute. Wait 1-2 minutes and try again.\n"
                "- **Check API Key:** Ensure your API key is correct and has access to Google AI Studio.\n"
                "- **Upgrade Plan:** Consider enabling pay-as-you-go billing in [Google AI Studio](https://aistudio.google.com/) for higher limits.\n\n"
                f"*Error Details: {e.message}*"
            )
        else:
            st.error(f"❌ **Gemini API Error (Status {e.code}):** {e.message}")
        st.stop()
    except Exception as e:
        st.error(f"❌ **Unexpected Error calling Gemini API:** {e}")
        st.stop()

# =========================
# TEXT EXTRACTION
# =========================

def extract_text_from_pdf(uploaded_file) -> str:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(uploaded_file.read())
        tmp_path = tmp.name
    reader = PdfReader(tmp_path)
    text = "\n".join(page.extract_text() or "" for page in reader.pages).strip()
    os.unlink(tmp_path)
    if not text:
        raise ValueError("Could not extract text from PDF. It may be image-based.")
    return text


def extract_text_from_docx(uploaded_file) -> str:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as tmp:
        tmp.write(uploaded_file.read())
        tmp_path = tmp.name
    doc = Document(tmp_path)
    text = "\n".join(para.text for para in doc.paragraphs).strip()
    os.unlink(tmp_path)
    if not text:
        raise ValueError("Could not extract text from DOCX.")
    return text


def extract_text(uploaded_file) -> str:
    name = uploaded_file.name.lower()
    if name.endswith(".pdf"):
        return extract_text_from_pdf(uploaded_file)
    elif name.endswith(".docx"):
        return extract_text_from_docx(uploaded_file)
    elif name.endswith(".txt"):
        return uploaded_file.read().decode("utf-8")
    else:
        raise ValueError(f"Unsupported format: {name}. Use PDF, DOCX, or TXT.")

# =========================
# HEADER
# =========================

st.title("📊 AI Resume Analyzer")
st.caption("Upload your resume for AI-powered scoring, analysis & job-tailoring")

# =========================
# SIDEBAR
# =========================

with st.sidebar:
    st.header("📄 Upload Resume")
    uploaded_resume = st.file_uploader(
        "Upload your resume (PDF, DOCX, or TXT)",
        type=["pdf", "docx", "txt"],
        key="resume_upload"
    )

    st.divider()
    mode = st.radio(
        "Analysis Mode",
        ["📊 Score & Analyze", "🎯 Tailor to Job Description"],
        index=0
    )

# =========================
# MAIN CONTENT
# =========================

if uploaded_resume:
    try:
        resume_text = extract_text(uploaded_resume)
        st.success(f"✅ Extracted {len(resume_text):,} characters from **{uploaded_resume.name}**")
    except Exception as e:
        st.error(f"❌ {e}")
        st.stop()

    # --- Score & Analyze Mode ---
    if mode == "📊 Score & Analyze":
        if st.button("🚀 Analyze Resume", type="primary"):
            with st.spinner("🤖 Analyzing your resume with Gemini..."):
                prompt = f"""You are an expert career coach and professional resume reviewer.

Analyze the following resume and provide:

1. **Overall Score**: A score out of 100 with a brief justification.
2. **Section-by-Section Breakdown** (score each out of 10):
   - Contact Information & Header
   - Professional Summary / Objective
   - Work Experience
   - Education
   - Skills
   - Formatting & Readability
3. **Top 5 Strengths**: What the resume does well.
4. **Top 5 Weaknesses**: What needs improvement.
5. **Actionable Suggestions**: Specific, concrete changes the candidate should make.

Be honest, constructive, and specific.

--- RESUME ---
{resume_text}
---"""
                response_text = call_gemini(prompt)
                st.markdown("---")
                st.subheader("📊 Analysis Results")
                st.markdown(response_text)

    # --- Tailor to Job Description Mode ---
    elif mode == "🎯 Tailor to Job Description":
        job_description = st.text_area(
            "📋 Paste the Job Description",
            height=250,
            placeholder="Paste the full job description here..."
        )

        if st.button("🎯 Tailor Resume", type="primary"):
            if not job_description or len(job_description) < 20:
                st.warning("⚠️ Please paste a complete job description.")
            else:
                with st.spinner("🤖 Tailoring your resume with Gemini..."):
                    prompt = f"""You are an expert career coach specializing in resume optimization.

Given the resume and job description below, provide:

1. **Match Score**: Percentage (0-100%) of how well the resume matches.
2. **Keyword Gap Analysis**: Important keywords missing from the resume.
3. **Experience Alignment**: How well experience maps to job requirements.
4. **Tailored Suggestions**: Specific rewrites with *before → after* examples.
5. **Rewritten Professional Summary**: A new summary tailored to this role.

--- RESUME ---
{resume_text}
---

--- JOB DESCRIPTION ---
{job_description}
---"""
                    response_text = call_gemini(prompt)
                    st.markdown("---")
                    st.subheader("🎯 Tailoring Results")
                    st.markdown(response_text)
else:
    st.info("👈 Upload a resume from the sidebar to get started.")
