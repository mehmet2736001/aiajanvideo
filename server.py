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
    add_scene_to_timeline
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
    "message": "Hazır",
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

class TimelineUpdateScenesRequest(BaseModel):
    scenes: List[Dict[str, Any]]

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
        raise HTTPException(status_code=404, detail="Key bulunamadı")
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
        raise HTTPException(status_code=404, detail="Key bulunamadı")
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

# VIRAL PRESETS ENDPOINT
@app.get("/api/presets")
def get_presets():
    return [
        {
            "category": "İslam & Tefekkür",
            "icon": "fa-moon",
            "items": [
                {"title": "Allah kâinatı neden birden değil de altı günde yarattı?", "layout": "cards", "theme": "notebook"},
                {"title": "Kalbin mühürlenmesi ne demektir? Bir insan nasıl hissizleşir?", "layout": "quote_spotlight", "theme": "parchment"},
                {"title": "Karıncanın rızkı ve ilahi nizamın kusursuz matematiği", "layout": "flowchart", "theme": "kraft"}
            ]
        },
        {
            "category": "Tarih & Düşünürler",
            "icon": "fa-scroll",
            "items": [
                {"title": "İbn-i Sina bir kitabı neden 40 kez okudu ve yine anlamadı?", "layout": "metric_impact", "theme": "parchment"},
                {"title": "İmam Gazali akıl ile kalp arasındaki şüphe krizini nasıl aştı?", "layout": "vs_split", "theme": "kraft"},
                {"title": "Mimar Sinan'ın Süleymaniye'deki akustiği çözen kandil ve devekuşu sırrı", "layout": "flowchart", "theme": "blueprint"}
            ]
        },
        {
            "category": "Felsefe & Psikoloji",
            "icon": "fa-brain",
            "items": [
                {"title": "Stoacılık vs Modern Telaş: Kontrol edemediğin şeyleri dert etme!", "layout": "vs_split", "theme": "chalkboard"},
                {"title": "İnsan neden en çok sevdiği şeyleri erteler? Prokrastinasyon tuzağı", "layout": "cards", "theme": "notebook"},
                {"title": "Yalnızlık hissi modern insanın neden en büyük sınavı?", "layout": "quote_spotlight", "theme": "notebook"}
            ]
        },
        {
            "category": "Evren & Bilim",
            "icon": "fa-atom",
            "items": [
                {"title": "Zaman dağlarda neden daha hızlı akar? Einstein'ın sırrı", "layout": "metric_impact", "theme": "blueprint"},
                {"title": "Karadeliklerin olay ufkunu geçersek gerçekte ne görürüz?", "layout": "flowchart", "theme": "chalkboard"},
                {"title": "Işık hızına yaklaştıkça kütle neden sonsuza gider?", "layout": "cards", "theme": "blueprint"}
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
                raise HTTPException(status_code=400, detail="Mevcut video verisi bulunamadı.")

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
        raise HTTPException(status_code=404, detail=f"{lang} dil dosyası bulunamadı.")

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
        raise HTTPException(status_code=404, detail="Proje bulunamadı.")
    with open(bundle_meta, "r", encoding="utf-8") as f:
        meta = json.load(f)
    return meta

# PROMPT OPTIMIZER (AI ASSISTANT)
@app.post("/api/prompt/optimize")
def optimize_prompt(req: OptimizeRequest):
    topic = req.topic.strip()
    if not topic:
        raise HTTPException(status_code=400, detail="Konu boş olamaz")
    
    style_prompts = {
        "curiosity": "Merak uyandıran, izleyicide soru işareti bırakan ve tıklama isteği doğuran bir kanca sorusu hazırla.",
        "philosophy": "Derin felsefi ve tefekkür içeren, insanın hayatını sorgulatan bilgece bir cümle hazırla.",
        "science": "Çarpıcı bir bilimsel paradoks veya evren sırrını ortaya koyan heyecan verici bir ifade hazırla.",
        "viral": "YouTube Shorts ve TikTok için tıklanma rekoru kıracak en yüksek kanca (click-hook) etkili başlığı üret."
    }
    style_instruction = style_prompts.get(req.style, style_prompts["curiosity"])

    prompt = f"""Sen viral Shorts ve TikTok içerik kancası ustasısın.
Kullanıcı konusu: '{topic}'
Hedef Üslup: {style_instruction}

Lütfen bu konuyu defter formatında tek satırlık efsanevi bir soruya/kancaya dönüştür ve en uygun layoutType öner (cards, vs_split, flowchart, quote_spotlight, metric_impact).

SADECE SAF JSON FORMATINDA YANIT VER:
{{
  "optimized_topic": "Dönüştürülmüş kanca başlığı",
  "suggested_layout": "cards",
  "reason": "Neden bu formatın seçildiğinin 1 cümlelik açıklaması"
}}
"""
    effective_model = req.model or DEFAULT_MODEL
    res, key_name = pool.query_with_rotation(prompt, "You are a specialized hook optimizer. Output ONLY raw JSON.", model=effective_model)
    if not res:
        raise HTTPException(status_code=500, detail="Key havuzundan yanıt alınamadı.")

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
            "reason": "Doğrudan konu kullanıldı."
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
        full_transcript = w_res.get("text", "").strip() or "Kullanıcının yüklediği ses kaydı"

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
            "text_spoken": slice_text or f"{i+1}. Bölüm Konuşması"
        })

    # 7. Gemini 3 Director Prompt for Multi-Scene Storyboard
    effective_model = model or DEFAULT_MODEL
    prompt = f"""Sen viral YouTube Shorts, TikTok ve Mini-Belgesel prodüksiyonlarının BAŞ YAPAY ZEKÂ YÖNETMENİ ve senaristisin.
Kullanıcı kendi ses kaydını yükledi!
Toplam Ses Süresi: {total_duration:.1f} saniye.
Tam Ses Dökümü: '{full_transcript}'

Bu ses {num_scenes} ardışık bölüme/sahneye ayrıldı. Her sahne yaklaşık {total_duration / num_scenes:.1f} saniye sürmektedir:
{json.dumps(scene_slices, ensure_ascii=False, indent=2)}

GÖREVİN:
1. Temayı belirle: 'dark_minimalist' | 'gold_luxury' | 'neon_cyber' | 'parchment' | 'notebook' | 'kraft' | 'chalkboard' | 'blueprint'
   (KURAL: İslami / derin tefekkür dendiğinde KESİNLİKLE 'dark_minimalist' veya 'gold_luxury'; Bilim / teknoloji / evren için 'neon_cyber' veya 'blueprint'; Tarih / felsefe için 'parchment' veya 'kraft')
2. HER BİR BÖLÜM (SCENE) İÇİN:
   - Önceki sahnenin bittiği yerden devam edecek şekilde ve görsel monotonluğu kırmak için FARKLI bir şablon (layoutType) seç:
     'cards' | 'vs_split' | 'flowchart' | 'quote_spotlight' | 'metric_impact' | 'grid_explosion' | 'tri_concept'
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
      "startTime": 0.0,
      "endTime": {scene_slices[0]['end_time']},
      "layoutType": "grid_explosion",
      "headerSubtitle": "1. Bölüm",
      "headerLine1": "İLK SIR",
      "circledWord": "BAŞLANGIÇ",
      "headerLine2": "",
      "highlightedText": "CANLI SES VURGUSU",
      "strikeWord": "TESADÜF",
      "gridExplosion": {{
        "title": "EŞSİZ İŞARET",
        "subtitle": "Kelimelerin Ardındaki Derin Anlam",
        "iconType": "fingerprint",
        "itemCount": 12,
        "badgeText": "BİRİNCİ AŞAMA"
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

    import re
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
    video_data["audioUrl"] = "audio.mp3"
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
                {"id": "1", "label": "1. Anahtar", "value": "Açıklama", "icon": "brain", "color": "#1e3a8a"},
                {"id": "2", "label": "2. Anahtar", "value": "Gelişme", "icon": "scale", "color": "#15803d"},
                {"id": "3", "label": "3. Anahtar", "value": "Sonuç", "icon": "lightbulb", "color": "#d97706"}
            ]
        elif sc_layout == "vs_split" and not sc.get("vsData"):
            sc["vsData"] = {
                "leftTitle": "Zan / Yanılgı",
                "leftSubtitle": "Görünen",
                "leftPoints": ["Yüzeysel algı"],
                "rightTitle": "Hakikat",
                "rightSubtitle": "Gerçek Olan",
                "rightPoints": ["Derin anlam"],
                "verdict": "Hakikat daima ayrıntılarda gizlidir."
            }
        elif sc_layout == "flowchart" and not sc.get("flowchartSteps"):
            sc["flowchartSteps"] = [
                {"stepNumber": 1, "badge": "Giriş", "title": "Büyük Soru"},
                {"stepNumber": 2, "badge": "Gelişme", "title": "Dönüm Noktası"},
                {"stepNumber": 3, "badge": "Sonuç", "title": "Çıkarım"}
            ]
        elif sc_layout == "tri_concept" and not sc.get("triConcept"):
            sc["triConcept"] = {
                "badge": f"{i+1}. BÖLÜM",
                "concept1": {"title": "BEYİN", "icon": "brain"},
                "concept2": {"title": "KALP", "icon": "heart"},
                "concept3": {"title": "GÖZ", "icon": "eye"},
                "bottomNote": "Her parça tek bir ahengin ifadesidir."
            }
        elif sc_layout == "metric_impact" and not sc.get("metricImpact"):
            sc["metricImpact"] = {
                "bigNumber": "%100",
                "bigLabel": "DOĞRULUK",
                "subheading": "Eşsiz İfade",
                "keyTakeaway": "Sözler doğru anahtarla açılır."
            }
        elif sc_layout == "quote_spotlight" and not sc.get("quoteSpotlight"):
            sc["quoteSpotlight"] = {
                "speaker": "Ses Kaydı",
                "quoteText": sl["text_spoken"][:90] or full_transcript[:90]
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
            "startTime": sl["start_time"],
            "endTime": sl["end_time"],
            "layoutType": sc_layout,
            "headerSubtitle": sc.get("headerSubtitle") or f"{i+1}. Bölüm ({sl['start_time']}s - {sl['end_time']}s)",
            "headerLine1": sc.get("headerLine1") or (full_transcript.split()[0].upper() if full_transcript.split() else "DİKKAT"),
            "circledWord": sc.get("circledWord") or (full_transcript.split()[1].upper() if len(full_transcript.split()) > 1 else "BÜYÜK"),
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
        "topic": f"🎙️ Ses Yükleme: {full_transcript[:60]}...",
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
        "director_reason": director_dec.get("directorReason") or f"Yüklenen {total_duration:.1f} saniyelik ses kaydı için {len(synced_scenes)} bölümlü dinamik video kurgulandı."
    }

@app.post("/api/generate")
def generate_video_content(req: GenerateRequest):
    topic = req.topic.strip()
    if not topic:
        raise HTTPException(status_code=400, detail="Konu boş olamaz")

    is_auto = (req.mode == "auto" or not req.mode)

    # In manual mode, word requirement depends on explicit duration_mode
    word_req = "90-130 kelimelik derin, belgesel kurgulu, tefekkür ve merak uyandıran" if req.duration_mode == "deep" else "35-50 kelimelik akıcı, merak uyandıran"

    prompt = f"""Sen viral YouTube Shorts, TikTok ve Mini-Belgesel prodüksiyonlarının BAŞ YAPAY ZEKÂ YÖNETMENİ ve senaristisin.
Kullanıcı Talebi / Girdisi: '{topic}'
Çalışma Modu: {'🤖 AI YÖNETMEN MODU (Tüm kararları sen ver)' if is_auto else f'🛠️ MANUEL KULLANICI MODU (Seçilen: Tema: {req.theme}, Şablon: {req.layout_type}, Süre: {req.duration_mode})'}

GÖREV 1: YÖNETMEN KARARI (DIRECTOR DECISION)
Kullanıcının yazdığı metni derinlemesine analiz et. Eğer kullanıcı örtük veya açık bir tema (örn: 'islami', 'karanlık tema', 'felsefe', 'karatahta', 'belgesel', 'hızlı') belirttiyse veya sadece yalın bir konu verdiyse, EN UYGUN ve en viral parametreleri seç:
- 'theme': 'dark_minimalist' | 'gold_luxury' | 'neon_cyber' | 'parchment' | 'notebook' | 'kraft' | 'chalkboard' | 'blueprint'
  (KURAL: 'islami' ve 'karanlık' veya 'derin tefekkür' dendiğinde KESİNLİKLE 'dark_minimalist' veya 'gold_luxury' seç; 'felsefe/tarih' için 'parchment' veya 'kraft'; 'bilim/evren' için 'blueprint' veya 'neon_cyber')
- 'layoutType': 'pip_split' | 'grid_explosion' | 'tri_concept' | 'vs_split' | 'flowchart' | 'quote_spotlight' | 'metric_impact' | 'cards'
  (KURAL: 'görsel / fotoğraf / polaroid / kurgu / sinematik' veya portre odaklı anlatımlarda 'pip_split' seç; 'parmak izi / milyarlarca insan / mühür' için 'grid_explosion'; 3 kavram karşılaştırmasında 'tri_concept'; ayet/vecize için 'quote_spotlight'; karşılaştırma ise 'vs_split')
- 'illustrationPrompt': Konuya uygun İngilizce sanatsal AI görsel üretim promptu (Örn: 'vintage oil painting of Galileo looking through telescope at starry night, dramatic lighting, 8k')
- 'illustrationCaption': Görselin altına el yazısıyla yazılacak kısa Türkçe başlık (Örn: 'Gökyüzünün Sırrı')
- 'brollType': 'none' | 'cosmic' | 'clouds' | 'waves' | 'ink'
- 'durationMode': 'deep' (60-90s, derin anlatım) veya 'quick' (35s, hızlı shorts)
- 'particles': 'dust' (altın tozu) | 'embers' (kıvılcım) | 'fog' | 'stars' | 'none'
- 'ambientPattern': 'fingerprint' | 'islamic_geometric' | 'dna' | 'cosmic' | 'none'
- 'doodleType': 'compass' | 'galaxy' | 'hourglass' | 'book' | 'lightbulb' | 'none'
- 'directorReason': Neden bu tema, şablon ve görsel atmosferin seçildiğinin 1 cümlelik profesyonel Türkçe açıklaması.

GÖREV 2: GEREKLİ ASSET VE İKON LİSTESİ
- 'requiredIcons': ['crescent', 'kaaba', 'fingerprint', 'dna', 'atom', 'brain', 'heart', 'eye', 'scale', 'hourglass', 'book', 'lightbulb', 'compass', 'shield', 'infinity'] arasından veya yeni gereken ikon adları.

GÖREV 3: SENARYO VE VİRAL ŞEMA
- 'strikeWord': Üzeri kırmızı çizgiyle çizilecek çürütülen kelime/iddia (Örn: 'TESADÜF' veya 'YARATMAK' veya '')
- 'narration': Profesyonel, etkileyici Türkçe seslendirme metni.

SADECE SAF GEÇERLİ JSON DÖNDÜR:
{{
  "directorDecision": {{
    "theme": "{req.theme if not is_auto else 'dark_minimalist'}",
    "layoutType": "{req.layout_type if not is_auto else 'grid_explosion'}",
    "durationMode": "{req.duration_mode if not is_auto else 'deep'}",
    "particles": "dust",
    "ambientPattern": "fingerprint",
    "doodleType": "none",
    "directorReason": "İslami tefekkür ve biyolojik mühür vurgusu için karanlık minimal tuval ve 12'li parmak izi ızgarası seçildi."
  }},
  "requiredIcons": ["fingerprint", "dna", "scale"],
  "headerSubtitle": "Akıl Almaz Sır",
  "headerLine1": "PARMAK UCUNDAKİ",
  "circledWord": "BÜYÜK",
  "headerLine2": "SIR",
  "highlightedText": "MİLYARLARCA MÜHÜR",
  "strikeWord": "TESADÜF",
  "layoutType": "{req.layout_type if not is_auto else 'grid_explosion'}",
  "cards": [
    {{"id": "1", "label": "DNA Şifresi", "value": "%100 Aynı", "icon": "dna", "color": "#1e3a8a"}},
    {{"id": "2", "label": "İkizler", "value": "Farklı İz", "icon": "fingerprint", "color": "#15803d"}},
    {{"id": "3", "label": "Tesviye", "value": "1400 Yıl", "icon": "scale", "color": "#d97706"}}
  ],
  "vsData": {{
    "leftTitle": "DNA Benzerliği",
    "leftSubtitle": "Genler Birebir Aynı",
    "leftPoints": ["Aynı genetik kod", "Aynı kan grubu", "Aynı fiziksel yapı"],
    "leftColor": "#dc2626",
    "rightTitle": "Parmak Uçları",
    "rightSubtitle": "Eşsiz Biyolojik Mühür",
    "rightPoints": ["Anne karnında mikro temas", "Asla değişmeyen geometri", "Milyarlarca insanda tek"],
    "rightColor": "#16a34a",
    "verdict": "İkizlerin DNA'sı bile aynıyken, parmak izi her insanı tek ve eşsiz kılar."
  }},
  "flowchartSteps": [
    {{"stepNumber": 1, "badge": "1. Aşama", "title": "Büyük Soru", "desc": "Çürüyüp dağılan kemikler nasıl diriltilecek?", "color": "#1e3a8a"}},
    {{"stepNumber": 2, "badge": "2. Kırılma", "title": "En İnce Detay", "desc": "Kur'an beyne değil, parmak ucunun milimetrik çizgilerine işaret etti.", "color": "#d97706"}},
    {{"stepNumber": 3, "badge": "3. Hakikat", "title": "Tesviye Sırrı", "desc": "19. yüzyılda keşfedilen biometrik imza asırlar önce haber verildi.", "color": "#15803d"}}
  ],
  "quoteSpotlight": {{
    "speaker": "Kıyamet Suresi",
    "title": "4. AYET",
    "quoteText": "Evet, bizim onun parmak uçlarını bile derleyip yeniden düzene koymaya gücümüz yeter.",
    "sourceRef": "Kıyamet Suresi, 3-4"
  }},
  "metricImpact": {{
    "bigNumber": "8 MİLYAR",
    "bigLabel": "İNSAN İÇİNDE",
    "subheading": "Hiçbirinin Parmak İzi Aynı Değil",
    "keyTakeaway": "Çünkü her insan varoluşun altına atılmış özel bir imzadır."
  }},
  "gridExplosion": {{
    "title": "MİLYARLARCA İNSAN",
    "subtitle": "Hiçbirinin Parmak İzi Birbirine Benzemeğecek Şekilde Yaratıldı",
    "iconType": "fingerprint",
    "itemCount": 12,
    "badgeText": "EŞSİZ BİYOLOJİK MÜHÜR"
  }},
  "triConcept": {{
    "badge": "BEKLENEN CEVAP",
    "concept1": {{"title": "BEYİN", "subtitle": "En Karmaşık Hafıza", "icon": "brain", "color": "#38bdf8"}},
    "concept2": {{"title": "KALP", "subtitle": "Yaşam Merkezi", "icon": "heart", "color": "#ef4444"}},
    "concept3": {{"title": "GÖZ", "subtitle": "Hassas Mercek", "icon": "eye", "color": "#facc15"}},
    "bottomNote": "FAKAT KUR'AN PARMAK UCUNA ODAKLANDI"
  }},
  "timeline": {{
    "startYear": "Kıyamet",
    "endYear": "Diriliş",
    "durationLabel": "Tesviye",
    "title": "Kusursuz Dizilim",
    "ayahArabic": "",
    "ayahTranslation": "Evet, bizim onun parmak uçlarını bile derleyip yeniden düzene koymaya gücümüz yeter.",
    "ayahRef": "Kıyamet Suresi, 3-4"
  }},
  "narration": "DNA'sı yüzde yüz aynı olan tek yumurta ikizlerini bile birbirinden ayıran tek bir sır vardır. Çürüyüp toprak olduktan sonra nasıl diriltileceğini soranlara, Kur'an tam da parmak uçlarına işaret ederek cevap verdi. Milyarlarca insanın her biri, parmak ucundaki o eşsiz mühürle yeniden var edilir.",
  "viral": {{
    "hookScore": 99,
    "viralTitles": [
      "Parmak Ucundaki BÜYÜK Sır! Kıyamet Suresi 3-4",
      "İkizlerin Bile Farklı: 1400 Yıl Önceki Akıl Almaz Detay!"
    ],
    "hashtags": ["#bilim", "#kuran", "#parmakizi", "#mucize", "#tefekkür", "#shorts"],
    "loopEnding": "ve işte bu yüzden her insan aslında...",
    "description": "Parmak uçlarındaki dermatoglif şifresi ve Kıyamet Suresi'nin mucizevi detayları."
  }}
}}
"""

    effective_model = req.model or DEFAULT_MODEL
    res, key_name = pool.query_with_rotation(prompt, "You are a specialized JSON video schema generator. Output ONLY raw JSON.", model=effective_model)
    if not res:
        raise HTTPException(status_code=500, detail=f"Key havuzundaki tüm anahtarlar denendi ({effective_model}) ancak yanıt alınamadı.")

    import re
    cleaned = re.sub(r"```json\s*", "", res)
    cleaned = re.sub(r"```\s*", "", cleaned).strip()

    try:
        video_data = json.loads(cleaned)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLM JSON çıktısı ayrıştırılamadı: {str(e)}")

    # 1. AI Director vs Manual Decisions Sync
    director_dec = video_data.get("directorDecision", {})
    topic_lower = topic.lower()

    if is_auto:
        # AI Director selects
        theme = director_dec.get("theme")
        if not theme:
            if "karanlık" in topic_lower or "dark" in topic_lower or "islam" in topic_lower:
                theme = "dark_minimalist"
            elif "felsefe" in topic_lower or "tarih" in topic_lower:
                theme = "parchment"
            else:
                theme = req.theme or "notebook"

        layout_type = director_dec.get("layoutType")
        if not layout_type:
            if any(w in topic_lower for w in ["parmak", "milyar", "mühür"]):
                layout_type = "grid_explosion"
            elif any(w in topic_lower for w in ["beyin", "kalp", "göz", "üç", "3"]):
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
    should_gen_image = req.enable_illustration or (is_auto and (layout_type == "pip_split" or any(w in topic_lower for w in ["resim", "görsel", "fotoğraf", "tablo", "portre"])))
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
        if any(w in topic_lower for w in ["evren", "yıldız", "zaman", "uzay"]) or theme == "neon_cyber":
            broll_choice = "cosmic"
        elif any(w in topic_lower for w in ["deniz", "su", "okyanus"]):
            broll_choice = "waves"
        elif any(w in topic_lower for w in ["tefekkür", "felsefe", "derin"]) or theme == "dark_minimalist":
            broll_choice = "ink"
        elif any(w in topic_lower for w in ["gökyüzü", "hava", "bulut"]):
            broll_choice = "clouds"

    video_data["brollType"] = broll_choice
    video_data["brollOpacity"] = req.broll_opacity or 0.18

    # 2. Adım 2: Asset Manager & Ingestor Pipeline (Varlık Taraması & Otomatik İndirme)
    video_data = process_video_assets(video_data, pool=pool)

    # 3. Adım 3: Studio TTS Audio & Whisper-aligned Subtitles (Faz 7 Multi-TTS)
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
    director_reason = director_dec.get("directorReason") or f"{'Yapay Zekâ Yönetmeni' if is_auto else 'Kullanıcı'} konuya uygun olarak {theme} temasını ve {layout_type} sahne yapısını seçti."
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

def run_remotion_render():
    global render_state
    render_state["status"] = "rendering"
    render_state["message"] = "Remotion motoru videoyu renderlıyor (1080x1920)..."
    try:
        result = subprocess.run(
            ["npm.cmd", "run", "build"],
            cwd=BASE_DIR,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False
        )
        if result.returncode == 0:
            # Also render thumbnail automatically
            subprocess.run(
                ["npx.cmd", "remotion", "still", "src/index.ts", "NotebookVideo", "out/thumbnail.png", "--frame=45"],
                cwd=BASE_DIR,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                check=False
            )
            render_state["status"] = "completed"
            render_state["message"] = "Video ve kapak görseli başarıyla oluşturuldu!"
            t_now = str(int(time.time() * 1000))
            render_state["video_url"] = f"/out/video.mp4?t={t_now}"
            render_state["thumbnail_url"] = f"/out/thumbnail.png?t={t_now}"
            render_state["last_rendered_at"] = time.strftime("%Y-%m-%d %H:%M:%S")
        else:
            render_state["status"] = "error"
            render_state["message"] = f"Render hatası: {result.stderr[:200]}"
    except Exception as e:
        render_state["status"] = "error"
        render_state["message"] = f"Beklenmeyen hata: {str(e)}"

@app.post("/api/render")
def trigger_render(bg_tasks: BackgroundTasks):
    global render_state
    if render_state["status"] == "rendering":
        return {"status": "rendering", "message": "Zaten bir video renderlanıyor, lütfen bekleyin."}
    
    bg_tasks.add_task(run_remotion_render)
    render_state["status"] = "rendering"
    render_state["message"] = "Render işlemi başlatıldı..."
    return {"status": "rendering", "message": "Render işlemi arka planda başlatıldı."}

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
            raise HTTPException(status_code=500, detail=f"Thumbnail oluşturulamadı: {res.stderr[:200]}")
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
# FAZ 4: OTOPİLOT DAĞITIM & YOUTUBE SHORTS API BOTU
# =========================================================================

# 1. YOUTUBE OAUTH & UPLOADER ENDPOINTS
@app.get("/api/youtube/status")
def get_youtube_status():
    return uploader.get_channel_status()

@app.post("/api/youtube/save-credentials")
def save_youtube_credentials(req: YouTubeCredentialsRequest):
    ok = uploader.save_client_secrets(req.client_id, req.client_secret)
    return {"success": ok, "message": "Google Client credentials başarıyla kaydedildi."}

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
        raise HTTPException(status_code=400, detail="Henüz renderlanmış MP4 videosu bulunamadı. Lütfen önce '1080x1920 MP4 Render' butonuna basın.")

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
    caption_content = f"""══════════════════════════════════════════════════
📱 NOTEBOOK AI SHORTS · PAYLAŞIM PAKETİ
══════════════════════════════════════════════════

📌 ÖNERİLEN VİRAL BAŞLIK:
{title_text}

📝 VİDEO AÇIKLAMASI (YouTube / TikTok / Reels):
{viral_info.get('description', gen_data.get('narration', ''))}

🏷️ TREND HASHTAGLER:
{hashtags}

🔄 DÖNGÜ (LOOP) BİTİŞ CÜMLESİ:
{viral_info.get('loopEnding', 've işte bu yüzden...')}

💡 PAYLAŞIM TAVSİYELERİ:
- En yüksek etkileşim saatleri: Hafta içi 18:30 - 21:30
- TikTok ve Reels'ta trend olan bir arka plan sesiyle sesi miksleyin (Orijinal ses %90, Trend ses %10).
- İlk 3 saniyede soru/kanca ekranda vurgulandığı için izleyiciyi hemen tutacaktır.
══════════════════════════════════════════════════
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
        raise HTTPException(status_code=404, detail="Proje verisi (generatedData.json) bulunamadı.")
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
        subtitles = generate_subtitles_fallback(full_text or "Kendi eklediğiniz ses kaydı", duration)

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
        raise HTTPException(status_code=404, detail="Proje verisi bulunamadı.")
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
        raise HTTPException(status_code=404, detail="Proje verisi bulunamadı.")
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
        raise HTTPException(status_code=404, detail="Proje verisi bulunamadı.")
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
        raise HTTPException(status_code=404, detail="Proje verisi bulunamadı.")
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
        raise HTTPException(status_code=404, detail="Proje verisi bulunamadı.")
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
        raise HTTPException(status_code=404, detail="Proje verisi bulunamadı.")
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
        raise HTTPException(status_code=404, detail=f"'{scene_id}' sahnesi bulunamadı.")
        
    with open(data_file, "w", encoding="utf-8") as f:
        json.dump(video_data, f, ensure_ascii=False, indent=2)
    return {"success": True, "scene": target, "video_data": video_data}

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
        raise HTTPException(status_code=404, detail="Görev bulunamadı")
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
    print("🚀 Notebook Video AI Studio Pro 4.0 Titanium")
    print("📍 Web UI: http://localhost:8080")
    print("🔑 Key Havuzu: 136 Anahtar Yüklendi")
    print("=======================================================\n")
    uvicorn.run(app, host="127.0.0.1", port=8080)
