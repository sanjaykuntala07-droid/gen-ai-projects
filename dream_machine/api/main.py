"""
Dream Machine — FastAPI Backend
REST API wrapper around existing Gemini + SQLite logic.
"""
import sys
import os
import json
import uuid
import asyncio
from pathlib import Path
from typing import Optional, List

# Make sure we can import dream_machine components
ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel

# Import existing Dream Machine components
from components.db import (
    init_db, list_blueprints, get_blueprint, save_blueprint,
    update_blueprint_section, add_vote, get_votes,
    delete_blueprint, get_stats
)
from components.gemini_client import (
    detect_idea_type, generate_questions, generate_blueprint_section,
    generate_blueprint_comparison,
    IDEA_TYPE_ICONS, SECTIONS
)

# ── Init DB on startup ────────────────────────────────────────────────────────
init_db()

app = FastAPI(title="Dream Machine API", version="2.0")

# ── CORS — allow React dev server + Capacitor ─────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        "capacitor://localhost",
        "http://localhost",
        "null",  # file:// origin from Capacitor
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Pydantic Models ───────────────────────────────────────────────────────────

class IdeaRequest(BaseModel):
    idea: str

class QuestionsRequest(BaseModel):
    idea: str
    idea_type: str

class GenerateBlueprintRequest(BaseModel):
    idea: str
    idea_type: str
    answers: dict
    user_name: Optional[str] = "User"

class SaveBlueprintRequest(BaseModel):
    blueprint_id: str
    section_key: str
    content: str

class VoteRequest(BaseModel):
    blueprint_id: str
    section_key: str
    vote: int  # 1 = up, -1 = down

class CompareRequest(BaseModel):
    blueprint_id_a: str
    blueprint_id_b: str


# ── Health ────────────────────────────────────────────────────────────────────

@app.get("/api/health")
async def health():
    return {"status": "ok", "version": "2.0"}


# ── Idea Type Detection ───────────────────────────────────────────────────────

@app.post("/api/detect-type")
async def detect_type(req: IdeaRequest):
    try:
        idea_type = detect_idea_type(req.idea)
        icon = IDEA_TYPE_ICONS.get(idea_type, "💡")
        return {"idea_type": idea_type, "icon": icon}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── Discovery Questions ───────────────────────────────────────────────────────

@app.post("/api/questions")
async def get_questions(req: QuestionsRequest):
    try:
        questions = generate_questions(req.idea, req.idea_type)
        return {"questions": questions}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── Blueprint Generation (Streaming) ─────────────────────────────────────────

@app.post("/api/generate/stream")
async def generate_stream(req: GenerateBlueprintRequest):
    """
    Stream blueprint generation section by section.
    Each chunk is a JSON line: {"section": "...", "key": "...", "chunk": "...", "done": false}
    Final line per section: {"section": "...", "key": "...", "done": true}
    """
    blueprint_id = str(uuid.uuid4())

    async def event_generator():
        # Send blueprint ID first
        yield json.dumps({"type": "init", "blueprint_id": blueprint_id}) + "\n"

        # Save initial blueprint record
        try:
            save_blueprint(
                blueprint_id=blueprint_id,
                idea=req.idea,
                idea_type=req.idea_type,
                answers=req.answers,
                user_name=req.user_name,
            )
        except Exception as e:
            yield json.dumps({"type": "error", "message": str(e)}) + "\n"
            return

        context = f"""Idea: {req.idea}
Type: {req.idea_type}
Discovery Answers: {json.dumps(req.answers, indent=2)}"""

        for section_key, section_label in SECTIONS:
            yield json.dumps({
                "type": "section_start",
                "key": section_key,
                "label": section_label
            }) + "\n"

            max_retries = 3
            retry_count = 0
            success = False

            while retry_count < max_retries and not success:
                try:
                    section_content = ""
                    # generate_blueprint_section returns a generator
                    for chunk in generate_blueprint_section(section_key, context):
                        section_content += chunk
                        yield json.dumps({
                            "type": "chunk",
                            "key": section_key,
                            "chunk": chunk
                        }) + "\n"
                        await asyncio.sleep(0.015)  # yield control & stream pacing

                    # Save completed section
                    update_blueprint_section(blueprint_id, section_key, section_content)

                    yield json.dumps({
                        "type": "section_done",
                        "key": section_key,
                        "content": section_content
                    }) + "\n"
                    success = True

                except Exception as e:
                    err_msg = str(e)
                    if "429" in err_msg or "exhausted" in err_msg.lower() or "limit" in err_msg.lower():
                        retry_count += 1
                        if retry_count < max_retries:
                            yield json.dumps({
                                "type": "chunk",
                                "key": section_key,
                                "chunk": f"\n\n*(⚠️ API rate limit reached. Retrying section in 5s... Attempt {retry_count}/{max_retries})*\n\n"
                            }) + "\n"
                            await asyncio.sleep(5)
                            continue
                    
                    yield json.dumps({
                        "type": "section_error",
                        "key": section_key,
                        "message": err_msg
                    }) + "\n"
                    break

            # Pacing delay between sections to stay under rate limits
            await asyncio.sleep(1.2)

        yield json.dumps({"type": "complete", "blueprint_id": blueprint_id}) + "\n"

    return StreamingResponse(
        event_generator(),
        media_type="application/x-ndjson",
        headers={"X-Blueprint-ID": blueprint_id}
    )


# ── Blueprint CRUD ────────────────────────────────────────────────────────────

@app.get("/api/blueprints")
async def get_blueprints(limit: int = 20, user_only: bool = False):
    try:
        items = list_blueprints(limit=limit, all_users=not user_only)
        return {"blueprints": [dict(b) for b in items]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/blueprints/{blueprint_id}")
async def get_blueprint_detail(blueprint_id: str):
    try:
        bp = get_blueprint(blueprint_id)
        if not bp:
            raise HTTPException(status_code=404, detail="Blueprint not found")
        return dict(bp)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/blueprints/{blueprint_id}")
async def delete_blueprint_endpoint(blueprint_id: str):
    try:
        delete_blueprint(blueprint_id)
        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── Voting ────────────────────────────────────────────────────────────────────

@app.post("/api/vote")
async def vote_endpoint(req: VoteRequest):
    try:
        add_vote(req.blueprint_id, req.section_key, req.vote)
        votes = get_votes(req.blueprint_id, req.section_key)
        return {"votes": votes}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── Stats ─────────────────────────────────────────────────────────────────────

@app.get("/api/stats")
async def get_app_stats():
    try:
        stats = get_stats(all_users=True)
        return dict(stats) if stats else {}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── Idea Types ────────────────────────────────────────────────────────────────

@app.get("/api/idea-types")
async def get_idea_types():
    return {
        "types": [
            {"name": name, "icon": icon}
            for name, icon in IDEA_TYPE_ICONS.items()
        ]
    }


# ── Blueprint Sections Metadata ───────────────────────────────────────────────

@app.get("/api/sections")
async def get_sections():
    return {"sections": [{"key": k, "label": l} for k, l in SECTIONS]}


# ── Compare ───────────────────────────────────────────────────────────────────

@app.post("/api/compare")
async def compare_blueprints(req: CompareRequest):
    try:
        bp_a = get_blueprint(req.blueprint_id_a)
        bp_b = get_blueprint(req.blueprint_id_b)
        if not bp_a or not bp_b:
            raise HTTPException(status_code=404, detail="One or both blueprints not found")

        analysis = generate_blueprint_comparison(dict(bp_a), dict(bp_b))
        return {
            "blueprint_a": dict(bp_a),
            "blueprint_b": dict(bp_b),
            "analysis": analysis
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
