"""
Dream Machine — Gemini AI Engine
Streaming generation for all blueprint sections, questions, mockups, and chat.
"""
import os
import json
import re
import base64
from functools import lru_cache
try:
    from google import genai
except ImportError:
    import google.generativeai as genai  # fallback
from dotenv import load_dotenv

load_dotenv()

_API_KEY = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
_client = None
MODEL = "gemini-2.5-flash"


def _get_client():
    global _client
    if _client is None:
        if not _API_KEY:
            raise ValueError("GEMINI_API_KEY not found in .env file")
        _client = genai.Client(api_key=_API_KEY)
    return _client


# ──────────────────────────────────────────────
# IDEA TYPE DETECTION
# ──────────────────────────────────────────────

IDEA_TYPES = [
    "SaaS Platform", "Mobile App", "Physical Product", "Workflow Automation",
    "Business Concept", "Social Cause", "AI Tool", "Game", "Marketplace",
    "Service Business", "Hardware Device", "Content Platform", "Browser Extension",
    "API / Developer Tool", "E-commerce", "Other"
]

IDEA_TYPE_ICONS = {
    "SaaS Platform": "🖥️", "Mobile App": "📱", "Physical Product": "📦",
    "Workflow Automation": "⚙️", "Business Concept": "💼", "Social Cause": "🌍",
    "AI Tool": "🤖", "Game": "🎮", "Marketplace": "🛒",
    "Service Business": "🤝", "Hardware Device": "🔌", "Content Platform": "🎬",
    "Browser Extension": "🧩", "API / Developer Tool": "🔧",
    "E-commerce": "🛍️", "Other": "💡"
}


@lru_cache(maxsize=512)
def detect_idea_type(idea: str) -> str:
    """Return one of the predefined idea type strings."""
    try:
        prompt = f"""Analyze this idea and respond with ONLY one of these exact types (pick the best match):
{chr(10).join(IDEA_TYPES)}

Idea: {idea}

Respond with ONLY the type name, nothing else."""
        client = _get_client()
        resp = client.models.generate_content(model=MODEL, contents=prompt,
                                              config={"temperature": 0})
        result = resp.text.strip()
        for t in IDEA_TYPES:
            if t.lower() in result.lower():
                return t
        return "Other"
    except Exception:
        return "Other"


# ──────────────────────────────────────────────
# DISCOVERY QUESTIONS
# ──────────────────────────────────────────────

def generate_questions(idea: str, idea_type: str) -> list[dict]:
    """Generate 6 discovery questions tailored to the idea type."""
    prompt = f"""You are a top-tier product strategist running a discovery call with a founder.
Generate exactly 6 insightful, context-aware discovery questions for this idea.

Idea: {idea}
Idea Type: {idea_type}

Return ONLY valid JSON array (no markdown, no explanation) like:
[
  {{
    "question": "Who is the primary user of this product?",
    "options": ["Developers", "Business owners", "Students", "General consumers"],
    "placeholder": "Describe your target user..."
  }}
]

Rules:
- Questions must be highly specific to the idea, not generic
- Each question has exactly 3-4 option chips AND a placeholder for custom text
- Cover: target user, core problem, business model, key differentiator, tech/platform, scale
- Make questions feel like a conversation with a brilliant advisor"""

    try:
        client = _get_client()
        resp = client.models.generate_content(model=MODEL, contents=prompt,
                                              config={"temperature": 0.4})
        text = resp.text.strip()
        # Strip markdown code fences if present
        text = re.sub(r"```(?:json)?", "", text).strip().rstrip("`").strip()
        return json.loads(text)
    except Exception as e:
        # Fallback generic questions
        return [
            {"question": "Who is your primary target user?",
             "options": ["Businesses (B2B)", "Consumers (B2C)", "Developers", "Students"],
             "placeholder": "Describe your ideal user..."},
            {"question": "What core problem does this solve?",
             "options": ["Saves time", "Saves money", "Improves experience", "Solves a new problem"],
             "placeholder": "Describe the problem..."},
            {"question": "What's the primary business model?",
             "options": ["Subscription (SaaS)", "One-time purchase", "Freemium", "Marketplace commission"],
             "placeholder": "Describe how you'll make money..."},
            {"question": "What platform will this live on?",
             "options": ["Web browser", "iOS / Android", "Desktop", "API / Embedded"],
             "placeholder": "Describe the platform..."},
            {"question": "What is your biggest competitive advantage?",
             "options": ["10x cheaper", "10x faster", "Unique AI", "Better UX"],
             "placeholder": "What makes this special..."},
            {"question": "What's your 12-month scale goal?",
             "options": ["1,000 users", "10,000 users", "100,000 users", "Enterprise clients"],
             "placeholder": "Describe your scale goal..."},
        ]


# ──────────────────────────────────────────────
# BLUEPRINT SECTION GENERATORS (STREAMING)
# ──────────────────────────────────────────────

SECTIONS = [
    ("executive_summary", "📋 Executive Summary"),
    ("user_personas", "👥 User Personas"),
    ("core_features", "⚡ Core Feature List"),
    ("architecture", "🏗️ Architecture Map"),
    ("tech_stack", "🔧 Tech Stack"),
    ("roadmap", "🗓️ Roadmap"),
    ("business_model", "💰 Business Model"),
    ("risk_analysis", "⚠️ Risk Analysis"),
    ("competitor_landscape", "🏁 Competitor Landscape"),
    ("success_metrics", "📊 Success Metrics"),
]

SECTION_PROMPTS = {
    "executive_summary": """Write a compelling 3-paragraph Executive Summary for this product idea.
Paragraph 1: What it is and what problem it solves (be specific, not generic).
Paragraph 2: Who it's for and why NOW is the right time.
Paragraph 3: The core value proposition in one memorable sentence.
Keep it visionary, crisp, and investor-ready.""",

    "user_personas": """Create exactly 3 detailed user personas for this product.
For each persona format exactly like this:

**[Name] — [Role/Title]**
- 🎯 Goal: [their main goal with this product]
- 😤 Pain Point: [their biggest frustration today]
- 💡 How this helps: [specific way the product solves their problem]
- 📊 Behavior: [1 sentence about their behavior/context]

Make personas feel like real people, not stereotypes.""",

    "core_features": """Create a prioritized feature list in two tiers:

**🚀 MVP Features (Ship First)**
List 5-7 core features that define the product. For each:
- Feature name and one-line description
- Why it's essential (user value)

**📈 Phase 2 Features (After PMF)**  
List 4-5 growth/scale features. For each:
- Feature name and one-line description
- What it unlocks

Be specific. No fluff. Every feature must earn its place.""",

    "architecture": """Describe the system architecture as a clear text flowchart.

Format it as a readable flow diagram using arrows:
[Component A] → [Component B] → [Component C]

Cover:
1. User entry points (web, mobile, API)
2. Frontend layer and key screens
3. Backend services and APIs
4. Data storage (databases, caches)
5. Third-party integrations
6. AI/ML components if applicable

Then write 2-3 sentences explaining the key architectural decisions and why they were chosen.""",

    "tech_stack": """Recommend the optimal tech stack for this product.

Format as:
**Frontend:** [tech] — why chosen
**Backend:** [tech] — why chosen
**Database:** [tech] — why chosen
**Auth:** [tech] — why chosen
**AI/ML:** [tech if applicable] — why chosen
**Hosting:** [platform] — why chosen
**Key APIs:** List 3-5 third-party APIs/services this product needs

End with one paragraph on why this stack is the right choice for this specific product.""",

    "roadmap": """Create a realistic 6-month build roadmap.

**Weeks 1-2: Foundation**
- [specific tasks]

**Weeks 3-4: Core Product**  
- [specific tasks]

**Month 2: Beta Launch**
- [milestones]

**Month 3: Growth & Iteration**
- [milestones]

**Months 4-6: Scale**
- [milestones]

Include: key milestones, launch gates, user feedback cycles.""",

    "business_model": """Design the business model with specifics.

**Revenue Streams:**
Describe 2-3 specific revenue streams with:
- Model type (subscription, freemium, etc.)
- Pricing tiers and amounts (be specific: "$29/mo Pro, $99/mo Business")
- Why users will pay

**Unit Economics:**
- Estimated Customer Acquisition Cost (CAC)
- Estimated Lifetime Value (LTV)
- Target LTV:CAC ratio

**Path to $1M ARR:**
How many customers at what price point to reach $1M ARR?""",

    "risk_analysis": """Identify the top 3 risks and mitigation strategies.

For each risk:

**Risk [N]: [Risk Name]**
- 🚨 Threat: [What could go wrong and how bad]
- 📊 Likelihood: [Low/Medium/High] | Impact: [Low/Medium/High]
- 🛡️ Mitigation: [Specific action plan to prevent or reduce this risk]
- 🔄 Contingency: [What you do if it happens anyway]""",

    "competitor_landscape": """Analyze the competitive landscape.

**Direct Competitors** (doing exactly this):
List 2-3 competitors with: name, what they do, their weakness

**Indirect Competitors** (solving the same problem differently):
List 1-2 alternatives users might choose

**Your Differentiation Matrix:**
| Factor | Competitor A | Competitor B | This Product |
|--------|-------------|-------------|--------------|
| [Key factor] | ... | ... | ✅ [advantage] |

End with a 2-sentence "Blue Ocean" statement: what white space this product uniquely owns.""",

    "success_metrics": """Define the KPIs and success metrics.

**Launch Metrics (Month 1-2):**
List 4 specific metrics with targets

**Growth Metrics (Month 3-6):**
List 4 specific metrics with targets

**North Star Metric:**
[Single metric that best captures product value] — Target: [specific number]

**Investor Metrics (Month 12):**
- MAU/DAU target
- Revenue target
- Churn rate target
- NPS target

Explain why the North Star Metric was chosen for this specific product.""",
}


def stream_section(idea: str, idea_type: str, answers: dict, section_key: str):
    """Generator that streams text chunks for a blueprint section."""
    answers_text = "\n".join(
        f"- {q}: {a}" for q, a in answers.items() if a
    ) or "No additional context provided."

    prompt = f"""You are an expert product strategist, startup advisor, and technical architect.
Generate the {section_key.replace('_', ' ').title()} section for this product blueprint.

IDEA: {idea}
TYPE: {idea_type}
USER CONTEXT:
{answers_text}

INSTRUCTIONS:
{SECTION_PROMPTS.get(section_key, "Provide a detailed, actionable analysis.")}

Be specific to THIS idea — not generic advice. Write as if you know this product deeply.
Use markdown formatting for structure. Be bold and visionary."""

    client = _get_client()
    for chunk in client.models.generate_content_stream(
        model=MODEL,
        contents=prompt,
        config={"temperature": 0.7}
    ):
        if chunk.text:
            yield chunk.text


def generate_section_sync(idea: str, idea_type: str, answers: dict, section_key: str) -> str:
    """Synchronous version — returns full text for a section."""
    return "".join(stream_section(idea, idea_type, answers, section_key))


# ──────────────────────────────────────────────
# MOCKUP GENERATOR
# ──────────────────────────────────────────────

def generate_mockup(idea: str, idea_type: str, answers: dict, style: str = "modern") -> str:
    """Generate a full HTML/CSS wireframe mockup for the idea."""
    style_desc = {
        "modern": "modern, dark, minimal with sharp typography",
        "minimal": "ultra-minimal, lots of white space, subtle borders",
        "colorful": "vibrant, colorful, gradient-heavy, energetic",
    }.get(style, "modern")

    prompt = f"""Create a complete, realistic HTML/CSS UI mockup for this product.

Product: {idea}
Type: {idea_type}
Style: {style_desc}

Generate a FULL HTML document with embedded CSS that shows:
1. A top navigation bar with logo and nav items
2. A hero/main action section (core use case)
3. A features or content grid section
4. Realistic-looking UI components (cards, buttons, inputs)

Requirements:
- Self-contained HTML (all CSS inline in <style> tag)
- Dark theme: background #0D0D1A, primary #5C6BFF, accent #00F5D4
- Use realistic-looking content (not lorem ipsum — real content relevant to the product)
- Clean, professional, modern design
- Include hover states in CSS
- Font: use system fonts or Google Fonts via CDN link
- Make it look like a REAL product, not a wireframe
- Width: 100%, responsive
- Add subtle animations (CSS only)

RETURN ONLY the HTML code starting with <!DOCTYPE html>. No explanation."""

    try:
        client = _get_client()
        resp = client.models.generate_content(
            model=MODEL,
            contents=prompt,
            config={"temperature": 0.8, "max_output_tokens": 8192}
        )
        html = resp.text.strip()
        # Clean markdown fences if present
        html = re.sub(r"```(?:html)?", "", html).strip().rstrip("`").strip()
        return html
    except Exception as e:
        return _fallback_mockup(idea, idea_type)


def _fallback_mockup(idea: str, idea_type: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{idea[:40]}</title>
<style>
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: #0D0D1A; color: #E8E8F0; }}
nav {{ display: flex; align-items: center; justify-content: space-between; padding: 16px 40px; border-bottom: 1px solid rgba(92,107,255,0.2); }}
.logo {{ font-weight: 700; font-size: 1.2rem; background: linear-gradient(135deg, #5C6BFF, #00F5D4); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }}
.nav-links {{ display: flex; gap: 24px; list-style: none; }}
.nav-links a {{ color: #9999BB; text-decoration: none; font-size: 14px; }}
.cta {{ padding: 8px 20px; background: #5C6BFF; border: none; border-radius: 8px; color: white; cursor: pointer; font-weight: 600; }}
.hero {{ text-align: center; padding: 100px 40px 80px; }}
.hero h1 {{ font-size: 3rem; font-weight: 700; margin-bottom: 20px; letter-spacing: -0.03em; }}
.hero p {{ color: #6B6B8A; font-size: 1.1rem; max-width: 500px; margin: 0 auto 40px; line-height: 1.6; }}
.hero-btn {{ padding: 14px 32px; background: linear-gradient(135deg, #5C6BFF, #4050E8); border: none; border-radius: 12px; color: white; font-size: 1rem; font-weight: 600; cursor: pointer; box-shadow: 0 4px 20px rgba(92,107,255,0.4); }}
.features {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 24px; padding: 0 40px 80px; }}
.feature-card {{ background: rgba(255,255,255,0.03); border: 1px solid rgba(92,107,255,0.2); border-radius: 16px; padding: 28px; }}
.feature-icon {{ font-size: 2rem; margin-bottom: 16px; }}
.feature-title {{ font-weight: 600; font-size: 1.05rem; margin-bottom: 8px; }}
.feature-text {{ color: #6B6B8A; font-size: 14px; line-height: 1.6; }}
</style>
</head>
<body>
<nav>
  <div class="logo">✦ {idea[:20]}</div>
  <ul class="nav-links">
    <li><a href="#">Features</a></li>
    <li><a href="#">Pricing</a></li>
    <li><a href="#">Docs</a></li>
  </ul>
  <button class="cta">Get Started →</button>
</nav>
<div class="hero">
  <h1>The future of<br><span style="background:linear-gradient(135deg,#5C6BFF,#00F5D4);-webkit-background-clip:text;-webkit-text-fill-color:transparent">{idea_type}</span></h1>
  <p>{idea[:120]}{"..." if len(idea) > 120 else ""}</p>
  <button class="hero-btn">Start Building →</button>
</div>
<div class="features">
  <div class="feature-card"><div class="feature-icon">⚡</div><div class="feature-title">Lightning Fast</div><div class="feature-text">Built for speed from the ground up. Every interaction feels instant.</div></div>
  <div class="feature-card"><div class="feature-icon">🤖</div><div class="feature-title">AI-Powered</div><div class="feature-text">Intelligent automation that learns from your workflow and adapts.</div></div>
  <div class="feature-card"><div class="feature-icon">🔒</div><div class="feature-title">Enterprise Grade</div><div class="feature-text">Bank-level security with full compliance and data sovereignty.</div></div>
</div>
</body>
</html>"""


# ──────────────────────────────────────────────
# AI CHAT
# ──────────────────────────────────────────────

def stream_chat(idea: str, idea_type: str, sections: dict, history: list[dict], user_message: str):
    """Stream a chat response about the blueprint."""
    blueprint_summary = "\n".join(
        f"**{k.replace('_', ' ').title()}:**\n{v[:500]}..."
        for k, v in sections.items() if v
    )

    history_text = "\n".join(
        f"{msg['role'].upper()}: {msg['content']}"
        for msg in history[-8:]  # Last 8 messages for context
    )

    prompt = f"""You are Dream Machine's expert AI advisor. You have deep knowledge of this specific product blueprint.

PRODUCT: {idea}
TYPE: {idea_type}

BLUEPRINT SUMMARY:
{blueprint_summary}

CONVERSATION HISTORY:
{history_text}

USER: {user_message}

Respond as a brilliant product advisor who knows this idea deeply. Be specific, actionable, and concise.
Use markdown formatting where helpful. Don't repeat the full blueprint — give focused, expert insight."""

    client = _get_client()
    for chunk in client.models.generate_content_stream(
        model=MODEL,
        contents=prompt,
        config={"temperature": 0.7}
    ):
        if chunk.text:
            yield chunk.text


# ──────────────────────────────────────────────
# SMART SUGGESTIONS
# ──────────────────────────────────────────────

def get_smart_suggestions(idea: str, idea_type: str) -> list[str]:
    """Get 3 proactive improvement suggestions for the idea."""
    try:
        prompt = f"""As a top startup advisor, give 3 short, specific improvement suggestions for this idea.
Each suggestion should be 1 sentence, actionable, and insightful.
Return as JSON array of strings.

Idea: {idea}
Type: {idea_type}

Return ONLY: ["suggestion 1", "suggestion 2", "suggestion 3"]"""

        client = _get_client()
        resp = client.models.generate_content(model=MODEL, contents=prompt,
                                              config={"temperature": 0.7})
        text = resp.text.strip()
        text = re.sub(r"```(?:json)?", "", text).strip().rstrip("`").strip()
        return json.loads(text)
    except Exception:
        return [
            "💡 Consider adding a freemium tier to reduce adoption friction.",
            "🔗 An API integration marketplace could create powerful network effects.",
            "📱 A companion mobile app could increase daily engagement significantly."
        ]


# ──────────────────────────────────────────────
# TITLE GENERATOR
# ──────────────────────────────────────────────

def generate_title(idea: str, idea_type: str) -> str:
    """Generate a catchy, memorable product name/title for the idea."""
    try:
        prompt = f"""Generate a short, catchy, memorable product name for this idea.
The name should be 2-6 words max, brandable, and specific to what the product does.
Do NOT use vague words alone like 'AI', 'App', 'Pro', 'Smart', or 'Next'.
Make it something a startup would actually be called.

Idea: {idea}
Type: {idea_type}

Respond with ONLY the product name. No explanation, no quotes, no punctuation at end."""
        client = _get_client()
        resp = client.models.generate_content(model=MODEL, contents=prompt,
                                              config={"temperature": 0.85})
        title = resp.text.strip().strip('"').strip("'").strip(".")
        if title and 2 <= len(title) <= 80:
            return title
        return idea[:60] + ("..." if len(idea) > 60 else "")
    except Exception:
        return idea[:60] + ("..." if len(idea) > 60 else "")


# ──────────────────────────────────────────────
# PITCH DECK GENERATOR
# ──────────────────────────────────────────────

def generate_pitch_deck(idea: str, idea_type: str, sections: dict,
                        style: str = "Seed / Angel", num_slides: int = 10) -> list:
    """Generate structured pitch deck slides from blueprint sections."""
    sections_summary = "\n".join(
        f"=== {k.replace('_', ' ').upper()} ===\n{v[:600]}\n"
        for k, v in sections.items() if v
    )

    prompt = f"""You are a world-class pitch coach and startup advisor.
Create a {num_slides}-slide investor pitch deck for this product.

PRODUCT IDEA: {idea}
TYPE: {idea_type}
PITCH STYLE: {style}

BLUEPRINT DATA:
{sections_summary}

Generate EXACTLY {num_slides} slides as a JSON array. Each slide must have:
{{
  "type": "one of: title|problem|solution|market|product|traction|business_model|team|financials|ask|content",
  "title": "slide headline (max 8 words)",
  "subtitle": "supporting text (1 sentence)",
  "bullets": ["bullet 1", "bullet 2", "bullet 3"],
  "stats": [{{"value": "$1M", "label": "TAM"}}],
  "speaker_notes": "what to say aloud (2-3 sentences)"
}}

Slide order for investor decks:
1. Title / Company intro
2. Problem (the pain point)
3. Solution (your product)
4. Market Size (TAM/SAM/SOM)
5. Product / How it works
6. Traction / Validation
7. Business Model
8. Team
9. Financials / Projections
10. The Ask

Include specific numbers, metrics, and details from the blueprint data above.
Return ONLY valid JSON array. No markdown fences, no explanation."""

    try:
        client = _get_client()
        resp = client.models.generate_content(
            model=MODEL,
            contents=prompt,
            config={"temperature": 0.7, "max_output_tokens": 8192}
        )
        text = resp.text.strip()
        text = re.sub(r"```(?:json)?", "", text).strip().rstrip("`").strip()
        slides = json.loads(text)
        if isinstance(slides, list) and len(slides) > 0:
            return slides
        return _fallback_pitch_slides(idea, idea_type, num_slides)
    except Exception:
        return _fallback_pitch_slides(idea, idea_type, num_slides)


def _fallback_pitch_slides(idea: str, idea_type: str, num_slides: int) -> list:
    """Fallback pitch slides when AI generation fails."""
    base = [
        {"type": "title", "title": idea[:40], "subtitle": f"A {idea_type} startup",
         "bullets": ["Solving a real problem", "Backed by data", "Ready to scale"],
         "stats": [], "speaker_notes": "Introduce yourself and the company."},
        {"type": "problem", "title": "The Problem", "subtitle": "A massive, underserved pain point",
         "bullets": ["Current solutions are broken", "The market is frustrated", "We've validated this pain"],
         "stats": [{"value": "83%", "label": "Affected"}],
         "speaker_notes": "Make the audience feel the pain. Use a story."},
        {"type": "solution", "title": "Our Solution", "subtitle": "Simple. Elegant. 10x better.",
         "bullets": ["Built for the user", "AI-powered core", "Instant value"],
         "stats": [], "speaker_notes": "Demo if possible."},
        {"type": "market", "title": "Market Opportunity",
         "subtitle": "A massive market at an inflection point",
         "bullets": ["TAM: $50B+", "SAM: $5B addressable", "Our beachhead: $500M"],
         "stats": [{"value": "$50B", "label": "TAM"}, {"value": "$5B", "label": "SAM"}],
         "speaker_notes": "Show bottom-up market sizing."},
        {"type": "business_model", "title": "Business Model",
         "subtitle": "Simple, scalable revenue",
         "bullets": ["Subscription SaaS", "$29/mo Pro · $99/mo Business",
                     "Path to $1M ARR: 1,000 customers"],
         "stats": [{"value": "$29", "label": "Starting"}, {"value": "80%", "label": "Margin"}],
         "speaker_notes": "Explain unit economics clearly."},
        {"type": "ask", "title": "The Ask",
         "subtitle": "Join us to capture this opportunity",
         "bullets": ["Raising $500K seed round", "Product development 60%", "Go-to-market 40%"],
         "stats": [{"value": "$500K", "label": "Raising"}],
         "speaker_notes": "Be specific about the ask and use of funds."},
    ]
    while len(base) < num_slides:
        base.append({"type": "content", "title": "Appendix",
                     "subtitle": "Supporting data", "bullets": [], "stats": [],
                     "speaker_notes": ""})
    return base[:num_slides]


# ──────────────────────────────────────────────
# MINI BLUEPRINT (Fast — Capture Mode)
# ──────────────────────────────────────────────

def generate_mini_blueprint(idea: str, idea_type: str) -> dict:
    """Generate a fast 2-section mini blueprint: summary + core features.
    Optimized for speed — returns in ~10 seconds.
    """
    prompt = f"""You are a sharp product strategist. In under 200 words total, produce a mini product blueprint.

IDEA: {idea}
TYPE: {idea_type}

Return ONLY valid JSON with exactly this structure:
{{
  "one_liner": "One unforgettable sentence describing the product",
  "problem": "The exact problem this solves (2 sentences max)",
  "solution": "How this solves it (2 sentences max)",
  "top_features": ["Feature 1", "Feature 2", "Feature 3", "Feature 4", "Feature 5"],
  "target_user": "Who this is for (1 sentence)",
  "business_model": "How it makes money (1 sentence)",
  "next_step": "The single most important first action to take"
}}

No markdown fences. No explanation. Pure JSON only."""

    try:
        client = _get_client()
        resp = client.models.generate_content(
            model=MODEL,
            contents=prompt,
            config={"temperature": 0.6, "max_output_tokens": 1024}
        )
        text = resp.text.strip()
        text = re.sub(r"```(?:json)?", "", text).strip().rstrip("`").strip()
        return json.loads(text)
    except Exception:
        return {
            "one_liner": f"A {idea_type} that revolutionizes how people {idea[:40]}",
            "problem": "Existing solutions are too slow, expensive, or complex.",
            "solution": "A streamlined AI-powered platform that cuts through the complexity.",
            "top_features": ["Core AI engine", "Simple onboarding", "Real-time analytics",
                             "API integrations", "Mobile access"],
            "target_user": "Professionals who need faster, smarter tools.",
            "business_model": "Monthly subscription with a generous free tier.",
            "next_step": "Validate with 5 potential users this week."
        }


# ──────────────────────────────────────────────
# MIND MAP GENERATOR
# ──────────────────────────────────────────────

def generate_mindmap(idea: str, idea_type: str) -> str:
    """Generate a Mermaid mindmap diagram for the idea."""
    prompt = f"""Create a Mermaid mindmap diagram for this product idea.

IDEA: {idea}
TYPE: {idea_type}

Generate a Mermaid mindmap with:
- Root node: the product name/concept
- 5-6 main branches: Problem, Solution, Users, Features, Business Model, Tech
- 2-3 sub-nodes per branch with specific details

Use this exact format:
mindmap
  root((Product Name))
    Problem
      Pain point 1
      Pain point 2
    Solution
      Core capability
      Key differentiator
    Users
      Primary user type
      Secondary user type
    Features
      Feature 1
      Feature 2
      Feature 3
    Business
      Revenue model
      Pricing
    Tech
      Frontend
      Backend

Return ONLY the Mermaid mindmap code starting with 'mindmap'. No markdown fences, no explanation."""

    try:
        client = _get_client()
        resp = client.models.generate_content(
            model=MODEL,
            contents=prompt,
            config={"temperature": 0.5, "max_output_tokens": 1024}
        )
        text = resp.text.strip()
        text = re.sub(r"```(?:mermaid)?", "", text).strip().rstrip("`").strip()
        if text.startswith("mindmap"):
            return text
        return _fallback_mindmap(idea, idea_type)
    except Exception:
        return _fallback_mindmap(idea, idea_type)


def _fallback_mindmap(idea: str, idea_type: str) -> str:
    name = idea[:25].strip()
    return f"""mindmap
  root(({name}))
    Problem
      Existing solutions lack speed
      High cost & complexity
    Solution
      AI-powered automation
      Intuitive interface
    Users
      Primary: {idea_type} professionals
      Secondary: Teams & enterprises
    Features
      Core engine
      Dashboard
      API access
      Mobile app
    Business
      SaaS subscription
      Freemium entry
    Tech
      Cloud-native
      Real-time sync"""


# ──────────────────────────────────────────────
# AUDIO TRANSCRIPTION
# ──────────────────────────────────────────────

def transcribe_audio_bytes(audio_bytes: bytes, mime_type: str = "audio/wav") -> str:
    """Transcribe audio bytes using Gemini's multimodal capability."""
    try:
        audio_b64 = base64.b64encode(audio_bytes).decode("utf-8")
        client = _get_client()
        resp = client.models.generate_content(
            model=MODEL,
            contents=[{
                "parts": [
                    {
                        "inline_data": {
                            "mime_type": mime_type,
                            "data": audio_b64
                        }
                    },
                    {
                        "text": ("Please transcribe this audio recording accurately. "
                                 "Return ONLY the transcribed text, nothing else. "
                                 "If no speech is detected, return: [No speech detected]")
                    }
                ]
            }],
            config={"temperature": 0}
        )
        return resp.text.strip()
    except Exception as e:
        return f"[Transcription failed: {e}]"


# ──────────────────────────────────────────────
# BLUEPRINT COMPARISON
# ──────────────────────────────────────────────

def generate_blueprint_comparison(bp_a: dict, bp_b: dict) -> str:
    """Generate an AI-powered comparative analysis between two blueprints."""
    # Build a summary of sections for both blueprints
    sections_a = bp_a.get("sections", {})
    sections_b = bp_b.get("sections", {})
    
    sections_summary_a = "\n".join([f"- **{k.replace('_',' ').title()}**: {v[:300]}..." for k, v in sections_a.items() if v])
    sections_summary_b = "\n".join([f"- **{k.replace('_',' ').title()}**: {v[:300]}..." for k, v in sections_b.items() if v])

    prompt = f"""You are a senior product strategist and venture capitalist.
Analyze and compare the following two product/business blueprints side-by-side.

BLUEPRINT A:
Title: {bp_a.get('title')}
Type: {bp_a.get('idea_type')}
Description: {bp_a.get('idea')}
Key Sections:
{sections_summary_a}

BLUEPRINT B:
Title: {bp_b.get('title')}
Type: {bp_b.get('idea_type')}
Description: {bp_b.get('idea')}
Key Sections:
{sections_summary_b}

Write a detailed, structured comparative report in Markdown.
The report MUST contain:
1. 📊 Executive Comparison Matrix (combining target users, business model, and differentiator)
2. ⚔️ Competitive & Market Positioning (if both products entered the same space, how would they fare? What are their key differences?)
3. 🤝 Synergies & Potential Merger (could these ideas be combined? How would a merged product look?)
4. ⚖️ Strategic Verdict (which idea seems more viable/scalable, and what are the immediate next steps for both?)

Keep the tone objective, analytical, and highly strategic. Avoid generic statements; refer directly to the details of both ideas.
Return the output in Markdown format. Use emojis and bold headers to make it look premium and readable."""

    try:
        client = _get_client()
        resp = client.models.generate_content(
            model=MODEL,
            contents=prompt,
            config={"temperature": 0.4, "max_output_tokens": 2048}
        )
        return resp.text.strip()
    except Exception as e:
        return f"### Comparative Analysis Failed\nAn error occurred while generating the AI comparison: {e}"

