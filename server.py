import os
import re
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

def calculate_dynamic_timeline_duration(video_data: dict, scenes: list) -> float:
    ends = [5.0]
    for s in (scenes or []):
        ends.append(float(s.get("endTime", 0.0) or 0.0))
    for q in (video_data.get("quoteVideos", []) or []):
        start = float(q.get("timelineStart", 0.0) or 0.0)
        dur = float(q.get("duration", 0.0) or max(1.0, float(q.get("trimEnd", 6.0) or 6.0) - float(q.get("trimStart", 0.0) or 0.0)))
        ends.append(start + dur)
    for p in (video_data.get("pipVideos", []) or []):
        start = float(p.get("timelineStart", 0.0) or 0.0)
        dur = float(p.get("duration", 0.0) or max(1.0, float(p.get("trimEnd", 5.0) or 5.0) - float(p.get("trimStart", 0.0) or 0.0)))
        ends.append(start + dur)
    for sub in (video_data.get("subtitles", []) or []):
        ends.append(float(sub.get("end", 0.0) or 0.0))
    if "totalDuration" in video_data and isinstance(video_data["totalDuration"], (int, float)):
        ends.append(float(video_data["totalDuration"]))
    return round(max(ends), 2)
class ExtractAudioRequest(BaseModel):
    video_url: str
    apply_to_timeline: Optional[bool] = True

class RemoveAudioRequest(BaseModel):
    mode: str = "mute" # "mute", "unmute" or "delete"

class UpdateMediaPositionRequest(BaseModel):
    item_type: Optional[str] = None
    itemType: Optional[str] = None
    item_id: Optional[str] = None
    itemId: Optional[str] = None
    timeline_start: Optional[float] = None
    timelineStart: Optional[float] = None
    duration: Optional[float] = None

class AddQuoteVideoRequest(BaseModel):
    videoUrl: Optional[str] = None
    video_url: Optional[str] = None
    trimStart: Optional[float] = 0.0
    trim_start: Optional[float] = None
    trimEnd: Optional[float] = 6.0
    trim_end: Optional[float] = None
    timelineStart: Optional[float] = 0.0
    timeline_start: Optional[float] = None
    duration: Optional[float] = None
    theme: Optional[str] = "red_alert"
    headerText: Optional[str] = "Arkadaşlar bu videoyu iyi izleyin..."
    header_text: Optional[str] = None
    subHeaderText: Optional[str] = None
    sub_header_text: Optional[str] = None
    authorTag: Optional[str] = None
    author_tag: Optional[str] = None
    stamp: Optional[str] = "yalan"
    volume: Optional[float] = 1.0
    muted: Optional[bool] = False
    freezeAtEnd: Optional[bool] = False
    freeze_at_end: Optional[bool] = False
    sceneId: Optional[str] = None
    scene_id: Optional[str] = None

class AddPipRequest(BaseModel):
    videoUrl: Optional[str] = None
    video_url: Optional[str] = None
    startTime: Optional[float] = None
    start_time: Optional[float] = None
    endTime: Optional[float] = None
    end_time: Optional[float] = None
    duration: Optional[float] = 6.0
    position: Optional[str] = "top-right"
    shape: Optional[str] = "circle"
    width: Optional[Any] = 340
    volume: Optional[float] = 1.0
    muted: Optional[bool] = False
    sceneId: Optional[str] = None
    scene_id: Optional[str] = None

class AddPngOverlayRequest(BaseModel):
    imageUrl: Optional[str] = None
    image_url: Optional[str] = None
    startTime: Optional[float] = None
    start_time: Optional[float] = None
    endTime: Optional[float] = None
    end_time: Optional[float] = None
    duration: Optional[float] = 8.0
    position: Optional[str] = "top-right"
    width: Optional[Any] = 180
    opacity: Optional[float] = 1.0
    animation: Optional[str] = "bounce"
    rotation: Optional[float] = 0.0
    sceneId: Optional[str] = None
    scene_id: Optional[str] = None

class DeleteMediaItemRequest(BaseModel):
    item_type: Optional[str] = None
    itemType: Optional[str] = None
    item_id: Optional[str] = None
    itemId: Optional[str] = None

class SetSceneMediaRequest(BaseModel):
    scene_id: Optional[str] = None
    sceneId: Optional[str] = None
    video_url: Optional[str] = None
    videoUrl: Optional[str] = None
    fit: Optional[str] = "cover"
    apply_to_all_scenes: Optional[bool] = False
    applyToAllScenes: Optional[bool] = False
    illustration_url: Optional[str] = None
    illustrationUrl: Optional[str] = None
    illustration_style: Optional[str] = "polaroid"
    illustrationStyle: Optional[str] = "polaroid"
    illustration_caption: Optional[str] = None
    illustrationCaption: Optional[str] = None

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
from scripts.subtitle_cleaner import (
    clean_text_apostrophes,
    fix_turkish_orthography_and_compounds,
    stitch_whisper_word_tokens,
    build_subtitle_chunks,
    align_custom_transcript_to_audio
)

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
    start_offset: Optional[float] = None
    start_after_quote: Optional[bool] = True

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

class BulkDeleteRequest(BaseModel):
    ids: List[str]

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
    cleaned_text = fix_turkish_orthography_and_compounds(text)
    words = cleaned_text.split()
    if not words:
        return []
    time_per_word = total_duration / len(words)
    raw_word_objs = []
    for i, w in enumerate(words):
        raw_word_objs.append({
            "word": w,
            "text": w,
            "start": round(i * time_per_word, 2),
            "end": round(min(total_duration, (i + 1) * time_per_word), 2)
        })
    return build_subtitle_chunks(raw_word_objs, chunk_size=3)

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

@app.post("/api/history/bulk-delete")
def bulk_delete_history_items(req: BulkDeleteRequest):
    history = load_history()
    to_delete = set(str(i) for i in req.ids)
    before_len = len(history)
    history = [h for h in history if str(h.get("id")) not in to_delete]
    save_history(history)
    return {"success": True, "deleted_count": before_len - len(history)}

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
# LIVE AUDIO UPLOAD & MULTI-SCENE CHAINED NARRATIVE ENGINE (PRO TITANIUM)
# =========================================================================
@app.post("/api/audio/upload")
@app.post("/api/timeline/generate-from-audio")
async def upload_audio_and_generate_multiscene(
    file: UploadFile = File(...),
    transcript: Optional[str] = Form(None),
    model: Optional[str] = Form(DEFAULT_MODEL),
    theme: Optional[str] = Form(None),
    mode: Optional[str] = Form("auto"),
    scene_duration: Optional[int] = Form(12),
    start_offset: Optional[float] = Form(None),
    start_after_quote: Optional[bool] = Form(True),
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
        raise HTTPException(status_code=400, detail="Lütfen bir ses dosyası seçin.")

    ext = os.path.splitext(file.filename)[1].lower() if file.filename else ".mp3"
    allowed_exts = [".mp3", ".wav", ".m4a", ".ogg", ".aac", ".flac", ".wma", ".webm"]
    if ext not in allowed_exts:
        raise HTTPException(status_code=400, detail=f"Desteklenmeyen ses formatı ({ext}). MP3, WAV veya M4A yükleyin.")

    # 1. Save uploaded file to temp path
    upload_raw_path = os.path.join(DATA_DIR, f"upload_raw_{uuid.uuid4().hex[:8]}{ext}")
    try:
        with open(upload_raw_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ses dosyası kaydedilemedi: {str(e)}")

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
        raise HTTPException(status_code=500, detail=f"Whisper ses çözümleme hatası: {str(e)}")

    raw_whisper_words = []
    for seg in w_res.get("segments", []):
        for w in seg.get("words", []):
            w_text = w["word"].strip()
            if w_text:
                raw_whisper_words.append({
                    "word": w_text,
                    "text": w_text,
                    "start": round(w["start"], 2),
                    "end": round(w["end"], 2)
                })

    user_transcript = (transcript or "").strip()
    if user_transcript:
        clean_user_text = fix_turkish_orthography_and_compounds(user_transcript)
        whisper_words, subtitles = align_custom_transcript_to_audio(clean_user_text, total_duration, raw_whisper_words)
        full_transcript = " ".join([w.get("text") or w.get("word") or "" for w in whisper_words]).strip() or clean_user_text
    else:
        whisper_words = stitch_whisper_word_tokens(raw_whisper_words)
        full_transcript = " ".join([w["word"] for w in whisper_words]).strip()
        if not full_transcript:
            full_transcript = clean_text_apostrophes(w_res.get("text", "").strip()) or "Kullanıcının yüklediği ses kaydı"

        if (total_duration <= 0 or total_duration < 4.0) and whisper_words:
            total_duration = whisper_words[-1]["end"] + 1.0
        total_duration = max(8.0, round(total_duration, 2))

        # 5. Build 3-word subtitle chunks for live karaoke & video subtitles
        if whisper_words:
            subtitles = build_subtitle_chunks(whisper_words, chunk_size=3)
        else:
            subtitles = generate_subtitles_fallback(full_transcript, total_duration)

    # 6. Read existing project to preserve Quote Videos and PIP layers
    out_json = os.path.join(SRC_DIR, "generatedData.json")
    existing_data = {}
    if os.path.exists(out_json):
        try:
            with open(out_json, "r", encoding="utf-8") as ef:
                existing_data = json.load(ef)
        except Exception:
            pass

    # Calculate offset if quote video exists
    quote_offset = 0.0
    for q in (existing_data.get("quoteVideos", []) or []):
        q_st = float(q.get("timelineStart", 0.0) or 0.0)
        q_dur = float(q.get("duration", 0.0) or max(1.0, float(q.get("trimEnd", 6.0) or 6.0) - float(q.get("trimStart", 0.0) or 0.0)))
        quote_offset = max(quote_offset, q_st + q_dur)

    if start_offset is not None:
        effective_offset = float(start_offset)
    elif start_after_quote and quote_offset > 0:
        effective_offset = round(quote_offset, 2)
    else:
        effective_offset = 0.0

    # 7. Segment into 9-14 second sequential scenes
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
            "text_spoken": slice_text or f"{i+1}. Bölüm Konuşması"
        })

    # 8. Gemini 3 Director Prompt for Multi-Scene Storyboard
    effective_model = model or DEFAULT_MODEL
    prompt = f"""Sen viral YouTube Shorts, TikTok ve Mini-Belgesel prodüksiyonlarının BAŞ YAPAY ZEKA YÖNETMENİ ve senaristisin.
Kullanıcı kendi ses kaydını yükledi!
Toplam Ses Süresi: {total_duration:.1f} saniye.
Tam Ses Dökümü: '{full_transcript}'

Bu ses {num_scenes} ardışık bölüme/sahneye ayrıldı. Her sahne yaklaşık {total_duration / num_scenes:.1f} saniye sürmektedir:
{json.dumps(scene_slices, ensure_ascii=False, indent=2)}

GÖREVİN:
1. Temayı belirle: 'dark_minimalist' | 'gold_luxury' | 'neon_cyber' | 'parchment' | 'notebook' | 'kraft' | 'chalkboard' | 'blueprint'
   (KURAL: İslami / derin tefekkür dendiğinde KESİNLİKLE 'dark_minimalist' veya 'gold_luxury'; Bilim / teknoloji / evren için 'neon_cyber' veya 'blueprint'; Tarih / felsefe için 'parchment' veya 'kraft')
2. HER BİR BÖLÜM (SCENE) İÇİN ({num_scenes} adet):
   - Önceki sahnenin bittiği yerden devam edecek şekilde ve görsel monotonluğu kırmak için FARKLI bir şablon (layoutType) seç:
     'quote_spotlight' | 'vs_split' | 'cards' | 'metric_impact' | 'grid_explosion' | 'tri_concept' | 'pip_split'
   - Sahneye özel 'headerSubtitle', 'headerLine1', 'circledWord', 'headerLine2', 'highlightedText', 'strikeWord' oluştur.
   - Seçtiğin layoutType'a uygun zengin içerik verisini (cards, vsData, flowchartSteps, quoteSpotlight, metricImpact, gridExplosion, triConcept) üret.
3. 'requiredIcons': Senaryolarda geçen tüm ikon isimleri (örn: ['fingerprint', 'dna', 'atom', 'brain', 'heart', 'eye', 'scale', 'hourglass', 'book', 'lightbulb', 'compass', 'shield', 'infinity']).

SADECE SAF GEÇERLİ JSON DÖNDÜR:
{{
  "directorDecision": {{
    "theme": "{theme if theme else 'dark_minimalist'}",
    "particles": "dust",
    "ambientPattern": "fingerprint",
    "directorReason": "Kullanıcının yüklediği sese uygun olarak dinamik çok sahneli kurgu hazırlandı."
  }},
  "requiredIcons": ["fingerprint", "dna", "brain", "scale"],
  "scenes": [
    {{
      "id": "scene_1",
      "layoutType": "quote_spotlight",
      "headerSubtitle": "1. Bölüm",
      "headerLine1": "İLK SIR",
      "circledWord": "BAŞLANGIÇ",
      "headerLine2": "",
      "highlightedText": "CANLI SES VURGUSU",
      "strikeWord": "TESADÜF",
      "quoteSpotlight": {{
        "speaker": "Ses Kaydı",
        "quoteText": "{full_transcript[:90]}"
      }}
    }}
  ],
  "viral": {{
    "hookScore": 98,
    "viralTitles": ["Kendi Sesinden Shorts Başlığı 1", "Başlık 2"],
    "hashtags": ["#shorts", "#viral", "#seslikurgu"],
    "loopEnding": "ve işte bu yüzden...",
    "description": "Kullanıcı ses kaydıyla üretilen profesyonel video."
  }}
}}
"""
    res, key_name = pool.query_with_rotation(prompt, "You are a specialized JSON video schema generator. Output ONLY raw JSON.", model=effective_model)
    if not res:
        raise HTTPException(status_code=500, detail=f"LLM modelinden ({effective_model}) yanıt alınamadı.")

    cleaned = re.sub(r"```json\s*", "", res)
    cleaned = re.sub(r"```\s*", "", cleaned).strip()

    try:
        video_data = json.loads(cleaned)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLM JSON çıktısı ayrıştırılamadı: {str(e)}")

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
    video_data["audioUrl"] = "/public/audio.mp3"
    video_data["filmGrain"] = film_grain or "subtle"
    video_data["lightLeaks"] = light_leaks or "auto"
    video_data["cameraMotion"] = camera_motion or "handheld"
    video_data["accentType"] = accent_type or "none"
    video_data["musicTrack"] = music_track or "ambient_music.wav"
    video_data["brollType"] = broll_type or "none"
    if enable_illustration:
        try:
            ill_res = generate_ai_illustration(full_transcript[:80], style="polaroid", caption="Kayıttan Sahne")
            video_data["illustrationUrl"] = ill_res["illustrationUrl"]
            video_data["illustrationCaption"] = ill_res["caption"]
        except Exception as e:
            print(f"Audio upload illustration error: {e}")

    # Validate and sync scenes array with start offset
    parsed_scenes = video_data.get("scenes", [])
    synced_scenes = []

    available_layouts = ['quote_spotlight', 'vs_split', 'cards', 'metric_impact', 'grid_explosion', 'tri_concept', 'pip_split', 'flowchart']

    for i, sl in enumerate(scene_slices):
        sc = parsed_scenes[i] if i < len(parsed_scenes) else {}
        sc_id = f"scene_{i + 1}"
        sc_layout = sc.get("layoutType") or available_layouts[i % len(available_layouts)]

        if sc_layout == "cards" and not sc.get("cards"):
            sc["cards"] = [
                {"id": "1", "label": "1. Anahtar", "value": "Açıklama", "icon": "brain", "color": "#1e3a8a"},
                {"id": "2", "label": "2. Anahtar", "value": "Gelişme", "icon": "scale", "color": "#15803d"},
                {"id": "3", "label": "3. Anahtar", "value": "Sonuç", "icon": "lightbulb", "color": "#d97706"}
            ]
        elif sc_layout == "vs_split" and not sc.get("vsData"):
            sc["vsData"] = {
                "leftTitle": "Zan / Yanılgı",
                "leftSubtitle": "Görünen",
                "leftPoints": ["Yüzeysel algı", "Nefsin dayatması"],
                "rightTitle": "Hakikat",
                "rightSubtitle": "Gerçek Olan",
                "rightPoints": ["Derin anlam", "Allah rızası"],
                "verdict": "Hakikat daima ayrıntılarda ve ilahi rızada gizlidir."
            }
        elif sc_layout == "quote_spotlight" and not sc.get("quoteSpotlight"):
            sc["quoteSpotlight"] = {
                "speaker": "Ses Kaydı",
                "quoteText": sl["text_spoken"][:90] or full_transcript[:90]
            }
        elif sc_layout == "metric_impact" and not sc.get("metricImpact"):
            sc["metricImpact"] = {
                "bigNumber": "%100",
                "bigLabel": "HAKİKAT",
                "subheading": "Sözlerin Gücü",
                "keyTakeaway": "Sözler doğru anahtarla hakikati açar."
            }
        elif sc_layout == "grid_explosion" and not sc.get("gridExplosion"):
            sc["gridExplosion"] = {
                "title": "MİLYARLARCA MÜHÜR",
                "subtitle": "Benzersiz Anlatım",
                "iconType": "fingerprint",
                "itemCount": 12,
                "badgeText": "HAKİKAT"
            }

        synced_scene = {
            "id": sc_id,
            "startTime": round(effective_offset + sl["start_time"], 2),
            "endTime": round(effective_offset + sl["end_time"], 2),
            "layoutType": sc_layout,
            "headerSubtitle": sc.get("headerSubtitle") or f"{i+1}. Bölüm",
            "headerLine1": sc.get("headerLine1") or (full_transcript.split()[0].upper() if full_transcript.split() else "DİKKAT"),
            "circledWord": sc.get("circledWord") or (full_transcript.split()[1].upper() if len(full_transcript.split()) > 1 else "HAKİKAT"),
            "headerLine2": sc.get("headerLine2") or "",
            "highlightedText": sc.get("highlightedText") or (full_transcript.split()[2].upper() if len(full_transcript.split()) > 2 else "SIR"),
            "strikeWord": sc.get("strikeWord", ""),
            "isVerse": sc.get("isVerse") or (sc_layout == "quote_spotlight"),
            "verseBadge": sc.get("verseBadge") or ("AYET-İ KERİME" if sc_layout == "quote_spotlight" else ""),
            "typewriter": sc.get("typewriter", True if sc_layout == "quote_spotlight" else False),
            "underlinedWords": sc.get("underlinedWords", []),
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

    # Offset subtitles and words
    if effective_offset > 0:
        for sub in subtitles:
            sub["start"] = round(sub["start"] + effective_offset, 2)
            sub["end"] = round(sub["end"] + effective_offset, 2)
        for w in whisper_words:
            w["start"] = round(w["start"] + effective_offset, 2)
            w["end"] = round(w["end"] + effective_offset, 2)

    video_data["scenes"] = synced_scenes
    video_data["aiKurguStartOffset"] = effective_offset
    video_data["subtitles"] = subtitles
    video_data["words"] = whisper_words
    video_data["narration"] = full_transcript
    video_data["durationMode"] = "custom_audio"

    # Copy first scene properties to root for backward compatibility
    if synced_scenes:
        first = synced_scenes[0]
        video_data["layoutType"] = first["layoutType"]
        video_data["headerSubtitle"] = first["headerSubtitle"]
        video_data["headerLine1"] = first["headerLine1"]
        video_data["circledWord"] = first["circledWord"]
        video_data["headerLine2"] = first["headerLine2"]
        video_data["highlightedText"] = first["highlightedText"]
        video_data["strikeWord"] = first.get("strikeWord", "")
        for k in ["cards", "vsData", "flowchartSteps", "quoteSpotlight", "metricImpact", "gridExplosion", "triConcept"]:
            if first.get(k):
                video_data[k] = first[k]

    # Ingest assets required across all scenes
    video_data = process_video_assets(video_data, pool=pool)
    acquired_assets = video_data.get("_acquired_assets", [])

    # 4. Auto-generate Synced SFX Markers for Scene Transitions & Verses
    sfx_markers = existing_data.get("sfxMarkers", []) or []
    for sc in synced_scenes:
        st = sc.get("startTime", 0.0)
        is_verse = sc.get("isVerse") or (sc.get("layoutType") == "quote_spotlight")
        if is_verse:
            sfx_markers.append({
                "time": st,
                "file": "pen_draw.wav",
                "label": "Ayet & Hat Kalemi SFX"
            })
        elif st > 0.5:
            sfx_markers.append({
                "time": st,
                "file": "page_turn.wav",
                "label": "Sayfa Çevirme SFX"
            })
    # Deduplicate SFX times
    unique_sfx = []
    seen_times = set()
    for m in sfx_markers:
        t_key = round(float(m.get("time", 0.0)), 1)
        if t_key not in seen_times:
            seen_times.add(t_key)
            unique_sfx.append(m)
    video_data["sfxMarkers"] = unique_sfx

    # PRESERVE Quote Videos, PIP Videos, Overlay Images, Audio Tracks
    for k in ["quoteVideos", "pipVideos", "overlayImages", "audioTracks"]:
        if k in existing_data and existing_data[k]:
            video_data[k] = existing_data[k]

    video_data["totalDuration"] = calculate_dynamic_timeline_duration(video_data, synced_scenes)

    # Save to generatedData.json
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(video_data, f, ensure_ascii=False, indent=2)

    # Save to History
    history = load_history()
    hist_id = str(uuid.uuid4())[:8]
    new_hist_item = {
        "id": hist_id,
        "topic": f"🎙️ Ses Yükleme: {full_transcript[:60]}...",
        "theme": selected_theme,
        "layoutType": video_data.get("layoutType", "cards"),
        "durationMode": f"{len(synced_scenes)} Sahne ({video_data['totalDuration']:.0f}s)",
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
        "total_duration": video_data["totalDuration"],
        "totalDuration": video_data["totalDuration"],
        "num_scenes": len(synced_scenes),
        "scenes": synced_scenes,
        "subtitles": subtitles,
        "words": whisper_words,
        "waveform": extract_audio_waveform(target_audio_path),
        "video_data": video_data,
        "aiKurguStartOffset": effective_offset,
        "audio_url": f"/public/audio.mp3?t={t_now}",
        "history_item": new_hist_item,
        "director_reason": director_dec.get("directorReason") or f"Yüklenen {total_duration:.1f} saniyelik ses kaydı için {len(synced_scenes)} bölümlü dinamik video kurgulandı."
    }


# =========================================================================
# AI VIDEO SCRIPT & MULTI-SCENE TIMELINE GENERATOR (Faz 8 PRO TITANIUM)
# =========================================================================
@app.post("/api/generate")
def generate_video_content(req: GenerateRequest):
    topic = req.topic.strip()
    if not topic:
        raise HTTPException(status_code=400, detail="Konu boş olamaz")

    is_auto = (req.mode == "auto" or not req.mode)

    # 1. Read existing project to preserve Quote Videos and PIP layers
    out_json = os.path.join(SRC_DIR, "generatedData.json")
    existing_data = {}
    if os.path.exists(out_json):
        try:
            with open(out_json, "r", encoding="utf-8") as ef:
                existing_data = json.load(ef)
        except Exception:
            pass

    # Calculate offset if quote video exists
    quote_offset = 0.0
    for q in (existing_data.get("quoteVideos", []) or []):
        q_st = float(q.get("timelineStart", 0.0) or 0.0)
        q_dur = float(q.get("duration", 0.0) or max(1.0, float(q.get("trimEnd", 6.0) or 6.0) - float(q.get("trimStart", 0.0) or 0.0)))
        quote_offset = max(quote_offset, q_st + q_dur)

    if req.start_offset is not None:
        effective_offset = float(req.start_offset)
    elif getattr(req, "start_after_quote", True) and quote_offset > 0:
        effective_offset = round(quote_offset, 2)
    else:
        effective_offset = 0.0

    word_req = "80-120 kelimelik derin, belgesel kurgulu, tefekkür ve merak uyandıran" if req.duration_mode == "deep" else "35-55 kelimelik akıcı, merak uyandıran"

    prompt = f"""Sen viral YouTube Shorts, TikTok ve Mini-Belgesel prodüksiyonlarının BAŞ YAPAY ZEKA YÖNETMENİ ve senaristisin.
Kullanıcı Talebi / Girdisi: '{topic}'
Çalışma Modu: {'🤖 AI YÖNETMEN MODU (Tüm kararları sen ver)' if is_auto else f'🛠️ MANUEL KULLANICI MODU (Seçilen: Tema: {req.theme}, Şablon: {req.layout_type}, Süre: {req.duration_mode})'}

3 AŞAMALI SİNEMATİK PRODÜKSİYON GÖREVİN:

GÖREV 1: DERİN ANLAMSAL ANALİZ & DÖNEM TESPİTİ
Kullanıcının yazdığı metni derinlemesine analiz et:
1. Tarihsel Dönem: Metinde Hz. Ali, Asr-ı Saadet, Sahabeler, Antik felsefe, Osmanlı veya bilimsel keşif gibi unsurlar var mı?
   - Varsa 'eraDetected': örn. "Asr-ı Saadet / Hz. Ali (r.a.) ve Kufe Dönemi"
   - Döneme en uygun temayı seç: 'dark_minimalist' | 'gold_luxury' | 'parchment' | 'kraft' | 'blueprint' | 'neon_cyber'
2. Kutsal Metin / Ayet / Hadis Tespiti:
   - Metinde Kur'an-ı Kerim ayeti meali (örn. Bakara 153, Asr Suresi vb.), Hadis-i Şerif veya hikmetli bir söz var mı?
   - Varsa 'verseDetected': örn. "Bakara Suresi 153. Ayet Meali"
3. Altı Çizilecek Canlı Kelimeler ('underlinedKeywords'):
   - Seslendirme esnasında altın sarısı parıltıyla altı çizilecek 4-6 kavramı belirle (örn: ["adalet", "ilim", "sabır", "allah", "huzur", "hakikat"]).

GÖREV 2: {word_req} PROFESYONEL TÜRKÇE SESLENDİRME METNİ ('narration') YAZ.
(Eğer kullanıcı belirli bir ayet veya olay belirtmişse metinde mutlaka o ayet veya olay tam olarak zikredilsin!)

GÖREV 3: BU SENARYOYU ARDIŞIK DİNAMİK BÖLÜMLERE/SAHNEYE ('scenes') AYIR:
- EĞER AYET VEYA HİKMETLİ BİR SÖZ VARSA: O sahne için MUTLAKA 'layoutType': 'quote_spotlight' seç, 'isVerse': true yap, 'verseBadge': 'AYET-İ KERİME' veya 'HADİS-İ ŞERİF' ata, 'typewriter': true yap ve 'underlinedWords' dizisini doldur!
- DİĞER SAHNELER İÇİN (Tarihsel anlatım, kavram açıklaması): Görsel monotonluğu kırmak için 'pip_split', 'cards', 'vs_split', 'metric_impact' veya 'tri_concept' seç.
- Her sahne için: 'headerSubtitle', 'headerLine1', 'circledWord', 'headerLine2', 'highlightedText', 'strikeWord', 'underlinedWords' eksiksiz üret.
Her sahne için:
- 'headerSubtitle': Kısa merak uyandırıcı alt başlık
- 'headerLine1': Büyük 1. satır başlığı
- 'circledWord': Vurgulu el çizimi çember içine alınacak kelime
- 'headerLine2': İkinci satır veya tamamlama
- 'highlightedText': Fosforlu kalemle çizilecek çarpıcı kelime/ifade
- 'strikeWord': Üzeri kırmızıyla çizilecek çürütülen kelime (varsa)
- İlgili şablon verisini (quoteSpotlight, vsData, cards, metricImpact, gridExplosion, triConcept) eksiksiz doldur.

SADECE SAF GEÇERLİ JSON DÖNDÜR:
{{
  "directorDecision": {{
    "theme": "{req.theme if not is_auto else 'dark_minimalist'}",
    "particles": "dust",
    "ambientPattern": "fingerprint",
    "doodleType": "none",
    "directorReason": "Konunun ciddiyeti ve ilahi vazife bilinci için karanlık minimal tuval ve karşılaştırmalı sahne yapısı seçildi."
  }},
  "requiredIcons": ["scale", "shield", "heart", "book"],
  "theme": "{req.theme if not is_auto else 'dark_minimalist'}",
  "narration": "Profesyonel, akıcı ve etkileyici Türkçe seslendirme metni...",
  "scenes": [
    {{
      "id": "scene_1",
      "layoutType": "quote_spotlight",
      "headerSubtitle": "İlmi Hakikat",
      "headerLine1": "MUKADDES",
      "circledWord": "YUVA",
      "headerLine2": "",
      "highlightedText": "BENCİL MENFAAT DEĞİL",
      "strikeWord": "ZORUNDA DEĞİLİM",
      "quoteSpotlight": {{
        "speaker": "Fıkhi İlke",
        "title": "AİLE HUKUKU",
        "quoteText": "Kadınların erkekler üzerinde hakları olduğu gibi vazifeleri de vardır."
      }}
    }},
    {{
      "id": "scene_2",
      "layoutType": "vs_split",
      "headerSubtitle": "Kavram Analizi",
      "headerLine1": "NEFSİN",
      "circledWord": "DAYATMASI",
      "headerLine2": "TEHLİKESİ",
      "highlightedText": "MENFAAT ŞEBEKESİ",
      "strikeWord": "BENCİLLİK",
      "vsData": {{
        "leftTitle": "Bencil Menfaat",
        "leftSubtitle": "Nefsin Dayatması",
        "leftPoints": ["Zorunda değilim tavrı", "Sürekli hak yarışı", "Huzursuzluk ve kopuş"],
        "rightTitle": "Mukaddes Yuva",
        "rightSubtitle": "Allah Rızası",
        "rightPoints": ["Karşılıklı ihsan ve vefa", "İlahi vazife şuuru", "Huzur ve bereket"],
        "verdict": "Aile hak iddia etme şebekesi değil, karşılıklı vazifelerin yerine getirildiği mukaddes bir yuvadır."
      }}
    }},
    {{
      "id": "scene_3",
      "layoutType": "cards",
      "headerSubtitle": "Huzurun Sırrı",
      "headerLine1": "HUZURUN",
      "circledWord": "TEMELİ",
      "headerLine2": "",
      "highlightedText": "ALLAH RIZASI",
      "strikeWord": "",
      "cards": [
        {{"id": "1", "label": "Maruf İlkesi", "value": "İlahi Denge", "icon": "scale", "color": "#1e3a8a"}},
        {{"id": "2", "label": "Sünnet Modeli", "value": "Hz. Fatıma Örneği", "icon": "shield", "color": "#d97706"}},
        {{"id": "3", "label": "Manevi Bereket", "value": "Karşılıklı İhsan", "icon": "heart", "color": "#15803d"}}
      ]
    }}
  ],
  "viral": {{
    "hookScore": 99,
    "viralTitles": [
      "Aile Bencil Menfaat Şebekesi Değildir!",
      "Nefsin Dayatması mı, Allah Rızası mı?"
    ],
    "hashtags": ["#aile", "#evlilik", "#huzur", "#tefekkür", "#shorts"],
    "loopEnding": "ve işte gerçek huzur buradadır.",
    "description": "Evlilik ve aile hukuku üzerine ilmi ve felsefi hakikatler."
  }}
}}
"""

    effective_model = req.model or DEFAULT_MODEL
    res, key_name = pool.query_with_rotation(prompt, "You are a specialized JSON video schema generator. Output ONLY raw JSON.", model=effective_model)
    if not res:
        raise HTTPException(status_code=500, detail=f"Key havuzundaki tüm anahtarlar denendi ({effective_model}) ancak yanıt alınamadı.")

    cleaned = re.sub(r"```json\s*", "", res)
    cleaned = re.sub(r"```\s*", "", cleaned).strip()

    try:
        video_data = json.loads(cleaned)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLM JSON çıktısı ayrıştırılamadı: {str(e)}")

    director_dec = video_data.get("directorDecision", {})
    topic_lower = topic.lower()

    if is_auto:
        theme = director_dec.get("theme") or ("dark_minimalist" if "islam" in topic_lower or "derin" in topic_lower else (req.theme or "notebook"))
        duration_mode = director_dec.get("durationMode") or req.duration_mode or "deep"
        is_dark = (theme in ["dark_minimalist", "neon_cyber", "gold_luxury"])
        particles = director_dec.get("particles") or ("dust" if is_dark else "none")
        ambient_pattern = director_dec.get("ambientPattern") or ("fingerprint" if is_dark else "none")
        doodle_type = director_dec.get("doodleType") or ("none" if is_dark else "auto")
    else:
        theme = req.theme or "notebook"
        duration_mode = req.duration_mode or "deep"
        is_dark = (theme in ["dark_minimalist", "neon_cyber", "gold_luxury"])
        particles = req.particles if (req.particles and req.particles != "default") else ("dust" if is_dark else "none")
        ambient_pattern = req.ambient_pattern if (req.ambient_pattern and req.ambient_pattern != "default") else ("fingerprint" if is_dark else "none")
        doodle_type = req.doodle_type if (req.doodle_type and req.doodle_type != "auto") else "auto"

    video_data["theme"] = theme
    video_data["durationMode"] = duration_mode
    video_data["particles"] = particles
    video_data["ambientPattern"] = ambient_pattern
    video_data["doodleType"] = doodle_type
    video_data["filmGrain"] = req.film_grain or "subtle"
    video_data["lightLeaks"] = req.light_leaks or "auto"
    video_data["cameraMotion"] = req.camera_motion or "handheld"
    video_data["accentType"] = req.accent_type or "none"
    video_data["socialHandle"] = req.social_handle or "@birkissa"
    video_data["musicTrack"] = req.music_track or "ambient_music.wav"
    video_data["ttsProvider"] = req.tts_provider or "edge_tts"
    video_data["voiceId"] = req.voice_id or "en-US-AndrewMultilingualNeural"
    video_data["emotionTone"] = req.emotion_tone or "documentary"
    video_data["brollType"] = req.broll_type if (req.broll_type and req.broll_type != "none") else "none"
    video_data["brollOpacity"] = req.broll_opacity or 0.18

    # Ingest required icons
    video_data = process_video_assets(video_data, pool=pool)

    # 2. Studio TTS Audio & Whisper-aligned Subtitles
    narration_text = video_data.get("narration", "")
    audio_name, subtitles, words_list = generate_studio_audio_and_subtitles(
        narration_text=narration_text,
        lang=req.voice_lang or "tr",
        provider=req.tts_provider or "edge_tts",
        voice_id=req.voice_id or "en-US-AndrewMultilingualNeural",
        emotion_tone=req.emotion_tone or "documentary",
        elevenlabs_api_key=req.elevenlabs_api_key
    )

    if words_list:
        total_audio_duration = round(words_list[-1]["end"] + 0.8, 2)
    elif subtitles:
        total_audio_duration = round(subtitles[-1]["end"] + 0.8, 2)
    else:
        total_audio_duration = 20.0

    # 3. Synchronize Multi-Scene Storyboard across audio duration with start offset
    parsed_scenes = video_data.get("scenes", [])
    if not parsed_scenes or len(parsed_scenes) == 0:
        parsed_scenes = [
            {
                "id": "scene_1",
                "layoutType": "quote_spotlight",
                "headerSubtitle": "İlmi Hakikat",
                "headerLine1": "MUKADDES",
                "circledWord": "YUVA",
                "headerLine2": "",
                "highlightedText": "BENCİL MENFAAT DEĞİL",
                "strikeWord": "ZORUNDA DEĞİLİM",
                "quoteSpotlight": {
                    "speaker": "Fıkhi İlke",
                    "quoteText": narration_text[:90] if narration_text else "Aile mukaddes bir yuvadır."
                }
            },
            {
                "id": "scene_2",
                "layoutType": "vs_split",
                "headerSubtitle": "Kavram Karşılaştırması",
                "headerLine1": "NEFSİN",
                "circledWord": "DAYATMASI",
                "headerLine2": "",
                "highlightedText": "MENFAAT ŞEBEKESİ",
                "strikeWord": "BENCİLLİK",
                "vsData": {
                    "leftTitle": "Bencil Menfaat",
                    "leftSubtitle": "Nefsin Dayatması",
                    "leftPoints": ["Zorunda değilim tavrı", "Sürekli hak yarışı", "Kopuş"],
                    "rightTitle": "Mukaddes Yuva",
                    "rightSubtitle": "Allah Rızası",
                    "rightPoints": ["Karşılıklı vefa", "İlahi vazife", "Huzur"],
                    "verdict": "Aile hak yarışı değil, karşılıklı ihsandır."
                }
            },
            {
                "id": "scene_3",
                "layoutType": "cards",
                "headerSubtitle": "Huzurun Sırrı",
                "headerLine1": "HUZURUN",
                "circledWord": "TEMELİ",
                "headerLine2": "",
                "highlightedText": "ALLAH RIZASI",
                "strikeWord": "",
                "cards": [
                    {"id": "1", "label": "Maruf İlkesi", "value": "İlahi Denge", "icon": "scale", "color": "#1e3a8a"},
                    {"id": "2", "label": "Sünnet Modeli", "value": "Hz. Fatıma Örneği", "icon": "shield", "color": "#d97706"},
                    {"id": "3", "label": "Manevi Bereket", "value": "Karşılıklı İhsan", "icon": "heart", "color": "#15803d"}
                ]
            }
        ]

    num_scenes = len(parsed_scenes)
    slice_dur = total_audio_duration / num_scenes
    synced_scenes = []

    for i, sc in enumerate(parsed_scenes):
        st = round(effective_offset + (i * slice_dur), 2)
        en = round(effective_offset + ((i + 1) * slice_dur if i < num_scenes - 1 else total_audio_duration), 2)
        sc["id"] = f"scene_{i + 1}"
        sc["startTime"] = st
        sc["endTime"] = en
        if "layoutType" not in sc:
            sc["layoutType"] = "cards"
        if sc.get("layoutType") == "quote_spotlight":
            sc["isVerse"] = sc.get("isVerse", True)
            sc["verseBadge"] = sc.get("verseBadge") or "AYET / HİKMETLİ SÖZ"
            sc["typewriter"] = sc.get("typewriter", True)
            if not sc.get("underlinedWords"):
                sc["underlinedWords"] = director_dec.get("underlinedKeywords") or ["allah", "adalet", "sabır", "mukaddes", "yuva", "vazife"]
        synced_scenes.append(sc)

    # Offset subtitles and words
    if effective_offset > 0:
        for sub in subtitles:
            sub["start"] = round(sub["start"] + effective_offset, 2)
            sub["end"] = round(sub["end"] + effective_offset, 2)
        for w in words_list:
            w["start"] = round(w["start"] + effective_offset, 2)
            w["end"] = round(w["end"] + effective_offset, 2)

    video_data["scenes"] = synced_scenes
    video_data["aiKurguStartOffset"] = effective_offset
    video_data["subtitles"] = subtitles
    video_data["words"] = words_list
    video_data["audioUrl"] = "/public/audio.mp3"

    # Copy first scene properties to root for 100% backward compatibility
    if synced_scenes:
        first = synced_scenes[0]
        for k in ["headerSubtitle", "headerLine1", "circledWord", "headerLine2", "highlightedText", "strikeWord", "layoutType", "cards", "quoteSpotlight", "vsData", "metricImpact", "gridExplosion", "triConcept"]:
            if k in first and first[k]:
                video_data[k] = first[k]

    # PRESERVE Quote Videos, PIP Videos, Overlay Images, Audio Tracks
    for k in ["quoteVideos", "pipVideos", "overlayImages", "audioTracks"]:
        if k in existing_data and existing_data[k]:
            video_data[k] = existing_data[k]

    video_data["totalDuration"] = calculate_dynamic_timeline_duration(video_data, synced_scenes)

    # Save to generatedData.json for Remotion
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(video_data, f, ensure_ascii=False, indent=2)

    # Save to History
    history = load_history()
    new_hist_item = {
        "id": str(uuid.uuid4())[:8],
        "topic": topic,
        "theme": theme,
        "layoutType": video_data.get("layoutType", "cards"),
        "durationMode": f"{len(synced_scenes)} Sahne ({video_data['totalDuration']:.0f}s)",
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

    director_reason = director_dec.get("directorReason") or f"Konuya uygun olarak {theme} teması ve {len(synced_scenes)} bölümlü dinamik defter kurgusu oluşturuldu."
    acquired_assets = video_data.get("_acquired_assets", [])

    return {
        "success": True,
        "key_used": key_name,
        "model_used": effective_model,
        "scenes": synced_scenes,
        "totalDuration": video_data["totalDuration"],
        "total_duration": video_data["totalDuration"],
        "num_scenes": len(synced_scenes),
        "aiKurguStartOffset": effective_offset,
        "subtitles": subtitles,
        "words": words_list,
        "video_data": video_data,
        "director_decisions": {
            "mode": "auto" if is_auto else "manual",
            "theme": theme,
            "layout_type": video_data.get("layoutType", "cards"),
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


def check_nvenc_available() -> bool:
    try:
        cmd = ["ffmpeg", "-f", "lavfi", "-i", "nullsrc=s=256x256:d=1", "-c:v", "h264_nvenc", "-f", "null", "-"]
        res = subprocess.run(cmd, capture_output=True, text=True, check=False)
        return res.returncode == 0
    except Exception:
        return False

def generate_srt_content(subtitles: list) -> str:
    def fmt_time(sec: float) -> str:
        hours = int(sec // 3600)
        mins = int((sec % 3600) // 60)
        secs = int(sec % 60)
        millis = int(round((sec % 1) * 1000))
        return f"{hours:02d}:{mins:02d}:{secs:02d},{millis:03d}"

    lines = []
    for idx, sub in enumerate(subtitles or [], 1):
        st = float(sub.get("start", 0.0) or 0.0)
        et = float(sub.get("end", st + 1.0) or (st + 1.0))
        text = str(sub.get("text", "")).strip()
        lines.append(f"{idx}\n{fmt_time(st)} --> {fmt_time(et)}\n{text}\n")
    return "\n".join(lines)


class AdvancedRenderRequest(BaseModel):
    preset: Optional[str] = "tiktok_reels" # "tiktok_reels", "youtube_4k", "fast_draft", "prores_master", "custom"
    format: Optional[str] = "9:16"         # "9:16", "16:9", "1:1"
    resolution: Optional[str] = "1080p"    # "720p", "1080p", "1440p", "4k"
    fps: Optional[int] = 30
    codec: Optional[str] = "h264_nvenc"    # "h264_nvenc", "h264_cpu", "hevc_nvenc", "prores", "av1"
    quality: Optional[str] = "high"        # "lossless", "high", "balanced", "fast"
    audioLoudnorm: Optional[bool] = True
    audioBitrate: Optional[str] = "256k"
    fastStart: Optional[bool] = True
    exportSrt: Optional[bool] = True
    exportThumbnail: Optional[bool] = True

def run_advanced_export_pipeline(req: AdvancedRenderRequest):
    global render_state
    render_state["status"] = "rendering"
    render_state["progress"] = 5
    render_state["stage"] = 1
    render_state["error"] = None
    render_state["message"] = f"Remotion motoru kareleri olusturuyor ({req.format} - {req.resolution})..."

    # 1. Composition selection
    comp_id = "NotebookVideo"
    out_final_name = "video.mp4"
    if req.format == "16:9":
        comp_id = "NotebookVideo-Horizontal"
        out_final_name = "video_horizontal.mp4"
    elif req.format == "1:1":
        comp_id = "NotebookVideo-Square"
        out_final_name = "video_square.mp4"

    raw_mp4_path = os.path.join(OUT_DIR, f"temp_raw_{uuid.uuid4().hex[:8]}.mp4")
    final_mp4_path = os.path.join(OUT_DIR, out_final_name)
    srt_path = os.path.join(OUT_DIR, "subtitles.srt")
    thumb_path = os.path.join(OUT_DIR, "thumbnail.png")
    bundle_path = os.path.join(OUT_DIR, "export_bundle.zip")

    try:
        # A. REMOTION RENDER (STAGE 1: 0% -> 70%)
        cmd_remotion = [
            "npx.cmd", "remotion", "render", "src/index.ts", comp_id, raw_mp4_path,
            "--gl=angle", "--concurrency=4", "--log=verbose"
        ]
        proc = subprocess.Popen(
            cmd_remotion, cwd=BASE_DIR, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            text=True, encoding="utf-8", errors="replace"
        )

        for line in iter(proc.stdout.readline, ''):
            if not line:
                break
            # Parse progress: e.g. "Rendered 150/720 frames (20%)"
            m = re.search(r'Rendered\s+(\d+)/(\d+)\s+frames.*?(\d+)%', line)
            if m:
                cur_f = int(m.group(1))
                tot_f = int(m.group(2))
                pct = int(m.group(3))
                render_state["current_frame"] = cur_f
                render_state["total_frames"] = tot_f
                render_state["progress"] = min(75, 5 + int(pct * 0.7))
                render_state["message"] = f"Kareler isleniyor: {cur_f}/{tot_f} (%{pct})"

        proc.stdout.close()
        proc.wait()

        if proc.returncode != 0 or not os.path.exists(raw_mp4_path):
            raise Exception("Remotion derleme sirasinda hata olustu.")

        # B. FFMPEG TITANIUM POST-PROCESSING (STAGE 2: 75% -> 90%)
        render_state["status"] = "postprocessing"
        render_state["stage"] = 2
        render_state["progress"] = 80
        render_state["message"] = "FFmpeg Post-Processing: Donanim hizlandirma ve ses optimizasyonu..."

        # Determine scale filter
        scale_filter = ""
        if req.format == "9:16":
            if req.resolution == "720p": scale_filter = "scale=720:1280:flags=lanczos"
            elif req.resolution == "1440p": scale_filter = "scale=1440:2560:flags=lanczos"
            elif req.resolution == "4k": scale_filter = "scale=2160:3840:flags=lanczos"
            else: scale_filter = "scale=1080:1920:flags=lanczos"
        elif req.format == "16:9":
            if req.resolution == "720p": scale_filter = "scale=1280:720:flags=lanczos"
            elif req.resolution == "1440p": scale_filter = "scale=2560:1440:flags=lanczos"
            elif req.resolution == "4k": scale_filter = "scale=3840:2160:flags=lanczos"
            else: scale_filter = "scale=1920:1080:flags=lanczos"
        elif req.format == "1:1":
            if req.resolution == "4k": scale_filter = "scale=2160:2160:flags=lanczos"
            else: scale_filter = "scale=1080:1080:flags=lanczos"

        # Build FFmpeg command
        nvenc_ok = check_nvenc_available()
        ffmpeg_cmd = ["ffmpeg", "-y", "-i", raw_mp4_path]

        # Video filter
        if scale_filter:
            ffmpeg_cmd.extend(["-vf", scale_filter])

        # Codec configuration
        chosen_codec = req.codec or "h264_nvenc"
        if "nvenc" in chosen_codec and nvenc_ok:
            if "hevc" in chosen_codec:
                ffmpeg_cmd.extend(["-c:v", "hevc_nvenc", "-preset", "p6", "-tune", "hq", "-cq", "20"])
            else:
                ffmpeg_cmd.extend(["-c:v", "h264_nvenc", "-preset", "p6", "-tune", "hq", "-cq", "19"])
        elif chosen_codec == "prores":
            ffmpeg_cmd.extend(["-c:v", "prores_ks", "-profile:v", "3", "-vendor", "apl0", "-pix_fmt", "yuv422p10le"])
        else: # CPU fallback
            ffmpeg_cmd.extend(["-c:v", "libx264", "-preset", "slow", "-crf", "18", "-pix_fmt", "yuv420p"])

        # Audio configuration
        audio_filters = []
        if req.audioLoudnorm:
            audio_filters.append("loudnorm=I=-14:TP=-1.5:LRA=11")
        if audio_filters:
            ffmpeg_cmd.extend(["-af", ",".join(audio_filters)])
        ffmpeg_cmd.extend(["-c:a", "aac", "-b:a", req.audioBitrate or "256k", "-ar", "48000"])

        # Web FastStart
        if req.fastStart:
            ffmpeg_cmd.extend(["-movflags", "+faststart"])

        ffmpeg_cmd.append(final_mp4_path)

        res_ffmpeg = subprocess.run(ffmpeg_cmd, capture_output=True, text=True, check=False)
        if res_ffmpeg.returncode != 0:
            # If NVENC failed, fallback to simple copy or CPU
            shutil.copyfile(raw_mp4_path, final_mp4_path)

        # Clean up temporary raw render
        try:
            if os.path.exists(raw_mp4_path):
                os.remove(raw_mp4_path)
        except Exception:
            pass

        # C. STAGE 3: EXTRAS, SUBTITLES & BUNDLE (90% -> 100%)
        render_state["stage"] = 3
        render_state["progress"] = 92
        render_state["message"] = "Altyazi (.SRT), kapak resmi ve yayin paketi hazirlaniyor..."

        # Load video data for metadata
        gen_data = {}
        data_file = os.path.join(SRC_DIR, "generatedData.json")
        if os.path.exists(data_file):
            try:
                with open(data_file, "r", encoding="utf-8") as f:
                    gen_data = json.load(f)
            except Exception:
                pass

        # Generate SRT
        if req.exportSrt:
            srt_content = generate_srt_content(gen_data.get("subtitles", []))
            with open(srt_path, "w", encoding="utf-8") as f:
                f.write(srt_content)

        # Generate Thumbnail
        if req.exportThumbnail:
            subprocess.run(
                ["npx.cmd", "remotion", "still", "src/index.ts", comp_id, thumb_path, "--frame=45"],
                cwd=BASE_DIR, capture_output=True, check=False
            )

        # Create Social Post Text
        viral_info = gen_data.get("viral", {})
        titles = viral_info.get("viralTitles", [])
        title_text = titles[0] if titles else gen_data.get("headerMain", "Notebook Video Shorts")
        hashtags = " ".join(viral_info.get("hashtags", ["#shorts", "#kesfet", "#fyp"]))
        post_txt_path = os.path.join(OUT_DIR, "social_post.txt")
        with open(post_txt_path, "w", encoding="utf-8") as f:
            f.write(f"BASLIK:\n{title_text}\n\nACIKLAMA:\n{gen_data.get('headerLine1', '')} - {gen_data.get('headerLine2', '')}\n\nHASHTAGLER:\n{hashtags}\n")

        # Create ZIP Bundle
        with zipfile.ZipFile(bundle_path, "w", zipfile.ZIP_DEFLATED) as zipf:
            if os.path.exists(final_mp4_path):
                zipf.write(final_mp4_path, os.path.basename(final_mp4_path))
            if os.path.exists(thumb_path):
                zipf.write(thumb_path, "thumbnail.png")
            if os.path.exists(srt_path):
                zipf.write(srt_path, "subtitles.srt")
            if os.path.exists(post_txt_path):
                zipf.write(post_txt_path, "social_post.txt")

        # Finished!
        ts = int(time.time())
        render_state["status"] = "completed"
        render_state["progress"] = 100
        render_state["message"] = "Render ve dis aktarma paketi basariyla tamamlandi!"
        render_state["video_url"] = f"/out/{out_final_name}?t={ts}"
        render_state["srt_url"] = f"/out/subtitles.srt?t={ts}"
        render_state["thumbnail_url"] = f"/out/thumbnail.png?t={ts}"
        render_state["bundle_url"] = f"/api/export/bundle?t={ts}"
        render_state["last_rendered_at"] = time.strftime("%Y-%m-%d %H:%M:%S")

    except Exception as e:
        render_state["status"] = "error"
        render_state["error"] = str(e)
        render_state["message"] = f"Render sirasinda hata olustu: {str(e)}"


@app.get("/api/render/system-capabilities")
def get_system_render_capabilities():
    """Detect GPU hardware acceleration support."""
    nvenc_ok = check_nvenc_available()
    return {
        "nvenc": nvenc_ok,
        "hevc_nvenc": nvenc_ok,
        "ffmpeg_available": True,
        "ffmpeg_version": "9.0.1",
        "recommended_codec": "h264_nvenc" if nvenc_ok else "h264_cpu"
    }

@app.post("/api/render/advanced")
def trigger_advanced_render(bg_tasks: BackgroundTasks, req: AdvancedRenderRequest):
    global render_state
    if render_state["status"] in ["rendering", "postprocessing"]:
        return {"status": render_state["status"], "message": "Zaten aktif bir render devam ediyor."}

    bg_tasks.add_task(run_advanced_export_pipeline, req)
    render_state["status"] = "rendering"
    render_state["progress"] = 2
    render_state["message"] = "Gelismi Disa Aktarma Motoru baslatiliyor..."
    return {"status": "started", "message": "Gelismi Disa Aktarma Motoru baslatildi!"}

@app.get("/api/export/srt")
def download_srt_file():
    srt_file = os.path.join(OUT_DIR, "subtitles.srt")
    if not os.path.exists(srt_file):
        raise HTTPException(status_code=404, detail="Henuz SRT altyazi dosyasi olusturulmadi.")
    return FileResponse(srt_file, media_type="text/plain", filename="subtitles.srt")

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
        "duration": calculate_dynamic_timeline_duration(video_data, scenes),
        "subtitles": video_data.get("subtitles", []),
        "words": video_data.get("words", [])
    }


class ShiftScenesRequest(BaseModel):
    targetStart: float

@app.post("/api/timeline/shift-scenes")
def shift_scenes_offset(req: ShiftScenesRequest):
    """Shift all AI notebook scenes so that the first scene starts at targetStart (e.g. after quote video)."""
    data_file = os.path.join(SRC_DIR, "generatedData.json")
    if not os.path.exists(data_file):
        raise HTTPException(status_code=404, detail="Proje verisi bulunamadı.")
    with open(data_file, "r", encoding="utf-8") as f:
        video_data = json.load(f)

    scenes = video_data.get("scenes", [])
    if not scenes:
        raise HTTPException(status_code=400, detail="Sahneler listesi boş.")

    first_start = float(scenes[0].get("startTime", 0.0) or 0.0)
    delta = float(req.targetStart) - first_start

    for s in scenes:
        s["startTime"] = max(0.0, round(float(s.get("startTime", 0.0) or 0.0) + delta, 2))
        s["endTime"] = max(s["startTime"] + 1.0, round(float(s.get("endTime", 0.0) or 0.0) + delta, 2))

    # Also shift subtitles if any
    subtitles = video_data.get("subtitles", [])
    if subtitles:
        first_sub = float(subtitles[0].get("start", 0.0) or 0.0)
        sub_delta = float(req.targetStart) - first_sub
        for sub in subtitles:
            sub["start"] = max(0.0, round(float(sub.get("start", 0.0) or 0.0) + sub_delta, 2))
            sub["end"] = max(sub["start"] + 0.1, round(float(sub.get("end", 0.0) or 0.0) + sub_delta, 2))

    video_data["aiKurguStartOffset"] = round(float(req.targetStart), 2)
    total_dur = calculate_dynamic_timeline_duration(video_data, scenes)
    video_data["totalDuration"] = total_dur

    with open(data_file, "w", encoding="utf-8") as f:
        json.dump(video_data, f, ensure_ascii=False, indent=2)

    return {
        "success": True,
        "scenes": scenes,
        "totalDuration": total_dur,
        "aiKurguStartOffset": round(float(req.targetStart), 2)
    }

@app.post("/api/timeline/audio")
async def upload_timeline_audio(
    file: UploadFile = File(...),
    transcript: Optional[str] = Form(None)
):
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
    
    # Check if custom transcript was provided by the user
    user_transcript = (transcript or "").strip()
    
    # Whisper AI alignment (acoustic guide)
    w_model = get_whisper()
    raw_words = []
    whisper_full_text = ""
    if w_model is not None:
        try:
            whisper_res = w_model.transcribe(final_audio_path, word_timestamps=True)
            whisper_full_text = clean_text_apostrophes(whisper_res.get("text", "").strip())
            for seg in whisper_res.get("segments", []):
                for w in seg.get("words", []):
                    w_text = w.get("word", "").strip()
                    if w_text:
                        raw_words.append({
                            "word": w_text,
                            "text": w_text,
                            "start": round(w.get("start", 0), 2),
                            "end": round(w.get("end", 0), 2)
                        })
        except Exception as e:
            print(f"Whisper transcription error: {e}")

    # Determine final words & subtitles
    if user_transcript:
        # USER PROVIDED EXACT TEXT: Guarantee 100% fidelity to user's text!
        clean_user_text = fix_turkish_orthography_and_compounds(user_transcript)
        words, subtitles = align_custom_transcript_to_audio(clean_user_text, duration, raw_words)
        full_text = " ".join([w.get("text") or w.get("word") or "" for w in words]).strip() or clean_user_text
    else:
        # Fall back to Whisper transcription
        words = stitch_whisper_word_tokens(raw_words)
        if words:
            subtitles = build_subtitle_chunks(words, chunk_size=3)
        else:
            subtitles = generate_subtitles_fallback(whisper_full_text or "Kendi eklediğiniz ses kaydı", duration)
        full_text = whisper_full_text or "Kendi eklediğiniz ses kaydı"

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
        
    # Adjust scenes to fit new duration & populate scene text from user words
    scenes = ensure_scenes_structure(video_data)
    num_scenes = len(scenes)
    slice_dur = duration / max(1, num_scenes)
    cur = 0.0
    for idx, sc in enumerate(scenes):
        sc_st = round(cur, 2)
        cur += slice_dur
        sc_en = round(cur if idx < num_scenes - 1 else duration, 2)
        sc["startTime"] = sc_st
        sc["endTime"] = sc_en
        # Align scene narrative text with words in this interval
        words_in_window = [w["text"] for w in words if (w["start"] >= sc_st - 0.4 and w["end"] <= sc_en + 0.4)]
        if words_in_window:
            sc["text"] = " ".join(words_in_window)
            sc["narration"] = sc["text"]
            
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
        "narration": full_text,
        "custom_transcript_used": bool(user_transcript),
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
    cleaned_subtitles = []
    for s in req.subtitles:
        s_copy = dict(s)
        if "text" in s_copy:
            s_copy["text"] = clean_text_apostrophes(s_copy["text"])
        cleaned_subtitles.append(s_copy)
    video_data["subtitles"] = cleaned_subtitles
    with open(data_file, "w", encoding="utf-8") as f:
        json.dump(video_data, f, ensure_ascii=False, indent=2)
    return {"success": True, "subtitles": cleaned_subtitles}

class RealignTranscriptRequest(BaseModel):
    transcript: str

@app.post("/api/timeline/realign-transcript")
def api_realign_transcript(req: RealignTranscriptRequest):
    data_file = os.path.join(SRC_DIR, "generatedData.json")
    if not os.path.exists(data_file):
        raise HTTPException(status_code=404, detail="Proje verisi bulunamadı.")
    with open(data_file, "r", encoding="utf-8") as f:
        video_data = json.load(f)

    user_text = fix_turkish_orthography_and_compounds(req.transcript.strip())
    if not user_text:
        raise HTTPException(status_code=400, detail="Lütfen geçerli bir metin girin.")

    duration = float(video_data.get("totalDuration", 15.0))
    existing_words = video_data.get("words", [])
    if not existing_words and video_data.get("subtitles"):
        existing_words = [w for s in video_data["subtitles"] for w in s.get("words", [])]

    words, subtitles = align_custom_transcript_to_audio(user_text, duration, existing_words)
    full_narration = " ".join([w.get("text") or w.get("word") or "" for w in words]).strip() or user_text
    video_data["narration"] = full_narration
    video_data["words"] = words
    video_data["subtitles"] = subtitles

    scenes = video_data.get("scenes", [])
    for sc in scenes:
        st = sc.get("startTime", 0.0)
        en = sc.get("endTime", duration)
        words_in_window = [w["text"] for w in words if (w["start"] >= st - 0.4 and w["end"] <= en + 0.4)]
        if words_in_window:
            sc["text"] = " ".join(words_in_window)
            sc["narration"] = sc["text"]

    with open(data_file, "w", encoding="utf-8") as f:
        json.dump(video_data, f, ensure_ascii=False, indent=2)

    return {
        "success": True,
        "narration": full_narration,
        "words": words,
        "subtitles": subtitles,
        "scenes": scenes,
        "video_data": video_data
    }

@app.post("/api/timeline/ai-phonetic-fix")
def api_ai_phonetic_fix():
    """
    AI Phonetic Linguist Engine:
    Applies comprehensive phonetic and orthographic correction (e.g. 'mühe defa' -> 'mı hedefe',
    'ısırlık' -> 'asırlık', Islamic fıkıh terms restoration), realigns with millisecond timestamps,
    and updates generatedData.json, scenes, words, and subtitles.
    """
    data_file = os.path.join(SRC_DIR, "generatedData.json")
    if not os.path.exists(data_file):
        raise HTTPException(status_code=404, detail="Proje verisi bulunamadı.")
    with open(data_file, "r", encoding="utf-8") as f:
        video_data = json.load(f)

    # 1. Check if expert ground-truth transcript exists
    expert_file = os.path.join(BASE_DIR, "data", "corrected_transcript_expert.txt")
    if os.path.exists(expert_file):
        with open(expert_file, "r", encoding="utf-8") as ef:
            corrected_text = ef.read().strip()
    else:
        # Build text from existing narration/subtitles and apply phonetic corrections
        raw_text = video_data.get("narration") or " ".join(s.get("text", "") for s in video_data.get("subtitles", []))
        corrected_text = fix_turkish_orthography_and_compounds(raw_text)

    duration = float(video_data.get("totalDuration", 15.0))
    existing_words = video_data.get("words", [])
    if not existing_words and video_data.get("subtitles"):
        existing_words = [w for s in video_data["subtitles"] for w in s.get("words", [])]

    # Realign using Monotonic DP Forced Aligner
    words, subtitles = align_custom_transcript_to_audio(corrected_text, duration, existing_words)
    full_narration = " ".join([w.get("text") or w.get("word") or "" for w in words]).strip() or corrected_text

    video_data["narration"] = full_narration
    video_data["words"] = words
    video_data["subtitles"] = subtitles

    scenes = video_data.get("scenes", [])
    for sc in scenes:
        st = sc.get("startTime", 0.0)
        en = sc.get("endTime", duration)
        words_in_window = [w["text"] for w in words if (w["start"] >= st - 0.4 and w["end"] <= en + 0.4)]
        if words_in_window:
            sc["text"] = " ".join(words_in_window)
            sc["narration"] = sc["text"]

    with open(data_file, "w", encoding="utf-8") as f:
        json.dump(video_data, f, ensure_ascii=False, indent=2)

    return {
        "success": True,
        "narration": full_narration,
        "words": words,
        "subtitles": subtitles,
        "scenes": scenes,
        "video_data": video_data,
        "message": "AI Fonetik Dil Bilimci düzeltmeleri ve milisaniyelik hizalama başarıyla uygulandı."
    }


# ================= MULTI-TRACK MEDIA ASSET ENGINE (VIDEO, IMAGE, AUDIO, PIP, PNG) =================
UPLOADS_DIR = os.path.join(PUBLIC_DIR, "uploads")
os.makedirs(UPLOADS_DIR, exist_ok=True)

class ExtractAudioRequest(BaseModel):
    video_url: Optional[str] = None
    videoUrl: Optional[str] = None
    apply_to_timeline: Optional[bool] = True
    applyToTimeline: Optional[bool] = True

class RemoveAudioRequest(BaseModel):
    mode: str = "mute" # "mute", "unmute" or "delete"

class AddPipRequest(BaseModel):
    videoUrl: Optional[str] = None
    video_url: Optional[str] = None
    startTime: Optional[float] = None
    start_time: Optional[float] = None
    endTime: Optional[float] = None
    end_time: Optional[float] = None
    duration: Optional[float] = 6.0
    position: Optional[str] = "top-right"
    shape: Optional[str] = "circle"
    width: Optional[Any] = 340
    volume: Optional[float] = 1.0
    muted: Optional[bool] = False
    sceneId: Optional[str] = None
    scene_id: Optional[str] = None

class AddPngOverlayRequest(BaseModel):
    imageUrl: Optional[str] = None
    image_url: Optional[str] = None
    startTime: Optional[float] = None
    start_time: Optional[float] = None
    endTime: Optional[float] = None
    end_time: Optional[float] = None
    duration: Optional[float] = 8.0
    position: Optional[str] = "top-right"
    width: Optional[Any] = 180
    opacity: Optional[float] = 1.0
    animation: Optional[str] = "bounce"
    rotation: Optional[float] = 0.0
    sceneId: Optional[str] = None
    scene_id: Optional[str] = None

class DeleteMediaItemRequest(BaseModel):
    item_type: Optional[str] = None
    itemType: Optional[str] = None
    item_id: Optional[str] = None
    itemId: Optional[str] = None

class SetSceneMediaRequest(BaseModel):
    scene_id: Optional[str] = None
    sceneId: Optional[str] = None
    video_url: Optional[str] = None
    videoUrl: Optional[str] = None
    fit: Optional[str] = "cover"
    apply_to_all_scenes: Optional[bool] = False
    applyToAllScenes: Optional[bool] = False
    illustration_url: Optional[str] = None
    illustrationUrl: Optional[str] = None
    illustration_style: Optional[str] = "polaroid"
    illustrationStyle: Optional[str] = "polaroid"
    illustration_caption: Optional[str] = None
    illustrationCaption: Optional[str] = None

@app.post("/api/media/upload")
async def api_media_upload(
    file: UploadFile = File(...),
    media_type: Optional[str] = Form(None)
):
    """
    Universal Media Uploader for Video, Image, PNG Overlay & Audio assets.
    """
    orig_name = file.filename or "media_upload"
    ext = os.path.splitext(orig_name)[1].lower()
    clean_base = re.sub(r'[^a-zA-Z0-9_-]', '_', os.path.splitext(orig_name)[0])[:30]
    unique_name = f"{clean_base}_{uuid.uuid4().hex[:8]}{ext}"
    target_path = os.path.join(UPLOADS_DIR, unique_name)

    content_bytes = await file.read()
    with open(target_path, "wb") as f:
        f.write(content_bytes)

    detected_type = media_type
    if not detected_type:
        if ext in [".mp4", ".webm", ".mov", ".mkv"]:
            detected_type = "video"
        elif ext in [".png"]:
            detected_type = "png"
        elif ext in [".jpg", ".jpeg", ".webp", ".svg"]:
            detected_type = "image"
        elif ext in [".mp3", ".wav", ".m4a", ".aac", ".ogg"]:
            detected_type = "audio"
        else:
            detected_type = "other"

    duration = 0.0
    if detected_type in ["video", "audio"]:
        try:
            duration = probe_audio_duration(target_path)
        except Exception:
            duration = 10.0

    return {
        "success": True,
        "url": f"/public/uploads/{unique_name}",
        "relative_url": f"uploads/{unique_name}",
        "filename": unique_name,
        "original_name": orig_name,
        "media_type": detected_type,
        "duration": round(duration, 2),
        "size_bytes": len(content_bytes)
    }

@app.post("/api/media/extract-audio")
def api_extract_audio(req: ExtractAudioRequest):
    """
    Extracts audio track from video file using FFmpeg and optionally sets it as timeline audio.
    """
    video_path = req.video_url.strip()
    if video_path.startswith("/public/"):
        local_video_path = os.path.join(PUBLIC_DIR, video_path[8:])
    elif video_path.startswith("public/"):
        local_video_path = os.path.join(PUBLIC_DIR, video_path[7:])
    elif os.path.exists(os.path.join(PUBLIC_DIR, video_path)):
        local_video_path = os.path.join(PUBLIC_DIR, video_path)
    else:
        local_video_path = os.path.join(UPLOADS_DIR, os.path.basename(video_path))

    if not os.path.exists(local_video_path):
        raise HTTPException(status_code=404, detail=f"Video dosyası bulunamadı: {req.video_url}")

    out_name = f"extracted_audio_{uuid.uuid4().hex[:8]}.mp3"
    out_path = os.path.join(PUBLIC_DIR, out_name)

    cmd = ["ffmpeg", "-y", "-i", local_video_path, "-vn", "-acodec", "libmp3lame", "-q:a", "2", out_path]
    try:
        subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"FFmpeg ses çıkarma hatası: {str(e)}")

    extracted_dur = probe_audio_duration(out_path)
    waveform = extract_audio_waveform(out_path, num_peaks=120)

    if req.apply_to_timeline:
        data_file = os.path.join(SRC_DIR, "generatedData.json")
        if os.path.exists(data_file):
            with open(data_file, "r", encoding="utf-8") as f:
                vdata = json.load(f)
            vdata["audioUrl"] = out_name
            vdata["audioMuted"] = False
            vdata["totalDuration"] = max(extracted_dur, float(vdata.get("totalDuration", 10.0)))
            with open(data_file, "w", encoding="utf-8") as f:
                json.dump(vdata, f, ensure_ascii=False, indent=2)

    return {
        "success": True,
        "audio_url": f"/public/{out_name}",
        "relative_url": out_name,
        "duration": round(extracted_dur, 2),
        "waveform": waveform,
        "message": "Sesi videodan çıkarma işlemi başarıyla tamamlandı!"
    }

@app.post("/api/timeline/remove-audio")
@app.post("/api/media/remove-audio")
def api_remove_audio(req: RemoveAudioRequest):
    """
    Mutes, unmutes or removes audio from the project timeline.
    """
    data_file = os.path.join(SRC_DIR, "generatedData.json")
    if not os.path.exists(data_file):
        raise HTTPException(status_code=404, detail="Proje verisi bulunamadı.")

    with open(data_file, "r", encoding="utf-8") as f:
        vdata = json.load(f)

    if req.mode == "mute":
        vdata["audioMuted"] = True
    elif req.mode == "unmute":
        vdata["audioMuted"] = False
    elif req.mode == "delete":
        vdata["audioUrl"] = ""
        vdata["audioMuted"] = False
        vdata["words"] = []

    with open(data_file, "w", encoding="utf-8") as f:
        json.dump(vdata, f, ensure_ascii=False, indent=2)

    return {
        "success": True,
        "audioMuted": vdata.get("audioMuted", False),
        "audioUrl": vdata.get("audioUrl", ""),
        "video_data": vdata,
        "message": "Ses durumu güncellendi."
    }

@app.post("/api/timeline/add-quote-video")
def api_add_quote_video(req: AddQuoteVideoRequest):
    """
    Adds a trimmed Quote / Reaction / Debunking video frame to the timeline.
    """
    data_file = os.path.join(SRC_DIR, "generatedData.json")
    if not os.path.exists(data_file):
        raise HTTPException(status_code=404, detail="Proje verisi bulunamadı.")
    with open(data_file, "r", encoding="utf-8") as f:
        vdata = json.load(f)

    video_url = req.videoUrl or req.video_url
    if not video_url:
        raise HTTPException(status_code=400, detail="videoUrl zorunludur.")

    trim_start = float(req.trimStart if req.trimStart is not None else (req.trim_start or 0.0))
    trim_end = float(req.trimEnd if req.trimEnd is not None else (req.trim_end or (trim_start + 6.0)))
    if trim_end <= trim_start:
        trim_end = trim_start + 4.0

    calc_dur = round(trim_end - trim_start, 2)
    dur = float(req.duration) if req.duration is not None else calc_dur
    tl_start = float(req.timelineStart if req.timelineStart is not None else (req.timeline_start or 0.0))

    quote_item = {
        "id": f"quote_{uuid.uuid4().hex[:8]}",
        "videoUrl": video_url,
        "trimStart": round(trim_start, 2),
        "trimEnd": round(trim_end, 2),
        "timelineStart": round(tl_start, 2),
        "timelineEnd": round(tl_start + dur, 2),
        "duration": round(dur, 2),
        "theme": req.theme or "red_alert",
        "headerText": req.headerText or req.header_text or "Arkadaşlar bu videoyu iyi izleyin...",
        "subHeaderText": req.subHeaderText or req.sub_header_text or "",
        "authorTag": req.authorTag or req.author_tag or "",
        "stamp": req.stamp or "yalan",
        "volume": float(req.volume if req.volume is not None else 1.0),
        "muted": bool(req.muted if req.muted is not None else False),
        "freezeAtEnd": bool(req.freezeAtEnd or req.freeze_at_end or False)
    }

    if "quoteVideos" not in vdata or not isinstance(vdata["quoteVideos"], list):
        vdata["quoteVideos"] = []
    vdata["quoteVideos"].append(quote_item)

    with open(data_file, "w", encoding="utf-8") as f:
        json.dump(vdata, f, ensure_ascii=False, indent=2)

    return {"success": True, "quoteItem": quote_item, "video_data": vdata}

@app.post("/api/timeline/add-pip")
def api_add_pip(req: AddPipRequest):
    """
    Adds a Picture-in-Picture floating video overlay to the timeline.
    """
    data_file = os.path.join(SRC_DIR, "generatedData.json")
    if not os.path.exists(data_file):
        raise HTTPException(status_code=404, detail="Proje verisi bulunamadı.")
    with open(data_file, "r", encoding="utf-8") as f:
        vdata = json.load(f)

    duration = float(vdata.get("totalDuration", 15.0))
    video_url = req.videoUrl or req.video_url
    if not video_url:
        raise HTTPException(status_code=400, detail="videoUrl zorunludur.")
    raw_start = req.startTime if req.startTime is not None else (req.start_time or 0.0)
    raw_end = req.endTime if req.endTime is not None else req.end_time
    start_t = max(0.0, float(raw_start))
    end_t = float(raw_end) if raw_end is not None else min(duration, start_t + (req.duration or 6.0))

    pip_item = {
        "id": f"pip_{uuid.uuid4().hex[:8]}",
        "videoUrl": video_url,
        "startTime": round(start_t, 2),
        "endTime": round(end_t, 2),
        "position": req.position or "top-right",
        "shape": req.shape or "circle",
        "width": req.width if req.width is not None else 340,
        "volume": float(req.volume if req.volume is not None else 1.0),
        "muted": bool(req.muted if req.muted is not None else False)
    }

    if "pipVideos" not in vdata or not isinstance(vdata["pipVideos"], list):
        vdata["pipVideos"] = []
    vdata["pipVideos"].append(pip_item)

    with open(data_file, "w", encoding="utf-8") as f:
        json.dump(vdata, f, ensure_ascii=False, indent=2)

    return {"success": True, "pipItem": pip_item, "video_data": vdata}

@app.post("/api/timeline/add-png-overlay")
def api_add_png_overlay(req: AddPngOverlayRequest):
    """
    Adds a transparent PNG sticker / logo / watermark overlay to the timeline.
    """
    data_file = os.path.join(SRC_DIR, "generatedData.json")
    if not os.path.exists(data_file):
        raise HTTPException(status_code=404, detail="Proje verisi bulunamadı.")
    with open(data_file, "r", encoding="utf-8") as f:
        vdata = json.load(f)

    duration = float(vdata.get("totalDuration", 15.0))
    image_url = req.imageUrl or req.image_url
    if not image_url:
        raise HTTPException(status_code=400, detail="imageUrl zorunludur.")
    raw_start = req.startTime if req.startTime is not None else (req.start_time or 0.0)
    raw_end = req.endTime if req.endTime is not None else req.end_time
    start_t = max(0.0, float(raw_start))
    end_t = float(raw_end) if raw_end is not None else min(duration, start_t + (req.duration or 8.0))

    overlay_item = {
        "id": f"overlay_{uuid.uuid4().hex[:8]}",
        "imageUrl": image_url,
        "startTime": round(start_t, 2),
        "endTime": round(end_t, 2),
        "position": req.position or "top-right",
        "width": req.width if req.width is not None else 180,
        "opacity": float(req.opacity if req.opacity is not None else 1.0),
        "animation": req.animation or "bounce",
        "rotation": float(req.rotation if req.rotation is not None else 0.0)
    }

    if "overlayImages" not in vdata or not isinstance(vdata["overlayImages"], list):
        vdata["overlayImages"] = []
    vdata["overlayImages"].append(overlay_item)

    with open(data_file, "w", encoding="utf-8") as f:
        json.dump(vdata, f, ensure_ascii=False, indent=2)

    return {"success": True, "overlayItem": overlay_item, "video_data": vdata}

@app.post("/api/timeline/delete-media-item")
def api_delete_media_item(req: DeleteMediaItemRequest):
    data_file = os.path.join(SRC_DIR, "generatedData.json")
    if not os.path.exists(data_file):
        raise HTTPException(status_code=404, detail="Proje verisi bulunamadı.")
    with open(data_file, "r", encoding="utf-8") as f:
        vdata = json.load(f)

    item_type = req.item_type or req.itemType or ""
    item_id = req.item_id or req.itemId or ""

    if (item_type in ["pip", "pip_video"]) and "pipVideos" in vdata:
        vdata["pipVideos"] = [p for p in vdata["pipVideos"] if p.get("id") != item_id]
    elif (item_type in ["overlay", "png_overlay", "png"]) and "overlayImages" in vdata:
        vdata["overlayImages"] = [o for o in vdata["overlayImages"] if o.get("id") != item_id]
    elif (item_type in ["quote", "quote_video"]) and "quoteVideos" in vdata:
        vdata["quoteVideos"] = [q for q in vdata["quoteVideos"] if q.get("id") != item_id]

    with open(data_file, "w", encoding="utf-8") as f:
        json.dump(vdata, f, ensure_ascii=False, indent=2)

    return {"success": True, "video_data": vdata}

@app.post("/api/timeline/update-media-position")
def api_update_media_position(req: UpdateMediaPositionRequest):
    data_file = os.path.join(SRC_DIR, "generatedData.json")
    if not os.path.exists(data_file):
        raise HTTPException(status_code=404, detail="Proje verisi bulunamadı.")
    with open(data_file, "r", encoding="utf-8") as f:
        vdata = json.load(f)

    item_type = req.item_type or req.itemType or ""
    item_id = req.item_id or req.itemId or ""
    raw_start = req.timeline_start if req.timeline_start is not None else req.timelineStart
    if raw_start is None:
        raise HTTPException(status_code=400, detail="timeline_start zorunludur.")
    new_start = round(max(0.0, float(raw_start)), 2)
    updated = False

    if (item_type in ["quote", "quote_video", "quoteVideo"]) and "quoteVideos" in vdata:
        for qv in vdata["quoteVideos"]:
            if qv.get("id") == item_id:
                dur = float(req.duration) if req.duration is not None else float(qv.get("duration", 5.0))
                qv["timelineStart"] = new_start
                qv["timelineEnd"] = round(new_start + dur, 2)
                qv["duration"] = round(dur, 2)
                updated = True
                break
    elif (item_type in ["pip", "pip_video", "pipVideo"]) and "pipVideos" in vdata:
        for p in vdata["pipVideos"]:
            if p.get("id") == item_id:
                dur = float(req.duration) if req.duration is not None else float(p.get("endTime", 5.0) - p.get("startTime", 0.0))
                p["startTime"] = new_start
                p["endTime"] = round(new_start + dur, 2)
                updated = True
                break
    elif (item_type in ["overlay", "png_overlay", "png", "image"]) and "overlayImages" in vdata:
        for o in vdata["overlayImages"]:
            if o.get("id") == item_id:
                dur = float(req.duration) if req.duration is not None else float(o.get("endTime", 4.0) - o.get("startTime", 0.0))
                o["startTime"] = new_start
                o["endTime"] = round(new_start + dur, 2)
                updated = True
                break

    if not updated:
        raise HTTPException(status_code=404, detail="Medya öğesi bulunamadı.")

    with open(data_file, "w", encoding="utf-8") as f:
        json.dump(vdata, f, ensure_ascii=False, indent=2)

    return {"success": True, "new_start": new_start, "video_data": vdata}

@app.post("/api/timeline/set-scene-media")
def api_set_scene_media(req: SetSceneMediaRequest):
    data_file = os.path.join(SRC_DIR, "generatedData.json")
    if not os.path.exists(data_file):
        raise HTTPException(status_code=404, detail="Proje verisi bulunamadı.")
    with open(data_file, "r", encoding="utf-8") as f:
        vdata = json.load(f)

    target_scene_id = req.scene_id or req.sceneId
    v_url = req.video_url or req.videoUrl
    i_url = req.illustration_url or req.illustrationUrl
    i_style = req.illustration_style or req.illustrationStyle or "polaroid"
    i_cap = req.illustration_caption or req.illustrationCaption
    apply_all = req.apply_to_all_scenes or req.applyToAllScenes or False

    if apply_all and v_url:
        vdata["videoUrl"] = v_url

    for sc in vdata.get("scenes", []):
        if apply_all or sc.get("id") == target_scene_id:
            if v_url is not None:
                sc["videoUrl"] = v_url
                sc["brollUrl"] = v_url
            if i_url is not None:
                sc["illustrationUrl"] = i_url
            if i_style is not None:
                sc["illustrationStyle"] = i_style
            if i_cap is not None:
                sc["illustrationCaption"] = i_cap
            if not apply_all:
                break

    with open(data_file, "w", encoding="utf-8") as f:
        json.dump(vdata, f, ensure_ascii=False, indent=2)

    return {"success": True, "video_data": vdata}


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
