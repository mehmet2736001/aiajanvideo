from datetime import datetime
import os
import sys
import threading
import time
from collections import deque
from typing import Any, Dict, List, Optional

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import uvicorn
from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from core.director_brain import DirectorBrain
from core.orchestrator import StudioOrchestrator
from core.production_tracker import tracker
from core.turso_client import TursoVoiceClient
from core.utils import BASE_DIR, InvalidSlugError, read_json, validate_slug

AGENTS_DIR = os.path.join(BASE_DIR, "brain", "agents")
BRAIN_DIR = os.path.join(BASE_DIR, "brain")
PROD_DIR = os.path.join(BASE_DIR, "out")
PUBLIC_DIR = os.path.join(BASE_DIR, "public")
WEB_DIR = os.path.join(BASE_DIR, "web")
os.makedirs(PROD_DIR, exist_ok=True)

app = FastAPI(title="Nexus AI Video Studio")

# Yalnızca yerel arayüz (localhost / 127.0.0.1, her port) çağrı yapabilir.
app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"^https?://(localhost|127\.0\.0\.1)(:\d+)?$",
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/out", StaticFiles(directory=PROD_DIR), name="out")
if os.path.isdir(PUBLIC_DIR):
    app.mount("/public", StaticFiles(directory=PUBLIC_DIR), name="public")

orchestrator = StudioOrchestrator()
turso_client = TursoVoiceClient()
director_brain = DirectorBrain()
CURRENT_VOICE = "0001"
_produce_lock = threading.Lock()

# Sunucu tarafı hata günlüğü (arayüzdeki "Sistem Denetimi" paneli için)
ERROR_LOG: deque = deque(maxlen=100)


def log_error(source: str, message: str) -> None:
    ERROR_LOG.append({"time": time.strftime("%H:%M:%S"), "source": source, "message": str(message)[:500]})


def _err(status: int, message: str) -> JSONResponse:
    return JSONResponse(status_code=status, content={"status": "error", "message": message, "error": message})


CURRENT_STATE: Dict[str, Any] = {"status": "ready", "pre_render_package": None}


def _load_initial_package() -> Optional[dict]:
    """Geçmişteki son başarılı üretimi (varsa) başlangıç paketi olarak yükler."""
    hist = read_json(os.path.join(BRAIN_DIR, "video_history.json"), [])
    for h in reversed(hist if isinstance(hist, list) else []):
        out = h.get("output_path", "")
        if out.endswith(".mp4") and os.path.exists(os.path.join(BASE_DIR, out)):
            slug = os.path.basename(out)[:-4]
            script_path = os.path.join(PUBLIC_DIR, slug, "metin.txt")
            script = ""
            if os.path.exists(script_path):
                with open(script_path, "r", encoding="utf-8") as f:
                    script = f.read()
            return {
                "topic": h.get("title", slug),
                "script": script,
                "scenes_count": len([l for l in script.splitlines() if l.strip()]),
                "audio_url": f"/public/{slug}/ses.mp3",
                "video_url": f"/{out}",
                "pano_url": f"/out/{slug}/pano.jpg",
                "quality_score": h.get("quality_score"),
            }
    return None


CURRENT_STATE["pre_render_package"] = _load_initial_package() or {
    "topic": "", "script": "", "scenes_count": 0,
    "audio_url": None, "video_url": None, "pano_url": None, "quality_score": None,
}


# ---------------------------------------------------------------- sayfa & durum
@app.get("/", response_class=HTMLResponse)
def get_index():
    with open(os.path.join(WEB_DIR, "index.html"), "r", encoding="utf-8") as f:
        return f.read()


@app.get("/api/health")
def health():
    import shutil
    return {
        "status": "ok",
        "ffmpeg": bool(shutil.which("ffmpeg")),
        "node": bool(shutil.which("node")),
        "node_modules": os.path.isdir(os.path.join(BASE_DIR, "node_modules")),
        "gemini_keys": len(director_brain.keys),
    }



AVAILABLE_SKILLS = [
    {
        "id": "canvas_story",
        "name": "Canvas Story Animation",
        "icon": "palette",
        "badge": "2D Deterministic",
        "description": "Tek zaman değişkeni (t=0..DUR), Hermite smoothstep ve deterministik PRNG ile sinematik 2D görsel hikaye anlatımı.",
        "starter_prompt": "Canvas Story Animation mimarisiyle; çözünürlükten bağımsız U birimi, Hermite geçişleri ve çok katmanlı 2D Canvas görsel akışıyla sarsıcı bir tefekkür senaryosu tasarla."
    },
    {
        "id": "3d_canvas_story",
        "name": "3D Stories Canvas Animasyon",
        "icon": "box",
        "badge": "3D Perspective",
        "description": "3D perspektif izdüşümü (focal/depth), 3D kamera matrisleri (yaw/pitch/dolly), derinlik sıralaması ve 3D holo modellerle sinematik görsel hikaye anlatımı.",
        "starter_prompt": "3D Stories Canvas Animasyon mimarisiyle; tek zaman t değişkeni, 3D perspektif kamera izdüşümü, derinlik sisi, 3D stardust tüneli ve 3D dönen holo modellerle (Fe-26 / Jiroskop Mizan) sarsıcı bir tefekkür senaryosu tasarla."
    },
    {
        "id": "tefekkur",
        "name": "İslami Tefekkür & İlim",
        "icon": "book-open",
        "badge": "Ayet & Hadis",
        "description": "Kur'an-ı Kerim ayetleri, sahih sünnet ve kalbe dokunan derin hikmet dili.",
        "starter_prompt": "Bana Kur'an-ı Kerim'den bir ayet ekseninde kalbe dokunacak 45 saniyelik dikey bir tefekkür videosu tasarla."
    },
    {
        "id": "kanca",
        "name": "Viral Kanca & Ritim",
        "icon": "zap",
        "badge": "0-3 Sn Kilit",
        "description": "İlk 3 saniyede izleyiciyi ekrana kilitleyen, merak ve şok etkisi uyandıran 9:16 akışı.",
        "starter_prompt": "İzleyicinin dikkatini ilk 3 saniyede yakalayacak 3 sarsıcı kanca (hook) cümlesi ve senaryo girişi yaz."
    },
    {
        "id": "dervis_ses",
        "name": "Derviş Ses & Akustik",
        "icon": "mic",
        "badge": "114 Hz Huşu",
        "description": "114 Hz derinlik, ağırbaşlı tefekkür tınısı ve helal akustik mastering.",
        "starter_prompt": "Bu video için tefekkür ve huşu veren derviş ses tonunda okuma ritmini ve seslendirme karakterini belirle."
    },
    {
        "id": "remotion_tasarim",
        "name": "Remotion Sahne Kurgusu",
        "icon": "clapperboard",
        "badge": "1080x1920 30FPS",
        "description": "Saf SVG, altın oran tipografi ve matematiksel spring geçişleri.",
        "starter_prompt": "Metni 1080x1920 dikey Remotion sahnelerine ayır, her sahnenin tipografisini ve görsel dengesini planla."
    },
    {
        "id": "denetim",
        "name": "48 Kare Görsel Denetim",
        "icon": "shield-check",
        "badge": "Estetik Kalite",
        "description": "Sahne kareleri estetik, boşluk, kontrast ve ritim kalite denetimi.",
        "starter_prompt": "Mevcut sahne akışının kontrast, yazı büyüklükleri ve görsel hiyerarşi kurallarını denetle."
    },
    {
        "id": "hizli_uretim",
        "name": "Tek Tıkla Senaryodan Videoya",
        "icon": "play-circle",
        "badge": "Otomatik Render",
        "description": "Aklındaki fikri doğrudan 1080x1920 MP4 videoya dönüştüren tam otomatik üretim.",
        "starter_prompt": "Konuyu kararlaştırdık; hemen senaryoyu tamamla ve tek tıkla render edilecek nexus-video paketini sun."
    }
]


class SaveSkillRequest(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    description: str = Field(min_length=1, max_length=300)
    prompt: str = Field(min_length=1, max_length=4000)
    icon: Optional[str] = "sparkles"
    badge: Optional[str] = "Özel Skill"


class SettingsRequest(BaseModel):
    voice: Optional[str] = "dervis"
    voice_name: Optional[str] = "derviş"
    voice_title: Optional[str] = "Derviş (Charon 114 Hz)"
    speed: Optional[str] = "-4%"
    pitch: Optional[str] = "-1Hz"
    model: Optional[str] = "gemini-3.8-flash"


@app.get("/api/skills")
def get_skills():
    from core.director_brain import load_custom_skills
    custom = load_custom_skills()
    return {"status": "success", "skills": AVAILABLE_SKILLS + custom}


@app.post("/api/skills/save")
def save_skill_api(req: SaveSkillRequest):
    from core.director_brain import save_custom_skill
    saved = save_custom_skill(req.dict())
    return {"status": "success", "skill": saved}


@app.delete("/api/skills/{skill_id}")
def delete_skill_api(skill_id: str):
    from core.director_brain import load_custom_skills, CUSTOM_SKILLS_FILE
    from core.utils import atomic_write_json
    skills = [s for s in load_custom_skills() if s.get("id") != skill_id]
    atomic_write_json(CUSTOM_SKILLS_FILE, skills)
    return {"status": "success", "message": "Beceri silindi."}


@app.get("/api/settings")
def get_settings_api():
    from core.director_brain import load_settings
    return {"status": "success", "settings": load_settings()}


@app.post("/api/settings")
def save_settings_api(req: SettingsRequest):
    from core.director_brain import save_settings, load_settings
    curr = load_settings()
    data = req.dict(exclude_unset=True)
    curr.update(data)
    save_settings(curr)
    global CURRENT_VOICE
    if "voice" in curr:
        CURRENT_VOICE = curr["voice"]
    return {"status": "success", "settings": curr}


@app.get("/api/videos")
def list_videos():
    videos = []
    if os.path.isdir(PROD_DIR):
        for name in sorted(os.listdir(PROD_DIR), reverse=True):
            folder = os.path.join(PROD_DIR, name)
            if os.path.isdir(folder):
                mp4 = os.path.join(folder, f"{name}.mp4")
                if os.path.exists(mp4):
                    stat = os.stat(mp4)
                    props_f = os.path.join(folder, "props.json")
                    props = read_json(props_f, {}) if os.path.exists(props_f) else {}
                    title = props.get("title") or name.replace("-", " ").title()
                    pano_path = os.path.join(folder, "pano.jpg")
                    videos.append({
                        "slug": name,
                        "title": title,
                        "video_url": f"/out/{name}/{name}.mp4",
                        "pano_url": f"/out/{name}/pano.jpg" if os.path.exists(pano_path) else None,
                        "size_mb": round(stat.st_size / (1024 * 1024), 2),
                        "created_at": datetime.fromtimestamp(stat.st_mtime).strftime("%d.%m.%Y %H:%M")
                    })
    return {"status": "success", "total": len(videos), "videos": videos}

@app.get("/api/state")
def get_state():
    return CURRENT_STATE


@app.get("/api/key_pool")
def get_key_pool():
    st = director_brain.get_status()
    return {"total_keys": st["total_keys"], "active_keys": st["total_keys"], "models": st["models"]}


@app.get("/api/agents")
def list_agents():
    agents = []
    if os.path.isdir(AGENTS_DIR):
        for folder in sorted(os.listdir(AGENTS_DIR)):
            data = read_json(os.path.join(AGENTS_DIR, folder, "memory.json"), None)
            if data is not None:
                agents.append(data)
    return {"total": len(agents), "agents": agents}


# ---------------------------------------------------------------- ses kütüphanesi
@app.get("/api/audio_library")
def get_audio_library():
    try:
        voices = turso_client.list_voices()
        return {"total": len(voices), "active_voice_id": CURRENT_VOICE, "voices": voices}
    except Exception as e:
        log_error("audio_library", e)
        return {"total": 0, "active_voice_id": CURRENT_VOICE, "voices": [], "error": str(e)}


@app.get("/api/audio_sample/{voice_id}")
def get_audio_sample(voice_id: str):
    try:
        raw, mime = turso_client.get_sample_audio(voice_id)
        if not raw:
            return _err(404, "Örnek ses bulunamadı")
        return Response(content=raw, media_type=mime or "audio/wav")
    except Exception as e:
        log_error("audio_sample", e)
        return _err(500, str(e))


@app.post("/api/voices/{voice_id}/favorite")
def toggle_voice_favorite(voice_id: str):
    try:
        return {"status": "success", "voice_id": voice_id, "is_favorite": turso_client.toggle_favorite(voice_id)}
    except Exception as e:
        log_error("favorite", e)
        return _err(500, str(e))


class SelectVoiceRequest(BaseModel):
    voice_id: str = Field(min_length=1, max_length=100)


@app.post("/api/voices/select")
def select_voice(req: SelectVoiceRequest):
    global CURRENT_VOICE
    CURRENT_VOICE = req.voice_id
    return {"status": "success", "active_voice_id": CURRENT_VOICE}


# ---------------------------------------------------------------- model & hata günlüğü
class SetModelRequest(BaseModel):
    model: str = Field(min_length=1, max_length=100)


@app.post("/api/set_model")
def set_model(req: SetModelRequest):
    ok = director_brain.prefer_model(req.model)
    return {"status": "success" if ok else "unchanged", "model": req.model, "active_model": director_brain.model_chain[0]}


@app.get("/api/errors")
def get_errors():
    return {"errors": list(ERROR_LOG)}


class ReportErrorRequest(BaseModel):
    error: Optional[Dict[str, Any]] = None


@app.post("/api/errors/report")
def report_error(req: ReportErrorRequest):
    if req.error:
        log_error("arayüz", req.error.get("message", req.error))
    return {"status": "reported"}


@app.post("/api/errors/clear")
def clear_errors():
    ERROR_LOG.clear()
    return {"status": "cleared"}


# ---------------------------------------------------------------- senaryo & hafıza
class UpdateScriptRequest(BaseModel):
    script: str = Field(max_length=20000)


@app.post("/api/update_script")
def update_script(req: UpdateScriptRequest):
    CURRENT_STATE["pre_render_package"]["script"] = req.script
    return {"status": "success"}


class PrepareMaterialsRequest(BaseModel):
    topic: str = Field(default="", max_length=300)
    style: Optional[str] = "Karma"
    voice_id: Optional[str] = None
    animation_style: Optional[str] = "2d_canvas"
    ambience_id: Optional[str] = None


@app.post("/api/prepare_materials")
def prepare_materials(req: PrepareMaterialsRequest):
    """Konuyu ve (varsa) sesi kaydeder. Senaryoyu Başyönetmen sohbetinden alın."""
    global CURRENT_VOICE
    if req.voice_id:
        CURRENT_VOICE = req.voice_id
    pkg = CURRENT_STATE["pre_render_package"]
    topic = req.topic.strip() or pkg.get("topic", "")
    pkg["topic"] = topic
    return {"status": "success", "message": f"«{topic}» konusu kaydedildi.", "package": pkg}


@app.get("/api/memory")
def get_memory():
    return read_json(os.path.join(BRAIN_DIR, "experience_memory.json"), {})


@app.get("/api/history")
def get_history():
    return read_json(os.path.join(BRAIN_DIR, "video_history.json"), [])


# ---------------------------------------------------------------- Başyönetmen sohbeti
class ChatMessage(BaseModel):
    message: str = Field(min_length=1, max_length=8000)
    channel_id: Optional[str] = None
    history: Optional[List[Dict[str, Any]]] = None
    model: Optional[str] = None
    skill: Optional[str] = None


@app.post("/api/chat/message")
def handle_chat(msg: ChatMessage):
    if msg.model:
        director_brain.prefer_model(msg.model)
    result = director_brain.chat(msg.message, skill=msg.skill)
    if "error" in result:
        return _err(400, result["error"])
    if result.get("degraded"):
        log_error("chat", result["reply"][:200])
    if result.get("suggested_topic"):
        CURRENT_STATE["pre_render_package"]["topic"] = result["suggested_topic"]
    return {
        "status": "success",
        "reply": result["reply"],
        "sender": result["sender"],
        "model_used": result["model_used"],
        "active_wardrobe": result["active_wardrobe"],
        "total_turns": result["total_turns"],
        "suggested_topic": result.get("suggested_topic"),
        "tracker_status": tracker.get_status(),
        "package": CURRENT_STATE.get("pre_render_package"),
    }


@app.get("/api/chat/history")
def get_chat_history():
    return {"status": "success", "history": director_brain.get_history(), "director_status": director_brain.get_status()}


@app.post("/api/chat/new")
def new_chat_session():
    return director_brain.new_session()


@app.post("/api/chat/clear")
@app.delete("/api/chat/history")
def clear_chat_history():
    return director_brain.clear_history()


@app.get("/api/director/status")
def get_director_status():
    return director_brain.get_status()


# ---------------------------------------------------------------- üretim
@app.get("/api/production/status")
def get_production_status():
    return tracker.get_status()


@app.post("/api/production/reset")
def reset_production_status():
    if tracker.busy:
        return _err(409, "Devam eden bir üretim var; bitmeden sıfırlanamaz.")
    tracker.reset()
    return {"status": "reset", "tracker": tracker.get_status()}


class ProduceRequest(BaseModel):
    project_slug: str
    title: str = Field(min_length=1, max_length=200)
    lines: List[str] = Field(min_length=1, max_length=60)
    category: Optional[str] = "İslami Tefekkür"
    voice_id: Optional[str] = None
    animation_style: Optional[str] = "2d_canvas"


@app.post("/api/produce")
def produce_video(req: ProduceRequest):
    """Üretimi yürütür ve bitince sonucu döndürür. İlerleme için /api/production/status sorgulanır."""
    try:
        validate_slug(req.project_slug)
    except InvalidSlugError as e:
        return _err(422, str(e))

    if not _produce_lock.acquire(blocking=False):
        return _err(409, "Başka bir video üretimi sürüyor. Bitmesini bekleyin.")
    try:
        from core.director_brain import load_settings
        st = load_settings()
        chosen_voice = req.voice_id or st.get("voice") or CURRENT_VOICE
        result = orchestrator.produce_video_from_lines(
            project_slug=req.project_slug,
            title=req.title,
            lines=req.lines,
            category=req.category,
            voice_id=chosen_voice,
            animation_style=req.animation_style or "2d_canvas",
        )
    finally:
        _produce_lock.release()

    if result.get("status") != "success":
        msg = result.get("error", "Üretim başarısız")
        log_error("produce", msg)
        return _err(500, msg)

    slug = req.project_slug
    pkg = {
        "topic": req.title,
        "script": "\n".join(req.lines),
        "scenes_count": len(req.lines),
        "audio_url": f"/public/{slug}/ses.mp3",
        "video_url": f"/out/{slug}/{slug}.mp4",
        "pano_url": f"/out/{slug}/pano.jpg",
        "quality_score": result.get("score"),
        "quality_notes": result.get("notes", []),
    }
    CURRENT_STATE["pre_render_package"] = pkg
    result.update(package=pkg, video_url=pkg["video_url"], pano_url=pkg["pano_url"], audio_url=pkg["audio_url"])
    return result


@app.post("/api/approve_and_render")
def approve_and_render():
    """Mevcut paketin hazır olup olmadığını bildirir (render /api/produce ile yapılır)."""
    pkg = CURRENT_STATE.get("pre_render_package") or {}
    if not pkg.get("video_url"):
        return _err(409, "Henüz üretilmiş bir video yok. Önce /api/produce ile üretin.")
    return {"status": "success", "message": "Video hazır.", "package": pkg}


if __name__ == "__main__":
    print("[NEXUS] AI Video Studio: http://127.0.0.1:8000")
    uvicorn.run("web.server:app", host="127.0.0.1", port=8000, reload=False)
