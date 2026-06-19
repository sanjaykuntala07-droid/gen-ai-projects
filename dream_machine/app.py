"""
Dream Machine — Landing Page
"Describe it. We'll build it."
"""
import streamlit as st
import streamlit.components.v1 as components
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from components.styles import inject_styles, inject_pwa_tags
from components.db import init_db, list_blueprints
from components.gemini_client import detect_idea_type, IDEA_TYPE_ICONS

# ── Page Config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Dream Machine — Innovate the Future",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="collapsed",
)

inject_styles()
inject_pwa_tags()  # PWA meta tags for mobile "Add to Home Screen"
init_db()

# ── Session State Init ────────────────────────────────────────────────────────
for key, default in [
    ("idea", ""),
    ("idea_type", ""),
    ("questions", []),
    ("answers", {}),
    ("current_blueprint_id", None),
    ("blueprint_data", {}),
    ("user_name", ""),
    ("onboarded", False),
]:
    if key not in st.session_state:
        st.session_state[key] = default

# ── Hero Section ──────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero-section">
    <div class="hero-eyebrow">✦ Dream Machine <span style="opacity:0.5">·</span> AI Innovation Platform</div>
    <h1 class="hero-title">
        Your idea.<br>
        <span class="hero-gradient">Fully engineered.</span><br>
        In 60 seconds.
    </h1>
    <p class="hero-subtitle">
        Describe any idea — a product, business, app, invention, or workflow.
        Get a complete Blueprint, interactive mockup, and strategic roadmap instantly.
    </p>
</div>
""", unsafe_allow_html=True)

# ── Cycling Placeholder Animation ─────────────────────────────────────────────
components.html("""
<style>
  #placeholder-anim {
    position: absolute;
    pointer-events: none;
    color: rgba(107,107,138,0.8);
    font-family: 'Inter', sans-serif;
    font-size: 15px;
    padding: 10px 16px;
    z-index: 999;
    top: 0; left: 0;
  }
  .cursor {
    display: inline-block;
    width: 2px; height: 1em;
    background: #5C6BFF;
    margin-left: 2px;
    vertical-align: text-bottom;
    animation: blink 1s step-end infinite;
  }
  @keyframes blink { 0%,100%{opacity:1} 50%{opacity:0} }
</style>
<div id="placeholder-anim"><span id="typed-text"></span><span class="cursor"></span></div>
<script>
const ideas = [
  "An AI tutor that adapts to each student's learning style...",
  "A marketplace for renting out professional equipment...",
  "A smart home system that predicts your needs...",
  "A social app for connecting local freelancers...",
  "An inventory system powered by computer vision...",
  "A mental health companion using conversational AI...",
  "A blockchain-based supply chain tracker...",
  "A no-code tool for building mobile apps with voice commands...",
];
let idx = 0, charIdx = 0, deleting = false;
const el = document.getElementById('typed-text');
function type() {
  const cur = ideas[idx];
  if (!deleting) {
    el.textContent = cur.slice(0, ++charIdx);
    if (charIdx === cur.length) { deleting = true; setTimeout(type, 2000); return; }
  } else {
    el.textContent = cur.slice(0, --charIdx);
    if (charIdx === 0) { deleting = false; idx = (idx+1) % ideas.length; }
  }
  setTimeout(type, deleting ? 30 : 55);
}
type();
</script>
""", height=0)

# ── Main Input ────────────────────────────────────────────────────────────────
col_main, col_side = st.columns([2, 1], gap="large")

with col_main:
    idea_input = st.text_area(
        "DESCRIBE YOUR IDEA",
        placeholder="An AI-powered platform that...",
        height=140,
        key="idea_input_box",
        help="Be as specific or as vague as you like — our AI will ask the right follow-up questions.",
    )

    # Real-time idea type detection
    if idea_input and len(idea_input) > 20 and idea_input != st.session_state.idea:
        with st.spinner(""):
            detected = detect_idea_type(idea_input)
            icon = IDEA_TYPE_ICONS.get(detected, "💡")
            st.markdown(
                f'<div class="idea-type-pill">{icon} Detected: <strong>{detected}</strong></div>',
                unsafe_allow_html=True
            )
            st.session_state.idea_type = detected
    elif st.session_state.idea_type and idea_input:
        icon = IDEA_TYPE_ICONS.get(st.session_state.idea_type, "💡")
        st.markdown(
            f'<div class="idea-type-pill">{icon} Detected: <strong>{st.session_state.idea_type}</strong></div>',
            unsafe_allow_html=True
        )

    st.markdown("<br>", unsafe_allow_html=True)

    col_btn1, col_btn2, col_btn3 = st.columns([2, 1, 1])
    with col_btn1:
        dream_btn = st.button("✦ Dream It →", type="primary", use_container_width=True, key="dream_btn")
    with col_btn2:
        skip_btn = st.button("⚡ Skip Questions", use_container_width=True, key="skip_btn")
    with col_btn3:
        clear_btn = st.button("🗑️ Clear", use_container_width=True, key="clear_btn")

    if clear_btn:
        st.session_state.idea = ""
        st.session_state.idea_type = ""
        st.rerun()

    if (dream_btn or skip_btn) and idea_input.strip():
        st.session_state.idea = idea_input.strip()
        if not st.session_state.idea_type:
            with st.spinner("Detecting idea type..."):
                st.session_state.idea_type = detect_idea_type(idea_input)

        if skip_btn:
            st.session_state.questions = []
            st.session_state.answers = {}
            st.switch_page("pages/2_Generating.py")
        else:
            st.session_state.questions = []
            st.session_state.answers = {}
            st.switch_page("pages/1_Questions.py")

    elif (dream_btn or skip_btn) and not idea_input.strip():
        st.warning("✦ Hmm — what are you going to build? Describe your idea above to get started.")

with col_side:
    st.markdown("""
    <div class="dream-card" style="margin-top:0;">
        <div class="section-tag">How it works</div>
        <div style="display:flex;flex-direction:column;gap:16px;margin-top:16px;">
            <div style="display:flex;gap:14px;align-items:flex-start;">
                <div style="width:32px;height:32px;border-radius:50%;background:rgba(92,107,255,0.15);border:1px solid rgba(92,107,255,0.3);display:flex;align-items:center;justify-content:center;font-size:14px;font-weight:700;color:#5C6BFF;flex-shrink:0;">1</div>
                <div><div style="font-weight:600;font-size:14px;margin-bottom:4px;color:#E8E8F0;">Describe your idea</div><div style="font-size:13px;color:#6B6B8A;line-height:1.5;">Any idea. Any stage. Any domain.</div></div>
            </div>
            <div style="display:flex;gap:14px;align-items:flex-start;">
                <div style="width:32px;height:32px;border-radius:50%;background:rgba(92,107,255,0.15);border:1px solid rgba(92,107,255,0.3);display:flex;align-items:center;justify-content:center;font-size:14px;font-weight:700;color:#5C6BFF;flex-shrink:0;">2</div>
                <div><div style="font-weight:600;font-size:14px;margin-bottom:4px;color:#E8E8F0;">Answer smart questions</div><div style="font-size:13px;color:#6B6B8A;line-height:1.5;">Context-aware discovery in 60 seconds.</div></div>
            </div>
            <div style="display:flex;gap:14px;align-items:flex-start;">
                <div style="width:32px;height:32px;border-radius:50%;background:rgba(92,107,255,0.15);border:1px solid rgba(92,107,255,0.3);display:flex;align-items:center;justify-content:center;font-size:14px;font-weight:700;color:#5C6BFF;flex-shrink:0;">3</div>
                <div><div style="font-weight:600;font-size:14px;margin-bottom:4px;color:#E8E8F0;">Get your Blueprint</div><div style="font-size:13px;color:#6B6B8A;line-height:1.5;">Full strategy, architecture, mockup, and roadmap.</div></div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Recent blueprints quick nav
    blueprints = list_blueprints(limit=3)
    if blueprints:
        st.markdown('<div class="section-tag" style="margin-top:20px;">Recent blueprints</div>', unsafe_allow_html=True)
        for bp in blueprints:
            icon = IDEA_TYPE_ICONS.get(bp["idea_type"], "💡")
            if st.button(f"{icon} {bp['title'][:35]}...", key=f"recent_{bp['id']}", use_container_width=True):
                st.session_state.current_blueprint_id = bp["id"]
                st.switch_page("pages/3_Blueprint.py")

# ── Stats Bar ─────────────────────────────────────────────────────────────────
total_bps = len(list_blueprints(limit=1000, all_users=True))
st.markdown(f"""
<div class="stats-bar">
    <div class="stat-item">
        <span class="stat-value">{max(total_bps, 0):,}</span>
        <span class="stat-label">Blueprints Created</span>
    </div>
    <div class="stat-item">
        <span class="stat-value">10</span>
        <span class="stat-label">Blueprint Sections</span>
    </div>
    <div class="stat-item">
        <span class="stat-value">&lt;90s</span>
        <span class="stat-label">Time to Blueprint</span>
    </div>
    <div class="stat-item">
        <span class="stat-value">∞</span>
        <span class="stat-label">Ideas Possible</span>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Example Ideas ─────────────────────────────────────────────────────────────
st.markdown("""
<div style="text-align:center;margin-bottom:24px;">
    <div class="section-tag" style="display:inline-flex;">Try an example</div>
</div>
""", unsafe_allow_html=True)

examples = [
    ("🤖", "AI-Powered Code Reviewer", "A SaaS tool that automatically reviews pull requests, identifies bugs, suggests improvements, and enforces coding standards using AI — integrated directly into GitHub."),
    ("🌱", "Carbon Footprint Tracker", "A mobile app that tracks individual carbon footprint in real-time by connecting to bank transactions, smart home devices, and travel data — and suggests offset actions."),
    ("🎓", "Adaptive Learning Platform", "An educational platform where AI tutors adapt lesson difficulty, teaching style, and pacing to each student's real-time performance and learning patterns."),
]

ex_cols = st.columns(3)
for i, (icon, name, desc) in enumerate(examples):
    with ex_cols[i]:
        st.markdown(f"""
        <div class="dream-card" style="cursor:pointer;text-align:left;">
            <div style="font-size:28px;margin-bottom:12px;">{icon}</div>
            <div style="font-family:'Space Grotesk',sans-serif;font-weight:600;font-size:15px;margin-bottom:8px;color:#E8E8F0;">{name}</div>
            <div style="font-size:13px;color:#6B6B8A;line-height:1.6;">{desc[:100]}...</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button(f"Use this idea →", key=f"ex_{i}", use_container_width=True):
            st.session_state.idea = desc
            st.session_state.idea_type = ""
            st.session_state.questions = []
            st.session_state.answers = {}
            st.switch_page("pages/1_Questions.py")

# ── Footer ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="text-align:center;padding:60px 0 20px;color:#3A3A5A;font-size:13px;">
    ✦ Dream Machine — Built with Google Gemini AI<br>
    <span style="font-size:11px;">Turn any idea into a complete product blueprint in seconds.</span>
</div>
""", unsafe_allow_html=True)
