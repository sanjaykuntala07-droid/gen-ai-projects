"""
AI Chatbot — Streamlit App (Port 8501)
Powered by Google Gemini (new google-genai SDK)
"""

import os
import streamlit as st
from google import genai
from dotenv import load_dotenv

load_dotenv()

# =========================
# PAGE CONFIG
# =========================

st.set_page_config(
    page_title="AI Chatbot",
    page_icon="🤖",
    layout="centered"
)

# =========================
# GEMINI SETUP
# =========================

API_KEY = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")

if not API_KEY:
    st.error("⚠️ GEMINI_API_KEY not found. Add it to your `.env` file.")
    st.stop()

client = genai.Client(api_key=API_KEY)

# =========================
# MODEL
# =========================

MODEL_NAME = "gemini-2.0-flash"

# =========================
# SESSION MEMORY
# =========================

if "messages" not in st.session_state:
    st.session_state.messages = []

# =========================
# HEADER
# =========================

st.title("🤖 Gemini AI Chatbot")
st.caption("Powered by Google Gemini — with conversation memory")

# =========================
# SIDEBAR
# =========================

with st.sidebar:
    st.header("⚙️ Settings")

    temperature = st.slider("Temperature", 0.0, 1.0, 0.7, 0.1)

    system_prompt = st.text_area(
        "System Prompt",
        value="You are a helpful AI assistant."
    )

    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = []
        st.rerun()

# =========================
# SHOW CHAT HISTORY
# =========================

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# =========================
# CHAT INPUT
# =========================

user_prompt = st.chat_input("Ask anything...")

if user_prompt:
    st.session_state.messages.append({"role": "user", "content": user_prompt})

    with st.chat_message("user"):
        st.markdown(user_prompt)

    # Build conversation context
    conversation = f"System: {system_prompt}\n\n"
    for m in st.session_state.messages:
        conversation += f"{m['role']}: {m['content']}\n"

    with st.chat_message("assistant"):
        placeholder = st.empty()

        try:
            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=conversation,
                config={
                    "temperature": temperature,
                },
            )
            answer = response.text
            placeholder.markdown(answer)

            st.session_state.messages.append(
                {"role": "assistant", "content": answer}
            )

        except Exception as e:
            st.error(f"🤖 **Error:** {e}")
