"""
Dream Machine — Unified Workspace Studio
A tabbed, professional, mobile-ready interface combining:
1. Idea Input / Speech Capture
2. Mini Blueprint
3. Mind Map
4. Full Blueprint (Questions + Inline Builder + Viewer + Advisor Chat)
5. Personal Notes & Reminders (with browser notifications)
"""
import streamlit as st
try:
    import streamlit.components.v1 as components
except ImportError:
    components = None
import sys
import os
import json
import time
from datetime import datetime, timedelta

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from components.styles import inject_styles
from components.db import (
    init_db, save_capture, update_capture, list_captures,
    delete_capture, list_blueprints, get_blueprint, toggle_blueprint_public,
    update_blueprint_status, save_chat_message, get_chat_history, clear_chat_history,
    create_blueprint, update_blueprint_sections, update_blueprint_mockup, update_blueprint_title,
    create_reminder, list_reminders, mark_reminder_notified, delete_reminder
)
from components.gemini_client import (
    detect_idea_type, generate_mini_blueprint, generate_mindmap,
    transcribe_audio_bytes, IDEA_TYPE_ICONS, generate_questions,
    SECTIONS, generate_section_sync, generate_mockup, generate_title,
    stream_chat, get_smart_suggestions
)
from components.export import export_pdf_bytes, export_markdown

# ── Page Config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Workspace — Dream Machine",
    page_icon="🎤",
    layout="wide",
    initial_sidebar_state="collapsed",
)
inject_styles()
init_db()

# ── Query Params Processing ──────────────────────────────────────────────────
if "voice_transcript" in st.query_params:
    val = st.query_params["voice_transcript"]
    st.session_state.capture_text = val
    st.session_state.capture_text_area = val
    del st.query_params["voice_transcript"]
    st.toast("Voice transcript applied! 🎤")
    st.rerun()

if "notified_reminder_id" in st.query_params:
    rid = st.query_params["notified_reminder_id"]
    mark_reminder_notified(rid)
    del st.query_params["notified_reminder_id"]
    st.toast("Reminder completed! 🔔")
    st.rerun()

# ── Session State Initialization ──────────────────────────────────────────────
for key, val in [
    ("capture_text", ""),
    ("capture_output_type", "Mini Blueprint"),
    ("capture_result", None),
    ("capture_mindmap", ""),
    ("capture_generating", False),
    ("full_bp_state", "not_started"),
    ("full_bp_current_q", 0),
    ("full_bp_questions", []),
    ("full_bp_answers", {}),
    ("current_blueprint_id", None),
]:
    if key not in st.session_state:
        st.session_state[key] = val

# Sync active blueprint if not loaded but exists
if not st.session_state.current_blueprint_id:
    bps = list_blueprints(limit=1)
    if bps:
        st.session_state.current_blueprint_id = bps[0]["id"]
        st.session_state.full_bp_state = "complete"

# ── Header ───────────────────────────────────────────────────────────────────
st.markdown("""
<div style="margin-bottom:24px; display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:12px;">
    <div>
        <div class="section-tag">Workspace & Innovation Hub</div>
        <h1 style="font-family:'Space Grotesk',sans-serif;font-size:2.2rem;font-weight:700;
                   letter-spacing:-0.04em;color:#EEEEF6;margin:6px 0 0 0;">
            Dream Machine Studio
        </h1>
        <div style="font-size:14px;color:#A0A0BC;line-height:1.4;">
            Speak, type, organize notes, set reminders, and engineer plans instantly.
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Input Area (Top Block) ───────────────────────────────────────────────────
with st.container():
    st.markdown('<div class="dream-card" style="margin-bottom:20px; padding:20px;">', unsafe_allow_html=True)
    
    # Text Input
    idea_text = st.text_area(
        "DESCRIBE YOUR IDEA OR PERSONAL NOTE",
        value=st.session_state.capture_text,
        height=100,
        placeholder="Type your startup idea, a workflow problem, or a reminder here...",
        label_visibility="collapsed",
        key="capture_text_area",
        help="Type or speak. Use the tabs below to convert this input into different formats."
    )
    if idea_text != st.session_state.capture_text:
        st.session_state.capture_text = idea_text

    # Voice Input & Controls Row
    col_v1, col_v2, col_clear = st.columns([3, 3, 2], gap="small")
    
    with col_v1:
        # Standard Audio Input Widget
        audio_val = None
        try:
            audio_val = st.audio_input(
                "Record Voice",
                label_visibility="collapsed",
                key="audio_input_widget"
            )
        except AttributeError:
            # Fallback file upload
            uploaded = st.file_uploader(
                "Upload audio",
                type=["wav", "mp3", "ogg", "m4a", "webm"],
                label_visibility="collapsed",
                key="audio_upload_fallback"
            )
            if uploaded:
                audio_val = uploaded

        if audio_val:
            audio_bytes = audio_val.read()
            with st.spinner("🎤 Transcribing..."):
                transcript = transcribe_audio_bytes(audio_bytes)
            if transcript and not transcript.startswith("["):
                st.session_state.capture_text = transcript
                st.session_state.capture_text_area = transcript
                st.toast("Voice note transcribed! 🎤")
                st.rerun()

    with col_v2:
        # Live Web Speech API Recorder (for Chrome/Edge users with direct copy redirect)
        VOICE_COMPONENT_HTML = """
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body { font-family: 'Inter', sans-serif; background: transparent; color: #EEEEF6; }
  .controls { display: flex; gap: 8px; align-items: center; }
  #start-btn, #stop-btn {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 8px 16px;
    border-radius: 8px;
    border: none;
    font-family: inherit;
    font-size: 13px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s ease;
    height: 38px;
  }
  #start-btn { background: rgba(92,107,255,0.15); border: 1px solid rgba(92,107,255,0.3); color: #7B88FF; }
  #start-btn:hover { background: rgba(92,107,255,0.25); }
  #stop-btn { background: #FF4060; color: white; display: none; }
  .status { font-size: 11px; color: #5A5A78; font-family: monospace; text-transform: uppercase; letter-spacing: 0.5px; }
  #copy-btn { display: none; padding: 8px 14px; border-radius: 8px; border: 1px solid #00F5D4; background: rgba(0,245,212,0.1); color: #00F5D4; font-size: 13px; font-weight: 600; cursor: pointer; height: 38px; }
</style>
</head>
<body>
  <div class="controls">
    <button id="start-btn" onclick="startListening()">🎤 Streaming Record</button>
    <button id="stop-btn" onclick="stopListening()">⏹ Stop</button>
    <button id="copy-btn" onclick="copyTranscript()">✓ Apply</button>
    <span class="status" id="status-text">Ready</span>
  </div>
<script>
  let recognition = null;
  let finalTranscript = '';
  let isSupported = false;
  if ('SpeechRecognition' in window || 'webkitSpeechRecognition' in window) {
    isSupported = true;
    recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
    recognition.continuous = true;
    recognition.interimResults = true;
    recognition.lang = 'en-US';
    recognition.onresult = function(event) {
      let interim = '';
      for (let i = event.resultIndex; i < event.results.length; i++) {
        if (event.results[i].isFinal) finalTranscript += event.results[i][0].transcript + ' ';
        else interim += event.results[i][0].transcript;
      }
      document.getElementById('status-text').textContent = 'Listening...';
    };
    recognition.onerror = function(e) {
      document.getElementById('status-text').textContent = 'Error: ' + e.error;
    };
  } else {
    document.getElementById('start-btn').style.display = 'none';
    document.getElementById('status-text').textContent = 'Web Speech not supported';
  }
  function startListening() {
    if (!isSupported) return;
    finalTranscript = '';
    document.getElementById('start-btn').style.display = 'none';
    document.getElementById('stop-btn').style.display = 'inline-flex';
    document.getElementById('copy-btn').style.display = 'none';
    document.getElementById('status-text').textContent = 'Recording...';
    recognition.start();
  }
  function stopListening() {
    if (recognition) recognition.stop();
    document.getElementById('stop-btn').style.display = 'none';
    document.getElementById('start-btn').style.display = 'inline-flex';
    document.getElementById('status-text').textContent = 'Done';
    if (finalTranscript.trim()) {
      document.getElementById('copy-btn').style.display = 'inline-flex';
    }
  }
  function copyTranscript() {
    if (!finalTranscript.trim()) return;
    const parentUrl = new URL(window.top.location.href);
    parentUrl.searchParams.set("voice_transcript", finalTranscript.trim());
    window.top.location.href = parentUrl.toString();
  }
</script>
</body>
</html>
"""
        if components:
            components.html(VOICE_COMPONENT_HTML, height=44)

    with col_clear:
        if st.button("🗑️ Clear Inputs", use_container_width=True, key="clear_workspace_inputs"):
            st.session_state.capture_text = ""
            st.session_state.capture_text_area = ""
            st.session_state.capture_result = None
            st.session_state.capture_mindmap = ""
            st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

# ── Unified Tabs ─────────────────────────────────────────────────────────────
tab_mini, tab_map, tab_full, tab_reminders = st.tabs([
    "🧠 Mini Blueprint", 
    "🗺️ Mind Map", 
    "🚀 Full Blueprint", 
    "🔔 Personal Notes & Reminders"
])

# ─────────────────────────────────────────────────────────────────────────────
# TAB 1: MINI BLUEPRINT
# ─────────────────────────────────────────────────────────────────────────────
with tab_mini:
    st.markdown('<div style="padding:10px 0;"></div>', unsafe_allow_html=True)
    if not st.session_state.capture_text.strip():
        st.info("💡 Type or record an idea in the input block above to generate a Mini Blueprint.")
    else:
        result = st.session_state.capture_result
        if not result:
            col_g, _ = st.columns([2, 2])
            with col_g:
                if st.button("✦ Generate Mini Blueprint", type="primary", use_container_width=True):
                    with st.spinner("Analyzing and constructing Mini Blueprint..."):
                        idea_type = detect_idea_type(st.session_state.capture_text)
                        result = generate_mini_blueprint(st.session_state.capture_text, idea_type)
                        st.session_state.capture_result = result
                        save_capture(st.session_state.capture_text, "text", str(result), "")
                        st.toast("Mini Blueprint ready! 🧠")
                        st.rerun()
        else:
            # Display Mini Blueprint
            st.markdown(f"""
            <div class="mini-bp-card">
                <div style="font-family:'JetBrains Mono',monospace;font-size:11px;color:#00F5D4;text-transform:uppercase;letter-spacing:2px;margin-bottom:8px;">
                    ✦ Instant Innovation
                </div>
                <div style="font-family:'Space Grotesk',sans-serif;font-size:1.3rem;font-weight:700;color:#EEEEF6;line-height:1.4;letter-spacing:-0.02em;">
                    "{result.get('one_liner', '')}"
                </div>
            </div>
            """, unsafe_allow_html=True)

            sec_cols = st.columns(2)
            with sec_cols[0]:
                st.markdown(f"""
                <div style="background:rgba(255,100,80,0.04);border:1px solid rgba(255,100,80,0.14);border-radius:12px;padding:16px;margin-bottom:12px;">
                    <div style="font-size:10px;color:#FF6450;text-transform:uppercase;letter-spacing:1.5px;font-family:'JetBrains Mono',monospace;margin-bottom:8px;">🔴 Problem</div>
                    <div style="font-size:13px;color:#B0B0C8;line-height:1.6;">{result.get('problem', '')}</div>
                </div>
                """, unsafe_allow_html=True)

                st.markdown(f"""
                <div style="background:rgba(0,245,212,0.04);border:1px solid rgba(0,245,212,0.14);border-radius:12px;padding:16px;margin-bottom:12px;">
                    <div style="font-size:10px;color:#00F5D4;text-transform:uppercase;letter-spacing:1.5px;font-family:'JetBrains Mono',monospace;margin-bottom:8px;">✅ Solution</div>
                    <div style="font-size:13px;color:#B0B0C8;line-height:1.6;">{result.get('solution', '')}</div>
                </div>
                """, unsafe_allow_html=True)

            with sec_cols[1]:
                features = result.get("top_features", [])
                features_html = "".join(
                    f'<div style="display:flex;gap:8px;align-items:flex-start;margin-bottom:6px;">'
                    f'<span style="color:#5C6BFF;flex-shrink:0;margin-top:2px;">◆</span>'
                    f'<span style="font-size:13px;color:#B0B0C8;line-height:1.5;">{f}</span>'
                    f'</div>'
                    for f in features[:5]
                )
                st.markdown(f"""
                <div style="background:rgba(92,107,255,0.04);border:1px solid rgba(92,107,255,0.14);border-radius:12px;padding:16px;margin-bottom:12px;">
                    <div style="font-size:10px;color:#7B88FF;text-transform:uppercase;letter-spacing:1.5px;font-family:'JetBrains Mono',monospace;margin-bottom:10px;">⚡ Top Features</div>
                    {features_html}
                </div>
                """, unsafe_allow_html=True)

                st.markdown(f"""
                <div style="background:rgba(255,184,0,0.04);border:1px solid rgba(255,184,0,0.14);border-radius:12px;padding:16px;margin-bottom:12px;">
                    <div style="font-size:10px;color:#FFB800;text-transform:uppercase;letter-spacing:1.5px;font-family:'JetBrains Mono',monospace;margin-bottom:8px;">💰 Business Model</div>
                    <div style="font-size:13px;color:#B0B0C8;line-height:1.6;">{result.get('business_model', '')}</div>
                </div>
                """, unsafe_allow_html=True)

            st.markdown(f"""
            <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-top:4px;">
                <div style="background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.06);border-radius:12px;padding:14px;">
                    <div style="font-size:10px;color:#5A5A78;text-transform:uppercase;letter-spacing:1.5px;font-family:'JetBrains Mono',monospace;margin-bottom:6px;">👤 Target User</div>
                    <div style="font-size:13px;color:#B0B0C8;line-height:1.5;">{result.get('target_user', '')}</div>
                </div>
                <div style="background:rgba(0,245,212,0.05);border:1px solid rgba(0,245,212,0.18);border-radius:12px;padding:14px;">
                    <div style="font-size:10px;color:#00F5D4;text-transform:uppercase;letter-spacing:1.5px;font-family:'JetBrains Mono',monospace;margin-bottom:6px;">🎯 Next Step</div>
                    <div style="font-size:13px;color:#B0B0C8;line-height:1.5;font-weight:500;">{result.get('next_step', '')}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)
            exp_col1, exp_col2 = st.columns(2)
            with exp_col1:
                export_text = f"""# Mini Blueprint: {result.get('one_liner', '')}
**Problem:** {result.get('problem', '')}
**Solution:** {result.get('solution', '')}
**Top Features:**
{chr(10).join(f'- {f}' for f in features)}
**Target User:** {result.get('target_user', '')}
**Business Model:** {result.get('business_model', '')}
**Next Step:** {result.get('next_step', '')}
"""
                st.download_button(
                    "📥 Export Mini Blueprint",
                    data=export_text,
                    file_name="mini_blueprint.md",
                    mime="text/markdown",
                    use_container_width=True
                )
            with exp_col2:
                if st.button("🗑️ Reset Mini Blueprint", use_container_width=True):
                    st.session_state.capture_result = None
                    st.rerun()

# ─────────────────────────────────────────────────────────────────────────────
# TAB 2: MIND MAP
# ─────────────────────────────────────────────────────────────────────────────
with tab_map:
    st.markdown('<div style="padding:10px 0;"></div>', unsafe_allow_html=True)
    if not st.session_state.capture_text.strip():
        st.info("💡 Type or record an idea in the input block above to generate a Mind Map.")
    else:
        mindmap = st.session_state.capture_mindmap
        if not mindmap:
            col_m, _ = st.columns([2, 2])
            with col_m:
                if st.button("🗺️ Generate Mind Map", type="primary", use_container_width=True):
                    with st.spinner("Creating mind map flowchart..."):
                        idea_type = detect_idea_type(st.session_state.capture_text)
                        mindmap = generate_mindmap(st.session_state.capture_text, idea_type)
                        st.session_state.capture_mindmap = mindmap
                        save_capture(st.session_state.capture_text, "text", "", mindmap)
                        st.toast("Mind Map ready! 🗺️")
                        st.rerun()
        else:
            escaped_mindmap = mindmap.replace("`", "&#96;").replace("\\", "\\\\")
            mermaid_html = f"""
<!DOCTYPE html>
<html>
<head>
<script type="module">
  import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.esm.min.mjs';
  mermaid.initialize({{
    startOnLoad: true,
    theme: 'dark',
    themeVariables: {{
      primaryColor: '#5C6BFF',
      primaryTextColor: '#EEEEF6',
      primaryBorderColor: '#5C6BFF',
      lineColor: '#5C6BFF',
      secondaryColor: '#0C0C1A',
      tertiaryColor: '#0C0C1A',
      background: '#07070F',
      nodeBorder: '#5C6BFF',
      edgeLabelBackground: '#0C0C1A',
      fontFamily: 'Inter, sans-serif',
      fontSize: '14px'
    }}
  }});
</script>
<style>
  * {{ margin: 0; padding: 0; }}
  body {{ background: transparent; display: flex; align-items: center; justify-content: center; min-height: 400px; }}
  .mermaid {{ width: 100%; max-width: 100%; }}
</style>
</head>
<body>
  <div class="mermaid">
{mindmap}
  </div>
</body>
</html>
"""
            if components:
                components.html(mermaid_html, height=450, scrolling=True)
            else:
                st.code(mindmap, language="text")

            st.markdown("<br>", unsafe_allow_html=True)
            m_col1, m_col2 = st.columns(2)
            with m_col1:
                st.download_button(
                    "📥 Export Mermaid Code",
                    data=mindmap,
                    file_name="mindmap.mmd",
                    mime="text/plain",
                    use_container_width=True
                )
            with m_col2:
                if st.button("🗑️ Reset Mind Map", use_container_width=True):
                    st.session_state.capture_mindmap = ""
                    st.rerun()

# ─────────────────────────────────────────────────────────────────────────────
# TAB 3: FULL BLUEPRINT
# ─────────────────────────────────────────────────────────────────────────────
with tab_full:
    st.markdown('<div style="padding:10px 0;"></div>', unsafe_allow_html=True)
    
    if not st.session_state.capture_text.strip():
        st.info("💡 Type or record an idea in the input block above to build a Full Blueprint.")
    else:
        # Check current state of blueprint flow
        if st.session_state.full_bp_state == "not_started":
            st.markdown("""
            <div style="background:rgba(92,107,255,0.04); border:1px solid var(--color-border); border-radius:12px; padding:24px; text-align:center;">
                <h3 style="margin-top:0;">🚀 Start Full Engineering Flow</h3>
                <p style="font-size:14px; color:#A0A0BC; max-width:550px; margin:8px auto 20px;">
                    This launches a 6-question discovery session followed by a live, structured 10-section startup & architecture blueprint generation using Gemini.
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            col_start, _ = st.columns([2, 2])
            with col_start:
                if st.button("✦ Start Discovery Session", type="primary", use_container_width=True):
                    with st.spinner("Initializing questions..."):
                        idea_type = detect_idea_type(st.session_state.capture_text)
                        questions = generate_questions(st.session_state.capture_text, idea_type)
                        st.session_state.full_bp_questions = questions
                        st.session_state.full_bp_answers = {}
                        st.session_state.full_bp_current_q = 0
                        st.session_state.full_bp_state = "questions"
                        st.rerun()
                        
        elif st.session_state.full_bp_state == "questions":
            questions = st.session_state.full_bp_questions
            current_q = st.session_state.full_bp_current_q
            total_q = len(questions)
            progress = current_q / total_q if total_q > 0 else 0
            
            # Progress bar
            st.markdown(f"""
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
                <span style="font-family:'JetBrains Mono',monospace; font-size:11px; color:#00F5D4; text-transform:uppercase;">
                    Question {min(current_q + 1, total_q)} of {total_q}
                </span>
                <span style="font-size:12px; color:#A0A0BC;">
                    {int(progress * 100)}% complete
                </span>
            </div>
            """, unsafe_allow_html=True)
            st.progress(progress)
            
            if current_q < total_q:
                q = questions[current_q]
                q_text = q.get("question", "")
                options = q.get("options", [])
                placeholder = q.get("placeholder", "Type your response...")
                
                st.markdown(f"""
                <div class="question-card" style="margin:16px 0;">
                    <div class="question-number">◆ Discovery Step {current_q + 1}</div>
                    <div class="question-text" style="font-size:1.1rem; font-weight:600; color:#EEEEF6; margin-top:6px;">{q_text}</div>
                </div>
                """, unsafe_allow_html=True)
                
                chip_key = f"full_chip_{current_q}"
                if chip_key not in st.session_state:
                    st.session_state[chip_key] = None
                
                # Chips
                if options:
                    st.markdown("<div style='margin-bottom:12px;'>", unsafe_allow_html=True)
                    chip_cols = st.columns(min(len(options), 4))
                    for idx, opt in enumerate(options):
                        with chip_cols[idx % len(chip_cols)]:
                            selected = st.session_state[chip_key] == opt
                            btn_label = f"✓ {opt}" if selected else opt
                            if st.button(btn_label, key=f"full_chip_btn_{current_q}_{idx}", use_container_width=True, type="primary" if selected else "secondary"):
                                st.session_state[chip_key] = opt
                                st.session_state.full_bp_answers[q_text] = opt
                                st.rerun()
                    st.markdown("</div>", unsafe_allow_html=True)
                
                # Input
                custom_ans = st.text_input(
                    "Custom answer",
                    label_visibility="collapsed",
                    placeholder=placeholder,
                    key=f"full_custom_{current_q}",
                    value=st.session_state.full_bp_answers.get(q_text, "") if st.session_state[chip_key] is None else ""
                )
                if custom_ans:
                    st.session_state.full_bp_answers[q_text] = custom_ans
                    st.session_state[chip_key] = None
                
                # Nav buttons
                st.markdown("<br>", unsafe_allow_html=True)
                nav_c1, nav_c2, nav_c3 = st.columns([1, 2, 1])
                with nav_c1:
                    if current_q > 0:
                        if st.button("← Back", use_container_width=True, key="full_bp_back"):
                            st.session_state.full_bp_current_q -= 1
                            st.rerun()
                with nav_c2:
                    is_answered = q_text in st.session_state.full_bp_answers and st.session_state.full_bp_answers[q_text]
                    next_label = "Next Question →" if current_q < total_q - 1 else "⚡ Generate Full Blueprint"
                    if st.button(next_label, type="primary" if is_answered else "secondary", use_container_width=True, key="full_bp_next"):
                        if not is_answered:
                            st.session_state.full_bp_answers[q_text] = "(skipped)"
                        
                        if current_q < total_q - 1:
                            st.session_state.full_bp_current_q += 1
                            st.rerun()
                        else:
                            st.session_state.full_bp_state = "generating"
                            st.rerun()
                with nav_c3:
                    if st.button("Skip →", use_container_width=True, key="full_bp_skip"):
                        st.session_state.full_bp_answers[q_text] = "(skipped)"
                        if current_q < total_q - 1:
                            st.session_state.full_bp_current_q += 1
                        else:
                            st.session_state.full_bp_state = "generating"
                        st.rerun()
            
        elif st.session_state.full_bp_state == "generating":
            st.markdown('<div class="dream-card">', unsafe_allow_html=True)
            st.markdown('<div class="section-tag">Generating Full System Blueprint</div>', unsafe_allow_html=True)
            
            # Placeholders
            progress_status = st.empty()
            checklist_container = st.container()
            live_out = st.empty()
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Setup checklist UI
            check_nodes = {}
            with checklist_container:
                for key, label in SECTIONS:
                    check_nodes[key] = st.empty()
                    check_nodes[key].markdown(f'<div class="gen-item"><div class="gen-dot"></div><span>{label}</span></div>', unsafe_allow_html=True)
            
            # Generation process
            idea = st.session_state.capture_text
            idea_type = detect_idea_type(idea)
            answers = st.session_state.full_bp_answers
            
            bid = create_blueprint(idea, idea_type, answers)
            st.session_state.current_blueprint_id = bid
            sections_data = {}
            total_sec = len(SECTIONS)
            
            for idx, (key, label) in enumerate(SECTIONS):
                # Active
                check_nodes[key].markdown(f'<div class="gen-item active"><div class="gen-dot active"></div><span style="color:#EEEEF6; font-weight:500;">⟳ {label}</span></div>', unsafe_allow_html=True)
                progress_status.markdown(f'<div style="font-size:12px; color:#A0A0BC; text-align:center;">Section {idx+1}/{total_sec} · {label}</div>', unsafe_allow_html=True)
                
                with live_out.container():
                    st.markdown(f'<div class="blueprint-section" style="animation:none;"><div class="blueprint-section-title">{label}</div>', unsafe_allow_html=True)
                    text_placeholder = st.empty()
                    try:
                        section_text = generate_section_sync(idea, idea_type, answers, key)
                        sections_data[key] = section_text
                        text_placeholder.markdown(section_text[:500] + ("..." if len(section_text) > 500 else ""))
                    except Exception as e:
                        sections_data[key] = f"*Error generating {label}: {e}*"
                        st.error(str(e))
                    st.markdown("</div>", unsafe_allow_html=True)
                
                # Done
                check_nodes[key].markdown(f'<div class="gen-item done"><div class="gen-dot done"></div><span>✓ {label}</span></div>', unsafe_allow_html=True)
            
            update_blueprint_sections(bid, sections_data)
            
            # Title & Mockup
            progress_status.markdown('<div style="font-size:12px; color:#5C6BFF; text-align:center;">Crafting catchy name & interface...</div>', unsafe_allow_html=True)
            try:
                ai_title = generate_title(idea, idea_type)
                update_blueprint_title(bid, ai_title)
                mock_html = generate_mockup(idea, idea_type, answers)
                update_blueprint_mockup(bid, mock_html)
            except Exception:
                pass
            
            st.session_state.full_bp_state = "complete"
            st.toast("Full Blueprint Generated! 🚀")
            st.rerun()
            
        elif st.session_state.full_bp_state == "complete":
            bid = st.session_state.current_blueprint_id
            bp = get_blueprint(bid)
            if not bp:
                st.error("Blueprint could not be loaded.")
                if st.button("Restart"):
                    st.session_state.full_bp_state = "not_started"
                    st.rerun()
            else:
                sections = bp.get("sections", {})
                idea = bp.get("idea", "")
                idea_type = bp.get("idea_type", "Other")
                title = bp.get("title", "Product Blueprint")
                icon = IDEA_TYPE_ICONS.get(idea_type, "💡")
                
                # Header card
                st.markdown(f"""
                <div style="background:rgba(255,255,255,0.02); border:1px solid var(--color-border); border-radius:12px; padding:18px 24px; margin-bottom:16px;">
                    <div class="idea-type-pill" style="margin-bottom:8px;">{icon} {idea_type}</div>
                    <h2 style="margin:4px 0; font-size:1.6rem; color:#EEEEF6;">{title}</h2>
                    <p style="font-size:13px; color:#A0A0BC; line-height:1.5; margin:4px 0 0 0;">{idea}</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Links / Actions row
                col_lnk1, col_lnk2, col_lnk3, col_lnk4, col_lnk5 = st.columns(5)
                with col_lnk1:
                    pdf_bytes = export_pdf_bytes(bp)
                    st.download_button("📄 PDF Export", data=pdf_bytes, file_name=f"blueprint_{bid[:8]}.pdf", mime="application/pdf", use_container_width=True)
                with col_lnk2:
                    md_text = export_markdown(bp)
                    st.download_button("📝 MD Export", data=md_text, file_name=f"blueprint_{bid[:8]}.md", mime="text/markdown", use_container_width=True)
                with col_lnk3:
                    if st.button("🎨 Wireframe Mockup", use_container_width=True):
                        st.switch_page("pages/4_Mockup.py")
                with col_lnk4:
                    if st.button("📃 Investor Pitch", use_container_width=True):
                        st.switch_page("pages/8_Pitch.py")
                with col_lnk5:
                    if st.button("⚡ Compare Ideas", use_container_width=True):
                        st.switch_page("pages/9_Compare.py")
                
                st.markdown("<br>", unsafe_allow_html=True)
                
                # Split layout inside tab: 3/5 Viewer, 2/5 Advisor Chat
                view_col, chat_col = st.columns([3, 2], gap="large")
                
                with view_col:
                    st.markdown('<div class="section-tag">System Blueprint Document</div>', unsafe_allow_html=True)
                    
                    # Section list selectbox or sub-tabs
                    sec_list = [
                        ("executive_summary", "📋 Executive Summary"),
                        ("user_personas", "👥 User Personas"),
                        ("core_features", "⚡ Core Feature List"),
                        ("architecture", "🏗️ System Architecture"),
                        ("tech_stack", "🔧 Recommended Tech Stack"),
                        ("roadmap", "🗓️ Implementation Roadmap"),
                        ("business_model", "💰 Pricing & Business Model"),
                        ("risk_analysis", "⚠️ Risks & Mitigation"),
                        ("competitor_landscape", "🏁 Competitors & Edge"),
                        ("success_metrics", "📊 Success Metrics"),
                    ]
                    
                    selected_sec_key = st.selectbox(
                        "SELECT SECTION TO VIEW",
                        [s[1] for s in sec_list],
                        label_visibility="collapsed"
                    )
                    selected_key = [s[0] for s in sec_list if s[1] == selected_sec_key][0]
                    content = sections.get(selected_key, "")
                    
                    st.markdown(f'<div class="blueprint-section" style="margin-top:10px; min-height:300px; padding:20px; border:1px solid rgba(255,255,255,0.05); background:rgba(255,255,255,0.01); border-radius:8px;">', unsafe_allow_html=True)
                    st.markdown(content if content else "*Section not generated.*")
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                    if st.button("🗑️ Start New Blueprint", key="restart_bp_flow"):
                        st.session_state.full_bp_state = "not_started"
                        st.session_state.current_blueprint_id = None
                        st.rerun()
                
                with chat_col:
                    st.markdown('<div class="section-tag">🤖 AI Advisor Chat</div>', unsafe_allow_html=True)
                    
                    # Advisor Chat Box
                    chat_history = get_chat_history(bid, limit=20)
                    chat_box = st.container(height=280)
                    
                    with chat_box:
                        if not chat_history:
                            st.markdown("""
                            <div style="text-align:center; padding:30px 10px; color:#6B6B8A; font-size:13px;">
                                Discuss scaling, UX design, launch strategies, or security architecture with your AI Advisor:
                            </div>
                            """, unsafe_allow_html=True)
                        else:
                            for msg in chat_history:
                                if msg["role"] == "user":
                                    st.markdown(f'<div class="chat-bubble-user">{msg["content"]}</div>', unsafe_allow_html=True)
                                else:
                                    st.markdown(f'<div class="chat-bubble-ai">🤖 {msg["content"]}</div>', unsafe_allow_html=True)
                                    
                    user_msg = st.chat_input("Ask advice...", key="advisor_chat_input")
                    if user_msg:
                        save_chat_message(bid, "user", user_msg)
                        with st.spinner("Thinking..."):
                            resp = "".join(stream_chat(idea, idea_type, sections, get_chat_history(bid, limit=8), user_msg))
                        save_chat_message(bid, "assistant", resp)
                        st.rerun()
                        
                    if chat_history:
                        if st.button("🗑️ Clear Chat", key="clear_advisor_chat", use_container_width=True):
                            clear_chat_history(bid)
                            st.rerun()

# ─────────────────────────────────────────────────────────────────────────────
# TAB 4: PERSONAL NOTES & REMINDERS
# ─────────────────────────────────────────────────────────────────────────────
with tab_reminders:
    st.markdown('<div style="padding:10px 0;"></div>', unsafe_allow_html=True)
    
    col_frm, col_lst = st.columns([1, 1], gap="large")
    
    with col_frm:
        st.markdown('<div class="section-tag">📌 Take Notes & Set Reminders</div>', unsafe_allow_html=True)
        
        # Note Text
        note_val = st.text_area(
            "Note / Reminder Text",
            value=st.session_state.capture_text,
            height=80,
            placeholder="Important reminder details..."
        )
        
        # Importance
        imp_level = st.selectbox(
            "Importance Level",
            ["Low 🟢", "Medium 🟡", "High 🟠", "Urgent 🔴"],
            index=1
        )
        
        # Target reminder time
        col_d, col_t = st.columns(2)
        with col_d:
            remind_date = st.date_input("Date", value=datetime.now().date())
        with col_t:
            remind_time = st.time_input("Time", value=(datetime.now() + timedelta(minutes=5)).time())
            
        if st.button("💾 Save Reminder Note", type="primary", use_container_width=True):
            if not note_val.strip():
                st.error("Please enter note content.")
            else:
                # Construct trigger time
                trigger_dt = datetime.combine(remind_date, remind_time)
                trigger_iso = trigger_dt.isoformat()
                
                # Strip emojis from importance for clean storage
                imp_clean = imp_level.split(" ")[0]
                
                create_reminder(note_val.strip(), imp_clean, trigger_iso)
                st.success("Reminder note saved! 🔔")
                time.sleep(0.5)
                st.rerun()
                
    with col_lst:
        st.markdown('<div class="section-tag">📋 Active Reminders</div>', unsafe_allow_html=True)
        
        all_reminders = list_reminders(limit=50)
        active_reminders = [r for r in all_reminders if not r["is_notified"]]
        completed_reminders = [r for r in all_reminders if r["is_notified"]]
        
        if not active_reminders:
            st.markdown('<div style="font-size:13px; color:#5A5A78; padding:10px 0;">No active reminders.</div>', unsafe_allow_html=True)
        else:
            for r in active_reminders:
                # Color code importance
                border_clr = {
                    "Urgent": "#FF6450",
                    "High": "#FFB800",
                    "Medium": "#5C6BFF",
                    "Low": "#00F5D4"
                }.get(r["importance"], "#5A5A78")
                
                # Format remind time
                remind_dt = datetime.fromisoformat(r["remind_at"])
                time_str = remind_dt.strftime("%b %d, %Y at %I:%M %p")
                
                st.markdown(f"""
                <div style="background:rgba(255,255,255,0.02); border-left:3px solid {border_clr}; border-radius:6px; padding:12px; margin-bottom:8px;">
                    <div style="display:flex; justify-content:space-between; margin-bottom:4px;">
                        <span style="font-size:11px; font-weight:700; color:{border_clr}; text-transform:uppercase; font-family:'JetBrains Mono',monospace;">{r['importance']}</span>
                        <span style="font-size:11px; color:#6B6B8A;">⏰ {time_str}</span>
                    </div>
                    <div style="font-size:13px; color:#EEEEF6; line-height:1.4;">{r['note_text']}</div>
                </div>
                """, unsafe_allow_html=True)
                
                # Quick actions row
                c_act1, c_act2 = st.columns(2)
                with c_act1:
                    if st.button("Complete ✓", key=f"done_rem_{r['id']}", use_container_width=True):
                        mark_reminder_notified(r["id"])
                        st.toast("Reminded!")
                        st.rerun()
                with c_act2:
                    if st.button("Delete 🗑️", key=f"del_rem_{r['id']}", use_container_width=True):
                        delete_reminder(r["id"])
                        st.toast("Deleted")
                        st.rerun()
                        
        if completed_reminders:
            with st.expander("Completed / Past Reminders", expanded=False):
                for r in completed_reminders[:15]:
                    st.markdown(f"""
                    <div style="font-size:12px; color:#5A5A78; text-decoration:line-through; margin-bottom:6px;">
                        • {r['note_text']} ({r['importance']})
                    </div>
                    """, unsafe_allow_html=True)
                    if st.button("Delete Permanent 🗑️", key=f"del_past_rem_{r['id']}", use_container_width=True):
                        delete_reminder(r["id"])
                        st.rerun()

# ── Background Notification Worker (Outside Tabs) ───────────────────────────
all_reminders = list_reminders(limit=50)
active_reminders = [r for r in all_reminders if not r["is_notified"]]

js_reminders = []
for r in active_reminders:
    js_reminders.append({
        "id": r["id"],
        "note_text": r["note_text"].replace('"', '\\"').replace('\n', ' '),
        "remind_at": r["remind_at"]
    })
js_reminders_json = json.dumps(js_reminders)

BACKGROUND_WORKER_HTML = """
<!DOCTYPE html>
<html>
<head>
<style>
  body { margin: 0; padding: 0; background: transparent; font-family: -apple-system, BlinkMacSystemFont, sans-serif; }
  .notify-btn {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 8px 16px;
    background: rgba(92,107,255,0.15);
    border: 1px solid rgba(92,107,255,0.3);
    border-radius: 8px;
    color: #7B88FF;
    font-size: 13px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s ease;
  }
  .notify-btn:hover { background: rgba(92,107,255,0.25); }
  .status { font-size: 12px; color: #5A5A78; }
</style>
</head>
<body>
  <div id="permission-box" style="display: none; align-items: center; gap: 12px; padding: 10px 0;">
    <button class="notify-btn" onclick="requestPermission()">🔔 Enable Desktop Notifications</button>
    <span class="status">Required to receive reminders on this device</span>
  </div>
  <div id="status-box" class="status" style="display: none; padding: 4px 0;">
    ✓ Desktop notifications active
  </div>
  <script>
    const reminders = """ + js_reminders_json + """;
    
    function checkPermissions() {
      if (!("Notification" in window)) return;
      if (Notification.permission === "granted") {
        document.getElementById("status-box").style.display = "block";
      } else if (Notification.permission !== "denied") {
        document.getElementById("permission-box").style.display = "flex";
      }
    }
    
    function requestPermission() {
      Notification.requestPermission().then(permission => {
        if (permission === "granted") {
          document.getElementById("permission-box").style.display = "none";
          document.getElementById("status-box").style.display = "block";
          playChime();
          new Notification("Reminders Active!", {
            body: "You will receive desktop notifications for your notes.",
            icon: "https://cdn-icons-png.flaticon.com/512/3602/3602145.png"
          });
        }
      });
    }
    function playChime() {
      try {
        const ctx = new (window.AudioContext || window.webkitAudioContext)();
        const osc1 = ctx.createOscillator();
        const osc2 = ctx.createOscillator();
        const gain = ctx.createGain();
        osc1.type = 'sine';
        osc1.frequency.setValueAtTime(587.33, ctx.currentTime);
        osc1.frequency.exponentialRampToValueAtTime(880.00, ctx.currentTime + 0.15);
        osc2.type = 'triangle';
        osc2.frequency.setValueAtTime(587.33, ctx.currentTime);
        osc2.frequency.exponentialRampToValueAtTime(880.00, ctx.currentTime + 0.15);
        gain.gain.setValueAtTime(0.35, ctx.currentTime);
        gain.gain.exponentialRampToValueAtTime(0.01, ctx.currentTime + 0.8);
        osc1.connect(gain);
        osc2.connect(gain);
        gain.connect(ctx.destination);
        osc1.start();
        osc2.start();
        osc1.stop(ctx.currentTime + 0.8);
        osc2.stop(ctx.currentTime + 0.8);
      } catch(e) {}
    }
    function checkReminders() {
      if (!reminders || reminders.length === 0) return;
      const now = new Date().getTime();
      for (const r of reminders) {
        if (localStorage.getItem("notified_" + r.id)) {
          continue;
        }
        const triggerTime = new Date(r.remind_at).getTime();
        if (now >= triggerTime) {
          localStorage.setItem("notified_" + r.id, "true");
          if (Notification.permission === "granted") {
            new Notification("Dream Machine Reminder", {
              body: r.note_text,
              requireInteraction: true,
              icon: "https://cdn-icons-png.flaticon.com/512/3602/3602145.png"
            });
          }
          playChime();
          try {
            const parentUrl = new URL(window.top.location.href);
            parentUrl.searchParams.set("notified_reminder_id", r.id);
            window.top.location.href = parentUrl.toString();
          } catch(e) {
            console.log("Redirect blocked, relying on direct manual/session sync.");
          }
          break;
        }
      }
    }
    checkPermissions();
    setInterval(checkReminders, 3000);
  </script>
</body>
</html>
"""
if components:
    st.markdown("<br>", unsafe_allow_html=True)
    components.html(BACKGROUND_WORKER_HTML, height=44)
