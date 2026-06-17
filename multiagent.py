import os
import time
import random
import streamlit as st
from google import genai
from google.genai.errors import APIError
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# ==========================================================
# PAGE CONFIG AND STYLING
# ==========================================================
st.set_page_config(
    page_title="Multi-Agent Developer Crew",
    page_icon="🤖",
    layout="wide"
)

# Custom CSS for premium styling
st.markdown("""
<style>
    .main-header {
        font-family: 'Outfit', 'Inter', sans-serif;
        background: linear-gradient(90deg, #4b6cb7 0%, #182848 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
        font-size: 2.5rem;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-family: 'Inter', sans-serif;
        color: #555555;
        font-size: 1.1rem;
        margin-bottom: 1.5rem;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: #f0f2f6;
        border-radius: 4px;
        padding-left: 20px;
        padding-right: 20px;
        font-weight: 600;
    }
    .stTabs [aria-selected="true"] {
        background-color: #4b6cb7;
        color: white !important;
    }
</style>
""", unsafe_allow_html=True)

# API Key Validation
api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
if not api_key:
    st.error("⚠️ `GEMINI_API_KEY` or `GOOGLE_API_KEY` not found in environment or `.env` file. Please configure your key.")
    st.stop()

# Initialize Gemini Client
client = genai.Client(api_key=api_key)

# ==========================================================
# Generic Agent Class
# ==========================================================
class Agent:
    def __init__(self, name, role, model_name, temperature):
        self.name = name
        self.role = role
        self.model_name = model_name
        self.temperature = temperature

    def run(self, task, status_placeholder=None):
        prompt = f"""
You are {self.name}

Role:
{self.role}

Task:
{task}

Return only the useful output.
"""
        max_retries = 5
        base_delay = 2.0
        max_delay = 30.0

        for attempt in range(max_retries + 1):
            try:
                response = client.models.generate_content(
                    model=self.model_name,
                    contents=prompt,
                    config={
                        "temperature": self.temperature
                    }
                )
                return response.text
            except APIError as e:
                # 429 is Resource Exhausted (Rate Limit), 5xx are Server Errors
                if (e.code == 429 or (e.code and 500 <= e.code < 600)) and attempt < max_retries:
                    delay = min(base_delay * (2 ** attempt) + random.uniform(0.1, 1.0), max_delay)
                    msg = f"⚠️ {self.name} encountered error {e.code} ({e.status or 'Unavailable'}). Retrying in {delay:.1f}s... (Attempt {attempt + 1}/{max_retries})"
                    if status_placeholder:
                        status_placeholder.write(msg)
                    else:
                        st.toast(msg)
                    time.sleep(delay)
                else:
                    raise e
            except Exception as e:
                if attempt < max_retries:
                    delay = min(base_delay * (2 ** attempt) + random.uniform(0.1, 1.0), max_delay)
                    msg = f"⚠️ {self.name} encountered connection issue: {str(e)}. Retrying in {delay:.1f}s... (Attempt {attempt + 1}/{max_retries})"
                    if status_placeholder:
                        status_placeholder.write(msg)
                    else:
                        st.toast(msg)
                    time.sleep(delay)
                else:
                    raise e


# ==========================================================
# Coordinator Agent
# ==========================================================
class CoordinatorAgent:
    def __init__(self, model_name, temperature):
        self.model_name = model_name
        self.temperature = temperature

        # Create agents dynamically based on configurations
        self.research_agent = Agent(
            "Research Agent",
            "Gather requirements, define software architecture, and explain key programming concepts.",
            self.model_name,
            self.temperature
        )
        self.coder_agent = Agent(
            "Coder Agent",
            "Write clean, optimized, and complete Python code following coding standards. Avoid placeholders.",
            self.model_name,
            self.temperature
        )
        self.review_agent = Agent(
            "Reviewer Agent",
            "Review Python code, identify potential bugs, logic flaws, or performance issues, and suggest improvements.",
            self.model_name,
            self.temperature
        )

    def execute(self, user_request, status_placeholder):
        status_placeholder.write("🔍 **Step 1: Research Agent** is analyzing the requirements...")
        research_output = self.research_agent.run(
            f"User requirement:\n\n{user_request}\n\nProduce detailed requirements and solution approach.",
            status_placeholder=status_placeholder
        )

        status_placeholder.write("💻 **Step 2: Coder Agent** is writing the implementation...")
        code_output = self.coder_agent.run(
            f"Based on the following analysis:\n\n{research_output}\n\nGenerate Python code.",
            status_placeholder=status_placeholder
        )

        status_placeholder.write("🔍 **Step 3: Reviewer Agent** is checking code quality...")
        review_output = self.review_agent.run(
            f"Review the following code:\n\n{code_output}\n\nSuggest improvements and possible bugs.",
            status_placeholder=status_placeholder
        )

        return {
            "research": research_output,
            "code": code_output,
            "review": review_output
        }


# ==========================================================
# Streamlit Interface
# ==========================================================
def main():
    st.markdown('<div class="main-header">🤖 Multi-Agent AI Developer Crew</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Collaborative research, code generation, and review powered by Google Gemini</div>', unsafe_allow_html=True)

    # Sidebar Settings
    with st.sidebar:
        st.header("⚙️ Agent Settings")
        model_choice = st.selectbox(
            "Select Gemini Model",
            ["gemini-2.5-flash", "gemini-2.0-flash"],
            index=0
        )
        temp_choice = st.slider(
            "Creativity / Temperature",
            min_value=0.0,
            max_value=1.0,
            value=0.1,
            step=0.1
        )
        st.divider()
        st.markdown(
            "**System Overview:**\n"
            "1. **Research Agent** defines requirements.\n"
            "2. **Coder Agent** writes the Python script.\n"
            "3. **Reviewer Agent** audits the code."
        )

    # Input Area
    task_input = st.text_area(
        "Enter what you want the AI Developer Crew to build:",
        value="Create a Python program that reads a CSV file and calculates average sales by month.",
        height=100
    )

    if st.button("🚀 Run Developer Crew", type="primary"):
        if not task_input.strip():
            st.warning("⚠️ Please provide a task for the developer crew.")
            st.stop()

        # Run process using st.status for premium experience
        with st.status("🤖 Developer Crew working on your request...", expanded=True) as status_box:
            try:
                coordinator = CoordinatorAgent(model_name=model_choice, temperature=temp_choice)
                results = coordinator.execute(task_input, status_box)
                status_box.update(label="✅ Software Development Process Finished!", state="complete", expanded=False)
            except Exception as e:
                status_box.update(label="❌ Error occurred during execution", state="error", expanded=True)
                st.error(f"The Developer Crew failed with an error: {e}")
                st.stop()

        # Output Results
        st.markdown("---")
        st.subheader("📦 Generated Deliverables")
        
        tab1, tab2, tab3 = st.tabs(["📝 Research & Plan", "💻 Generated Code", "🔍 Code Review"])
        
        with tab1:
            st.markdown("### 📝 Analysis & Architecture Plan")
            st.markdown(results["research"])
            
        with tab2:
            st.markdown("### 💻 Python Code")
            st.code(results["code"], language="python")
            
        with tab3:
            st.markdown("### 🔍 Code Quality Audit")
            st.markdown(results["review"])


if __name__ == "__main__":
    main()