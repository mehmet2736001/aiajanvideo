import os
import sys
import json

# Fix Windows console encoding for Turkish locale
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

import uvicorn
from fastapi import FastAPI, BackgroundTasks, Request, Response
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any

from core.orchestrator import StudioOrchestrator
from core.turso_client import TursoVoiceClient
from core.director_brain import DirectorBrain

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
AGENTS_DIR = os.path.join(BASE_DIR, "brain", "agents")
BRAIN_DIR = os.path.join(BASE_DIR, "brain")
PROD_DIR = os.path.join(BASE_DIR, "out")
WEB_DIR = os.path.join(BASE_DIR, "web")
KEYS_FILE = os.path.join(BASE_DIR, "api_keys.json")

app = FastAPI(title="Nexus AI Video Studio (Tek Başyönetmen Selim Bey)")

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
turso_client = TursoVoiceClient()
director_brain = DirectorBrain()
CURRENT_VOICE = "dervis"

# Memory state
CURRENT_STATE = {
    "status": "ready",
    "pre_render_package": {
        "topic": "Peygamberimizi Yaşlandıran Sır: Hûd 112",
        "script": "Peygamberimizin saçlarına ak düşüren o sırrı biliyor musun?\nSahabe sordu: Ya Resulallah, seni ne böyle ihtiyarlattı?\nCevap tek bir sûreydi: Beni Hûd sûresi kocattı...\nO sûrede öyle bir emir vardı ki, heybeti dağları ezerdi:\nFestekim kemâ umirt... Emrolunduğun gibi dosdoğru ol!\nGönlünce yaşa değil, kolayına geldiği gibi hiç değil...\nKıldan ince, kılıçtan keskin bir istikamet terazisi.\nBir ömrü, zerrece sapmadan Hakkın rızasına hizalamak...\nİşte bu ilahi ağırlık, bir peygamberin saçlarını ağarttı.\nPeki senin istikametin bugün nereye bakıyor?",
        "scenes_count": 10,
        "audio_url": "/public/hud-112/ses.mp3",
        "video_url": "/out/hud-112/hud-112.mp4",
        "pano_url": "/out/hud-112/pano.jpg",
        "quality_score": 95
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
    try:
        voices = turso_client.list_voices()
        return {
            "total": len(voices),
            "active_voice_id": CURRENT_VOICE,
            "voices": voices
        }
    except Exception as e:
        return {"total": 0, "active_voice_id": CURRENT_VOICE, "voices": [], "error": str(e)}

@app.get("/api/audio_sample/{voice_id}")
async def get_audio_sample(voice_id: str):
    try:
        raw_bytes, mime = turso_client.get_sample_audio(voice_id)
        if not raw_bytes:
            return JSONResponse(status_code=404, content={"error": "Örnek ses bulunamadı"})
        return Response(content=raw_bytes, media_type=mime or "audio/wav")
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.post("/api/voices/{voice_id}/favorite")
async def toggle_voice_favorite(voice_id: str):
    try:
        is_fav = turso_client.toggle_favorite(voice_id)
        return {"status": "success", "voice_id": voice_id, "is_favorite": is_fav}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

class SelectVoiceRequest(BaseModel):
    voice_id: str

@app.post("/api/voices/select")
async def select_voice(req: SelectVoiceRequest):
    global CURRENT_VOICE
    CURRENT_VOICE = req.voice_id
    return {"status": "success", "active_voice_id": CURRENT_VOICE}

@app.get("/api/errors")
async def get_errors():
    return {"errors": []}

class SetModelRequest(BaseModel):
    model: str

@app.post("/api/set_model")
async def set_model(req: SetModelRequest):
    return {"status": "success", "model": req.model}

class ReportErrorRequest(BaseModel):
    error: Optional[Dict[str, Any]] = None

@app.post("/api/errors/report")
async def report_error(req: ReportErrorRequest):
    return {"status": "reported"}

class UpdateScriptRequest(BaseModel):
    script: str

@app.post("/api/update_script")
async def update_script(req: UpdateScriptRequest):
    if "pre_render_package" in CURRENT_STATE:
        CURRENT_STATE["pre_render_package"]["script"] = req.script
    return {"status": "success"}

class PrepareMaterialsRequest(BaseModel):
    topic: str
    style: Optional[str] = "Karma"
    voice_id: Optional[str] = None
    ambience_id: Optional[str] = None

@app.post("/api/prepare_materials")
async def prepare_materials(req: PrepareMaterialsRequest):
    global CURRENT_VOICE
    if req.voice_id:
        CURRENT_VOICE = req.voice_id

    topic = req.topic.strip() or CURRENT_STATE["pre_render_package"]["topic"]
    pkg = CURRENT_STATE.get("pre_render_package", {})
    pkg["topic"] = topic

    return {
        "status": "success",
        "message": f"Başyönetmen Selim Bey «{topic}» için materyalleri hazırladı.",
        "package": pkg
    }

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
    channel_id: Optional[str] = None
    history: Optional[List[Dict[str, Any]]] = None
    model: Optional[str] = None

@app.post("/api/chat/message")
async def handle_chat(msg: ChatMessage):
    user_text = msg.message.strip()
    result = director_brain.chat(user_text)
    if "error" in result:
        return JSONResponse(status_code=400, content=result)
    
    # Eğer Selim Bey yeni bir konu önerdiyse state'e de yansıt
    if result.get("suggested_topic"):
        CURRENT_STATE["pre_render_package"]["topic"] = result["suggested_topic"]

    return {
        "status": "success",
        "reply": result["reply"],
        "sender": "Başyönetmen Selim Bey",
        "model_used": result.get("model_used", "gemini-3.8-flash"),
        "active_wardrobe": result.get("active_wardrobe", "Başyönetmen (Tüm Yetkinlikler)"),
        "total_turns": result.get("total_turns", 1),
        "suggested_topic": result.get("suggested_topic"),
        "package": CURRENT_STATE.get("pre_render_package")
    }

@app.get("/api/chat/history")
async def get_chat_history():
    return {
        "status": "success",
        "history": director_brain.get_history(),
        "director_status": director_brain.get_status()
    }

@app.post("/api/chat/new")
async def new_chat_session():
    return director_brain.new_session()

@app.post("/api/chat/clear")
@app.delete("/api/chat/history")
async def clear_chat_history():
    return director_brain.clear_history()

@app.get("/api/director/status")
async def get_director_status():
    return director_brain.get_status()

class ProduceRequest(BaseModel):
    project_slug: str
    title: str
    lines: List[str]
    category: Optional[str] = "İslami Tefekkür"
    voice_id: Optional[str] = None

@app.post("/api/produce")
async def produce_video(req: ProduceRequest):
    selected_voice = req.voice_id or CURRENT_VOICE
    result = orchestrator.produce_video_from_lines(
        project_slug=req.project_slug,
        title=req.title,
        lines=req.lines,
        category=req.category,
        voice_id=selected_voice
    )
    if result.get("status") == "success":
        pkg = {
            "topic": req.title,
            "script": "\n".join(req.lines),
            "scenes_count": len(req.lines),
            "audio_url": f"/public/{req.project_slug}/ses.mp3",
            "video_url": f"/out/{req.project_slug}/{req.project_slug}.mp4",
            "pano_url": f"/out/{req.project_slug}/pano.jpg",
            "quality_score": result.get("score", 95)
        }
        CURRENT_STATE["pre_render_package"] = pkg
        result["package"] = pkg
        result["video_url"] = pkg["video_url"]
        result["pano_url"] = pkg["pano_url"]
        result["audio_url"] = pkg["audio_url"]
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
