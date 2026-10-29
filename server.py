import os
import sys
import json
import time
import math
import shutil
import subprocess
import uuid
import zipfile
from typing import Optional, List, Dict, Any
from fastapi import FastAPI, HTTPException, BackgroundTasks, Request, UploadFile, File, Form
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse, RedirectResponse
from pydantic import BaseModel
from gtts import gTTS

sys.stdout.reconfigure(encoding='utf-8')

# Import Key Pool Manager, YouTube Uploader & Autopilot Scheduler
from scripts.key_pool import pool, DEFAULT_MODEL, SUPPORTED_MODELS
from scripts.youtube_uploader import uploader
from scripts.autopilot_scheduler import scheduler, VIRAL_BANK
from scripts.asset_manager import process_video_assets, initialize_core_assets
from scripts.tts_engine import (
    generate_full_narration_pipeline,
    VOICE_CATALOG,
    TONE_PROFILES,
    MUSIC_CATALOG
)
from scripts.image_engine import generate_ai_illustration
from scripts.multilingual_engine import (
    SUPPORTED_LANGUAGES,
    clone_project_to_all_languages,
    translate_video_script,
    dub_and_align_language
)
from scripts.timeline_engine import (
    extract_audio_waveform,
    ensure_scenes_structure,
    delete_scene_from_timeline,
    regenerate_scene_with_ai,
    split_scene_on_timeline,
    add_scene_to_timeline,
    trim_scene_on_timeline,
    reorder_scenes_on_timeline
)
from scripts.git_manager import (
    get_git_status,
    create_git_backup,
    list_git_history,
    rollback_to_commit,
    run_git
)
from scripts.audio_cleaner import clean_audio_and_realign

app = FastAPI(title="Notebook Video AI Studio Pro", version="4.0.0")

# Anti-Cache Middleware for Media & Dynamic Outputs
@app.middleware("http")
async def add_no_cache_headers(request: Request, call_next):
    response = await call_next(request)
    path = request.url.path
    if path.startswith("/out") or path.startswith("/public/audio.mp3") or path.startswith("/api/preview"):
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate, max-age=0"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
    return response

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.join(BASE_DIR, "out")
PUBLIC_DIR = os.path.join(BASE_DIR, "public")
DATA_DIR = os.path.join(BASE_DIR, "data")
SRC_DIR = os.path.join(BASE_DIR, "src")
HISTORY_FILE = os.path.join(DATA_DIR, "history.json")

os.makedirs(OUT_DIR, exist_ok=True)
os.makedirs(PUBLIC_DIR, exist_ok=True)
os.makedirs(DATA_DIR, exist_ok=True)

# Mount static files
app.mount("/out", StaticFiles(directory=OUT_DIR), name="out")
app.mount("/public", StaticFiles(directory=PUBLIC_DIR), name="public")

# Helper for history
def load_history() -> List[dict]:
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []

def save_history(history: List[dict]):
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)

# State for rendering progress
render_state = {
    "status": "idle",
    "progress": 0,
    "message": "HazÃ„Â±r",
    "video_url": "/out/video.mp4" if os.path.exists(os.path.join(OUT_DIR, "video.mp4")) else None,
    "thumbnail_url": "/out/thumbnail.png" if os.path.exists(os.path.join(OUT_DIR, "thumbnail.png")) else None,
    "last_rendered_at": None
}

class GenerateRequest(BaseModel):
    topic: str
    mode: Optional[str] = "auto" # "auto" (AI Director decides everything) or "manual"
    model: Optional[str] = DEFAULT_MODEL # Gemini model override (defaults to gemini-3.5-flash-lite)
    social_handle: Optional[str] = "@birkissa"
    voice_lang: Optional[str] = "tr"
    theme: Optional[str] = "notebook" # notebook, kraft, chalkboard, parchment, blueprint, dark_minimalist, neon_cyber, gold_luxury
    layout_type: Optional[str] = "cards" # cards, vs_split, flowchart, quote_spotlight, metric_impact, grid_explosion, tri_concept
    duration_mode: Optional[str] = "quick" # quick (~35s), deep (~90-120s)
    music_track: Optional[str] = "ambient_music.wav" # ambient_music.wav, ambient_documentary.wav, ambient_epic_cinematic.wav, ambient_mystic.wav
    tts_provider: Optional[str] = "edge_tts" # edge_tts, elevenlabs, gtts
    voice_id: Optional[str] = "en-US-AndrewMultilingualNeural"
    emotion_tone: Optional[str] = "documentary" # documentary, curiosity, dramatic, calm
    elevenlabs_api_key: Optional[str] = None
    particles: Optional[str] = None # dust, embers, fog, none
    ambient_pattern: Optional[str] = None # fingerprint, dna, cosmic, islamic_geometric, none
    doodle_type: Optional[str] = None # auto, galaxy, hourglass, book, lightbulb, compass, none
    film_grain: Optional[str] = "subtle" # subtle, vintage, heavy, none
    light_leaks: Optional[str] = "auto" # auto, golden_hour, cyan_dream, anamorphic, none
    camera_motion: Optional[str] = "handheld" # handheld, cinematic_drift, static
    accent_type: Optional[str] = "none" # curved_arrow, highlighter, burst, double_wave, zigzag, bracket, none
    enable_illustration: Optional[bool] = False
    illustration_prompt: Optional[str] = None
    illustration_caption: Optional[str] = None
    illustration_style: Optional[str] = "polaroid" # polaroid, torn_paper, clean_frame
    broll_type: Optional[str] = "none" # none, cosmic, clouds, waves, ink
    broll_opacity: Optional[float] = 0.18

class OptimizeRequest(BaseModel):
    topic: str
    style: Optional[str] = "curiosity" # curiosity, philosophy, science, viral
    model: Optional[str] = DEFAULT_MODEL

class UpdateDataRequest(BaseModel):
    video_data: dict

class KeyAddRequest(BaseModel):
    key_name: str
    api_key: str
    tier: Optional[str] = "free"

class MultilingualCloneRequest(BaseModel):
    project_id: Optional[str] = None
    target_languages: Optional[List[str]] = ["tr", "en", "ar", "es"]
    source_data: Optional[Dict[str, Any]] = None
    model: Optional[str] = None

class MultilingualSwitchRequest(BaseModel):
    project_id: str
    language: str

class SceneRegenerateRequest(BaseModel):
    prompt_override: Optional[str] = None
    layout_override: Optional[str] = None
    illustration_style_override: Optional[str] = None
    broll_override: Optional[str] = None
    model: Optional[str] = None

class SceneSplitRequest(BaseModel):
    scene_id: str
    split_time: float

class SceneTrimRequest(BaseModel):
    scene_id: str
    new_start: Optional[float] = None
    new_end: Optional[float] = None
    ripple: Optional[bool] = True

class SceneReorderRequest(BaseModel):
    scene_id: str
    new_index: int

class TimelineUpdateScenesRequest(BaseModel):
    scenes: List[Dict[str, Any]]

class SubtitleUpdateRequest(BaseModel):
    subtitles: List[Dict[str, Any]]

class AudioAutoCutRequest(BaseModel):
    min_duration: Optional[float] = 0.35
    keep_margin: Optional[float] = 0.08
    noise_threshold: Optional[str] = "-30dB"

class RenderMultiFormatRequest(BaseModel):
    formats: Optional[List[str]] = ["9:16"]

class CreateProjectRequest(BaseModel):
    title: Optional[str] = "Yeni Proje"
    format: Optional[str] = "9:16"
    theme: Optional[str] = "notebook"
    layoutType: Optional[str] = "pip_split"
    topic: Optional[str] = None

class GitBackupRequest(BaseModel):
    message: Optional[str] = None
    push: Optional[bool] = True

class GitRemoteRequest(BaseModel):
    remote_url: str

class GitRollbackRequest(BaseModel):
    commit_hash: str

class YouTubeCredentialsRequest(BaseModel):
    client_id: str
    client_secret: str

class YouTubeUploadRequest(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    tags: Optional[List[str]] = None
    privacy_status: Optional[str] = "public"
    publish_at: Optional[str] = None
    made_for_kids: Optional[bool] = False

class AutopilotJobRequest(BaseModel):
    title: str
    frequency: str = "daily"
    time: str = "18:00"
    interval_hours: Optional[int] = 6
    topic_source: Optional[str] = "bank"
    custom_topics: Optional[List[str]] = []
    theme: Optional[str] = "random"
    layout: Optional[str] = "auto"
    auto_upload: Optional[bool] = False
    privacy: Optional[str] = "private"
    webhook_url: Optional[str] = ""

whisper_model = None

def get_whisper():
    global whisper_model
    if whisper_model is None:
        try:
            import whisper
            whisper_model = whisper.load_model("tiny")
        except Exception as e:
            print(f"Whisper init error: {e}")
            whisper_model = None
    return whisper_model

def generate_subtitles_fallback(text: str, total_duration: float):
    words = text.split()
    if not words:
        return []
    time_per_word = total_duration / len(words)
    subtitles = []
    chunk_size = 3
    for i in range(0, len(words), chunk_size):
        chunk = words[i:i + chunk_size]
        start = round(i * time_per_word, 2)
        end = round(min(total_duration, (i + len(chunk)) * time_per_word), 2)
        subtitles.append({
            "text": " ".join(chunk),
            "start": start,
            "end": end
        })
    return subtitles

def generate_studio_audio_and_subtitles(
    narration_text: str,
    lang: str = "tr",
    provider: str = "edge_tts",
    voice_id: str = "en-US-AndrewMultilingualNeural",
    emotion_tone: str = "documentary",
    elevenlabs_api_key: Optional[str] = None
) -> tuple:
    """
    Faz 7 Multi-TTS Engine:
    1. Generates TTS audio with Edge-TTS Neural, ElevenLabs, or gTTS fallback.
    2. Applies emotion tone-based FFmpeg mastering (EQ + dynamic compand + pitch/rate).
    3. Runs Whisper AI word-level alignment and 3-word subtitle chunks.
    """
    try:
        res = generate_full_narration_pipeline(
            narration_text=narration_text,
            provider=provider or "edge_tts",
            voice_id=voice_id or "en-US-AndrewMultilingualNeural",
            emotion_tone=emotion_tone or "documentary",
            elevenlabs_api_key=elevenlabs_api_key,
            lang=lang or "tr"
        )
        return res["audioUrl"], res["subtitles"], res.get("words", [])
    except Exception as e:
        print(f"[Server] TTS Pipeline Error: {e}, attempting legacy fallback...")
        raw_audio_path = os.path.join(PUBLIC_DIR, "audio_raw.mp3")
        studio_audio_path = os.path.join(PUBLIC_DIR, "audio.mp3")
        try:
            tts = gTTS(text=narration_text, lang=lang or "tr")
            tts.save(raw_audio_path)
            filterchain = "equalizer=f=120:width_type=h:width=100:g=3.5,equalizer=f=3200:width_type=h:width=1200:g=2.5,compand=attacks=0.02:decays=0.2:points=-60/-60|-24/-12|0/-3:gain=2.5,atempo=1.06"
            subprocess.run(["ffmpeg", "-y", "-i", raw_audio_path, "-af", filterchain, studio_audio_path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception as ex:
            print(f"Fallback TTS error: {ex}")

        words = narration_text.split()
        subtitles = []
        cur = 0.0
        for i in range(0, len(words), 3):
            c = words[i:i + 3]
            subtitles.append({"text": " ".join(c), "start": round(cur, 2), "end": round(cur + 1.2, 2)})
            cur += 1.2
        return "audio.mp3", subtitles, []

@app.get("/")
def get_index():
    index_file = os.path.join(PUBLIC_DIR, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return {"message": "Notebook Video AI Pro Server Running"}

@app.get("/api/keys")
def get_keys():
    gemini_keys = [k for k in pool.keys if k.get("key_type") == "gemini_direct"]
    other_keys = [k for k in pool.keys if k.get("key_type") != "gemini_direct"]
    
    masked_list = []
    for k in pool.keys:
        raw_key = k.get("api_key", "")
        masked = raw_key[:8] + "..." + raw_key[-4:] if len(raw_key) > 12 else "***"
        masked_list.append({
            "id": k.get("id"),
            "key_name": k.get("key_name"),
            "masked_key": masked,
            "key_type": k.get("key_type"),
            "is_active": k.get("is_active", True),
            "status": k.get("status", "healthy"),
            "latency_ms": k.get("latency_ms", None),
            "daily_request_count": k.get("daily_request_count", 0),
            "success_count": k.get("success_count", 0),
            "error_count": k.get("error_count", 0),
            "last_used_at": k.get("last_used_at", ""),
            "last_error_message": k.get("last_error_message", "")
        })
    
    return {
        "total_keys": len(pool.keys),
        "gemini_direct_count": len(gemini_keys),
        "other_keys_count": len(other_keys),
        "active_keys_count": len([k for k in pool.keys if k.get("is_active", True)]),
        "keys": masked_list
    }

@app.post("/api/keys/test/{key_id}")
def test_single_key(key_id: str):
    target = next((k for k in pool.keys if str(k.get("id")) == str(key_id)), None)
    if not target:
        raise HTTPException(status_code=404, detail="Key bulunamadÃ„Â±")
    t0 = time.time()
    ok, msg = pool.test_key(target)
    latency = int((time.time() - t0) * 1000)
    target["latency_ms"] = latency if ok else 0
    pool.save_keys()
    return {"id": key_id, "success": ok, "message": msg, "status": target.get("status"), "latency_ms": latency}

@app.post("/api/keys/benchmark")
def benchmark_keys():
    gemini_keys = [k for k in pool.keys if k.get("key_type") == "gemini_direct" and k.get("is_active", True)][:6]
    results = []
    for k in gemini_keys:
        t0 = time.time()
        ok, msg = pool.test_key(k)
        lat = int((time.time() - t0) * 1000)
        k["latency_ms"] = lat if ok else 0
        results.append({
            "id": k["id"],
            "key_name": k["key_name"],
            "success": ok,
            "latency_ms": lat
        })
    pool.save_keys()
    return {"results": results}

@app.post("/api/keys/toggle/{key_id}")
def toggle_key(key_id: str):
    target = next((k for k in pool.keys if str(k.get("id")) == str(key_id)), None)
    if not target:
        raise HTTPException(status_code=404, detail="Key bulunamadÃ„Â±")
    target["is_active"] = not target.get("is_active", True)
    pool.save_keys()
    return {"id": key_id, "is_active": target["is_active"]}

@app.post("/api/keys/add")
def add_key(data: KeyAddRequest):
    new_id = str(max([int(k.get("id", 0)) for k in pool.keys] + [0]) + 1)
    key_type = "gemini_direct" if data.api_key.startswith("AIzaSy") else "vertex_custom"
    new_entry = {
        "id": new_id,
        "key_name": data.key_name,
        "api_key": data.api_key.strip(),
        "key_type": key_type,
        "is_active": True,
        "tier": data.tier,
        "daily_request_count": 0,
        "success_count": 0,
        "error_count": 0,
        "last_used_at": "",
        "last_error_at": "",
        "last_error_message": "",
        "status": "healthy"
    }
    pool.keys.insert(0, new_entry)
    pool.save_keys()
    return {"message": "Key eklendi", "key": new_entry}

# HISTORY ENDPOINTS
@app.get("/api/history")
def get_history_items():
    return load_history()

@app.delete("/api/history/{item_id}")
def delete_history_item(item_id: str):
    history = load_history()
    history = [h for h in history if h.get("id") != item_id]
    save_history(history)
    return {"success": True}

@app.post("/api/history/{item_id}/load")
def load_history_project(item_id: str):
    history = load_history()
    target = next((h for h in history if h.get("id") == item_id), None)
    if not target:
        raise HTTPException(status_code=404, detail="Proje bulunamadı.")
    
    v_data = target.get("video_data")
    if not v_data:
        v_data = {
            "topic": target.get("topic", "Yeni Proje"),
            "headerLine1": target.get("headerMain", "BAŞLIK"),
            "narration": target.get("narration", ""),
            "theme": target.get("theme", "notebook"),
            "layoutType": target.get("layoutType", "pip_split"),
            "scenes": target.get("scenes", [
                {
                    "id": "scene_1",
                    "headerSubtitle": "Bölüm 1",
                    "headerLine1": target.get("headerMain", "BAŞLIK"),
                    "circledWord": "İLK",
                    "headerLine2": "",
                    "highlightedText": "",
                    "layoutType": target.get("layoutType", "pip_split"),
                    "startTime": 0.0,
                    "endTime": 10.0,
                    "duration": 10.0
                }
            ]),
            "subtitles": target.get("subtitles", []),
            "totalDuration": target.get("duration", 10.0)
        }
    
    data_file = os.path.join(SRC_DIR, "generatedData.json")
    with open(data_file, "w", encoding="utf-8") as f:
        json.dump(v_data, f, ensure_ascii=False, indent=2)
        
    return {"success": True, "project": target, "video_data": v_data}

@app.post("/api/history/{item_id}/clone")
def clone_history_project(item_id: str):
    history = load_history()
    target = next((h for h in history if h.get("id") == item_id), None)
    if not target:
        raise HTTPException(status_code=404, detail="Proje bulunamadı.")
    
    cloned = json.loads(json.dumps(target))
    cloned["id"] = str(uuid.uuid4())[:8]
    cloned["topic"] = f"{target.get('topic', 'Proje')} (Kopya)"
    if "video_data" in cloned and isinstance(cloned["video_data"], dict):
        cloned["video_data"]["topic"] = cloned["topic"]
    cloned["created_at"] = time.strftime("%Y-%m-%d %H:%M:%S")
    history.insert(0, cloned)
    save_history(history[:30])
    return {"success": True, "project": cloned}

@app.post("/api/projects/new")
def create_new_blank_project(req: CreateProjectRequest):
    new_id = str(uuid.uuid4())[:8]
    title = req.title or req.topic or "Yeni Proje"
    default_scene = {
        "id": "scene_1",
        "headerSubtitle": "Bölüm 1",
        "headerLine1": title.upper(),
        "circledWord": "İLK",
        "headerLine2": "Fikrini Buraya Yaz",
        "highlightedText": "Önemli Nokta",
        "layoutType": req.layoutType or "pip_split",
        "startTime": 0.0,
        "endTime": 10.0,
        "duration": 10.0
    }
    new_data = {
        "topic": title,
        "theme": req.theme or "notebook",
        "format": req.format or "9:16",
        "headerSubtitle": "Bölüm 1",
        "headerLine1": title.upper(),
        "circledWord": "İLK",
        "headerLine2": "Fikrini Buraya Yaz",
        "highlightedText": "Önemli Nokta",
        "layoutType": req.layoutType or "pip_split",
        "scenes": [default_scene],
        "subtitles": [
            {"text": title, "start": 0.0, "end": 2.5},
            {"text": "kurgulamaya hemen başla", "start": 2.5, "end": 5.0}
        ],
        "totalDuration": 10.0,
        "created_at": time.strftime("%Y-%m-%d %H:%M:%S")
    }
    
    data_file = os.path.join(SRC_DIR, "generatedData.json")
    with open(data_file, "w", encoding="utf-8") as f:
        json.dump(new_data, f, ensure_ascii=False, indent=2)
        
    history = load_history()
    new_hist_item = {
        "id": new_id,
        "topic": title,
        "theme": req.theme or "notebook",
        "layoutType": req.layoutType or "pip_split",
        "durationMode": "10s",
        "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "headerMain": title.upper(),
        "thumbnail_url": "/out/thumbnail.png",
        "video_data": new_data
    }
    history.insert(0, new_hist_item)
    save_history(history[:30])
    
    return {"success": True, "project_id": new_id, "video_data": new_data, "project": new_hist_item}

# VIRAL PRESETS ENDPOINT
@app.get("/api/presets")
def get_presets():
    return [
        {
            "category": "Ã„Â°slam & TefekkÃƒÂ¼r",
            "icon": "fa-moon",
            "items": [
                {"title": "Allah kÃƒÂ¢inatÃ„Â± neden birden deÃ„Å¸il de altÃ„Â± gÃƒÂ¼nde yarattÃ„Â±?", "layout": "cards", "theme": "notebook"},
                {"title": "Kalbin mÃƒÂ¼hÃƒÂ¼rlenmesi ne demektir? Bir insan nasÃ„Â±l hissizleÃ…Å¸ir?", "layout": "quote_spotlight", "theme": "parchment"},
                {"title": "KarÃ„Â±ncanÃ„Â±n rÃ„Â±zkÃ„Â± ve ilahi nizamÃ„Â±n kusursuz matematiÃ„Å¸i", "layout": "flowchart", "theme": "kraft"}
            ]
        },
        {
            "category": "Tarih & DÃƒÂ¼Ã…Å¸ÃƒÂ¼nÃƒÂ¼rler",
            "icon": "fa-scroll",
            "items": [
                {"title": "Ã„Â°bn-i Sina bir kitabÃ„Â± neden 40 kez okudu ve yine anlamadÃ„Â±?", "layout": "metric_impact", "theme": "parchment"},
                {"title": "Ã„Â°mam Gazali akÃ„Â±l ile kalp arasÃ„Â±ndaki Ã…Å¸ÃƒÂ¼phe krizini nasÃ„Â±l aÃ…Å¸tÃ„Â±?", "layout": "vs_split", "theme": "kraft"},
                {"title": "Mimar Sinan'Ã„Â±n SÃƒÂ¼leymaniye'deki akustiÃ„Å¸i ÃƒÂ§ÃƒÂ¶zen kandil ve devekuÃ…Å¸u sÃ„Â±rrÃ„Â±", "layout": "flowchart", "theme": "blueprint"}
            ]
        },
        {
            "category": "Felsefe & Psikoloji",
            "icon": "fa-brain",
            "items": [
                {"title": "StoacÃ„Â±lÃ„Â±k vs Modern TelaÃ…Å¸: Kontrol edemediÃ„Å¸in Ã…Å¸eyleri dert etme!", "layout": "vs_split", "theme": "chalkboard"},
                {"title": "Ã„Â°nsan neden en ÃƒÂ§ok sevdiÃ„Å¸i Ã…Å¸eyleri erteler? Prokrastinasyon tuzaÃ„Å¸Ã„Â±", "layout": "cards", "theme": "notebook"},
                {"title": "YalnÃ„Â±zlÃ„Â±k hissi modern insanÃ„Â±n neden en bÃƒÂ¼yÃƒÂ¼k sÃ„Â±navÃ„Â±?", "layout": "quote_spotlight", "theme": "notebook"}
            ]
        },
        {
            "category": "Evren & Bilim",
            "icon": "fa-atom",
            "items": [
                {"title": "Zaman daÃ„Å¸larda neden daha hÃ„Â±zlÃ„Â± akar? Einstein'Ã„Â±n sÃ„Â±rrÃ„Â±", "layout": "metric_impact", "theme": "blueprint"},
                {"title": "Karadeliklerin olay ufkunu geÃƒÂ§ersek gerÃƒÂ§ekte ne gÃƒÂ¶rÃƒÂ¼rÃƒÂ¼z?", "layout": "flowchart", "theme": "chalkboard"},
                {"title": "IÃ…Å¸Ã„Â±k hÃ„Â±zÃ„Â±na yaklaÃ…Å¸tÃ„Â±kÃƒÂ§a kÃƒÂ¼tle neden sonsuza gider?", "layout": "cards", "theme": "blueprint"}
            ]
        }
    ]

# AVAILABLE GEMINI MODELS
@app.get("/api/models")
def get_available_models():
    return {
        "default": DEFAULT_MODEL,
        "models": SUPPORTED_MODELS
    }

# FAZ 7: MULTI-TTS VOICES & AUDIO TRACKS
@app.get("/api/audio/voices")
def get_audio_voices():
    """Returns available TTS providers, voice options, emotion profiles, and background music."""
    return {
        "voices": VOICE_CATALOG,
        "tones": TONE_PROFILES,
        "musicTracks": MUSIC_CATALOG
    }

@app.get("/api/audio/music-tracks")
def get_music_tracks():
    """Returns available ambient music tracks."""
    return MUSIC_CATALOG

# FAZ 9: MULTILINGUAL GLOBAL FACTORY & RTL ENDPOINTS
@app.get("/api/multilingual/languages")
def get_multilingual_languages():
    """Returns catalog of supported global languages and voice configurations."""
    return {
        "languages": SUPPORTED_LANGUAGES
    }

@app.post("/api/multilingual/translate-clone")
def clone_multilingual(req: MultilingualCloneRequest):
    """
    Clones video script into specified target languages (TR, EN, AR, ES),
    performs neural dubbing, Whisper DTW alignment, and returns full bundle.
    """
    try:
        source_data = req.source_data
        if not source_data:
            gen_path = os.path.join(SRC_DIR, "generatedData.json")
            if os.path.exists(gen_path):
                with open(gen_path, "r", encoding="utf-8") as f:
                    source_data = json.load(f)
            else:
                raise HTTPException(status_code=400, detail="Mevcut video verisi bulunamadÃ„Â±.")

        bundle = clone_project_to_all_languages(
            source_data=source_data,
            project_id=req.project_id,
            target_languages=req.target_languages or ["tr", "en", "ar", "es"],
            model=req.model or DEFAULT_MODEL
        )
        return {
            "success": True,
            "bundle": bundle
        }
    except Exception as e:
        print(f"[Multilingual Error] {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/multilingual/switch-preview")
def switch_multilingual_preview(req: MultilingualSwitchRequest):
    """
    Switches active preview in Remotion to the requested language from a project bundle.
    """
    pid = req.project_id
    lang = req.language
    lang_file = os.path.join(PUBLIC_DIR, "multilingual", pid, f"{lang}.json")
    if not os.path.exists(lang_file):
        raise HTTPException(status_code=404, detail=f"{lang} dil dosyasÃ„Â± bulunamadÃ„Â±.")

    with open(lang_file, "r", encoding="utf-8") as f:
        target_data = json.load(f)

    # Save to src/generatedData.json for Remotion
    gen_file = os.path.join(SRC_DIR, "generatedData.json")
    with open(gen_file, "w", encoding="utf-8") as f:
        json.dump(target_data, f, ensure_ascii=False, indent=2)

    return {
        "success": True,
        "language": lang,
        "isRTL": target_data.get("isRTL", False),
        "video_data": target_data
    }

@app.get("/api/multilingual/project/{project_id}")
def get_multilingual_project(project_id: str):
    """Returns all available language builds for a project."""
    bundle_meta = os.path.join(PUBLIC_DIR, "multilingual", project_id, "meta.json")
    if not os.path.exists(bundle_meta):
        raise HTTPException(status_code=404, detail="Proje bulunamadÃ„Â±.")
    with open(bundle_meta, "r", encoding="utf-8") as f:
        meta = json.load(f)
    return meta

# PROMPT OPTIMIZER (AI ASSISTANT)
@app.post("/api/prompt/optimize")
def optimize_prompt(req: OptimizeRequest):
    topic = req.topic.strip()
    if not topic:
        raise HTTPException(status_code=400, detail="Konu boÃ…Å¸ olamaz")
    
    style_prompts = {
        "curiosity": "Merak uyandÃ„Â±ran, izleyicide soru iÃ…Å¸areti bÃ„Â±rakan ve tÃ„Â±klama isteÃ„Å¸i doÃ„Å¸uran bir kanca sorusu hazÃ„Â±rla.",
        "philosophy": "Derin felsefi ve tefekkÃƒÂ¼r iÃƒÂ§eren, insanÃ„Â±n hayatÃ„Â±nÃ„Â± sorgulatan bilgece bir cÃƒÂ¼mle hazÃ„Â±rla.",
        "science": "Ãƒâ€¡arpÃ„Â±cÃ„Â± bir bilimsel paradoks veya evren sÃ„Â±rrÃ„Â±nÃ„Â± ortaya koyan heyecan verici bir ifade hazÃ„Â±rla.",
        "viral": "YouTube Shorts ve TikTok iÃƒÂ§in tÃ„Â±klanma rekoru kÃ„Â±racak en yÃƒÂ¼ksek kanca (click-hook) etkili baÃ…Å¸lÃ„Â±Ã„Å¸Ã„Â± ÃƒÂ¼ret."
    }
    style_instruction = style_prompts.get(req.style, style_prompts["curiosity"])

    prompt = f"""Sen viral Shorts ve TikTok iÃƒÂ§erik kancasÃ„Â± ustasÃ„Â±sÃ„Â±n.
KullanÃ„Â±cÃ„Â± konusu: '{topic}'
Hedef ÃƒÅ“slup: {style_instruction}

LÃƒÂ¼tfen bu konuyu defter formatÃ„Â±nda tek satÃ„Â±rlÃ„Â±k efsanevi bir soruya/kancaya dÃƒÂ¶nÃƒÂ¼Ã…Å¸tÃƒÂ¼r ve en uygun layoutType ÃƒÂ¶ner (cards, vs_split, flowchart, quote_spotlight, metric_impact).

SADECE SAF JSON FORMATINDA YANIT VER:
{{
  "optimized_topic": "DÃƒÂ¶nÃƒÂ¼Ã…Å¸tÃƒÂ¼rÃƒÂ¼lmÃƒÂ¼Ã…Å¸ kanca baÃ…Å¸lÃ„Â±Ã„Å¸Ã„Â±",
  "suggested_layout": "cards",
  "reason": "Neden bu formatÃ„Â±n seÃƒÂ§ildiÃ„Å¸inin 1 cÃƒÂ¼mlelik aÃƒÂ§Ã„Â±klamasÃ„Â±"
}}
"""
    effective_model = req.model or DEFAULT_MODEL
    res, key_name = pool.query_with_rotation(prompt, "You are a specialized hook optimizer. Output ONLY raw JSON.", model=effective_model)
    if not res:
        raise HTTPException(status_code=500, detail="Key havuzundan yanÃ„Â±t alÃ„Â±namadÃ„Â±.")

    import re
    cleaned = re.sub(r"```json\s*", "", res)
    cleaned = re.sub(r"```\s*", "", cleaned).strip()

    try:
        opt_data = json.loads(cleaned)
        return opt_data
    except Exception as e:
        return {
            "optimized_topic": topic,
            "suggested_layout": "cards",
            "reason": "DoÃ„Å¸rudan konu kullanÃ„Â±ldÃ„Â±."
        }

# INLINE STORYBOARD UPDATE (WYSIWYG)
@app.post("/api/update_data")
def update_storyboard_data(req: UpdateDataRequest):
    video_data = req.video_data
    narration_text = video_data.get("narration", "")
    
    # Re-generate TTS & Studio Subtitles if narration changed
    if narration_text:
        audio_name, subtitles, words_list = generate_studio_audio_and_subtitles(
            narration_text=narration_text,
            lang="tr",
            provider=video_data.get("ttsProvider", "edge_tts"),
            voice_id=video_data.get("voiceId", "en-US-AndrewMultilingualNeural"),
            emotion_tone=video_data.get("emotionTone", "documentary"),
            elevenlabs_api_key=video_data.get("elevenlabsApiKey")
        )
        video_data["subtitles"] = subtitles
        video_data["words"] = words_list
        video_data["audioUrl"] = audio_name

    # Save to generatedData.json
    out_json = os.path.join(SRC_DIR, "generatedData.json")
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(video_data, f, ensure_ascii=False, indent=2)

    return {
        "success": True,
        "video_data": video_data,
        "audio_url": "/public/audio.mp3?t=" + str(int(time.time()))
    }

def probe_audio_duration(file_path: str) -> float:
    try:
        cmd = [
            "ffprobe", "-v", "error", "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1", file_path
        ]
        res = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return float(res.stdout.strip())
    except Exception as e:
        print(f"ffprobe error: {e}")
        return 0.0

# =========================================================================
# LIVE AUDIO UPLOAD & MULTI-SCENE CHAINED NARRATIVE ENGINE
# =========================================================================
@app.post("/api/audio/upload")
async def upload_audio_and_generate_multiscene(
    file: UploadFile = File(...),
    model: Optional[str] = Form(DEFAULT_MODEL),
    theme: Optional[str] = Form(None),
    mode: Optional[str] = Form("auto"),
    scene_duration: Optional[int] = Form(12),
    social_handle: Optional[str] = Form("@birkissa"),
    film_grain: Optional[str] = Form("subtle"),
    light_leaks: Optional[str] = Form("auto"),
    camera_motion: Optional[str] = Form("handheld"),
    accent_type: Optional[str] = Form("none"),
    music_track: Optional[str] = Form("ambient_music.wav"),
    broll_type: Optional[str] = Form("none"),
    enable_illustration: Optional[bool] = Form(False)
):
    if not file:
        raise HTTPException(status_code=400, detail="LÃƒÂ¼tfen bir ses dosyasÃ„Â± seÃƒÂ§in.")

    ext = os.path.splitext(file.filename)[1].lower() if file.filename else ".mp3"
    allowed_exts = [".mp3", ".wav", ".m4a", ".ogg", ".aac", ".flac", ".wma", ".webm"]
    if ext not in allowed_exts:
        raise HTTPException(status_code=400, detail=f"Desteklenmeyen ses formatÃ„Â± ({ext}). MP3, WAV veya M4A yÃƒÂ¼kleyin.")

    # 1. Save uploaded file to temp path
    upload_raw_path = os.path.join(DATA_DIR, f"upload_raw_{uuid.uuid4().hex[:8]}{ext}")
    try:
        with open(upload_raw_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ses dosyasÃ„Â± kaydedilemedi: {str(e)}")

    target_audio_path = os.path.join(PUBLIC_DIR, "audio.mp3")

    # 2. FFmpeg Studio Mastering (warm EQ + punch compand + 24kHz mono MP3 conversion)
    filterchain = (
        "equalizer=f=120:width_type=h:width=100:g=3.5,"
        "equalizer=f=3200:width_type=h:width=1200:g=2.5,"
        "compand=attacks=0.02:decays=0.2:points=-60/-60|-24/-12|0/-3:gain=2.5"
    )
    try:
        cmd = ["ffmpeg", "-y", "-i", upload_raw_path, "-af", filterchain, "-ac", "1", "-ar", "24000", target_audio_path]
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    except Exception as e:
        print(f"FFmpeg conversion fallback: {e}")
        try:
            cmd = ["ffmpeg", "-y", "-i", upload_raw_path, "-ac", "1", "-ar", "24000", target_audio_path]
            subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        except Exception as e2:
            shutil.copyfile(upload_raw_path, target_audio_path)

    # 3. Probe audio duration
    total_duration = probe_audio_duration(target_audio_path)

    # 4. Whisper millisecond word-level alignment & full transcription
    try:
        whisper_m = get_whisper()
        w_res = whisper_m.transcribe(target_audio_path, word_timestamps=True, language="tr", fp16=False)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Whisper ses ÃƒÂ§ÃƒÂ¶zÃƒÂ¼mleme hatasÃ„Â±: {str(e)}")

    whisper_words = []
    for seg in w_res.get("segments", []):
        for w in seg.get("words", []):
            w_text = w["word"].strip()
            if w_text:
                whisper_words.append({
                    "text": w_text,
                    "start": round(w["start"], 2),
                    "end": round(w["end"], 2)
                })

    full_transcript = " ".join([w["text"] for w in whisper_words]).strip()
    if not full_transcript:
        full_transcript = w_res.get("text", "").strip() or "KullanÃ„Â±cÃ„Â±nÃ„Â±n yÃƒÂ¼klediÃ„Å¸i ses kaydÃ„Â±"

    if (total_duration <= 0 or total_duration < 4.0) and whisper_words:
        total_duration = whisper_words[-1]["end"] + 1.0
    total_duration = max(8.0, round(total_duration, 2))

    # 5. Build 3-word subtitle chunks for live karaoke & video subtitles
    subtitles = []
    chunk_size = 3
    if whisper_words:
        for i in range(0, len(whisper_words), chunk_size):
            ch = whisper_words[i:i + chunk_size]
            subtitles.append({
                "text": " ".join([w["text"] for w in ch]),
                "start": ch[0]["start"],
                "end": ch[-1]["end"]
            })
    else:
        # Fallback if whisper returned text without word timestamps
        subtitles = generate_subtitles_fallback(full_transcript, total_duration)

    # 6. Segment into 10-14 second sequential scenes
    sec_per_scene = max(8.0, min(16.0, float(scene_duration or 12)))
    num_scenes = max(1, math.ceil(total_duration / sec_per_scene))
    if num_scenes == 1 and total_duration > 18.0:
        num_scenes = 2

    scene_slices = []
    for i in range(num_scenes):
        st = round(i * (total_duration / num_scenes), 2)
        en = round((i + 1) * (total_duration / num_scenes), 2) if i < num_scenes - 1 else round(total_duration, 2)
        words_in_window = [w["text"] for w in whisper_words if (w["start"] >= st - 0.5 and w["end"] <= en + 0.5)]
        slice_text = " ".join(words_in_window)
        if not slice_text and i == 0:
            slice_text = full_transcript[:120]
        scene_slices.append({
            "scene_index": i + 1,
            "start_time": st,
            "end_time": en,
            "text_spoken": slice_text or f"{i+1}. BÃƒÂ¶lÃƒÂ¼m KonuÃ…Å¸masÃ„Â±"
        })

    # 7. Gemini 3 Director Prompt for Multi-Scene Storyboard
    effective_model = model or DEFAULT_MODEL
    prompt = f"""Sen viral YouTube Shorts, TikTok ve Mini-Belgesel prodÃƒÂ¼ksiyonlarÃ„Â±nÃ„Â±n BAÃ…Â YAPAY ZEKÃƒâ€š YÃƒâ€“NETMENÃ„Â° ve senaristisin.
KullanÃ„Â±cÃ„Â± kendi ses kaydÃ„Â±nÃ„Â± yÃƒÂ¼kledi!
Toplam Ses SÃƒÂ¼resi: {total_duration:.1f} saniye.
Tam Ses DÃƒÂ¶kÃƒÂ¼mÃƒÂ¼: '{full_transcript}'

Bu ses {num_scenes} ardÃ„Â±Ã…Å¸Ã„Â±k bÃƒÂ¶lÃƒÂ¼me/sahneye ayrÃ„Â±ldÃ„Â±. Her sahne yaklaÃ…Å¸Ã„Â±k {total_duration / num_scenes:.1f} saniye sÃƒÂ¼rmektedir:
{json.dumps(scene_slices, ensure_ascii=False, indent=2)}

GÃƒâ€“REVÃ„Â°N:
1. TemayÃ„Â± belirle: 'dark_minimalist' | 'gold_luxury' | 'neon_cyber' | 'parchment' | 'notebook' | 'kraft' | 'chalkboard' | 'blueprint'
   (KURAL: Ã„Â°slami / derin tefekkÃƒÂ¼r dendiÃ„Å¸inde KESÃ„Â°NLÃ„Â°KLE 'dark_minimalist' veya 'gold_luxury'; Bilim / teknoloji / evren iÃƒÂ§in 'neon_cyber' veya 'blueprint'; Tarih / felsefe iÃƒÂ§in 'parchment' veya 'kraft')
2. HER BÃ„Â°R BÃƒâ€“LÃƒÅ“M (SCENE) Ã„Â°Ãƒâ€¡Ã„Â°N:
   - Ãƒâ€“nceki sahnenin bittiÃ„Å¸i yerden devam edecek Ã…Å¸ekilde ve gÃƒÂ¶rsel monotonluÃ„Å¸u kÃ„Â±rmak iÃƒÂ§in FARKLI bir Ã…Å¸ablon (layoutType) seÃƒÂ§:
     'cards' | 'vs_split' | 'flowchart' | 'quote_spotlight' | 'metric_impact' | 'grid_explosion' | 'tri_concept'
   - Sahneye ÃƒÂ¶zel 'headerSubtitle', 'headerLine1', 'circledWord', 'headerLine2', 'highlightedText', 'strikeWord' oluÃ…Å¸tur.
   - SeÃƒÂ§tiÃ„Å¸in layoutType'a uygun zengin iÃƒÂ§erik verisini (cards, vsData, flowchartSteps, quoteSpotlight, metricImpact, gridExplosion, triConcept) ÃƒÂ¼ret.
3. 'requiredIcons': Senaryolarda geÃƒÂ§en tÃƒÂ¼m ikon isimleri (ÃƒÂ¶rn: ['fingerprint', 'dna', 'atom', 'brain', 'heart', 'eye', 'scale', 'hourglass', 'book', 'lightbulb', 'compass', 'shield', 'infinity']).

SADECE SAF GEÃƒâ€¡ERLÃ„Â° JSON DÃƒâ€“NDÃƒÅ“R:
{{
  "directorDecision": {{
    "theme": "{theme if theme else 'dark_minimalist'}",
    "particles": "dust",
    "ambientPattern": "fingerprint",
    "directorReason": "KullanÃ„Â±cÃ„Â±nÃ„Â±n yÃƒÂ¼klediÃ„Å¸i sese uygun olarak dinamik ÃƒÂ§ok sahneli kurgu hazÃ„Â±rlandÃ„Â±."
  }},
  "requiredIcons": ["fingerprint", "dna", "brain", "scale"],
  "scenes": [
    {{
      "id": "scene_1",
      "startTime": 0.0,
      "endTime": {scene_slices[0]['end_time']},
      "layoutType": "grid_explosion",
      "headerSubtitle": "1. BÃƒÂ¶lÃƒÂ¼m",
      "headerLine1": "Ã„Â°LK SIR",
      "circledWord": "BAÃ…ÂLANGIÃƒâ€¡",
      "headerLine2": "",
      "highlightedText": "CANLI SES VURGUSU",
      "strikeWord": "TESADÃƒÅ“F",
      "gridExplosion": {{
        "title": "EÃ…ÂSÃ„Â°Z Ã„Â°Ã…ÂARET",
        "subtitle": "Kelimelerin ArdÃ„Â±ndaki Derin Anlam",
        "iconType": "fingerprint",
        "itemCount": 12,
        "badgeText": "BÃ„Â°RÃ„Â°NCÃ„Â° AÃ…ÂAMA"
      }}
    }}
  ],
  "viral": {{
    "hookScore": 98,
    "viralTitles": ["Kendi Sesinden Shorts BaÃ…Å¸lÃ„Â±Ã„Å¸Ã„Â± 1", "BaÃ…Å¸lÃ„Â±k 2"],
    "hashtags": ["#shorts", "#viral", "#seslikurgu"],
    "loopEnding": "ve iÃ…Å¸te bu yÃƒÂ¼zden...",
    "description": "KullanÃ„Â±cÃ„Â± ses kaydÃ„Â±yla ÃƒÂ¼retilen profesyonel video."
  }}
}}
"""
    res, key_name = pool.query_with_rotation(prompt, "You are a specialized JSON video schema generator. Output ONLY raw JSON.", model=effective_model)
    if not res:
        raise HTTPException(status_code=500, detail=f"LLM modelinden ({effective_model}) yanÃ„Â±t alÃ„Â±namadÃ„Â±.")

    import re
    cleaned = re.sub(r"```json\s*", "", res)
    cleaned = re.sub(r"```\s*", "", cleaned).strip()

    try:
        video_data = json.loads(cleaned)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLM JSON ÃƒÂ§Ã„Â±ktÃ„Â±sÃ„Â± ayrÃ„Â±Ã…Å¸tÃ„Â±rÃ„Â±lamadÃ„Â±: {str(e)}")

    director_dec = video_data.get("directorDecision", {})
    selected_theme = theme or director_dec.get("theme") or "dark_minimalist"
    is_dark = (selected_theme in ["dark_minimalist", "neon_cyber", "gold_luxury"])
    particles = director_dec.get("particles") or ("dust" if is_dark else "none")
    ambient_pattern = director_dec.get("ambientPattern") or ("fingerprint" if is_dark else "none")

    # Enrich video_data with root properties & ensure scenes match timings
    video_data["theme"] = selected_theme
    video_data["particles"] = particles
    video_data["ambientPattern"] = ambient_pattern
    video_data["socialHandle"] = social_handle or "@birkissa"
    video_data["audioUrl"] = "audio.mp3"
    video_data["filmGrain"] = film_grain or "subtle"
    video_data["lightLeaks"] = light_leaks or "auto"
    video_data["cameraMotion"] = camera_motion or "handheld"
    video_data["accentType"] = accent_type or "none"
    video_data["musicTrack"] = music_track or "ambient_music.wav"
    video_data["brollType"] = broll_type or "none"
    if enable_illustration:
        try:
            ill_res = generate_ai_illustration(full_transcript[:80], style="polaroid", caption="KayÃ„Â±ttan Sahne")
            video_data["illustrationUrl"] = ill_res["illustrationUrl"]
            video_data["illustrationCaption"] = ill_res["caption"]
        except Exception as e:
            print(f"Audio upload illustration error: {e}")

    video_data["subtitles"] = subtitles
    video_data["words"] = whisper_words
    video_data["narration"] = full_transcript
    video_data["totalDuration"] = total_duration
    video_data["durationMode"] = "custom_audio"

    # Validate and sync scenes array
    parsed_scenes = video_data.get("scenes", [])
    synced_scenes = []

    available_layouts = ['pip_split', 'cards', 'vs_split', 'flowchart', 'quote_spotlight', 'metric_impact', 'grid_explosion', 'tri_concept']

    for i, sl in enumerate(scene_slices):
        sc = parsed_scenes[i] if i < len(parsed_scenes) else {}
        sc_id = f"scene_{i + 1}"
        sc_layout = sc.get("layoutType") or available_layouts[i % len(available_layouts)]
        
        # Ensure fallback data if LLM omitted specific layout
        if sc_layout == "cards" and not sc.get("cards"):
            sc["cards"] = [
                {"id": "1", "label": "1. Anahtar", "value": "AÃƒÂ§Ã„Â±klama", "icon": "brain", "color": "#1e3a8a"},
                {"id": "2", "label": "2. Anahtar", "value": "GeliÃ…Å¸me", "icon": "scale", "color": "#15803d"},
                {"id": "3", "label": "3. Anahtar", "value": "SonuÃƒÂ§", "icon": "lightbulb", "color": "#d97706"}
            ]
        elif sc_layout == "vs_split" and not sc.get("vsData"):
            sc["vsData"] = {
                "leftTitle": "Zan / YanÃ„Â±lgÃ„Â±",
                "leftSubtitle": "GÃƒÂ¶rÃƒÂ¼nen",
                "leftPoints": ["YÃƒÂ¼zeysel algÃ„Â±"],
                "rightTitle": "Hakikat",
                "rightSubtitle": "GerÃƒÂ§ek Olan",
                "rightPoints": ["Derin anlam"],
                "verdict": "Hakikat daima ayrÃ„Â±ntÃ„Â±larda gizlidir."
            }
        elif sc_layout == "flowchart" and not sc.get("flowchartSteps"):
            sc["flowchartSteps"] = [
                {"stepNumber": 1, "badge": "GiriÃ…Å¸", "title": "BÃƒÂ¼yÃƒÂ¼k Soru"},
                {"stepNumber": 2, "badge": "GeliÃ…Å¸me", "title": "DÃƒÂ¶nÃƒÂ¼m NoktasÃ„Â±"},
                {"stepNumber": 3, "badge": "SonuÃƒÂ§", "title": "Ãƒâ€¡Ã„Â±karÃ„Â±m"}
            ]
        elif sc_layout == "tri_concept" and not sc.get("triConcept"):
            sc["triConcept"] = {
                "badge": f"{i+1}. BÃƒâ€“LÃƒÅ“M",
                "concept1": {"title": "BEYÃ„Â°N", "icon": "brain"},
                "concept2": {"title": "KALP", "icon": "heart"},
                "concept3": {"title": "GÃƒâ€“Z", "icon": "eye"},
                "bottomNote": "Her parÃƒÂ§a tek bir ahengin ifadesidir."
            }
        elif sc_layout == "metric_impact" and not sc.get("metricImpact"):
            sc["metricImpact"] = {
                "bigNumber": "%100",
                "bigLabel": "DOÃ„ÂRULUK",
                "subheading": "EÃ…Å¸siz Ã„Â°fade",
                "keyTakeaway": "SÃƒÂ¶zler doÃ„Å¸ru anahtarla aÃƒÂ§Ã„Â±lÃ„Â±r."
            }
        elif sc_layout == "quote_spotlight" and not sc.get("quoteSpotlight"):
            sc["quoteSpotlight"] = {
                "speaker": "Ses KaydÃ„Â±",
                "quoteText": sl["text_spoken"][:90] or full_transcript[:90]
            }
        elif sc_layout == "grid_explosion" and not sc.get("gridExplosion"):
            sc["gridExplosion"] = {
                "title": "MÃ„Â°LYARLARCA MÃƒÅ“HÃƒÅ“R",
                "subtitle": "Benzersiz AnlatÃ„Â±m",
                "iconType": "fingerprint",
                "itemCount": 12,
                "badgeText": "HAKÃ„Â°KAT"
            }

        synced_scene = {
            "id": sc_id,
            "startTime": sl["start_time"],
            "endTime": sl["end_time"],
            "layoutType": sc_layout,
            "headerSubtitle": sc.get("headerSubtitle") or f"{i+1}. BÃƒÂ¶lÃƒÂ¼m ({sl['start_time']}s - {sl['end_time']}s)",
            "headerLine1": sc.get("headerLine1") or (full_transcript.split()[0].upper() if full_transcript.split() else "DÃ„Â°KKAT"),
            "circledWord": sc.get("circledWord") or (full_transcript.split()[1].upper() if len(full_transcript.split()) > 1 else "BÃƒÅ“YÃƒÅ“K"),
            "headerLine2": sc.get("headerLine2") or "",
            "highlightedText": sc.get("highlightedText") or (full_transcript.split()[2].upper() if len(full_transcript.split()) > 2 else "SIR"),
            "strikeWord": sc.get("strikeWord"),
            "cards": sc.get("cards"),
            "vsData": sc.get("vsData"),
            "flowchartSteps": sc.get("flowchartSteps"),
            "quoteSpotlight": sc.get("quoteSpotlight"),
            "metricImpact": sc.get("metricImpact"),
            "gridExplosion": sc.get("gridExplosion"),
            "triConcept": sc.get("triConcept"),
            "timeline": sc.get("timeline")
        }
        synced_scenes.append(synced_scene)

    video_data["scenes"] = synced_scenes

    # Copy first scene properties to root for 100% backward compatibility
    if synced_scenes:
        first = synced_scenes[0]
        video_data["layoutType"] = first["layoutType"]
        video_data["headerSubtitle"] = first["headerSubtitle"]
        video_data["headerLine1"] = first["headerLine1"]
        video_data["circledWord"] = first["circledWord"]
        video_data["headerLine2"] = first["headerLine2"]
        video_data["highlightedText"] = first["highlightedText"]
        video_data["strikeWord"] = first.get("strikeWord")
        for k in ["cards", "vsData", "flowchartSteps", "quoteSpotlight", "metricImpact", "gridExplosion", "triConcept"]:
            if first.get(k):
                video_data[k] = first[k]

    # Ingest assets required across all scenes
    video_data = process_video_assets(video_data, pool=pool)
    acquired_assets = video_data.get("_acquired_assets", [])

    # Save to generatedData.json
    out_json = os.path.join(SRC_DIR, "generatedData.json")
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(video_data, f, ensure_ascii=False, indent=2)

    # Save to History
    history = load_history()
    hist_id = str(uuid.uuid4())[:8]
    new_hist_item = {
        "id": hist_id,
        "topic": f"ÄŸÅ¸Ââ„¢Ã¯Â¸Â Ses YÃƒÂ¼kleme: {full_transcript[:60]}...",
        "theme": selected_theme,
        "layoutType": video_data.get("layoutType", "cards"),
        "durationMode": f"{len(synced_scenes)} Sahne ({total_duration:.0f}s)",
        "created_at": time.strftime("%Y-%m-%d %H:%M"),
        "headerMain": video_data.get("headerLine1", "") + " " + video_data.get("circledWord", "") + " " + video_data.get("highlightedText", ""),
        "narration": full_transcript,
        "hookScore": video_data.get("viral", {}).get("hookScore", 95),
        "key_used": key_name,
        "model_used": effective_model,
        "thumbnail_url": "/out/thumbnail.png?t=" + str(int(time.time())),
        "video_data": video_data
    }
    history.insert(0, new_hist_item)
    save_history(history[:30])

    t_now = str(int(time.time() * 1000))
    return {
        "success": True,
        "key_used": key_name,
        "model_used": effective_model,
        "total_duration": total_duration,
        "num_scenes": len(synced_scenes),
        "scenes": synced_scenes,
        "subtitles": subtitles,
        "words": whisper_words,
        "video_data": video_data,
        "audio_url": f"/public/audio.mp3?t={t_now}",
        "history_item": new_hist_item,
        "director_reason": director_dec.get("directorReason") or f"YÃƒÂ¼klenen {total_duration:.1f} saniyelik ses kaydÃ„Â± iÃƒÂ§in {len(synced_scenes)} bÃƒÂ¶lÃƒÂ¼mlÃƒÂ¼ dinamik video kurgulandÃ„Â±."
    }

@app.post("/api/generate")
def generate_video_content(req: GenerateRequest):
    topic = req.topic.strip()
    if not topic:
        raise HTTPException(status_code=400, detail="Konu boÃ…Å¸ olamaz")

    is_auto = (req.mode == "auto" or not req.mode)

    # In manual mode, word requirement depends on explicit duration_mode
    word_req = "90-130 kelimelik derin, belgesel kurgulu, tefekkÃƒÂ¼r ve merak uyandÃ„Â±ran" if req.duration_mode == "deep" else "35-50 kelimelik akÃ„Â±cÃ„Â±, merak uyandÃ„Â±ran"

    prompt = f"""Sen viral YouTube Shorts, TikTok ve Mini-Belgesel prodÃƒÂ¼ksiyonlarÃ„Â±nÃ„Â±n BAÃ…Â YAPAY ZEKÃƒâ€š YÃƒâ€“NETMENÃ„Â° ve senaristisin.
KullanÃ„Â±cÃ„Â± Talebi / Girdisi: '{topic}'
Ãƒâ€¡alÃ„Â±Ã…Å¸ma Modu: {'ÄŸÅ¸Â¤â€“ AI YÃƒâ€“NETMEN MODU (TÃƒÂ¼m kararlarÃ„Â± sen ver)' if is_auto else f'ÄŸÅ¸â€ºÂ Ã¯Â¸Â MANUEL KULLANICI MODU (SeÃƒÂ§ilen: Tema: {req.theme}, Ã…Âablon: {req.layout_type}, SÃƒÂ¼re: {req.duration_mode})'}

GÃƒâ€“REV 1: YÃƒâ€“NETMEN KARARI (DIRECTOR DECISION)
KullanÃ„Â±cÃ„Â±nÃ„Â±n yazdÃ„Â±Ã„Å¸Ã„Â± metni derinlemesine analiz et. EÃ„Å¸er kullanÃ„Â±cÃ„Â± ÃƒÂ¶rtÃƒÂ¼k veya aÃƒÂ§Ã„Â±k bir tema (ÃƒÂ¶rn: 'islami', 'karanlÃ„Â±k tema', 'felsefe', 'karatahta', 'belgesel', 'hÃ„Â±zlÃ„Â±') belirttiyse veya sadece yalÃ„Â±n bir konu verdiyse, EN UYGUN ve en viral parametreleri seÃƒÂ§:
- 'theme': 'dark_minimalist' | 'gold_luxury' | 'neon_cyber' | 'parchment' | 'notebook' | 'kraft' | 'chalkboard' | 'blueprint'
  (KURAL: 'islami' ve 'karanlÃ„Â±k' veya 'derin tefekkÃƒÂ¼r' dendiÃ„Å¸inde KESÃ„Â°NLÃ„Â°KLE 'dark_minimalist' veya 'gold_luxury' seÃƒÂ§; 'felsefe/tarih' iÃƒÂ§in 'parchment' veya 'kraft'; 'bilim/evren' iÃƒÂ§in 'blueprint' veya 'neon_cyber')
- 'layoutType': 'pip_split' | 'grid_explosion' | 'tri_concept' | 'vs_split' | 'flowchart' | 'quote_spotlight' | 'metric_impact' | 'cards'
  (KURAL: 'gÃƒÂ¶rsel / fotoÃ„Å¸raf / polaroid / kurgu / sinematik' veya portre odaklÃ„Â± anlatÃ„Â±mlarda 'pip_split' seÃƒÂ§; 'parmak izi / milyarlarca insan / mÃƒÂ¼hÃƒÂ¼r' iÃƒÂ§in 'grid_explosion'; 3 kavram karÃ…Å¸Ã„Â±laÃ…Å¸tÃ„Â±rmasÃ„Â±nda 'tri_concept'; ayet/vecize iÃƒÂ§in 'quote_spotlight'; karÃ…Å¸Ã„Â±laÃ…Å¸tÃ„Â±rma ise 'vs_split')
- 'illustrationPrompt': Konuya uygun Ã„Â°ngilizce sanatsal AI gÃƒÂ¶rsel ÃƒÂ¼retim promptu (Ãƒâ€“rn: 'vintage oil painting of Galileo looking through telescope at starry night, dramatic lighting, 8k')
- 'illustrationCaption': GÃƒÂ¶rselin altÃ„Â±na el yazÃ„Â±sÃ„Â±yla yazÃ„Â±lacak kÃ„Â±sa TÃƒÂ¼rkÃƒÂ§e baÃ…Å¸lÃ„Â±k (Ãƒâ€“rn: 'GÃƒÂ¶kyÃƒÂ¼zÃƒÂ¼nÃƒÂ¼n SÃ„Â±rrÃ„Â±')
- 'brollType': 'none' | 'cosmic' | 'clouds' | 'waves' | 'ink'
- 'durationMode': 'deep' (60-90s, derin anlatÃ„Â±m) veya 'quick' (35s, hÃ„Â±zlÃ„Â± shorts)
- 'particles': 'dust' (altÃ„Â±n tozu) | 'embers' (kÃ„Â±vÃ„Â±lcÃ„Â±m) | 'fog' | 'stars' | 'none'
- 'ambientPattern': 'fingerprint' | 'islamic_geometric' | 'dna' | 'cosmic' | 'none'
- 'doodleType': 'compass' | 'galaxy' | 'hourglass' | 'book' | 'lightbulb' | 'none'
- 'directorReason': Neden bu tema, Ã…Å¸ablon ve gÃƒÂ¶rsel atmosferin seÃƒÂ§ildiÃ„Å¸inin 1 cÃƒÂ¼mlelik profesyonel TÃƒÂ¼rkÃƒÂ§e aÃƒÂ§Ã„Â±klamasÃ„Â±.

GÃƒâ€“REV 2: GEREKLÃ„Â° ASSET VE Ã„Â°KON LÃ„Â°STESÃ„Â°
- 'requiredIcons': ['crescent', 'kaaba', 'fingerprint', 'dna', 'atom', 'brain', 'heart', 'eye', 'scale', 'hourglass', 'book', 'lightbulb', 'compass', 'shield', 'infinity'] arasÃ„Â±ndan veya yeni gereken ikon adlarÃ„Â±.

GÃƒâ€“REV 3: SENARYO VE VÃ„Â°RAL Ã…ÂEMA
- 'strikeWord': ÃƒÅ“zeri kÃ„Â±rmÃ„Â±zÃ„Â± ÃƒÂ§izgiyle ÃƒÂ§izilecek ÃƒÂ§ÃƒÂ¼rÃƒÂ¼tÃƒÂ¼len kelime/iddia (Ãƒâ€“rn: 'TESADÃƒÅ“F' veya 'YARATMAK' veya '')
- 'narration': Profesyonel, etkileyici TÃƒÂ¼rkÃƒÂ§e seslendirme metni.

SADECE SAF GEÃƒâ€¡ERLÃ„Â° JSON DÃƒâ€“NDÃƒÅ“R:
{{
  "directorDecision": {{
    "theme": "{req.theme if not is_auto else 'dark_minimalist'}",
    "layoutType": "{req.layout_type if not is_auto else 'grid_explosion'}",
    "durationMode": "{req.duration_mode if not is_auto else 'deep'}",
    "particles": "dust",
    "ambientPattern": "fingerprint",
    "doodleType": "none",
    "directorReason": "Ã„Â°slami tefekkÃƒÂ¼r ve biyolojik mÃƒÂ¼hÃƒÂ¼r vurgusu iÃƒÂ§in karanlÃ„Â±k minimal tuval ve 12'li parmak izi Ã„Â±zgarasÃ„Â± seÃƒÂ§ildi."
  }},
  "requiredIcons": ["fingerprint", "dna", "scale"],
  "headerSubtitle": "AkÃ„Â±l Almaz SÃ„Â±r",
  "headerLine1": "PARMAK UCUNDAKÃ„Â°",
  "circledWord": "BÃƒÅ“YÃƒÅ“K",
  "headerLine2": "SIR",
  "highlightedText": "MÃ„Â°LYARLARCA MÃƒÅ“HÃƒÅ“R",
  "strikeWord": "TESADÃƒÅ“F",
  "layoutType": "{req.layout_type if not is_auto else 'grid_explosion'}",
  "cards": [
    {{"id": "1", "label": "DNA Ã…Âifresi", "value": "%100 AynÃ„Â±", "icon": "dna", "color": "#1e3a8a"}},
    {{"id": "2", "label": "Ã„Â°kizler", "value": "FarklÃ„Â± Ã„Â°z", "icon": "fingerprint", "color": "#15803d"}},
    {{"id": "3", "label": "Tesviye", "value": "1400 YÃ„Â±l", "icon": "scale", "color": "#d97706"}}
  ],
  "vsData": {{
    "leftTitle": "DNA BenzerliÃ„Å¸i",
    "leftSubtitle": "Genler Birebir AynÃ„Â±",
    "leftPoints": ["AynÃ„Â± genetik kod", "AynÃ„Â± kan grubu", "AynÃ„Â± fiziksel yapÃ„Â±"],
    "leftColor": "#dc2626",
    "rightTitle": "Parmak UÃƒÂ§larÃ„Â±",
    "rightSubtitle": "EÃ…Å¸siz Biyolojik MÃƒÂ¼hÃƒÂ¼r",
    "rightPoints": ["Anne karnÃ„Â±nda mikro temas", "Asla deÃ„Å¸iÃ…Å¸meyen geometri", "Milyarlarca insanda tek"],
    "rightColor": "#16a34a",
    "verdict": "Ã„Â°kizlerin DNA'sÃ„Â± bile aynÃ„Â±yken, parmak izi her insanÃ„Â± tek ve eÃ…Å¸siz kÃ„Â±lar."
  }},
  "flowchartSteps": [
    {{"stepNumber": 1, "badge": "1. AÃ…Å¸ama", "title": "BÃƒÂ¼yÃƒÂ¼k Soru", "desc": "Ãƒâ€¡ÃƒÂ¼rÃƒÂ¼yÃƒÂ¼p daÃ„Å¸Ã„Â±lan kemikler nasÃ„Â±l diriltilecek?", "color": "#1e3a8a"}},
    {{"stepNumber": 2, "badge": "2. KÃ„Â±rÃ„Â±lma", "title": "En Ã„Â°nce Detay", "desc": "Kur'an beyne deÃ„Å¸il, parmak ucunun milimetrik ÃƒÂ§izgilerine iÃ…Å¸aret etti.", "color": "#d97706"}},
    {{"stepNumber": 3, "badge": "3. Hakikat", "title": "Tesviye SÃ„Â±rrÃ„Â±", "desc": "19. yÃƒÂ¼zyÃ„Â±lda keÃ…Å¸fedilen biometrik imza asÃ„Â±rlar ÃƒÂ¶nce haber verildi.", "color": "#15803d"}}
  ],
  "quoteSpotlight": {{
    "speaker": "KÃ„Â±yamet Suresi",
    "title": "4. AYET",
    "quoteText": "Evet, bizim onun parmak uÃƒÂ§larÃ„Â±nÃ„Â± bile derleyip yeniden dÃƒÂ¼zene koymaya gÃƒÂ¼cÃƒÂ¼mÃƒÂ¼z yeter.",
    "sourceRef": "KÃ„Â±yamet Suresi, 3-4"
  }},
  "metricImpact": {{
    "bigNumber": "8 MÃ„Â°LYAR",
    "bigLabel": "Ã„Â°NSAN Ã„Â°Ãƒâ€¡Ã„Â°NDE",
    "subheading": "HiÃƒÂ§birinin Parmak Ã„Â°zi AynÃ„Â± DeÃ„Å¸il",
    "keyTakeaway": "Ãƒâ€¡ÃƒÂ¼nkÃƒÂ¼ her insan varoluÃ…Å¸un altÃ„Â±na atÃ„Â±lmÃ„Â±Ã…Å¸ ÃƒÂ¶zel bir imzadÃ„Â±r."
  }},
  "gridExplosion": {{
    "title": "MÃ„Â°LYARLARCA Ã„Â°NSAN",
    "subtitle": "HiÃƒÂ§birinin Parmak Ã„Â°zi Birbirine BenzemeÃ„Å¸ecek Ã…Âekilde YaratÃ„Â±ldÃ„Â±",
    "iconType": "fingerprint",
    "itemCount": 12,
    "badgeText": "EÃ…ÂSÃ„Â°Z BÃ„Â°YOLOJÃ„Â°K MÃƒÅ“HÃƒÅ“R"
  }},
  "triConcept": {{
    "badge": "BEKLENEN CEVAP",
    "concept1": {{"title": "BEYÃ„Â°N", "subtitle": "En KarmaÃ…Å¸Ã„Â±k HafÃ„Â±za", "icon": "brain", "color": "#38bdf8"}},
    "concept2": {{"title": "KALP", "subtitle": "YaÃ…Å¸am Merkezi", "icon": "heart", "color": "#ef4444"}},
    "concept3": {{"title": "GÃƒâ€“Z", "subtitle": "Hassas Mercek", "icon": "eye", "color": "#facc15"}},
    "bottomNote": "FAKAT KUR'AN PARMAK UCUNA ODAKLANDI"
  }},
  "timeline": {{
    "startYear": "KÃ„Â±yamet",
    "endYear": "DiriliÃ…Å¸",
    "durationLabel": "Tesviye",
    "title": "Kusursuz Dizilim",
    "ayahArabic": "",
    "ayahTranslation": "Evet, bizim onun parmak uÃƒÂ§larÃ„Â±nÃ„Â± bile derleyip yeniden dÃƒÂ¼zene koymaya gÃƒÂ¼cÃƒÂ¼mÃƒÂ¼z yeter.",
    "ayahRef": "KÃ„Â±yamet Suresi, 3-4"
  }},
  "narration": "DNA'sÃ„Â± yÃƒÂ¼zde yÃƒÂ¼z aynÃ„Â± olan tek yumurta ikizlerini bile birbirinden ayÃ„Â±ran tek bir sÃ„Â±r vardÃ„Â±r. Ãƒâ€¡ÃƒÂ¼rÃƒÂ¼yÃƒÂ¼p toprak olduktan sonra nasÃ„Â±l diriltileceÃ„Å¸ini soranlara, Kur'an tam da parmak uÃƒÂ§larÃ„Â±na iÃ…Å¸aret ederek cevap verdi. Milyarlarca insanÃ„Â±n her biri, parmak ucundaki o eÃ…Å¸siz mÃƒÂ¼hÃƒÂ¼rle yeniden var edilir.",
  "viral": {{
    "hookScore": 99,
    "viralTitles": [
      "Parmak Ucundaki BÃƒÅ“YÃƒÅ“K SÃ„Â±r! KÃ„Â±yamet Suresi 3-4",
      "Ã„Â°kizlerin Bile FarklÃ„Â±: 1400 YÃ„Â±l Ãƒâ€“nceki AkÃ„Â±l Almaz Detay!"
    ],
    "hashtags": ["#bilim", "#kuran", "#parmakizi", "#mucize", "#tefekkÃƒÂ¼r", "#shorts"],
    "loopEnding": "ve iÃ…Å¸te bu yÃƒÂ¼zden her insan aslÃ„Â±nda...",
    "description": "Parmak uÃƒÂ§larÃ„Â±ndaki dermatoglif Ã…Å¸ifresi ve KÃ„Â±yamet Suresi'nin mucizevi detaylarÃ„Â±."
  }}
}}
"""

    effective_model = req.model or DEFAULT_MODEL
    res, key_name = pool.query_with_rotation(prompt, "You are a specialized JSON video schema generator. Output ONLY raw JSON.", model=effective_model)
    if not res:
        raise HTTPException(status_code=500, detail=f"Key havuzundaki tÃƒÂ¼m anahtarlar denendi ({effective_model}) ancak yanÃ„Â±t alÃ„Â±namadÃ„Â±.")

    import re
    cleaned = re.sub(r"```json\s*", "", res)
    cleaned = re.sub(r"```\s*", "", cleaned).strip()

    try:
        video_data = json.loads(cleaned)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLM JSON ÃƒÂ§Ã„Â±ktÃ„Â±sÃ„Â± ayrÃ„Â±Ã…Å¸tÃ„Â±rÃ„Â±lamadÃ„Â±: {str(e)}")

    # 1. AI Director vs Manual Decisions Sync
    director_dec = video_data.get("directorDecision", {})
    topic_lower = topic.lower()

    if is_auto:
        # AI Director selects
        theme = director_dec.get("theme")
        if not theme:
            if "karanlÃ„Â±k" in topic_lower or "dark" in topic_lower or "islam" in topic_lower:
                theme = "dark_minimalist"
            elif "felsefe" in topic_lower or "tarih" in topic_lower:
                theme = "parchment"
            else:
                theme = req.theme or "notebook"

        layout_type = director_dec.get("layoutType")
        if not layout_type:
            if any(w in topic_lower for w in ["parmak", "milyar", "mÃƒÂ¼hÃƒÂ¼r"]):
                layout_type = "grid_explosion"
            elif any(w in topic_lower for w in ["beyin", "kalp", "gÃƒÂ¶z", "ÃƒÂ¼ÃƒÂ§", "3"]):
                layout_type = "tri_concept"
            else:
                layout_type = req.layout_type or "cards"

        duration_mode = director_dec.get("durationMode") or req.duration_mode or "quick"
        is_dark = (theme in ["dark_minimalist", "neon_cyber", "gold_luxury"])
        particles = director_dec.get("particles") or ("dust" if is_dark else "none")
        ambient_pattern = director_dec.get("ambientPattern") or ("fingerprint" if "parmak" in topic_lower else ("islamic_geometric" if "islam" in topic_lower else ("dna" if "dna" in topic_lower else "none")))
        doodle_type = director_dec.get("doodleType") or ("none" if is_dark else "auto")
    else:
        # Manual Mode respects user
        theme = req.theme or "notebook"
        layout_type = req.layout_type or "cards"
        duration_mode = req.duration_mode or "quick"
        is_dark = (theme in ["dark_minimalist", "neon_cyber", "gold_luxury"])
        particles = req.particles if (req.particles and req.particles != "default") else ("dust" if is_dark else "none")
        ambient_pattern = req.ambient_pattern if (req.ambient_pattern and req.ambient_pattern != "default") else ("fingerprint" if is_dark else "none")
        doodle_type = req.doodle_type if (req.doodle_type and req.doodle_type != "auto") else "auto"

    video_data["theme"] = theme
    video_data["layoutType"] = layout_type
    video_data["durationMode"] = duration_mode
    video_data["particles"] = particles
    video_data["ambientPattern"] = ambient_pattern
    video_data["doodleType"] = doodle_type
    video_data["filmGrain"] = req.film_grain or "subtle"
    video_data["lightLeaks"] = req.light_leaks or "auto"
    video_data["cameraMotion"] = req.camera_motion or "handheld"
    video_data["accentType"] = req.accent_type or "none"
    video_data["socialHandle"] = req.social_handle
    video_data["musicTrack"] = req.music_track or "ambient_music.wav"
    video_data["ttsProvider"] = req.tts_provider or "edge_tts"
    video_data["voiceId"] = req.voice_id or "en-US-AndrewMultilingualNeural"
    video_data["emotionTone"] = req.emotion_tone or "documentary"

    # Faz 8: AI Illustration & B-Roll Resolution
    should_gen_image = req.enable_illustration or (is_auto and (layout_type == "pip_split" or any(w in topic_lower for w in ["resim", "gÃƒÂ¶rsel", "fotoÃ„Å¸raf", "tablo", "portre"])))
    if should_gen_image:
        ill_prompt = req.illustration_prompt or director_dec.get("illustrationPrompt") or f"vintage oil sketch of {topic}, dramatic lighting, masterwork, 8k"
        ill_caption = req.illustration_caption or director_dec.get("illustrationCaption") or topic[:35]
        ill_style = req.illustration_style or "polaroid"
        try:
            ill_res = generate_ai_illustration(prompt=ill_prompt, style=ill_style, caption=ill_caption)
            video_data["illustrationUrl"] = ill_res["illustrationUrl"]
            video_data["illustrationCaption"] = ill_res["caption"]
            video_data["illustrationStyle"] = ill_style
        except Exception as e:
            print(f"[Server] Illustration generation error: {e}")

    # B-Roll Selection
    broll_choice = req.broll_type if (req.broll_type and req.broll_type != "none") else director_dec.get("brollType", "none")
    if is_auto and broll_choice == "none":
        if any(w in topic_lower for w in ["evren", "yÃ„Â±ldÃ„Â±z", "zaman", "uzay"]) or theme == "neon_cyber":
            broll_choice = "cosmic"
        elif any(w in topic_lower for w in ["deniz", "su", "okyanus"]):
            broll_choice = "waves"
        elif any(w in topic_lower for w in ["tefekkÃƒÂ¼r", "felsefe", "derin"]) or theme == "dark_minimalist":
            broll_choice = "ink"
        elif any(w in topic_lower for w in ["gÃƒÂ¶kyÃƒÂ¼zÃƒÂ¼", "hava", "bulut"]):
            broll_choice = "clouds"

    video_data["brollType"] = broll_choice
    video_data["brollOpacity"] = req.broll_opacity or 0.18

    # 2. AdÃ„Â±m 2: Asset Manager & Ingestor Pipeline (VarlÃ„Â±k TaramasÃ„Â± & Otomatik Ã„Â°ndirme)
    video_data = process_video_assets(video_data, pool=pool)

    # 3. AdÃ„Â±m 3: Studio TTS Audio & Whisper-aligned Subtitles (Faz 7 Multi-TTS)
    narration_text = video_data.get("narration", "")
    audio_name, subtitles, words_list = generate_studio_audio_and_subtitles(
        narration_text=narration_text,
        lang=req.voice_lang or "tr",
        provider=req.tts_provider or "edge_tts",
        voice_id=req.voice_id or "en-US-AndrewMultilingualNeural",
        emotion_tone=req.emotion_tone or "documentary",
        elevenlabs_api_key=req.elevenlabs_api_key
    )
    video_data["subtitles"] = subtitles
    video_data["words"] = words_list
    video_data["audioUrl"] = audio_name

    # Save to generatedData.json for Remotion
    out_json = os.path.join(SRC_DIR, "generatedData.json")
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(video_data, f, ensure_ascii=False, indent=2)

    # Save to History
    history = load_history()
    new_hist_item = {
        "id": str(uuid.uuid4())[:8],
        "topic": topic,
        "theme": theme,
        "layoutType": layout_type,
        "durationMode": duration_mode,
        "created_at": time.strftime("%Y-%m-%d %H:%M"),
        "headerMain": video_data.get("headerLine1", "") + " " + video_data.get("circledWord", "") + " " + video_data.get("highlightedText", topic),
        "narration": narration_text,
        "hookScore": video_data.get("viral", {}).get("hookScore", 95),
        "key_used": key_name,
        "model_used": effective_model,
        "thumbnail_url": "/out/thumbnail.png?t=" + str(int(time.time())),
        "video_data": video_data
    }
    history.insert(0, new_hist_item)
    save_history(history[:30])

    # Final response with director feedback & asset log
    director_reason = director_dec.get("directorReason") or f"{'Yapay ZekÃƒÂ¢ YÃƒÂ¶netmeni' if is_auto else 'KullanÃ„Â±cÃ„Â±'} konuya uygun olarak {theme} temasÃ„Â±nÃ„Â± ve {layout_type} sahne yapÃ„Â±sÃ„Â±nÃ„Â± seÃƒÂ§ti."
    acquired_assets = video_data.get("_acquired_assets", [])

    return {
        "success": True,
        "key_used": key_name,
        "model_used": effective_model,
        "video_data": video_data,
        "director_decisions": {
            "mode": "auto" if is_auto else "manual",
            "theme": theme,
            "layout_type": layout_type,
            "duration_mode": duration_mode,
            "particles": particles,
            "ambient_pattern": ambient_pattern,
            "doodle_type": doodle_type,
            "film_grain": video_data.get("filmGrain", "subtle"),
            "light_leaks": video_data.get("lightLeaks", "auto"),
            "camera_motion": video_data.get("cameraMotion", "handheld"),
            "accent_type": video_data.get("accentType", "none"),
            "music_track": video_data.get("musicTrack", "ambient_music.wav"),
            "tts_provider": video_data.get("ttsProvider", "edge_tts"),
            "voice_id": video_data.get("voiceId", "en-US-AndrewMultilingualNeural"),
            "emotion_tone": video_data.get("emotionTone", "documentary"),
            "illustration_url": video_data.get("illustrationUrl"),
            "illustration_caption": video_data.get("illustrationCaption"),
            "broll_type": video_data.get("brollType", "none"),
            "reason": director_reason
        },
        "acquired_assets": acquired_assets,
        "audio_url": "/public/audio.mp3?t=" + str(int(time.time())),
        "history_item": new_hist_item
    }

def run_remotion_render(formats=None):
    global render_state
    if not formats:
        formats = ["9:16"]
    render_state["status"] = "rendering"
    render_state["message"] = f"Remotion motoru formatları derliyor: {', '.join(formats)}..."
    rendered_files = []
    try:
        if "9:16" in formats:
            render_state["message"] = "9:16 Shorts/Reels derleniyor (1080x1920)..."
            res916 = subprocess.run(["npm.cmd", "run", "build"], cwd=BASE_DIR, capture_output=True, text=True, encoding="utf-8", errors="replace", check=False)
            if res916.returncode == 0:
                rendered_files.append("9:16 (Dikey)")

        if "16:9" in formats:
            render_state["message"] = "16:9 YouTube Yatay derleniyor (1920x1080)..."
            res169 = subprocess.run(["npm.cmd", "run", "build:horizontal"], cwd=BASE_DIR, capture_output=True, text=True, encoding="utf-8", errors="replace", check=False)
            if res169.returncode == 0:
                rendered_files.append("16:9 (Yatay)")

        if "1:1" in formats:
            render_state["message"] = "1:1 Kare derleniyor (1080x1080)..."
            res11 = subprocess.run(["npm.cmd", "run", "build:square"], cwd=BASE_DIR, capture_output=True, text=True, encoding="utf-8", errors="replace", check=False)
            if res11.returncode == 0:
                rendered_files.append("1:1 (Kare)")

        # Render thumbnail
        subprocess.run(
            ["npx.cmd", "remotion", "still", "src/index.ts", "NotebookVideo", "out/thumbnail.png", "--frame=45"],
            cwd=BASE_DIR, capture_output=True, text=True, encoding="utf-8", errors="replace", check=False
        )

        render_state["status"] = "completed"
        t_now = str(int(time.time() * 1000))
        render_state["message"] = f"Render tamamlandı! ({', '.join(rendered_files)})"
        render_state["video_url"] = f"/out/video.mp4?t={t_now}"
        if os.path.exists(os.path.join(OUT_DIR, "video_horizontal.mp4")):
            render_state["video_horizontal_url"] = f"/out/video_horizontal.mp4?t={t_now}"
        if os.path.exists(os.path.join(OUT_DIR, "video_square.mp4")):
            render_state["video_square_url"] = f"/out/video_square.mp4?t={t_now}"
        render_state["thumbnail_url"] = f"/out/thumbnail.png?t={t_now}"
        render_state["last_rendered_at"] = time.strftime("%Y-%m-%d %H:%M:%S")
    except Exception as e:
        render_state["status"] = "error"
        render_state["message"] = f"Render hatası: {str(e)}"

@app.post("/api/render")
def trigger_render(bg_tasks: BackgroundTasks, req: Optional[RenderMultiFormatRequest] = None):
    global render_state
    if render_state["status"] == "rendering":
        return {"status": "rendering", "message": "Zaten bir video renderlanıyor, lütfen bekleyin."}
    
    formats = req.formats if req and req.formats else ["9:16"]
    bg_tasks.add_task(run_remotion_render, formats)
    render_state["status"] = "rendering"
    render_state["message"] = f"Render işlemi başlatıldı ({', '.join(formats)})..."
    return {"status": "rendering", "message": f"Render işlemi başlatıldı ({', '.join(formats)})..."}

@app.get("/api/render/status")
def get_render_status():
    global render_state
    return render_state

@app.post("/api/thumbnail")
def generate_thumbnail():
    try:
        cmd = ["npx.cmd", "remotion", "still", "src/index.ts", "NotebookVideo", "out/thumbnail.png", "--frame=45"]
        res = subprocess.run(cmd, cwd=BASE_DIR, capture_output=True, text=True, encoding="utf-8", errors="replace", check=False)
        if res.returncode == 0:
            thumb_url = "/out/thumbnail.png?t=" + str(int(time.time()))
            return {"success": True, "thumbnail_url": thumb_url}
        else:
            raise HTTPException(status_code=500, detail=f"Thumbnail oluÃ…Å¸turulamadÃ„Â±: {res.stderr[:200]}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# FORCE REFRESH & CACHE-BUSTING ENDPOINT
@app.post("/api/preview/refresh")
def refresh_preview():
    video_path = os.path.join(OUT_DIR, "video.mp4")
    video_exists = os.path.exists(video_path)
    thumb_path = os.path.join(OUT_DIR, "thumbnail.png")
    thumb_exists = os.path.exists(thumb_path)
    data_file = os.path.join(SRC_DIR, "generatedData.json")
    gen_data = {}
    if os.path.exists(data_file):
        try:
            with open(data_file, "r", encoding="utf-8") as f:
                gen_data = json.load(f)
        except Exception:
            pass

    t = str(int(time.time() * 1000))
    mtime = os.path.getmtime(video_path) if video_exists else 0
    formatted_mtime = time.strftime("%d.%m.%Y %H:%M:%S", time.localtime(mtime)) if mtime else None

    return {
        "success": True,
        "timestamp": t,
        "video_exists": video_exists,
        "video_url": f"/out/video.mp4?t={t}" if video_exists else None,
        "thumbnail_url": f"/out/thumbnail.png?t={t}" if thumb_exists else None,
        "video_data": gen_data,
        "video_mtime": mtime,
        "formatted_mtime": formatted_mtime
    }

# =========================================================================
# FAZ 4: OTOPÃ„Â°LOT DAÃ„ÂITIM & YOUTUBE SHORTS API BOTU
# =========================================================================

# 1. YOUTUBE OAUTH & UPLOADER ENDPOINTS
@app.get("/api/youtube/status")
def get_youtube_status():
    return uploader.get_channel_status()

@app.post("/api/youtube/save-credentials")
def save_youtube_credentials(req: YouTubeCredentialsRequest):
    ok = uploader.save_client_secrets(req.client_id, req.client_secret)
    return {"success": ok, "message": "Google Client credentials baÃ…Å¸arÃ„Â±yla kaydedildi."}

@app.get("/api/youtube/auth-url")
def get_youtube_auth_url(request: Request):
    base_url = str(request.base_url).rstrip("/")
    redirect_uri = f"{base_url}/api/youtube/callback"
    try:
        url = uploader.get_auth_url(redirect_uri)
        return {"success": True, "auth_url": url}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/youtube/callback")
def youtube_oauth_callback(code: str, request: Request):
    base_url = str(request.base_url).rstrip("/")
    redirect_uri = f"{base_url}/api/youtube/callback"
    try:
        uploader.exchange_code(code, redirect_uri)
        return RedirectResponse(url="/?youtube_auth=success")
    except Exception as e:
        return RedirectResponse(url=f"/?youtube_auth=error&msg={str(e)}")

@app.post("/api/youtube/upload")
def upload_to_youtube(req: YouTubeUploadRequest):
    # Locate latest rendered video file
    video_path = os.path.join(OUT_DIR, "video.mp4")
    if not os.path.exists(video_path):
        video_path = os.path.join(OUT_DIR, "video_test.mp4")
    
    if not os.path.exists(video_path):
        raise HTTPException(status_code=400, detail="HenÃƒÂ¼z renderlanmÃ„Â±Ã…Å¸ MP4 videosu bulunamadÃ„Â±. LÃƒÂ¼tfen ÃƒÂ¶nce '1080x1920 MP4 Render' butonuna basÃ„Â±n.")

    # Load metadata fallback from generatedData.json
    data_file = os.path.join(SRC_DIR, "generatedData.json")
    gen_data = {}
    if os.path.exists(data_file):
        try:
            with open(data_file, "r", encoding="utf-8") as f:
                gen_data = json.load(f)
        except Exception:
            pass

    title = req.title or gen_data.get("viral", {}).get("viralTitles", ["Notebook Explainer #Shorts"])[0]
    description = req.description or gen_data.get("viral", {}).get("description", gen_data.get("narration", "AI Notebook Shorts"))
    tags = req.tags or gen_data.get("viral", {}).get("hashtags", ["#shorts", "#bilim", "#felsefe"])

    res = uploader.upload_video(
        video_path=video_path,
        title=title,
        description=description,
        tags=tags,
        privacy_status=req.privacy_status or "public",
        publish_at=req.publish_at,
        made_for_kids=req.made_for_kids or False
    )
    return res

# 2. 1-CLICK ALL-IN-ONE EXPORT BUNDLE (ZIP)
@app.get("/api/export/bundle")
def download_export_bundle():
    """Packages MP4, Thumbnail, Copy-Paste Caption, and JSON metadata into a single .zip"""
    video_file = os.path.join(OUT_DIR, "video.mp4")
    if not os.path.exists(video_file):
        video_file = os.path.join(OUT_DIR, "video_test.mp4")
    
    thumb_file = os.path.join(OUT_DIR, "thumbnail.png")
    data_file = os.path.join(SRC_DIR, "generatedData.json")

    gen_data = {}
    if os.path.exists(data_file):
        try:
            with open(data_file, "r", encoding="utf-8") as f:
                gen_data = json.load(f)
        except Exception:
            pass

    # Create post caption text
    viral_info = gen_data.get("viral", {})
    titles = viral_info.get("viralTitles", [])
    title_text = titles[0] if titles else gen_data.get("headerMain", "Notebook Video Shorts")
    hashtags = " ".join(viral_info.get("hashtags", ["#shorts", "#kesfet", "#fyp"]))
    caption_content = f"""Ã¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢Â
ÄŸÅ¸â€œÂ± NOTEBOOK AI SHORTS Ã‚Â· PAYLAÃ…ÂIM PAKETÃ„Â°
Ã¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢Â

ÄŸÅ¸â€œÅ’ Ãƒâ€“NERÃ„Â°LEN VÃ„Â°RAL BAÃ…ÂLIK:
{title_text}

ÄŸÅ¸â€œÂ VÃ„Â°DEO AÃƒâ€¡IKLAMASI (YouTube / TikTok / Reels):
{viral_info.get('description', gen_data.get('narration', ''))}

ÄŸÅ¸ÂÂ·Ã¯Â¸Â TREND HASHTAGLER:
{hashtags}

ÄŸÅ¸â€â€ DÃƒâ€“NGÃƒÅ“ (LOOP) BÃ„Â°TÃ„Â°Ã…Â CÃƒÅ“MLESÃ„Â°:
{viral_info.get('loopEnding', 've iÃ…Å¸te bu yÃƒÂ¼zden...')}

ÄŸÅ¸â€™Â¡ PAYLAÃ…ÂIM TAVSÃ„Â°YELERÃ„Â°:
- En yÃƒÂ¼ksek etkileÃ…Å¸im saatleri: Hafta iÃƒÂ§i 18:30 - 21:30
- TikTok ve Reels'ta trend olan bir arka plan sesiyle sesi miksleyin (Orijinal ses %90, Trend ses %10).
- Ã„Â°lk 3 saniyede soru/kanca ekranda vurgulandÃ„Â±Ã„Å¸Ã„Â± iÃƒÂ§in izleyiciyi hemen tutacaktÃ„Â±r.
Ã¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢Â
"""
    zip_path = os.path.join(OUT_DIR, "export_bundle.zip")
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        if os.path.exists(video_file):
            zf.write(video_file, arcname="video_1080x1920.mp4")
        if os.path.exists(thumb_file):
            zf.write(thumb_file, arcname="thumbnail_cover.png")
        if os.path.exists(data_file):
            zf.write(data_file, arcname="project_metadata.json")
        zf.writestr("PAYLASIM_METNI_VE_SEO.txt", caption_content)

    return FileResponse(zip_path, filename="notebook_shorts_bundle.zip", media_type="application/zip")

# ==========================================
# PRO VIDEO EDITOR & TIMELINE API ENDPOINTS
# ==========================================
@app.get("/api/timeline/data")
def get_timeline_data():
    data_file = os.path.join(SRC_DIR, "generatedData.json")
    if not os.path.exists(data_file):
        raise HTTPException(status_code=404, detail="Proje verisi (generatedData.json) bulunamadÃ„Â±.")
    with open(data_file, "r", encoding="utf-8") as f:
        video_data = json.load(f)
    
    scenes = ensure_scenes_structure(video_data)
    audio_path = os.path.join(PUBLIC_DIR, "audio.mp3")
    waveform = extract_audio_waveform(audio_path, num_peaks=120)
    
    return {
        "success": True,
        "video_data": video_data,
        "scenes": scenes,
        "waveform": waveform,
        "duration": video_data.get("totalDuration", 15.0),
        "subtitles": video_data.get("subtitles", []),
        "words": video_data.get("words", [])
    }

@app.post("/api/timeline/audio")
async def upload_timeline_audio(file: UploadFile = File(...)):
    """Upload custom voiceover / audio directly from timeline, extract waveform, transcribe with Whisper & align scenes."""
    temp_path = os.path.join(PUBLIC_DIR, f"temp_{uuid.uuid4().hex}_{file.filename}")
    final_audio_path = os.path.join(PUBLIC_DIR, "audio.mp3")
    
    # Save uploaded file
    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    # Convert to MP3 if needed or normalize via ffmpeg
    cmd = [
        "ffmpeg", "-y", "-i", temp_path,
        "-af", "compand=attacks=0.02:decays=0.2:points=-60/-60|-24/-12|0/-3:gain=2.0",
        "-ar", "44100", "-ac", "2", "-b:a", "192k",
        final_audio_path
    ]
    subprocess.run(cmd, capture_output=True, check=False)
    if os.path.exists(temp_path):
        try:
            os.remove(temp_path)
        except Exception:
            pass
        
    # Measure audio duration
    dur_cmd = ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", final_audio_path]
    res_dur = subprocess.run(dur_cmd, capture_output=True, text=True, check=False)
    try:
        duration = float(res_dur.stdout.strip())
    except Exception:
        duration = 15.0
    duration = round(duration, 2)
    
    # Extract waveform
    waveform = extract_audio_waveform(final_audio_path, num_peaks=120)
    
    # Whisper AI alignment
    w_model = get_whisper()
    subtitles = []
    words = []
    full_text = ""
    if w_model is not None:
        try:
            whisper_res = w_model.transcribe(final_audio_path, word_timestamps=True)
            full_text = whisper_res.get("text", "").strip()
            for seg in whisper_res.get("segments", []):
                for w in seg.get("words", []):
                    words.append({
                        "word": w.get("word", "").strip(),
                        "start": round(w.get("start", 0), 2),
                        "end": round(w.get("end", 0), 2)
                    })
            chunk_size = 3
            for i in range(0, len(words), chunk_size):
                chunk = words[i:i + chunk_size]
                if chunk:
                    subtitles.append({
                        "text": " ".join([cw["word"] for cw in chunk]),
                        "start": chunk[0]["start"],
                        "end": chunk[-1]["end"]
                    })
        except Exception as e:
            print(f"Whisper transcription error: {e}")
            
    if not subtitles:
        subtitles = generate_subtitles_fallback(full_text or "Kendi eklediÃ„Å¸iniz ses kaydÃ„Â±", duration)

    # Update generatedData.json
    data_file = os.path.join(SRC_DIR, "generatedData.json")
    video_data = {}
    if os.path.exists(data_file):
        try:
            with open(data_file, "r", encoding="utf-8") as f:
                video_data = json.load(f)
        except Exception:
            pass
            
    video_data["audioUrl"] = "/public/audio.mp3"
    video_data["totalDuration"] = duration
    video_data["subtitles"] = subtitles
    video_data["words"] = words
    if full_text:
        video_data["narration"] = full_text
        
    # Adjust scenes to fit new duration
    scenes = ensure_scenes_structure(video_data)
    num_scenes = len(scenes)
    slice_dur = duration / max(1, num_scenes)
    cur = 0.0
    for idx, sc in enumerate(scenes):
        sc["startTime"] = round(cur, 2)
        cur += slice_dur
        sc["endTime"] = round(cur if idx < num_scenes - 1 else duration, 2)
    video_data["scenes"] = scenes
    
    with open(data_file, "w", encoding="utf-8") as f:
        json.dump(video_data, f, ensure_ascii=False, indent=2)
        
    return {
        "success": True,
        "duration": duration,
        "waveform": waveform,
        "scenes": scenes,
        "subtitles": subtitles,
        "words": words,
        "video_data": video_data
    }

@app.delete("/api/timeline/scenes/{scene_id}")
def delete_scene(scene_id: str):
    data_file = os.path.join(SRC_DIR, "generatedData.json")
    if not os.path.exists(data_file):
        raise HTTPException(status_code=404, detail="Proje verisi bulunamadÃ„Â±.")
    with open(data_file, "r", encoding="utf-8") as f:
        video_data = json.load(f)
        
    try:
        updated = delete_scene_from_timeline(video_data, scene_id)
        return {
            "success": True,
            "scenes": updated.get("scenes", []),
            "duration": updated.get("totalDuration", 15.0),
            "video_data": updated
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/timeline/scenes/{scene_id}/regenerate")
def regenerate_scene(scene_id: str, req: SceneRegenerateRequest):
    data_file = os.path.join(SRC_DIR, "generatedData.json")
    if not os.path.exists(data_file):
        raise HTTPException(status_code=404, detail="Proje verisi bulunamadÃ„Â±.")
    with open(data_file, "r", encoding="utf-8") as f:
        video_data = json.load(f)
        
    try:
        res = regenerate_scene_with_ai(
            video_data=video_data,
            scene_id=scene_id,
            prompt_override=req.prompt_override,
            layout_override=req.layout_override,
            illustration_style_override=req.illustration_style_override,
            broll_override=req.broll_override,
            model=req.model or DEFAULT_MODEL
        )
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/timeline/scenes/split")
def split_scene(req: SceneSplitRequest):
    data_file = os.path.join(SRC_DIR, "generatedData.json")
    if not os.path.exists(data_file):
        raise HTTPException(status_code=404, detail="Proje verisi bulunamadÃ„Â±.")
    with open(data_file, "r", encoding="utf-8") as f:
        video_data = json.load(f)
        
    try:
        updated = split_scene_on_timeline(video_data, req.scene_id, req.split_time)
        return {
            "success": True,
            "scenes": updated.get("scenes", []),
            "duration": updated.get("totalDuration", 15.0),
            "video_data": updated
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/timeline/scenes/add")
def add_scene(duration: float = 10.0):
    data_file = os.path.join(SRC_DIR, "generatedData.json")
    if not os.path.exists(data_file):
        raise HTTPException(status_code=404, detail="Proje verisi bulunamadÃ„Â±.")
    with open(data_file, "r", encoding="utf-8") as f:
        video_data = json.load(f)
        
    try:
        updated = add_scene_to_timeline(video_data, duration)
        return {
            "success": True,
            "scenes": updated.get("scenes", []),
            "duration": updated.get("totalDuration", 15.0),
            "video_data": updated
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.put("/api/timeline/scenes")
def update_timeline_scenes(req: TimelineUpdateScenesRequest):
    data_file = os.path.join(SRC_DIR, "generatedData.json")
    if not os.path.exists(data_file):
        raise HTTPException(status_code=404, detail="Proje verisi bulunamadÃ„Â±.")
    with open(data_file, "r", encoding="utf-8") as f:
        video_data = json.load(f)
        
    video_data["scenes"] = req.scenes
    if req.scenes:
        video_data["totalDuration"] = max([s.get("endTime", 10.0) for s in req.scenes])
        s0 = req.scenes[0]
        for key in ["headerSubtitle", "headerLine1", "circledWord", "headerLine2", "highlightedText", "strikeWord", "layoutType", "illustrationUrl", "illustrationCaption", "illustrationStyle"]:
            if key in s0:
                video_data[key] = s0[key]
    with open(data_file, "w", encoding="utf-8") as f:
        json.dump(video_data, f, ensure_ascii=False, indent=2)
    return {"success": True, "scenes": video_data["scenes"], "duration": video_data.get("totalDuration", 15.0)}

@app.put("/api/timeline/scenes/{scene_id}")
def update_single_scene(scene_id: str, scene_patch: Dict[str, Any]):
    data_file = os.path.join(SRC_DIR, "generatedData.json")
    if not os.path.exists(data_file):
        raise HTTPException(status_code=404, detail="Proje verisi bulunamadÃ„Â±.")
    with open(data_file, "r", encoding="utf-8") as f:
        video_data = json.load(f)
        
    scenes = ensure_scenes_structure(video_data)
    target = None
    for idx, s in enumerate(scenes):
        if s.get("id") == scene_id:
            s.update(scene_patch)
            target = s
            if idx == 0:
                for k in ["headerSubtitle", "headerLine1", "circledWord", "headerLine2", "highlightedText", "strikeWord", "layoutType", "illustrationUrl", "illustrationCaption", "illustrationStyle", "brollType"]:
                    if k in s:
                        video_data[k] = s[k]
            break
            
    if not target:
        raise HTTPException(status_code=404, detail=f"'{scene_id}' sahnesi bulunamadÃ„Â±.")
        
    with open(data_file, "w", encoding="utf-8") as f:
        json.dump(video_data, f, ensure_ascii=False, indent=2)
    return {"success": True, "scene": target, "video_data": video_data}

@app.post("/api/timeline/scenes/trim")
def api_trim_scene(req: SceneTrimRequest):
    data_file = os.path.join(SRC_DIR, "generatedData.json")
    if not os.path.exists(data_file):
        raise HTTPException(status_code=404, detail="Proje verisi bulunamadÄ±.")
    with open(data_file, "r", encoding="utf-8") as f:
        video_data = json.load(f)
    try:
        updated = trim_scene_on_timeline(
            video_data=video_data,
            scene_id=req.scene_id,
            new_start=req.new_start,
            new_end=req.new_end,
            ripple=True if req.ripple is None else req.ripple
        )
        return {"success": True, "scenes": updated.get("scenes", []), "duration": updated.get("totalDuration", 15.0), "video_data": updated}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/timeline/scenes/reorder")
def api_reorder_scene(req: SceneReorderRequest):
    data_file = os.path.join(SRC_DIR, "generatedData.json")
    if not os.path.exists(data_file):
        raise HTTPException(status_code=404, detail="Proje verisi bulunamadÄ±.")
    with open(data_file, "r", encoding="utf-8") as f:
        video_data = json.load(f)
    try:
        updated = reorder_scenes_on_timeline(
            video_data=video_data,
            scene_id=req.scene_id,
            new_index=req.new_index
        )
        return {"success": True, "scenes": updated.get("scenes", []), "duration": updated.get("totalDuration", 15.0), "video_data": updated}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/timeline/subtitles")
def api_update_subtitles(req: SubtitleUpdateRequest):
    data_file = os.path.join(SRC_DIR, "generatedData.json")
    if not os.path.exists(data_file):
        raise HTTPException(status_code=404, detail="Proje verisi bulunamadı.")
    with open(data_file, "r", encoding="utf-8") as f:
        video_data = json.load(f)
    video_data["subtitles"] = req.subtitles
    with open(data_file, "w", encoding="utf-8") as f:
        json.dump(video_data, f, ensure_ascii=False, indent=2)
    return {"success": True, "subtitles": video_data["subtitles"]}

@app.post("/api/audio/auto-cut")
def api_audio_auto_cut(req: AudioAutoCutRequest):
    data_file = os.path.join(SRC_DIR, "generatedData.json")
    if not os.path.exists(data_file):
        raise HTTPException(status_code=404, detail="Proje verisi bulunamadı.")
    with open(data_file, "r", encoding="utf-8") as f:
        video_data = json.load(f)
    audio_path = os.path.join(PUBLIC_DIR, "audio.mp3")
    if not os.path.exists(audio_path):
        raise HTTPException(status_code=404, detail="audio.mp3 bulunamadı.")
    try:
        res = clean_audio_and_realign(
            audio_path=audio_path,
            video_data=video_data,
            min_duration=req.min_duration or 0.35,
            noise_threshold=req.noise_threshold or "-30dB",
            keep_margin=req.keep_margin or 0.08
        )
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



# ==========================================
# GIT & GITHUB INSTANT BACKUP & ROLLBACK API
# ==========================================
@app.get("/api/backup/status")
def api_get_backup_status():
    status = get_git_status()
    history = list_git_history(10)
    return {"status": status, "history": history}

@app.post("/api/backup/commit")
def api_create_backup(req: GitBackupRequest):
    res = create_git_backup(commit_message=req.message, push_to_remote=req.push or False)
    return res

@app.post("/api/backup/remote")
def api_set_remote(req: GitRemoteRequest):
    url = req.remote_url.strip()
    check = run_git(["remote", "get-url", "origin"])
    if check.returncode == 0:
        res = run_git(["remote", "set-url", "origin", url])
    else:
        res = run_git(["remote", "add", "origin", url])
    if res.returncode == 0:
        return {"success": True, "remote_url": url}
    else:
        raise HTTPException(status_code=400, detail=res.stderr)

@app.post("/api/backup/rollback")
def api_rollback(req: GitRollbackRequest):
    res = rollback_to_commit(req.commit_hash)
    if not res.get("success"):
        raise HTTPException(status_code=400, detail=res.get("message"))
    return res

# 3. AUTOPILOT SCHEDULER & CONTENT FACTORY
def run_autopilot_pipeline(topic: str, layout: str, theme: str, job: dict):
    """Full autopilot execution: Prompt -> TTS -> FFmpeg Studio -> Whisper -> Remotion -> Optional YouTube Upload"""
    gen_req = GenerateRequest(
        topic=topic,
        layout_type=layout,
        theme=theme,
        social_handle="@birkissa",
        voice_lang="tr"
    )
    res_gen = generate_video_content(gen_req)
    video_data = res_gen.get("video_data", {})

    # Render Full HD MP4
    render_cmd = ["npm.cmd", "run", "build"]
    subprocess.run(render_cmd, cwd=BASE_DIR, capture_output=True, text=True, encoding="utf-8", errors="replace", check=False)
    
    # Render Thumbnail
    thumb_cmd = ["npx.cmd", "remotion", "still", "src/index.ts", "NotebookVideo", "out/thumbnail.png", "--frame=45"]
    subprocess.run(thumb_cmd, cwd=BASE_DIR, capture_output=True, text=True, encoding="utf-8", errors="replace", check=False)

    youtube_url = ""
    if job.get("auto_upload"):
        video_path = os.path.join(OUT_DIR, "video.mp4")
        if os.path.exists(video_path):
            titles = video_data.get("viral", {}).get("viralTitles", [topic])
            up_res = uploader.upload_video(
                video_path=video_path,
                title=titles[0],
                description=video_data.get("viral", {}).get("description", video_data.get("narration", "")),
                tags=video_data.get("viral", {}).get("hashtags", ["#shorts", "#bilim"]),
                privacy_status=job.get("privacy", "private")
            )
            youtube_url = up_res.get("url", "")

    if job.get("webhook_url"):
        try:
            import urllib.request
            payload = json.dumps({
                "job_title": job.get("title"),
                "topic": topic,
                "video_url": "http://127.0.0.1:8080/out/video.mp4",
                "youtube_url": youtube_url,
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            }).encode("utf-8")
            req = urllib.request.Request(job["webhook_url"], data=payload, headers={"Content-Type": "application/json"})
            urllib.request.urlopen(req, timeout=10)
        except Exception as e:
            print(f"Webhook dispatch error: {e}")

    return {
        "video_url": "/out/video.mp4",
        "youtube_url": youtube_url
    }

@app.get("/api/autopilot/jobs")
def get_autopilot_jobs():
    return {
        "jobs": scheduler.jobs,
        "history": scheduler.history,
        "active_execution": scheduler.active_execution
    }

@app.post("/api/autopilot/jobs")
def create_autopilot_job(req: AutopilotJobRequest):
    new_job = scheduler.add_job(req.dict())
    return {"success": True, "job": new_job}

@app.delete("/api/autopilot/jobs/{job_id}")
def delete_autopilot_job(job_id: str):
    ok = scheduler.delete_job(job_id)
    return {"success": ok}

@app.post("/api/autopilot/toggle/{job_id}")
def toggle_autopilot_job(job_id: str):
    target = next((j for j in scheduler.jobs if j["id"] == job_id), None)
    if not target:
        raise HTTPException(status_code=404, detail="GÃƒÂ¶rev bulunamadÃ„Â±")
    target["enabled"] = not target.get("enabled", True)
    scheduler.save_jobs()
    return {"success": True, "job": target}

@app.post("/api/autopilot/run-now/{job_id}")
def run_autopilot_job_now(job_id: str):
    res = scheduler.trigger_job_execution(job_id, run_autopilot_pipeline)
    return res

@app.on_event("startup")
def on_startup_handler():
    initialize_core_assets()
    scheduler.start_scheduler_loop(run_autopilot_pipeline)

if __name__ == "__main__":
    import uvicorn
    print("\n=======================================================")
    print("ÄŸÅ¸Å¡â‚¬ Notebook Video AI Studio Pro 4.0 Titanium")
    print("ÄŸÅ¸â€œÂ Web UI: http://localhost:8080")
    print("ÄŸÅ¸â€â€˜ Key Havuzu: 136 Anahtar YÃƒÂ¼klendi")
    print("=======================================================\n")
    uvicorn.run(app, host="127.0.0.1", port=8080)
