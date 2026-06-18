"""
Dream Machine — Community Gallery
Public blueprints shared by the community.
"""
import streamlit as st
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from components.styles import inject_styles
from components.db import init_db, list_public_blueprints, star_blueprint
from components.gemini_client import IDEA_TYPE_ICONS

st.set_page_config(
    page_title="Gallery — Dream Machine",
    page_icon="✦",
    layout="wide",
)
inject_styles()
init_db()

# ── Header ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="text-align:center;padding:40px 0 24px;">
    <div class="hero-eyebrow">✦ Community</div>
    <h1 style="font-family:'Space Grotesk',sans-serif;font-size:2.2rem;font-weight:700;
               letter-spacing:-0.03em;color:#E8E8F0;margin:12px 0 8px;">
        Idea Gallery
    </h1>
    <div style="font-size:15px;color:#6B6B8A;max-width:500px;margin:0 auto;">
        Explore blueprints shared by the Dream Machine community.
        Get inspired. Remix. Build.
    </div>
</div>
""", unsafe_allow_html=True)

# ── Category Filter ────────────────────────────────────────────────────────────
categories = ["🌟 All", "🖥️ SaaS Platform", "📱 Mobile App", "🤖 AI Tool",
              "💼 Business Concept", "🎮 Game", "🌍 Social Cause", "📦 Physical Product"]

cat_cols = st.columns(len(categories))
selected_cat = st.session_state.get("gallery_cat", "🌟 All")
for i, cat in enumerate(categories):
    with cat_cols[i]:
        if st.button(cat, key=f"cat_{i}",
                     type="primary" if cat == selected_cat else "secondary",
                     use_container_width=True):
            st.session_state.gallery_cat = cat
            st.rerun()

st.divider()

# ── Load Public Blueprints ─────────────────────────────────────────────────────
public_bps = list_public_blueprints(limit=50)

# Filter by category
if selected_cat != "🌟 All":
    cat_type = selected_cat.split(" ", 1)[1] if " " in selected_cat else selected_cat
    public_bps = [bp for bp in public_bps if cat_type in bp.get("idea_type", "")]

# ── Trending ──────────────────────────────────────────────────────────────────
if public_bps:
    st.markdown("""
    <div style="margin-bottom:20px;">
        <div class="section-tag">Trending This Week</div>
    </div>
    """, unsafe_allow_html=True)

    top_bps = sorted(public_bps, key=lambda x: x.get("stars", 0), reverse=True)[:3]

    if top_bps:
        trend_cols = st.columns(min(len(top_bps), 3))
        for i, bp in enumerate(top_bps):
            with trend_cols[i]:
                icon = IDEA_TYPE_ICONS.get(bp.get("idea_type", ""), "💡")
                stars = bp.get("stars", 0)
                sections = bp.get("sections", {})
                exec_sum = sections.get("executive_summary", "")[:120] if sections else ""

                st.markdown(f"""
                <div class="gallery-card" style="border-color:rgba(92,107,255,0.3);
                     background:linear-gradient(135deg,rgba(92,107,255,0.06),rgba(0,245,212,0.03));">
                    <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:12px;">
                        <div class="blueprint-card-type">{icon} {bp.get('idea_type','')}</div>
                        <div style="font-size:13px;color:#FFB800;">⭐ {stars}</div>
                    </div>
                    <div class="blueprint-card-title">{bp.get('title', '')[:50]}</div>
                    <div style="font-size:12px;color:#6B6B8A;line-height:1.5;margin-top:8px;">
                        {exec_sum}{"..." if exec_sum else ""}
                    </div>
                </div>
                """, unsafe_allow_html=True)

                col_a, col_b = st.columns(2)
                with col_a:
                    if st.button(f"⭐ Star ({stars})", key=f"star_top_{bp['id']}", use_container_width=True):
                        star_blueprint(bp["id"])
                        st.toast("Starred! ⭐")
                        st.rerun()
                with col_b:
                    if st.button("Remix →", key=f"remix_top_{bp['id']}", type="primary", use_container_width=True):
                        # Fork: copy idea to new session
                        st.session_state.idea = bp.get("idea", "")
                        st.session_state.idea_type = bp.get("idea_type", "")
                        st.session_state.generation_done = False
                        st.session_state.questions = []
                        st.session_state.answers = {}
                        st.switch_page("pages/1_Questions.py")

    st.divider()

# ── All Public Blueprints ──────────────────────────────────────────────────────
st.markdown(f"""
<div class="section-tag" style="margin-bottom:20px;">
    All Shared Blueprints ({len(public_bps)})
</div>
""", unsafe_allow_html=True)

if not public_bps:
    st.markdown("""
    <div class="empty-state">
        <div class="empty-state-icon">🌐</div>
        <div class="empty-state-title">The gallery is empty</div>
        <div class="empty-state-text">
            Be the first to share a blueprint!<br>
            Go to any blueprint and toggle "Share to Gallery" in the sidebar.
        </div>
    </div>
    """, unsafe_allow_html=True)
    if st.button("✦ Create & Share a Blueprint", type="primary"):
        st.switch_page("app.py")
else:
    num_cols = 3
    rows = [public_bps[i:i+num_cols] for i in range(0, len(public_bps), num_cols)]

    for row in rows:
        cols = st.columns(num_cols, gap="medium")
        for j, bp in enumerate(row):
            with cols[j]:
                icon = IDEA_TYPE_ICONS.get(bp.get("idea_type", ""), "💡")
                stars = bp.get("stars", 0)
                sections = bp.get("sections", {})
                exec_sum = sections.get("executive_summary", "")[:100] if sections else ""

                st.markdown(f"""
                <div class="gallery-card">
                    <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:10px;">
                        <div class="blueprint-card-type">{icon} {bp.get('idea_type','')}</div>
                        <div style="font-size:12px;color:#6B6B8A;">{bp.get('created_at','')[:10]}</div>
                    </div>
                    <div class="blueprint-card-title">{bp.get('title','')[:50]}</div>
                    <div style="font-size:12px;color:#6B6B8A;line-height:1.5;margin:8px 0 14px;">
                        {exec_sum}{"..." if exec_sum else bp.get('idea','')[:100] + "..."}
                    </div>
                </div>
                """, unsafe_allow_html=True)

                g_col1, g_col2 = st.columns(2)
                with g_col1:
                    if st.button(f"⭐ {stars}", key=f"star_{bp['id']}", use_container_width=True):
                        star_blueprint(bp["id"])
                        st.toast("Starred! ⭐")
                        st.rerun()
                with g_col2:
                    if st.button("🔀 Remix", key=f"remix_{bp['id']}", type="primary",
                                 use_container_width=True):
                        st.session_state.idea = bp.get("idea", "")
                        st.session_state.idea_type = bp.get("idea_type", "")
                        st.session_state.generation_done = False
                        st.session_state.questions = []
                        st.session_state.answers = {}
                        st.switch_page("pages/1_Questions.py")
