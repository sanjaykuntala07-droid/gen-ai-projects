# 🤖 GEN AI Projects — Sanjay Kumar

A collection of AI-powered Python & Streamlit applications built using **Google Gemini**, **LangGraph**, **FAISS**, and other cutting-edge AI tools.

---

## 📦 Projects

### 1. 🤖 Multi-Agent AI Developer Crew (`multiagent.py`)
A collaborative AI system where multiple specialized agents work together to build software:
- **Research Agent** — Analyzes requirements and defines architecture
- **Coder Agent** — Writes clean, optimized Python code
- **Reviewer Agent** — Audits code for bugs and quality

**Tech:** Streamlit, Google Gemini (gemini-2.5-flash), google-genai SDK

---

### 2. ✨ AI Resume Builder (`airesume.py`)
Improve your existing resume or generate a brand-new one from scratch:
- Upload PDF/DOCX/TXT resume → Get an AI-improved version
- Fill in your details → Generate a professional, ATS-friendly resume
- Download results as text

**Tech:** Streamlit, Google Gemini, pypdf, python-docx

---

### 3. 💬 Gemini AI Chatbot (`app.py`)
A conversational AI chatbot with persistent memory:
- Multi-turn conversation with memory
- Configurable system prompt and temperature
- Clean chat UI with message history

**Tech:** Streamlit, Google Gemini (gemini-2.0-flash)

---

### 4. 🔮 Divine AI 2.0 (`divine2.0.py`)
A spiritual AI assistant combining astrology, numerology, and ancient wisdom:
- **Zodiac & Numerology Analysis** — Personality, career, relationship insights
- **Bhagavad Gita RAG** — Ask questions, get wisdom from the Gita
- **Palm Reading** — Upload a hand photo for AI-powered palmistry
- **Festival Mantras** — Get relevant mantras for the current month
- **PDF Reports** — Download your personalized astrology report
- **Voice I/O** — Speak your questions and hear the answers

**Tech:** Streamlit, Google Gemini, LangGraph, FAISS, SentenceTransformers, MediaPipe, pyttsx3, SpeechRecognition, ReportLab

---

## 🚀 Getting Started

### Prerequisites
- Python 3.10+
- A Google Gemini API key → [Get one here](https://aistudio.google.com/app/apikey)

### Installation

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/YOUR_REPO.git
cd YOUR_REPO

# Create and activate virtual environment
python -m venv venv
venv\Scripts\activate   # Windows

# Install dependencies
pip install streamlit google-genai python-dotenv pypdf python-docx \
            langgraph sentence-transformers faiss-cpu numpy \
            opencv-python mediapipe pyttsx3 SpeechRecognition \
            reportlab pillow
```

### Configuration
Create a `.env` file in the root directory:
```
GEMINI_API_KEY=your_gemini_api_key_here
```

### Running the Apps

```bash
# Multi-Agent Developer Crew
streamlit run multiagent.py

# AI Resume Builder
streamlit run airesume.py

# AI Chatbot
streamlit run app.py

# Divine AI 2.0
streamlit run divine2.0.py
```

---

## 🛠️ Tech Stack

| Tool | Purpose |
|---|---|
| Streamlit | Web UI framework |
| Google Gemini | AI/LLM backbone |
| LangGraph | Agent workflow orchestration |
| FAISS | Vector similarity search |
| SentenceTransformers | Text embeddings |
| MediaPipe | Hand landmark detection |
| ReportLab | PDF generation |
| SQLite | User data persistence |

---

## ⚠️ Disclaimer
DivineAI features (astrology, numerology, palmistry) are based on traditional belief systems and are intended for entertainment and self-reflection only — not as guaranteed predictions.

---

## 👨‍💻 Author
**Kuntala Sanjay Kumar**  
Built with ❤️ using Google Gemini AI
