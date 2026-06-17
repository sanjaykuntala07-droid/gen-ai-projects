import os
import speech_recognition as sr
import pyttsx3
from pypdf import PdfReader
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import cv2
import mediapipe as mp
from typing import TypedDict
from langgraph.graph import StateGraph
from langgraph.graph import END, START
from PIL import Image
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer
)

from reportlab.lib.styles import getSampleStyleSheet
from datetime import datetime
from dotenv import load_dotenv
import sqlite3
import google.generativeai as genai
import streamlit as st

# ==========================================
# Load Gemini API Key
# ==========================================

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

model = genai.GenerativeModel("gemini-2.5-flash")

engine = pyttsx3.init()
mp_hands = mp.solutions.hands

hands = mp_hands.Hands(
    static_image_mode=True,
    max_num_hands=1
)

mp_draw = mp.solutions.drawing_utils
embedding_model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)
# ======================================
# STATE
# ======================================

class DivineState(TypedDict):

    name: str

    dob: str

    zodiac: str

    life_number: int

    personality: str

    career: str

    relationship: str

    spiritual: str

# ======================================
# MEMORY STORAGE
# ======================================

chat_history = []
# ==========================================
# AGENT 1 : USER AGENT
# ==========================================

def user_agent():

    print("\n===== DivineAI =====\n")

    name = input("Enter your name: ")

    dob = input("Enter Date of Birth (YYYY-MM-DD): ")

    return name, dob


# ==========================================
# AGENT 2 : ZODIAC AGENT
# ==========================================

def zodiac_agent(day, month):

    if (month == 3 and day >= 21) or (month == 4 and day <= 19):
        return "Aries"

    elif (month == 4 and day >= 20) or (month == 5 and day <= 20):
        return "Taurus"

    elif (month == 5 and day >= 21) or (month == 6 and day <= 20):
        return "Gemini"

    elif (month == 6 and day >= 21) or (month == 7 and day <= 22):
        return "Cancer"

    elif (month == 7 and day >= 23) or (month == 8 and day <= 22):
        return "Leo"

    elif (month == 8 and day >= 23) or (month == 9 and day <= 22):
        return "Virgo"

    elif (month == 9 and day >= 23) or (month == 10 and day <= 22):
        return "Libra"

    elif (month == 10 and day >= 23) or (month == 11 and day <= 21):
        return "Scorpio"

    elif (month == 11 and day >= 22) or (month == 12 and day <= 21):
        return "Sagittarius"

    elif (month == 12 and day >= 22) or (month == 1 and day <= 19):
        return "Capricorn"

    elif (month == 1 and day >= 20) or (month == 2 and day <= 18):
        return "Aquarius"

    else:
        return "Pisces"
def zodiac_node(state):

    date_obj = datetime.strptime(
        state["dob"],
        "%Y-%m-%d"
    )

    state["zodiac"] = zodiac_agent(
        date_obj.day,
        date_obj.month
    )

    return state


# ==========================================
# AGENT 3 : NUMEROLOGY AGENT
# ==========================================

def numerology_agent(dob):

    digits = dob.replace("-", "")

    total = sum(int(i) for i in digits)

    while total > 9:
        total = sum(int(i) for i in str(total))

    return total
def numerology_node(state):

    state["life_number"] = numerology_agent(
        state["dob"]
    )

    return state


# ==========================================
# AGENT 4 : PERSONALITY AGENT
# ==========================================

def personality_agent(number):

    data = {

        1: "Leader, creative and confident.",
        2: "Peaceful, caring and emotional.",
        3: "Social, artistic and expressive.",
        4: "Disciplined and hardworking.",
        5: "Adventurous and energetic.",
        6: "Loving and responsible.",
        7: "Spiritual and analytical.",
        8: "Ambitious and powerful.",
        9: "Wise and compassionate."

    }

    return data[number]
def personality_node(state):

    state["personality"] = personality_agent(
        state["life_number"]
    )

    return state

# ==========================================
# AGENT 5 : CAREER AGENT
# ==========================================

def career_agent(number):

    careers = {

        1: "Business and leadership roles.",
        2: "Teaching and counseling.",
        3: "Art, media and communication.",
        4: "Engineering and administration.",
        5: "Marketing and travel industries.",
        6: "Healthcare and service.",
        7: "Research and spiritual studies.",
        8: "Finance and entrepreneurship.",
        9: "Social work and leadership."

    }

    return careers[number]
def career_node(state):

    state["career"] = career_agent(
        state["life_number"]
    )

    return state


# ==========================================
# AGENT 6 : RELATIONSHIP AGENT
# ==========================================

def relationship_agent(number):

    relation = {

        1: "Values freedom and independence.",
        2: "Loving and emotional partner.",
        3: "Friendly and expressive.",
        4: "Loyal and trustworthy.",
        5: "Exciting and adventurous.",
        6: "Family-oriented and caring.",
        7: "Prefers deep connections.",
        8: "Honest and committed.",
        9: "Kind and understanding."

    }

    return relation[number]
def relationship_node(state):

    state["relationship"] = relationship_agent(
        state["life_number"]
    )

    return state  

# ==========================================
# AGENT 7 : SPIRITUAL AGENT
# ==========================================

def spiritual_agent(number):

    guidance = {

        1: "Practice meditation every morning.",
        2: "Spend time in gratitude and prayer.",
        3: "Repeat positive affirmations daily.",
        4: "Read spiritual books regularly.",
        5: "Practice yoga and mindfulness.",
        6: "Help others through service.",
        7: "Study sacred texts and meditate.",
        8: "Maintain discipline and gratitude.",
        9: "Focus on compassion and kindness."

    }

    return guidance[number]

def spiritual_node(state):

    state["spiritual"] = spiritual_agent(
        state["life_number"]
    )

    return state
# ==========================================
# AGENT 8 : GEMINI REPORT AGENT
# ==========================================

def report_agent(name, dob, zodiac,
                 number,
                 personality,
                 career,
                 relation,
                 spiritual):

    prompt = f"""

Name: {name}

Date of Birth: {dob}

Zodiac Sign: {zodiac}

Life Path Number: {number}

Personality: {personality}

Career Advice: {career}

Relationship Advice: {relation}

Spiritual Guidance: {spiritual}

Current Festival : {festival_name}

Suggested Mantra : {mantra}

Write a detailed report containing:

1. Personality
2. Strengths
3. Weaknesses
4. Career guidance
5. Relationships
6. Money
7. Lucky color
8. Lucky number
9. Daily motivation

Use simple English.

Mention that astrology and numerology are traditional belief systems and not guaranteed predictions.
"""

    response = model.generate_content(prompt)

    return response.text

# ======================================
# DATABASE AGENT
# ======================================

conn = sqlite3.connect(
    "users.db",
    check_same_thread=False
)

cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users(

id INTEGER PRIMARY KEY AUTOINCREMENT,

name TEXT,

dob TEXT,

zodiac TEXT,

life_number INTEGER,

report TEXT

)
""")

conn.commit()

# ======================================
# SAVE USER AGENT
# ======================================

def save_user_agent(
        name,
        dob,
        zodiac,
        life_number,
        report):

    cursor.execute(
        """
        INSERT INTO users(
        name,
        dob,
        zodiac,
        life_number,
        report
        )

        VALUES(?,?,?,?,?)
        """,

        (
            name,
            dob,
            zodiac,
            life_number,
            report
        )
    )

    conn.commit()

# ======================================
# HISTORY AGENT
# ======================================

def history_agent():

    cursor.execute(
        "SELECT * FROM users"
    )

    data = cursor.fetchall()

    return data

# =========================================
# PDF REPORT AGENT
# =========================================

def pdf_agent(
        name,
        dob,
        zodiac,
        life_number,
        personality,
        career,
        relation,
        spiritual,
        report):

    filename = f"{name}_Report.pdf"

    doc = SimpleDocTemplate(filename)

    styles = getSampleStyleSheet()

    story = []

    story.append(
        Paragraph(
            "DivineAI Astrology Report",
            styles['Title']
        )
    )

    story.append(Spacer(1,20))

    story.append(
        Paragraph(
            f"Name : {name}",
            styles['BodyText']
        )
    )

    story.append(
        Paragraph(
            f"Date of Birth : {dob}",
            styles['BodyText']
        )
    )

    story.append(
        Paragraph(
            f"Zodiac Sign : {zodiac}",
            styles['BodyText']
        )
    )

    story.append(
        Paragraph(
            f"Life Number : {life_number}",
            styles['BodyText']
        )
    )

    story.append(
        Paragraph(
            f"Personality : {personality}",
            styles['BodyText']
        )
    )

    story.append(
        Paragraph(
            f"Career Advice : {career}",
            styles['BodyText']
        )
    )

    story.append(
        Paragraph(
            f"Relationship Advice : {relation}",
            styles['BodyText']
        )
    )

    story.append(
        Paragraph(
            f"Spiritual Guidance : {spiritual}",
            styles['BodyText']
        )
    )

    story.append(Spacer(1,20))

    story.append(
        Paragraph(
            report,
            styles['BodyText']
        )
    )

    doc.build(story)

    return filename

# =========================================
# VOICE OUTPUT AGENT
# =========================================

def speak_agent(text):

    engine.say(text)

    engine.runAndWait()

# =========================================
# VOICE INPUT AGENT
# =========================================

def voice_input_agent():

    recognizer = sr.Recognizer()

    with sr.Microphone() as source:

        print("Listening...")

        audio = recognizer.listen(source)

    try:

        text = recognizer.recognize_google(audio)

        print("You said:", text)

        return text

    except:

        return "Could not understand."

# =========================================
# FESTIVAL AGENT
# =========================================

def festival_agent():

    festivals = {

        "January": {
            "festival": "Makar Sankranti",
            "mantra": "Om Suryaya Namah"
        },

        "March": {
            "festival": "Holi",
            "mantra": "Om Krishnaaya Namah"
        },

        "August": {
            "festival": "Janmashtami",
            "mantra": "Om Namo Bhagavate Vasudevaya"
        },

        "October": {
            "festival": "Navratri",
            "mantra": "Om Dum Durgaye Namah"
        },

        "November": {
            "festival": "Diwali",
            "mantra": "Om Mahalakshmi Namah"
        }

    }

    month = datetime.now().strftime("%B")

    if month in festivals:

        return festivals[month]

    return {
        "festival": "No major festival",
        "mantra": "Om Namah Shivaya"
    }

festival_data = festival_agent()
festival_name = festival_data["festival"]
mantra = festival_data["mantra"]

# ======================================
# BHAGAVAD GITA RAG AGENT
# ======================================

def gita_rag_agent(question):

    if not os.path.exists("gita.pdf"):
        return "Error: 'gita.pdf' was not found in the project directory. Please add 'gita.pdf' to enable Gita RAG."

    reader = PdfReader("gita.pdf")

    text = ""

    for page in reader.pages:

        text += page.extract_text()

    chunks = text.split("\n")

    embeddings = embedding_model.encode(chunks)

    dimension = embeddings.shape[1]

    index = faiss.IndexFlatL2(dimension)

    index.add(
        np.array(
            embeddings,
            dtype=np.float32
        )
    )

    question_embedding = embedding_model.encode(
        [question]
    )

    distances, indices = index.search(
        np.array(
            question_embedding,
            dtype=np.float32
        ),
        1
    )

    best_chunk = chunks[
        indices[0][0]
    ]

    prompt = f"""
User Question:

{question}

Bhagavad Gita Verse:

{best_chunk}

Explain the meaning in very simple words.
"""

    response = model.generate_content(prompt)

    return response.text

# ======================================
# MEMORY AGENT
# ======================================

def memory_agent(question, answer):

    chat_history.append({

        "question": question,

        "answer": answer

    })
# ======================================
# PALM READING AGENT
# ======================================

def palm_agent(uploaded_image):

    image = Image.open(uploaded_image).convert("RGB")

    rgb = np.array(image)

    result = hands.process(rgb)

    if result.multi_hand_landmarks:

        prompt = """
You are a traditional palmistry expert.

Provide:

1. Personality tendencies
2. Strengths
3. Weaknesses
4. Career tendencies
5. Relationship tendencies
6. Spiritual advice

Mention clearly that palmistry is a traditional belief system and should be viewed as guidance rather than certain predictions.

Keep language simple.
"""

        response = model.generate_content(prompt)

        return response.text

    else:

        return "No hand detected in image."
# ======================================
# CHAT HISTORY AGENT
# ======================================

def chat_history_agent():

    return chat_history

# ==========================================
# MAIN PROGRAM (Runs only in CLI mode)
# ==========================================

if not st.runtime.exists():
    name, dob = user_agent()

    date_obj = datetime.strptime(dob, "%Y-%m-%d")

    day = date_obj.day
    month = date_obj.month

    zodiac = zodiac_agent(day, month)

    number = numerology_agent(dob)

    personality = personality_agent(number)

    career = career_agent(number)

    relation = relationship_agent(number)

    spiritual = spiritual_agent(number)

    festival_data = festival_agent()

    festival_name = festival_data["festival"]

    mantra = festival_data["mantra"]

    report = report_agent(
        name,
        dob,
        zodiac,
        number,
        personality,
        career,
        relation,
        spiritual
    )

    print("\n")
    print("="*80)
    print(report)
    print("="*80)

# =====================================
# LANGGRAPH WORKFLOW
# =====================================

graph = StateGraph(
    DivineState
)
graph.add_node(
    "zodiac",
    zodiac_node
)

graph.add_node(
    "numerology",
    numerology_node
)

graph.add_node(
    "personality",
    personality_node
)

graph.add_node(
    "career",
    career_node
)

graph.add_node(
    "relationship",
    relationship_node
)

graph.add_node(
    "spiritual",
    spiritual_node
)

# Connect the nodes to form the workflow pipeline
graph.add_edge(START, "zodiac")
graph.add_edge("zodiac", "numerology")
graph.add_edge("numerology", "personality")
graph.add_edge("personality", "career")
graph.add_edge("career", "relationship")
graph.add_edge("relationship", "spiritual")
graph.add_edge("spiritual", END)

workflow = graph.compile()

# ======================================
# STREAMLIT WEBSITE
# ======================================

st.set_page_config(
    page_title="DivineAI 3.0",
    page_icon="🔮"
)

st.title("🔮 DivineAI 3.0")
st.subheader("Multi-Agent Astrology and Spiritual Guidance System")

# Initialize session state for persistent results
if "report" not in st.session_state:
    st.session_state.report = None
if "pdf_file" not in st.session_state:
    st.session_state.pdf_file = None
if "palm_result" not in st.session_state:
    st.session_state.palm_result = None
if "gita_question" not in st.session_state:
    st.session_state.gita_question = None
if "gita_answer" not in st.session_state:
    st.session_state.gita_answer = None

name = st.text_input("Enter Your Name")

dob = st.date_input(
    "Select Date of Birth",
    value=datetime(1980, 1, 1),
    min_value=datetime(1980, 1, 1),
    max_value=datetime.now()
)

palm_image = st.file_uploader(
    "Upload Palm Image (Optional)",
    type=["jpg", "jpeg", "png"]
)

if st.button("Generate Report"):
    if not name.strip():
        st.warning("Please enter your name.")
    else:
        date_obj = dob
        day = date_obj.day
        month = date_obj.month

        state = {
            "name": name,
            "dob": str(dob)
        }

        with st.spinner("Consulting the cosmos..."):
            result = workflow.invoke(state)
            zodiac = result["zodiac"]
            number = result["life_number"]
            personality = result["personality"]
            career = result["career"]
            relation = result["relationship"]
            spiritual = result["spiritual"]

            report = report_agent(
                name,
                str(dob),
                zodiac,
                number,
                personality,
                career,
                relation,
                spiritual
            )
            
            save_user_agent(
                name,
                str(dob),
                zodiac,
                number,
                report
            )
            
            pdf_file = pdf_agent(
                name,
                str(dob),
                zodiac,
                number,
                personality,
                career,
                relation,
                spiritual,
                report
            )
            
            st.session_state.report = report
            st.session_state.pdf_file = pdf_file

# Display report & Speech options if available
if st.session_state.report:
    st.success("Report Generated Successfully")
    st.write(st.session_state.report)
    st.success(f"PDF Created Successfully: {st.session_state.pdf_file}")
    
    if st.button("🔊 Listen to Report"):
        speak_agent(st.session_state.report)

st.markdown("---")

# Palm Reading Section
st.subheader("✋ Palm Reading")
if palm_image is not None:
    if st.button("Analyze Palm"):
        with st.spinner("Analyzing hand landmarks..."):
            palm_result = palm_agent(palm_image)
        st.session_state.palm_result = palm_result
else:
    st.info("Upload a palm image above to enable palm analysis.")

if st.session_state.palm_result:
    st.write(st.session_state.palm_result)
    if st.session_state.palm_result != "No hand detected in image.":
        if st.button("🔊 Listen to Palm Analysis"):
            speak_agent(st.session_state.palm_result)

st.markdown("---")

# Festival Information Section
st.subheader("📅 Festival Information")
st.write(f"**Current Month's Festival:** {festival_name}")
st.write(f"**Suggested Mantra:** {mantra}")

st.markdown("---")

# Bhagavad Gita Guidance Section
st.subheader("📖 Bhagavad Gita Guidance")
question = st.text_input("Ask a spiritual question (e.g., How do I find peace?)")

col1, col2 = st.columns(2)
with col1:
    get_guidance = st.button("Get Guidance", use_container_width=True)
with col2:
    voice_guidance = st.button("🎤 Ask via Voice", use_container_width=True)

if get_guidance:
    if not question.strip():
        st.warning("Please enter a question.")
    else:
        with st.spinner("Searching the Bhagavad Gita..."):
            answer = gita_rag_agent(question)
        st.session_state.gita_question = question
        st.session_state.gita_answer = answer
        memory_agent(question, answer)

elif voice_guidance:
    with st.spinner("Listening... Please speak into your microphone."):
        voice_question = voice_input_agent()
    if voice_question and voice_question != "Could not understand.":
        st.success(f"Recognized: {voice_question}")
        with st.spinner("Searching the Bhagavad Gita..."):
            answer = gita_rag_agent(voice_question)
        st.session_state.gita_question = voice_question
        st.session_state.gita_answer = answer
        memory_agent(voice_question, answer)
    else:
        st.error("Could not understand your voice. Please try again or type your question.")

if st.session_state.gita_answer:
    st.markdown("### Guidance Answer")
    st.write(f"**Question:** {st.session_state.gita_question}")
    st.write(st.session_state.gita_answer)
    if st.button("🔊 Listen to Guidance"):
        speak_agent(st.session_state.gita_answer)

st.markdown("---")

# Conversation Memory Section
st.subheader("💬 Conversation Memory")
if st.button("Show Chat History"):
    history = chat_history_agent()
    if not history:
        st.info("No chat history yet.")
    for item in history:
        st.write(f"**Question:** {item['question']}")
        st.write(f"**Answer:** {item['answer']}")
        st.write("---")

st.markdown("---")

# Previous Reports Section
st.subheader("📜 Previous Reports")
history_data = history_agent()
if not history_data:
    st.info("No previous reports found in database.")
for row in history_data:
    st.write(f"**ID:** {row[0]}")
    st.write(f"**Name:** {row[1]}")
    st.write(f"**DOB:** {row[2]}")
    st.write(f"**Zodiac:** {row[3]}")
    st.write(f"**Life Number:** {row[4]}")
    st.write("---")

