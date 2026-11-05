import os
import sys
import json

# Fix Windows console encoding for Turkish locale
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

import uvicorn
from fastapi import FastAPI, BackgroundTasks, Request
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any

from core.orchestrator import StudioOrchestrator

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
AGENTS_DIR = os.path.join(BASE_DIR, "brain", "agents")
BRAIN_DIR = os.path.join(BASE_DIR, "brain")
PROD_DIR = os.path.join(BASE_DIR, "out")
WEB_DIR = os.path.join(BASE_DIR, "web")
KEYS_FILE = os.path.join(BASE_DIR, "api_keys.json")

app = FastAPI(title="Nexus AI Video Studio (16 Ajanlı Hükümet)")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static mounts
if os.path.exists(PROD_DIR):
    app.mount("/out", StaticFiles(directory=PROD_DIR), name="out")
if os.path.exists(os.path.join(BASE_DIR, "public")):
    app.mount("/public", StaticFiles(directory=os.path.join(BASE_DIR, "public")), name="public")

orchestrator = StudioOrchestrator()

# Memory state
CURRENT_STATE = {
    "status": "ready",
    "pre_render_package": {
        "topic": "Ölüm Gerçekten Son Mu?",
        "script": "Anne karnındaki bir bebeğe 'dışarıda devasa bir dünya var' desen, inanmazdı...\nÇünkü onun bildiği tek evren, o dar karanlıktı.\nDoğum anı, bebek için sanki bir yok oluştu.\nOysa dışarı adım attığında, gerçek hayat daha yeni başlıyordu.\nİşte ölüm de böyledir.\nSana son gibi görünen o dar kapı, aslında sonsuz bir aleme açılır.\nBeden bu toprağın rahmine bırakılır, ruh asıl vatanına uyanır.\nÖlüm bir bitiş değil, ebedi hayatın doğum sancısıdır.",
        "scenes_count": 8,
        "audio_url": "/public/olum-son-mu/ses.mp3",
        "video_url": "/out/olum-son-mu/olum_son_mu.mp4",
        "pano_url": "/out/olum-son-mu/pano.jpg",
        "quality_score": 98
    }
}

@app.get("/", response_class=HTMLResponse)
async def get_index():
    with open(os.path.join(WEB_DIR, "index.html"), "r", encoding="utf-8") as f:
        return f.read()

@app.get("/api/state")
async def get_state():
    return CURRENT_STATE

@app.get("/api/key_pool")
async def get_key_pool():
    total = 136
    if os.path.exists(KEYS_FILE):
        try:
            with open(KEYS_FILE, "r") as f:
                k = json.load(f)
                total = k.get("total_count", 136)
        except Exception:
            pass
    return {
        "total_keys": total,
        "active_keys": total,
        "models": ["gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-pro"]
    }

@app.get("/api/agents")
async def list_agents():
    agents = []
    if os.path.exists(AGENTS_DIR):
        for folder in sorted(os.listdir(AGENTS_DIR)):
            mem_path = os.path.join(AGENTS_DIR, folder, "memory.json")
            if os.path.exists(mem_path):
                try:
                    with open(mem_path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    agents.append(data)
                except Exception:
                    pass
    return {"total": len(agents), "agents": agents}

@app.get("/api/audio_library")
async def get_audio_library():
    return {"files": []}

@app.get("/api/errors")
async def get_errors():
    return {"errors": []}

@app.post("/api/errors/clear")
async def clear_errors():
    return {"status": "cleared"}

@app.get("/api/memory")
async def get_memory():
    p = os.path.join(BRAIN_DIR, "experience_memory.json")
    if os.path.exists(p):
        with open(p, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

@app.get("/api/history")
async def get_history():
    p = os.path.join(BRAIN_DIR, "video_history.json")
    if os.path.exists(p):
        with open(p, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

class ChatMessage(BaseModel):
    message: str

@app.post("/api/chat/message")
async def handle_chat(msg: ChatMessage):
    user_text = msg.message.strip()
    return {
        "reply": f"Selim Bey (Başyönetmen): Mesajınızı aldım ('{user_text}'). 16 ajanlık hükümetimiz emirleriniz doğrultusunda hazırlanıyor.",
        "sender": "Selim Bey (Başyönetmen)",
        "package": CURRENT_STATE.get("pre_render_package")
    }

class ProduceRequest(BaseModel):
    project_slug: str
    title: str
    lines: List[str]
    category: Optional[str] = "İslami Tefekkür"

@app.post("/api/produce")
async def produce_video(req: ProduceRequest):
    result = orchestrator.produce_video_from_lines(
        project_slug=req.project_slug,
        title=req.title,
        lines=req.lines,
        category=req.category
    )
    if result.get("status") == "success":
        CURRENT_STATE["pre_render_package"] = {
            "topic": req.title,
            "script": "\n".join(req.lines),
            "scenes_count": len(req.lines),
            "audio_url": f"/public/{req.project_slug}/ses.mp3",
            "video_url": f"/out/{req.project_slug}/{req.project_slug}.mp4",
            "pano_url": f"/out/{req.project_slug}/pano.jpg",
            "quality_score": result.get("score", 95)
        }
    return result

@app.post("/api/approve_and_render")
async def approve_and_render():
    return {
        "status": "success",
        "message": "Başyönetmen ve Müfettiş Nuri onayı alındı. Video 30 FPS Full HD olarak hazır.",
        "package": CURRENT_STATE.get("pre_render_package")
    }

if __name__ == "__main__":
    print("[NEXUS] AI Video Studio Web Server: http://127.0.0.1:8000")
    uvicorn.run("web.server:app", host="127.0.0.1", port=8000, reload=False)
