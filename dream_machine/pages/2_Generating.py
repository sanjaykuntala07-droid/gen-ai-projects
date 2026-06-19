"""
Dream Machine — Live Generation Screen
Circuit animation + real-time streaming blueprint building.
"""
import streamlit as st
import streamlit.components.v1 as components
import time, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from components.styles import inject_styles
from components.db import init_db, create_blueprint, update_blueprint_sections, update_blueprint_mockup, update_blueprint_title
from components.gemini_client import SECTIONS, generate_section_sync, generate_mockup, IDEA_TYPE_ICONS, generate_title

st.set_page_config(
    page_title="Generating Blueprint — Dream Machine",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="collapsed",
)
inject_styles()
init_db()

# ── Guard ─────────────────────────────────────────────────────────────────────
if not st.session_state.get("idea"):
    st.warning("No idea found. Please start from the home page.")
    if st.button("← Go Home", type="primary"):
        st.switch_page("app.py")
    st.stop()

idea = st.session_state.idea
idea_type = st.session_state.get("idea_type", "Other")
answers = st.session_state.get("answers", {})
icon = IDEA_TYPE_ICONS.get(idea_type, "💡")

# ── Circuit Animation Background ───────────────────────────────────────────────
components.html("""
<style>
#circuit-canvas {
  position: fixed; top: 0; left: 0;
  width: 100vw; height: 100vh;
  z-index: 0; pointer-events: none;
  opacity: 0.35;
}
</style>
<canvas id="circuit-canvas"></canvas>
<script>
const canvas = document.getElementById('circuit-canvas');
const ctx = canvas.getContext('2d');
canvas.width = window.innerWidth;
canvas.height = window.innerHeight;

const nodes = [];
const NUM_NODES = 30;
const PRIMARY = '#5C6BFF';
const ACCENT = '#00F5D4';

for (let i = 0; i < NUM_NODES; i++) {
  nodes.push({
    x: Math.random() * canvas.width,
    y: Math.random() * canvas.height,
    vx: (Math.random() - 0.5) * 0.4,
    vy: (Math.random() - 0.5) * 0.4,
    r: Math.random() * 3 + 2,
    color: Math.random() > 0.5 ? PRIMARY : ACCENT,
    pulse: Math.random() * Math.PI * 2,
  });
}

function draw() {
  ctx.clearRect(0, 0, canvas.width, canvas.height);

  // Draw connections
  for (let i = 0; i < nodes.length; i++) {
    for (let j = i + 1; j < nodes.length; j++) {
      const dx = nodes[i].x - nodes[j].x;
      const dy = nodes[i].y - nodes[j].y;
      const dist = Math.sqrt(dx*dx + dy*dy);
      if (dist < 180) {
        ctx.beginPath();
        ctx.moveTo(nodes[i].x, nodes[i].y);
        ctx.lineTo(nodes[j].x, nodes[j].y);
        const alpha = (1 - dist/180) * 0.5;
        ctx.strokeStyle = `rgba(92,107,255,${alpha})`;
        ctx.lineWidth = 1;
        ctx.stroke();
      }
    }
  }

  // Draw nodes
  nodes.forEach(n => {
    n.pulse += 0.04;
    const radius = n.r + Math.sin(n.pulse) * 1.5;
    ctx.beginPath();
    ctx.arc(n.x, n.y, radius, 0, Math.PI * 2);
    ctx.fillStyle = n.color;
    ctx.shadowBlur = 10;
    ctx.shadowColor = n.color;
    ctx.fill();
    ctx.shadowBlur = 0;

    // Move
    n.x += n.vx;
    n.y += n.vy;
    if (n.x < 0 || n.x > canvas.width) n.vx *= -1;
    if (n.y < 0 || n.y > canvas.height) n.vy *= -1;
  });

  requestAnimationFrame(draw);
}
draw();
window.addEventListener('resize', () => {
  canvas.width = window.innerWidth;
  canvas.height = window.innerHeight;
});
</script>
""", height=0)

# ── Header ─────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div style="text-align:center;padding:40px 0 32px;">
    <div class="hero-eyebrow">✦ Building your dream</div>
    <h1 class="hero-title" style="font-size:2.2rem;margin-bottom:12px;">
        Engineering your <span class="hero-gradient">Blueprint</span>
    </h1>
    <div class="idea-type-pill" style="margin:0 auto;">{icon} {idea_type} · {idea[:60]}{"..." if len(idea) > 60 else ""}</div>
</div>
""", unsafe_allow_html=True)

# ── Two-Column Layout ─────────────────────────────────────────────────────────
left_col, right_col = st.columns([1, 2], gap="large")

with left_col:
    st.markdown('<div class="dream-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-tag">Generation Progress</div>', unsafe_allow_html=True)

    # Status placeholders for checklist
    section_statuses = {}
    for key, label in SECTIONS:
        section_statuses[key] = st.empty()
        section_statuses[key].markdown(f"""
        <div class="gen-item">
            <div class="gen-dot"></div>
            <span>{label}</span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('<br>', unsafe_allow_html=True)
    overall_progress = st.progress(0)
    progress_text = st.empty()
    st.markdown('</div>', unsafe_allow_html=True)

with right_col:
    st.markdown('<div class="section-tag">Live Output</div>', unsafe_allow_html=True)
    live_output = st.empty()

# ── Generation Logic ──────────────────────────────────────────────────────────
if "generation_done" not in st.session_state:
    st.session_state.generation_done = False

if not st.session_state.generation_done:
    # Create blueprint in DB
    bid = create_blueprint(idea, idea_type, answers)
    st.session_state.current_blueprint_id = bid

    sections_data = {}
    total = len(SECTIONS)

    for i, (key, label) in enumerate(SECTIONS):
        # Update checklist — active
        section_statuses[key].markdown(f"""
        <div class="gen-item active">
            <div class="gen-dot active"></div>
            <span style="color:#E8E8F0;font-weight:500;">⟳ {label}</span>
        </div>
        """, unsafe_allow_html=True)

        progress_text.markdown(f"""
        <div style="font-size:12px;color:#6B6B8A;text-align:center;margin-top:8px;">
            Section {i+1} of {total} · {label}
        </div>
        """, unsafe_allow_html=True)

        # Stream the section
        with live_output.container():
            st.markdown(f"""
            <div class="blueprint-section" style="animation:none;">
                <div class="blueprint-section-title">{label}</div>
            """, unsafe_allow_html=True)

            try:
                text_placeholder = st.empty()
                section_text = generate_section_sync(idea, idea_type, answers, key)
                sections_data[key] = section_text
                text_placeholder.markdown(section_text[:800] + ("..." if len(section_text) > 800 else ""))

            except Exception as e:
                sections_data[key] = f"*Generation error: {e}*"
                st.error(f"Error generating {label}: {e}")

            st.markdown("</div>", unsafe_allow_html=True)

        # Mark done
        section_statuses[key].markdown(f"""
        <div class="gen-item done">
            <div class="gen-dot done"></div>
            <span>✓ {label}</span>
        </div>
        """, unsafe_allow_html=True)

        overall_progress.progress((i + 1) / total)

    # Save sections to DB
    update_blueprint_sections(bid, sections_data)
    st.session_state.blueprint_data = sections_data

    # Generate AI title (catchy product name)
    progress_text.markdown('<div style="font-size:12px;color:#5C6BFF;text-align:center;margin-top:8px;">✦ Crafting product name...</div>', unsafe_allow_html=True)
    try:
        ai_title = generate_title(idea, idea_type)
        update_blueprint_title(bid, ai_title)
    except Exception as e:
        import logging
        logging.error(f"Error generating AI title: {e}")

    # Generate mockup
    progress_text.markdown('<div style="font-size:12px;color:#00F5D4;text-align:center;margin-top:8px;">✦ Generating interface mockup...</div>', unsafe_allow_html=True)
    try:
        mockup_html = generate_mockup(idea, idea_type, answers)
        update_blueprint_mockup(bid, mockup_html)
    except Exception as e:
        import logging
        logging.error(f"Error generating mockup HTML: {e}")
        fallback_html = f"""
        <div style="font-family:sans-serif; text-align:center; padding:100px; color:#6B6B8A; background:#0C0C1A; height:100%;">
            <h3>Mockup Generation Unavailable</h3>
            <p>We encountered an issue generating the interactive mockup: {e}</p>
        </div>
        """
        try:
            update_blueprint_mockup(bid, fallback_html)
        except Exception:
            pass

    st.session_state.generation_done = True
    overall_progress.progress(1.0)

    # Complete message
    st.markdown("""
    <div style="text-align:center;padding:32px 0;animation:fadeInUp 0.6s ease;">
        <div style="font-size:48px;margin-bottom:16px;">✦</div>
        <div style="font-family:'Space Grotesk',sans-serif;font-size:1.5rem;font-weight:700;color:#E8E8F0;margin-bottom:8px;">Blueprint Complete!</div>
        <div style="font-size:14px;color:#6B6B8A;">Your complete product blueprint is ready.</div>
    </div>
    """, unsafe_allow_html=True)

    time.sleep(1.5)
    st.switch_page("pages/3_Blueprint.py")

else:
    # Already generated — redirect
    if st.session_state.get("current_blueprint_id"):
        st.success("Blueprint already generated!")
        if st.button("View Blueprint →", type="primary"):
            st.switch_page("pages/3_Blueprint.py")
    else:
        st.info("No blueprint in progress.")
        if st.button("← Start Over", type="primary"):
            st.switch_page("app.py")
