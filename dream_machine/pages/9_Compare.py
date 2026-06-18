"""
Dream Machine — Blueprint Comparison Tool
Compare two blueprints side-by-side across all 10 sections.
"""
import streamlit as st
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from components.styles import inject_styles
from components.db import init_db, get_blueprint, list_blueprints
from components.gemini_client import IDEA_TYPE_ICONS

st.set_page_config(
    page_title="Compare Blueprints — Dream Machine",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="collapsed",
)
inject_styles()
init_db()

# ── Header ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="margin-bottom:24px;">
    <div class="section-tag">Blueprint Intelligence</div>
    <h1 style="font-family:'Space Grotesk',sans-serif;font-size:2rem;font-weight:700;
               letter-spacing:-0.03em;color:#E8E8F0;margin:8px 0;">
        Compare Blueprints
    </h1>
    <div style="font-size:14px;color:#6B6B8A;">
        Analyze two ideas side-by-side across all strategy dimensions.
    </div>
</div>
""", unsafe_allow_html=True)

# ── Load Blueprints List ───────────────────────────────────────────────────────
all_bps = list_blueprints(limit=200)

if len(all_bps) < 2:
    st.markdown("""
    <div class="empty-state">
        <div class="empty-state-icon">⚖️</div>
        <div class="empty-state-title">Need at least 2 blueprints</div>
        <div class="empty-state-text">Create a second blueprint to compare them side-by-side.</div>
    </div>
    """, unsafe_allow_html=True)
    if st.button("✦ Create Blueprint", type="primary"):
        st.switch_page("app.py")
    st.stop()

bp_labels = {f"{IDEA_TYPE_ICONS.get(b['idea_type'],'💡')} {b['title'][:55]}": b["id"] for b in all_bps}
label_list = list(bp_labels.keys())

# ── Blueprint Selectors ───────────────────────────────────────────────────────
sel_col1, mid_col, sel_col2 = st.columns([5, 1, 5])

with sel_col1:
    st.markdown('<div class="section-tag">Blueprint A</div>', unsafe_allow_html=True)
    sel_a = st.selectbox("Select first blueprint", label_list, index=0, key="cmp_sel_a",
                         label_visibility="collapsed")

with mid_col:
    st.markdown("""
    <div style="display:flex;align-items:center;justify-content:center;height:70px;
                font-size:24px;color:#5C6BFF;">VS</div>
    """, unsafe_allow_html=True)

with sel_col2:
    st.markdown('<div class="section-tag">Blueprint B</div>', unsafe_allow_html=True)
    default_b = 1 if len(label_list) > 1 else 0
    sel_b = st.selectbox("Select second blueprint", label_list, index=default_b, key="cmp_sel_b",
                         label_visibility="collapsed")

bid_a = bp_labels[sel_a]
bid_b = bp_labels[sel_b]

if bid_a == bid_b:
    st.warning("⚠️ Please select two different blueprints to compare.")
    st.stop()

bp_a = get_blueprint(bid_a)
bp_b = get_blueprint(bid_b)

if not bp_a or not bp_b:
    st.error("Could not load one or both blueprints.")
    st.stop()

st.divider()

# ── Overview Cards ────────────────────────────────────────────────────────────
card_a_col, vs_col, card_b_col = st.columns([5, 1, 5])

def overview_card(bp, color="#5C6BFF"):
    icon = IDEA_TYPE_ICONS.get(bp.get("idea_type", ""), "💡")
    status = bp.get("status", "draft")
    section_count = len([v for v in bp.get("sections", {}).values() if v])
    st.markdown(f"""
    <div style="background:rgba(255,255,255,0.03);border:1px solid {color}33;
                border-left:4px solid {color};border-radius:12px;padding:20px;">
        <div style="font-family:'JetBrains Mono',monospace;font-size:11px;color:{color};
                    text-transform:uppercase;letter-spacing:1.5px;margin-bottom:8px;">
            {icon} {bp.get('idea_type', '')}
        </div>
        <div style="font-family:'Space Grotesk',sans-serif;font-size:1.1rem;font-weight:700;
                    color:#E8E8F0;margin-bottom:8px;line-height:1.3;">
            {bp.get('title', '')[:60]}
        </div>
        <div style="font-size:12px;color:#6B6B8A;line-height:1.5;margin-bottom:12px;">
            {bp.get('idea', '')[:120]}{'...' if len(bp.get('idea','')) > 120 else ''}
        </div>
        <div style="display:flex;gap:12px;">
            <span style="font-size:11px;padding:3px 10px;border-radius:100px;
                         color:{color};background:{color}22;font-weight:600;">
                {status.replace('_',' ')}
            </span>
            <span style="font-size:11px;color:#6B6B8A;">{section_count}/10 sections</span>
            <span style="font-size:11px;color:#6B6B8A;">{bp.get('created_at','')[:10]}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

with card_a_col:
    overview_card(bp_a, "#5C6BFF")

with vs_col:
    st.markdown("""
    <div style="display:flex;align-items:center;justify-content:center;height:120px;">
        <div style="font-family:'Space Grotesk',sans-serif;font-size:13px;font-weight:700;
                    color:#3A3A5A;text-transform:uppercase;letter-spacing:2px;text-align:center;">
            VS
        </div>
    </div>
    """, unsafe_allow_html=True)

with card_b_col:
    overview_card(bp_b, "#00F5D4")

st.markdown("<br>", unsafe_allow_html=True)

# ── Section Comparison ────────────────────────────────────────────────────────
SECTION_META = [
    ("executive_summary", "📋 Executive Summary"),
    ("user_personas", "👥 User Personas"),
    ("core_features", "⚡ Core Features"),
    ("architecture", "🏗️ Architecture"),
    ("tech_stack", "🔧 Tech Stack"),
    ("roadmap", "🗓️ Roadmap"),
    ("business_model", "💰 Business Model"),
    ("risk_analysis", "⚠️ Risk Analysis"),
    ("competitor_landscape", "🏁 Competitors"),
    ("success_metrics", "📊 Success Metrics"),
]

# Section filter
st.markdown('<div class="section-tag">Compare Sections</div>', unsafe_allow_html=True)
section_options = ["All Sections"] + [meta[1] for meta in SECTION_META]
selected_section = st.selectbox(
    "Choose section",
    section_options,
    label_visibility="collapsed",
    key="cmp_section_sel"
)

sections_to_show = SECTION_META if selected_section == "All Sections" else [
    m for m in SECTION_META if m[1] == selected_section
]

secs_a = bp_a.get("sections", {})
secs_b = bp_b.get("sections", {})

for key, title in sections_to_show:
    content_a = secs_a.get(key, "")
    content_b = secs_b.get(key, "")

    if not content_a and not content_b:
        continue

    st.markdown(f"""
    <div style="margin:24px 0 12px;">
        <div style="font-family:'Space Grotesk',sans-serif;font-size:13px;font-weight:600;
                    color:#E8E8F0;display:flex;align-items:center;gap:10px;">
            <span>{title}</span>
            <div style="flex:1;height:1px;background:rgba(92,107,255,0.12);"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    col_a, sep_col, col_b = st.columns([5, 0, 5], gap="medium")

    with col_a:
        if content_a:
            st.markdown(f"""
            <div style="background:rgba(92,107,255,0.04);border:1px solid rgba(92,107,255,0.15);
                        border-left:3px solid #5C6BFF;border-radius:0 10px 10px 0;
                        padding:16px;min-height:80px;">
                <div style="font-size:10px;color:#5C6BFF;font-family:'JetBrains Mono',monospace;
                            text-transform:uppercase;letter-spacing:1px;margin-bottom:8px;">
                    Blueprint A
                </div>
                <div style="font-size:13px;color:#C0C0D8;line-height:1.7;">
                    {content_a[:600]}{'...' if len(content_a) > 600 else ''}
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="background:rgba(255,255,255,0.02);border:1px dashed rgba(92,107,255,0.12);
                        border-radius:10px;padding:16px;text-align:center;color:#3A3A5A;
                        font-size:13px;">Not generated yet</div>
            """, unsafe_allow_html=True)

    with col_b:
        if content_b:
            st.markdown(f"""
            <div style="background:rgba(0,245,212,0.04);border:1px solid rgba(0,245,212,0.15);
                        border-left:3px solid #00F5D4;border-radius:0 10px 10px 0;
                        padding:16px;min-height:80px;">
                <div style="font-size:10px;color:#00F5D4;font-family:'JetBrains Mono',monospace;
                            text-transform:uppercase;letter-spacing:1px;margin-bottom:8px;">
                    Blueprint B
                </div>
                <div style="font-size:13px;color:#C0C0D8;line-height:1.7;">
                    {content_b[:600]}{'...' if len(content_b) > 600 else ''}
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="background:rgba(255,255,255,0.02);border:1px dashed rgba(0,245,212,0.12);
                        border-radius:10px;padding:16px;text-align:center;color:#3A3A5A;
                        font-size:13px;">Not generated yet</div>
            """, unsafe_allow_html=True)

# ── Quick Stats Comparison ────────────────────────────────────────────────────
st.divider()
st.markdown('<div class="section-tag">Quick Comparison</div>', unsafe_allow_html=True)

stat1, stat2, stat3, stat4 = st.columns(4)

def count_words(text):
    if not text:
        return 0
    return len(text.split())

total_words_a = sum(count_words(v) for v in secs_a.values())
total_words_b = sum(count_words(v) for v in secs_b.values())
sections_a_count = len([v for v in secs_a.values() if v])
sections_b_count = len([v for v in secs_b.values() if v])

with stat1:
    st.markdown(f"""
    <div style="background:rgba(255,255,255,0.03);border:1px solid rgba(92,107,255,0.15);
                border-radius:12px;padding:16px;text-align:center;">
        <div style="font-size:11px;color:#6B6B8A;text-transform:uppercase;letter-spacing:1px;
                    font-family:'JetBrains Mono',monospace;margin-bottom:8px;">Sections</div>
        <div style="display:flex;justify-content:center;gap:20px;">
            <div>
                <div style="font-size:1.5rem;font-weight:700;color:#5C6BFF;">{sections_a_count}</div>
                <div style="font-size:11px;color:#6B6B8A;">A</div>
            </div>
            <div style="color:#3A3A5A;font-size:1.5rem;">|</div>
            <div>
                <div style="font-size:1.5rem;font-weight:700;color:#00F5D4;">{sections_b_count}</div>
                <div style="font-size:11px;color:#6B6B8A;">B</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

with stat2:
    st.markdown(f"""
    <div style="background:rgba(255,255,255,0.03);border:1px solid rgba(92,107,255,0.15);
                border-radius:12px;padding:16px;text-align:center;">
        <div style="font-size:11px;color:#6B6B8A;text-transform:uppercase;letter-spacing:1px;
                    font-family:'JetBrains Mono',monospace;margin-bottom:8px;">Total Words</div>
        <div style="display:flex;justify-content:center;gap:20px;">
            <div>
                <div style="font-size:1.5rem;font-weight:700;color:#5C6BFF;">{total_words_a:,}</div>
                <div style="font-size:11px;color:#6B6B8A;">A</div>
            </div>
            <div style="color:#3A3A5A;font-size:1.5rem;">|</div>
            <div>
                <div style="font-size:1.5rem;font-weight:700;color:#00F5D4;">{total_words_b:,}</div>
                <div style="font-size:11px;color:#6B6B8A;">B</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

with stat3:
    a_type = bp_a.get("idea_type", "—")
    b_type = bp_b.get("idea_type", "—")
    st.markdown(f"""
    <div style="background:rgba(255,255,255,0.03);border:1px solid rgba(92,107,255,0.15);
                border-radius:12px;padding:16px;text-align:center;">
        <div style="font-size:11px;color:#6B6B8A;text-transform:uppercase;letter-spacing:1px;
                    font-family:'JetBrains Mono',monospace;margin-bottom:8px;">Idea Type</div>
        <div>
            <div style="font-size:13px;font-weight:600;color:#5C6BFF;margin-bottom:4px;">{a_type}</div>
            <div style="font-size:13px;font-weight:600;color:#00F5D4;">{b_type}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

with stat4:
    a_status = bp_a.get("status", "draft")
    b_status = bp_b.get("status", "draft")
    st.markdown(f"""
    <div style="background:rgba(255,255,255,0.03);border:1px solid rgba(92,107,255,0.15);
                border-radius:12px;padding:16px;text-align:center;">
        <div style="font-size:11px;color:#6B6B8A;text-transform:uppercase;letter-spacing:1px;
                    font-family:'JetBrains Mono',monospace;margin-bottom:8px;">Status</div>
        <div>
            <div style="font-size:13px;font-weight:600;color:#5C6BFF;margin-bottom:4px;">
                {a_status.replace('_',' ').title()}
            </div>
            <div style="font-size:13px;font-weight:600;color:#00F5D4;">
                {b_status.replace('_',' ').title()}
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ── Navigation ─────────────────────────────────────────────────────────────────
st.divider()
nav1, nav2, nav3 = st.columns(3)
with nav1:
    if st.button("← New Idea", use_container_width=True):
        st.switch_page("app.py")
with nav2:
    if st.button("📊 Dashboard", use_container_width=True):
        st.switch_page("pages/5_Dashboard.py")
with nav3:
    if st.button("View Blueprint A →", type="primary", use_container_width=True):
        st.session_state.current_blueprint_id = bid_a
        st.switch_page("pages/3_Blueprint.py")
