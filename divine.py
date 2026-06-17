import os
from datetime import datetime
from dotenv import load_dotenv
from google import genai
import streamlit as st

# -------------------------------------------------
# Load Gemini API Key
# -------------------------------------------------

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


# =================================================
# AGENT 2 : ZODIAC AGENT
# =================================================

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


# =================================================
# AGENT 3 : NUMEROLOGY AGENT
# =================================================

def numerology_agent(dob):

    digits = dob.replace("-", "")

    total = sum(int(i) for i in digits)

    while total > 9:
        total = sum(int(i) for i in str(total))

    return total


# =================================================
# AGENT 4 : PERSONALITY AGENT
# =================================================

def personality_agent(number):

    personality = {

        1: "Leader and creative",
        2: "Peaceful and emotional",
        3: "Social and artistic",
        4: "Hardworking and disciplined",
        5: "Adventurous and energetic",
        6: "Caring and loving",
        7: "Spiritual and analytical",
        8: "Confident and ambitious",
        9: "Wise and compassionate"

    }

    return personality[number]


# =================================================
# AGENT 5 : CAREER AGENT
# =================================================

def career_agent(number):

    careers = {

        1: "Management and Entrepreneurship",
        2: "Teaching and Counseling",
        3: "Art and Media",
        4: "Engineering and Administration",
        5: "Marketing and Travel",
        6: "Healthcare and Service",
        7: "Research and Spiritual Studies",
        8: "Business and Finance",
        9: "Social Service and Leadership"

    }

    return careers[number]


# =================================================
# AGENT 6 : RELATIONSHIP AGENT
# =================================================

def relationship_agent(number):

    advice = {

        1: "You value independence in relationships.",
        2: "You are caring and emotional.",
        3: "You enjoy communication and friendship.",
        4: "You prefer loyalty and trust.",
        5: "You love freedom and excitement.",
        6: "Family is important to you.",
        7: "You seek deep connections.",
        8: "You appreciate honesty and commitment.",
        9: "You are generous and understanding."

    }

    return advice[number]


# =================================================
# AGENT 7 : SPIRITUAL AGENT
# =================================================

def spiritual_agent(number):

    spiritual = {

        1: "Practice morning meditation.",
        2: "Spend time in prayer and gratitude.",
        3: "Chant positive affirmations.",
        4: "Read spiritual books daily.",
        5: "Practice yoga and mindfulness.",
        6: "Help others through service.",
        7: "Meditate and study sacred texts.",
        8: "Maintain discipline and gratitude.",
        9: "Focus on compassion and kindness."

    }

    return spiritual[number]


# =================================================
# AGENT 8 : REPORT AGENT
# =================================================

def report_agent(name, dob, zodiac,
                 number,
                 personality,
                 career,
                 relation,
                 spiritual):


    prompt = f"""

You are DivineAI.

User Name : {name}

Date of Birth : {dob}

Zodiac Sign : {zodiac}

Life Path Number : {number}

Personality : {personality}

Career Advice : {career}

Relationship Advice : {relation}

Spiritual Guidance : {spiritual}

Write a beautiful report with:

1. Personality
2. Strengths
3. Weaknesses
4. Career
5. Relationships
6. Money
7. Lucky Color
8. Lucky Number
9. Daily Motivation

Use simple language.

Mention clearly that astrology and numerology are traditional belief systems and should be viewed as guidance rather than certain predictions.
"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    return response.text


# =================================================
# STREAMLIT INTERFACE
# =================================================

st.set_page_config(
    page_title="DivineAI — Astrology & Numerology",
    page_icon="✨",
    layout="centered"
)

# Custom CSS for premium styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&family=Inter:wght@300;400;600&display=swap');
    
    .main-title {
        font-family: 'Outfit', 'Inter', sans-serif;
        background: linear-gradient(135deg, #8A2387 0%, #E94057 50%, #F27121 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
        font-size: 3rem;
        margin-bottom: 0.2rem;
        text-align: center;
    }
    
    .subtitle {
        font-family: 'Inter', sans-serif;
        color: #888888;
        font-size: 1.1rem;
        margin-bottom: 2rem;
        text-align: center;
    }
    
    .card {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 16px;
        padding: 24px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        margin-bottom: 20px;
        transition: transform 0.3s ease;
    }
    
    .card:hover {
        transform: translateY(-5px);
        border-color: rgba(233, 64, 87, 0.4);
    }
    
    .card-title {
        font-family: 'Outfit', sans-serif;
        font-size: 1.3rem;
        font-weight: 600;
        color: #E94057;
        margin-bottom: 12px;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    
    .card-value {
        font-size: 1.8rem;
        font-weight: bold;
        color: #FFFFFF;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">✨ DivineAI</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Discover your Zodiac, Life Path, and receive personalized AI spiritual guidance</div>', unsafe_allow_html=True)

# Main Form
with st.form("divine_form"):
    name = st.text_input("👤 Enter your name", placeholder="e.g. Alexander")
    dob_val = st.date_input("📅 Enter Date of Birth", min_value=datetime(1900, 1, 1), max_value=datetime.now())
    
    submit_btn = st.form_submit_button("✨ Generate My Divine Report", use_container_width=True)

if submit_btn:
    if not name.strip():
        st.warning("⚠️ Please enter your name.")
    else:
        dob_str = dob_val.strftime("%Y-%m-%d")
        day = dob_val.day
        month = dob_val.month
        
        with st.spinner("🌌 Consulting the cosmos..."):
            zodiac = zodiac_agent(day, month)
            number = numerology_agent(dob_str)
            personality = personality_agent(number)
            career = career_agent(number)
            relation = relationship_agent(number)
            spiritual = spiritual_agent(number)
            
            # Generate Gemini AI report
            final_report = report_agent(
                name,
                dob_str,
                zodiac,
                number,
                personality,
                career,
                relation,
                spiritual
            )
            
        # Display Results
        st.markdown("---")
        st.subheader("🪐 Cosmic Alignment Dashboard")
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"""
            <div class="card">
                <div class="card-title">🌟 Zodiac Sign</div>
                <div class="card-value">{zodiac}</div>
                <p style="font-size: 0.9rem; color: #888; margin-top: 8px;">Your sun sign based on your birth month and day.</p>
            </div>
            """, unsafe_allow_html=True)
            
        with col2:
            st.markdown(f"""
            <div class="card">
                <div class="card-title">🔢 Life Path Number</div>
                <div class="card-value">{number}</div>
                <p style="font-size: 0.9rem; color: #888; margin-top: 8px;">Key indicator of your life purpose and direction.</p>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("### 🕊️ Core Guidance Archetypes")
        
        tab1, tab2, tab3, tab4 = st.tabs(["👤 Personality", "💼 Career Pathway", "❤️ Relationships", "🧘 Spiritual Practice"])
        
        with tab1:
            st.markdown(f"""
            <div style="padding: 15px; border-left: 4px solid #E94057; background: rgba(255, 255, 255, 0.02); border-radius: 4px;">
                <strong>Your Core Personality Traits:</strong><br>{personality}
            </div>
            """, unsafe_allow_html=True)
            
        with tab2:
            st.markdown(f"""
            <div style="padding: 15px; border-left: 4px solid #F27121; background: rgba(255, 255, 255, 0.02); border-radius: 4px;">
                <strong>Recommended Career Fields:</strong><br>{career}
            </div>
            """, unsafe_allow_html=True)
            
        with tab3:
            st.markdown(f"""
            <div style="padding: 15px; border-left: 4px solid #8A2387; background: rgba(255, 255, 255, 0.02); border-radius: 4px;">
                <strong>Relationship Dynamics & Advice:</strong><br>{relation}
            </div>
            """, unsafe_allow_html=True)
            
        with tab4:
            st.markdown(f"""
            <div style="padding: 15px; border-left: 4px solid #E94057; background: rgba(255, 255, 255, 0.02); border-radius: 4px;">
                <strong>Spiritual Practice Recommendation:</strong><br>{spiritual}
            </div>
            """, unsafe_allow_html=True)
            
        st.markdown("---")
        st.subheader("📝 Complete AI Spiritual Analysis & Report")
        st.markdown(final_report)
        
        st.download_button(
            label="📥 Download Divine Report (.txt)",
            data=final_report,
            file_name=f"divine_report_{name.lower().replace(' ', '_')}.txt",
            mime="text/plain",
            use_container_width=True
        )