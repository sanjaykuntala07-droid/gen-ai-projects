"""
Dream Machine — Discovery Questions
Typeform-style contextual question flow.
"""
import streamlit as st
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from components.styles import inject_styles
from components.gemini_client import generate_questions, IDEA_TYPE_ICONS

st.set_page_config(
    page_title="Discovery Questions — Dream Machine",
    page_icon="✦",
    layout="centered",
    initial_sidebar_state="collapsed",
)
inject_styles()

# ── Guard ─────────────────────────────────────────────────────────────────────
if not st.session_state.get("idea"):
    st.markdown("""
    <div class="empty-state">
        <div class="empty-state-icon">✦</div>
        <div class="empty-state-title">No idea found</div>
        <div class="empty-state-text">Start from the home page to describe your idea first.</div>
    </div>
    """, unsafe_allow_html=True)
    if st.button("← Go Home", type="primary"):
        st.switch_page("app.py")
    st.stop()

idea = st.session_state.idea
idea_type = st.session_state.get("idea_type", "Other")
icon = IDEA_TYPE_ICONS.get(idea_type, "💡")

# ── Generate Questions ─────────────────────────────────────────────────────────
if not st.session_state.get("questions"):
    with st.spinner("🤖 Generating your discovery questions..."):
        st.session_state.questions = generate_questions(idea, idea_type)
        st.session_state.answers = {}
        st.session_state.current_q = 0

questions = st.session_state.questions
if "current_q" not in st.session_state:
    st.session_state.current_q = 0

# ── Header ─────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div style="text-align:center;padding:40px 0 20px;">
    <div class="idea-type-pill" style="margin-bottom:16px;">{icon} {idea_type}</div>
    <div style="font-family:'Space Grotesk',sans-serif;font-size:14px;color:#6B6B8A;max-width:500px;margin:0 auto;line-height:1.6;">
        "{idea[:120]}{"..." if len(idea) > 120 else ""}"
    </div>
</div>
""", unsafe_allow_html=True)

# ── Progress ──────────────────────────────────────────────────────────────────
total_q = len(questions)
current_q = st.session_state.current_q
progress = current_q / total_q if total_q > 0 else 0

st.markdown(f"""
<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;">
    <span style="font-family:'JetBrains Mono',monospace;font-size:11px;color:#00F5D4;text-transform:uppercase;letter-spacing:1px;">
        Question {min(current_q + 1, total_q)} of {total_q}
    </span>
    <span style="font-family:'Space Grotesk',sans-serif;font-size:12px;color:#6B6B8A;">
        {int(progress * 100)}% complete
    </span>
</div>
""", unsafe_allow_html=True)
st.progress(progress)

st.markdown("<br>", unsafe_allow_html=True)

# ── Question Display ──────────────────────────────────────────────────────────
if current_q < total_q:
    q = questions[current_q]
    q_text = q.get("question", "")
    options = q.get("options", [])
    placeholder = q.get("placeholder", "Type your answer...")

    st.markdown(f"""
    <div class="question-card">
        <div class="question-number">◆ Question {current_q + 1}</div>
        <div class="question-text">{q_text}</div>
    </div>
    """, unsafe_allow_html=True)

    # Selected chip tracking
    chip_key = f"chip_select_{current_q}"
    if chip_key not in st.session_state:
        st.session_state[chip_key] = None

    # Render option chips as buttons
    if options:
        st.markdown("<div style='text-align:center;margin:20px 0 8px;'>", unsafe_allow_html=True)
        chip_cols = st.columns(min(len(options), 4))
        for i, opt in enumerate(options):
            with chip_cols[i % len(chip_cols)]:
                selected = st.session_state[chip_key] == opt
                btn_label = f"✓ {opt}" if selected else opt
                if st.button(btn_label, key=f"chip_{current_q}_{i}",
                             use_container_width=True,
                             type="primary" if selected else "secondary"):
                    st.session_state[chip_key] = opt
                    # Auto-save answer
                    st.session_state.answers[q_text] = opt
                    st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    # Custom text input
    st.markdown("<div style='text-align:center;margin-top:16px;margin-bottom:8px;font-size:13px;color:#6B6B8A;'>— or type your own answer —</div>", unsafe_allow_html=True)
    custom_ans = st.text_input(
        "Custom answer",
        label_visibility="collapsed",
        placeholder=placeholder,
        key=f"custom_{current_q}",
        value=st.session_state.answers.get(q_text, "") if st.session_state[chip_key] is None else ""
    )
    if custom_ans:
        st.session_state.answers[q_text] = custom_ans
        st.session_state[chip_key] = None

    # Navigation
    st.markdown("<br>", unsafe_allow_html=True)
    nav_col1, nav_col2, nav_col3 = st.columns([1, 2, 1])

    with nav_col1:
        if current_q > 0:
            if st.button("← Back", use_container_width=True):
                st.session_state.current_q -= 1
                st.rerun()

    with nav_col2:
        # Check if answered
        is_answered = q_text in st.session_state.answers and st.session_state.answers[q_text]
        next_label = "Next →" if current_q < total_q - 1 else "Generate Blueprint →"
        next_type = "primary" if is_answered else "secondary"

        if st.button(next_label, type=next_type, use_container_width=True, key="next_btn"):
            if not is_answered:
                # Allow skipping individual questions
                st.session_state.answers[q_text] = "(skipped)"

            if current_q < total_q - 1:
                st.session_state.current_q += 1
                st.rerun()
            else:
                st.switch_page("pages/2_Generating.py")

    with nav_col3:
        if st.button("Skip →", use_container_width=True, key="skip_q_btn"):
            st.session_state.current_q += 1 if current_q < total_q - 1 else total_q
            if current_q >= total_q - 1:
                st.switch_page("pages/2_Generating.py")
            st.rerun()

else:
    # All questions answered
    st.markdown("""
    <div class="question-card" style="background:rgba(0,245,212,0.05);border-color:rgba(0,245,212,0.3);">
        <div style="font-size:48px;margin-bottom:16px;">✦</div>
        <div class="question-text">All questions answered!</div>
        <div style="font-size:14px;color:#6B6B8A;margin-top:8px;">Ready to generate your Blueprint.</div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("← Review Answers", use_container_width=True):
            st.session_state.current_q = total_q - 1
            st.rerun()
    with col_b:
        if st.button("✦ Generate Blueprint →", type="primary", use_container_width=True):
            st.switch_page("pages/2_Generating.py")

# ── Skip All ──────────────────────────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
st.markdown('<div style="text-align:center;">', unsafe_allow_html=True)
if st.button("⚡ Skip all — generate now", key="skip_all_btn"):
    st.switch_page("pages/2_Generating.py")
st.markdown('</div>', unsafe_allow_html=True)

# ── Answers Summary ───────────────────────────────────────────────────────────
if st.session_state.answers:
    with st.expander("📝 Your answers so far", expanded=False):
        for q_text, ans in st.session_state.answers.items():
            if ans and ans != "(skipped)":
                st.markdown(f"""
                <div style="margin-bottom:8px;">
                    <div style="font-size:12px;color:#6B6B8A;margin-bottom:2px;">{q_text}</div>
                    <div style="font-size:14px;color:#E8E8F0;padding:8px 12px;background:rgba(255,255,255,0.03);border-radius:8px;border-left:2px solid #5C6BFF;">{ans}</div>
                </div>
                """, unsafe_allow_html=True)
