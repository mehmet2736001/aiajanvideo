import os
import sys
import subprocess
import asyncio
import json
import uuid
import requests
from typing import Tuple, List, Dict, Any, Optional

try:
    import edge_tts
except ImportError:
    edge_tts = None

try:
    from gtts import gTTS
except ImportError:
    gTTS = None

try:
    import whisper
except ImportError:
    whisper = None

from scripts.subtitle_cleaner import (
    clean_text_apostrophes,
    stitch_whisper_word_tokens,
    build_subtitle_chunks
)

# Base directories
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
PUBLIC_DIR = os.path.join(BASE_DIR, "public")
SFX_DIR = os.path.join(PUBLIC_DIR, "sfx")

# Available Voices Catalog
VOICE_CATALOG = {
    "edge_tts": [
        {
            "id": "en-US-AndrewMultilingualNeural",
            "name": "Andrew (Tok Belgesel & Anlatıcı)",
            "gender": "male",
            "recommended_tones": ["documentary", "dramatic"]
        },
        {
            "id": "tr-TR-EmelNeural",
            "name": "Emel (Doğal Türkçe Kadın)",
            "gender": "female",
            "recommended_tones": ["calm", "curiosity"]
        },
        {
            "id": "en-US-BrianMultilingualNeural",
            "name": "Brian (Dinamik & Samimi Erkek)",
            "gender": "male",
            "recommended_tones": ["curiosity", "documentary"]
        },
        {
            "id": "en-US-EmmaMultilingualNeural",
            "name": "Emma (Bilgelik & Merak Kadın)",
            "gender": "female",
            "recommended_tones": ["calm", "curiosity"]
        },
        {
            "id": "en-AU-WilliamMultilingualNeural",
            "name": "William (Epik Masal & Hikaye Anlatıcısı)",
            "gender": "male",
            "recommended_tones": ["dramatic", "documentary"]
        }
    ],
    "elevenlabs": [
        {
            "id": "pNInz6obpgDQGcFmaJgB",
            "name": "ElevenLabs: Adam (Derin & Karizmatik)",
            "gender": "male",
            "alias": "adam"
        },
        {
            "id": "ErXwobaYiN019PkySvjV",
            "name": "ElevenLabs: Antoni (Dengeli & Sakin)",
            "gender": "male",
            "alias": "antoni"
        },
        {
            "id": "21m00Tcm4TlvDq8ikWAM",
            "name": "ElevenLabs: Rachel (Sıcak & Anlatıcı Kadın)",
            "gender": "female",
            "alias": "rachel"
        },
        {
            "id": "TxGEqnHWrfWFTfGW9XjX",
            "name": "ElevenLabs: Josh (Yoğun & Genç Erkek)",
            "gender": "male",
            "alias": "josh"
        }
    ],
    "gtts": [
        {
            "id": "gtts_tr",
            "name": "Google Standart TTS (Türkçe)",
            "gender": "neutral"
        }
    ]
}

# Emotion & Tone Master Profiles
TONE_PROFILES = {
    "documentary": {
        "title": "Belgesel Otoritesi (Tok & Derin)",
        "rate": "-2%",
        "pitch": "-2Hz",
        "atempo": 1.04,
        "eq_filter": (
            "equalizer=f=110:width_type=h:width=80:g=4.2,"
            "equalizer=f=2800:width_type=h:width=1200:g=2.2,"
            "compand=attacks=0.02:decays=0.2:points=-60/-60|-24/-12|0/-3:gain=2.8"
        )
    },
    "curiosity": {
        "title": "Merak Uyandırıcı (Hafif Yükselen Tempo)",
        "rate": "+4%",
        "pitch": "+2Hz",
        "atempo": 1.08,
        "eq_filter": (
            "equalizer=f=140:width_type=h:width=100:g=2.5,"
            "equalizer=f=3600:width_type=h:width=1200:g=3.8,"
            "compand=attacks=0.015:decays=0.18:points=-60/-60|-22/-10|0/-2:gain=3.0"
        )
    },
    "dramatic": {
        "title": "Dramatik Kırılma (Ağır & Vurgulu)",
        "rate": "-5%",
        "pitch": "-3Hz",
        "atempo": 1.02,
        "eq_filter": (
            "equalizer=f=95:width_type=h:width=70:g=5.0,"
            "equalizer=f=2500:width_type=h:width=1000:g=2.0,"
            "compand=attacks=0.01:decays=0.25:points=-60/-60|-18/-8|0/-1:gain=3.6"
        )
    },
    "calm": {
        "title": "Huzurlu & Tefekkür (Yumuşak & Dingin)",
        "rate": "-3%",
        "pitch": "+0Hz",
        "atempo": 1.03,
        "eq_filter": (
            "equalizer=f=120:width_type=h:width=90:g=3.0,"
            "equalizer=f=3000:width_type=h:width=1500:g=1.8,"
            "compand=attacks=0.03:decays=0.3:points=-60/-60|-28/-16|0/-4:gain=2.0"
        )
    }
}

# Ambient Background Music Tracks Catalog
MUSIC_CATALOG = [
    {
        "id": "ambient_music.wav",
        "name": "Klasik Defter Düşünce Dronu",
        "description": "Sıcak D majör armoniler ve analog sayfa parıltısı."
    },
    {
        "id": "ambient_documentary.wav",
        "name": "Belgesel & Bilim Nabzı",
        "description": "1 Hz ritmik saat tik-takları ve derin C minör 7 akorları."
    },
    {
        "id": "ambient_epic_cinematic.wav",
        "name": "Epik Sinematik Yükseliş",
        "description": "Derin bas dalgaları ve sinematik yükselen dramatik doku."
    },
    {
        "id": "ambient_mystic.wav",
        "name": "Sufi & Tefekkür Mistisizmi",
        "description": "Ney nefesi fısıltısı ve meditatif D minör tefekkür dronu."
    }
]

# Global Whisper Model Cache
_WHISPER_MODEL = None

def get_whisper_model():
    global _WHISPER_MODEL
    if _WHISPER_MODEL is None and whisper is not None:
        print("[TTS Engine] Loading Whisper base model...")
        _WHISPER_MODEL = whisper.load_model("base")
    return _WHISPER_MODEL


def _run_edge_tts_subprocess(text: str, voice_id: str, tone_info: dict, output_path: str) -> bool:
    """
    Generates neural speech via an isolated edge-tts subprocess with temp file.
    Immune to Windows event-loop concurrency issues inside FastAPI/uvicorn.
    """
    rate = tone_info.get("rate", "+0%")
    pitch = tone_info.get("pitch", "+0Hz")
    temp_text_file = os.path.join(PUBLIC_DIR, f"temp_tts_{uuid.uuid4().hex[:8]}.txt")
    try:
        with open(temp_text_file, "w", encoding="utf-8") as f:
            f.write(text)
        
        cmd = [
            sys.executable, "-m", "edge_tts",
            f"--voice={voice_id}",
            f"--rate={rate}",
            f"--pitch={pitch}",
            f"--file={temp_text_file}",
            f"--write-media={output_path}"
        ]
        res = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=30)
        return res.returncode == 0 and os.path.exists(output_path) and os.path.getsize(output_path) > 1000
    except Exception as e:
        print(f"[TTS Engine] Subprocess edge-tts error: {e}")
        return False
    finally:
        if os.path.exists(temp_text_file):
            try:
                os.remove(temp_text_file)
            except Exception:
                pass


def _run_elevenlabs_tts(text: str, voice_id: str, api_key: str, output_path: str) -> bool:
    """Generates ultra-realistic speech using ElevenLabs API v1."""
    if not api_key:
        return False
    
    # Resolve aliases if short name provided
    alias_map = {
        "adam": "pNInz6obpgDQGcFmaJgB",
        "antoni": "ErXwobaYiN019PkySvjV",
        "rachel": "21m00Tcm4TlvDq8ikWAM",
        "josh": "TxGEqnHWrfWFTfGW9XjX"
    }
    actual_voice_id = alias_map.get(voice_id.lower(), voice_id)

    url = f"https://api.elevenlabs.io/v1/text-to-speech/{actual_voice_id}"
    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": api_key
    }
    data = {
        "text": text,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {
            "stability": 0.55,
            "similarity_boost": 0.75,
            "style": 0.15,
            "use_speaker_boost": True
        }
    }
    try:
        print(f"[TTS Engine] Requesting ElevenLabs audio (voice: {actual_voice_id})...")
        resp = requests.post(url, json=data, headers=headers, timeout=25)
        if resp.status_code == 200 and len(resp.content) > 1000:
            with open(output_path, "wb") as f:
                f.write(resp.content)
            print(f"[TTS Engine] ElevenLabs generation successful ({len(resp.content)} bytes).")
            return True
        else:
            print(f"[TTS Engine] ElevenLabs error {resp.status_code}: {resp.text}")
    except Exception as e:
        print(f"[TTS Engine] ElevenLabs request failed: {e}")
    return False


def _run_gtts(text: str, lang: str, output_path: str) -> bool:
    """Fallback to Google TTS."""
    if not gTTS:
        return False
    try:
        tts = gTTS(text=text, lang=lang or "tr")
        tts.save(output_path)
        return os.path.exists(output_path) and os.path.getsize(output_path) > 500
    except Exception as e:
        print(f"[TTS Engine] gTTS error: {e}")
    return False


def synthesize_narration(
    text: str,
    provider: str = "edge_tts",
    voice_id: str = "en-US-AndrewMultilingualNeural",
    emotion_tone: str = "documentary",
    elevenlabs_api_key: Optional[str] = None,
    output_raw_path: Optional[str] = None
) -> Tuple[bool, str]:
    """
    Synthesizes raw audio using the chosen provider and emotion profile.
    Automatically falls back if primary provider fails.
    """
    if not output_raw_path:
        output_raw_path = os.path.join(PUBLIC_DIR, "audio_raw.mp3")

    tone_info = TONE_PROFILES.get(emotion_tone, TONE_PROFILES["documentary"])
    success = False
    chosen_provider = provider

    # 1. ElevenLabs Provider
    if provider == "elevenlabs":
        key = elevenlabs_api_key or os.environ.get("ELEVENLABS_API_KEY", "")
        if key:
            success = _run_elevenlabs_tts(text, voice_id, key, output_raw_path)
        if not success:
            print("[TTS Engine] Falling back from ElevenLabs to Edge-TTS...")
            chosen_provider = "edge_tts"
            voice_id = "en-US-AndrewMultilingualNeural"

    # 2. Edge-TTS Provider
    if chosen_provider == "edge_tts":
        success = _run_edge_tts_subprocess(text, voice_id, tone_info, output_raw_path)

    # 3. Fallback to gTTS if still failed
    if not success:
        print("[TTS Engine] Falling back to gTTS...")
        success = _run_gtts(text, "tr", output_raw_path)

    return success, output_raw_path


def master_studio_audio(
    raw_path: str,
    studio_path: str,
    emotion_tone: str = "documentary"
) -> bool:
    """
    Applies FFmpeg warm studio mastering:
    EQ curves, vocal air, dynamic compand, and natural tempo matching the emotion profile.
    """
    tone_info = TONE_PROFILES.get(emotion_tone, TONE_PROFILES["documentary"])
    eq_filter = tone_info.get("eq_filter")
    atempo = tone_info.get("atempo", 1.05)
    filterchain = f"{eq_filter},atempo={atempo}"

    cmd = [
        "ffmpeg", "-y",
        "-i", raw_path,
        "-af", filterchain,
        "-ar", "44100",
        "-b:a", "192k",
        studio_path
    ]
    try:
        res = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=20)
        return res.returncode == 0 and os.path.exists(studio_path) and os.path.getsize(studio_path) > 1000
    except Exception as e:
        print(f"[TTS Engine] Audio mastering FFmpeg error: {e}")
        # If FFmpeg fails, simply copy raw to studio
        try:
            import shutil
            shutil.copy2(raw_path, studio_path)
            return True
        except Exception:
            return False


def align_subtitles_whisper(audio_path: str, lang: str = "tr") -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Runs Whisper AI for millisecond word-level timestamps.
    Returns:
      (subtitles, words)
      - subtitles: 3-word punchy sentence chunks with exact start/end in seconds.
      - words: array of every single word with start/end in seconds.
    """
    subtitles = []
    words_list = []

    model = get_whisper_model()
    if model is None:
        return subtitles, words_list

    try:
        result = model.transcribe(
            audio_path,
            word_timestamps=True,
            language=lang or "tr",
            fp16=False
        )

        raw_words = []
        for segment in result.get("segments", []):
            for w in segment.get("words", []):
                cleaned_word = w.get("word", "").strip()
                if cleaned_word:
                    raw_words.append({
                        "word": cleaned_word,
                        "text": cleaned_word,
                        "start": round(w.get("start", 0.0), 2),
                        "end": round(w.get("end", 0.0), 2)
                    })

        # Intelligent stitching for words like Kur'an, Allah'ın etc.
        words_list = stitch_whisper_word_tokens(raw_words)

        # Build chunks with stitched words
        subtitles = build_subtitle_chunks(words_list, chunk_size=3)

    except Exception as e:
        print(f"[TTS Engine] Whisper alignment error: {e}")

    return subtitles, words_list


def generate_full_narration_pipeline(
    narration_text: str,
    provider: str = "edge_tts",
    voice_id: str = "en-US-AndrewMultilingualNeural",
    emotion_tone: str = "documentary",
    elevenlabs_api_key: Optional[str] = None,
    lang: str = "tr",
    output_studio_path: Optional[str] = None
) -> Dict[str, Any]:
    """
    Full end-to-end voiceover generation:
    1. Speech synthesis (Edge-TTS / ElevenLabs / gTTS)
    2. Emotion-based mastering EQ & dynamics
    3. Whisper AI millisecond word alignment
    4. Subtitles chunks & words array
    """
    if output_studio_path:
        studio_path = output_studio_path
        raw_path = output_studio_path.replace(".mp3", "_raw.mp3")
    else:
        raw_path = os.path.join(PUBLIC_DIR, "audio_raw.mp3")
        studio_path = os.path.join(PUBLIC_DIR, "audio.mp3")

    rel_audio_url = os.path.relpath(studio_path, PUBLIC_DIR).replace("\\", "/")

    print(f"[TTS Engine] Synthesizing speech: provider={provider}, voice={voice_id}, tone={emotion_tone}...")
    success, _ = synthesize_narration(
        text=narration_text,
        provider=provider,
        voice_id=voice_id,
        emotion_tone=emotion_tone,
        elevenlabs_api_key=elevenlabs_api_key,
        output_raw_path=raw_path
    )

    if not success:
        raise RuntimeError("Failed to synthesize audio through any TTS provider.")

    print(f"[TTS Engine] Mastering audio with tone profile: {emotion_tone}...")
    master_studio_audio(raw_path, studio_path, emotion_tone)

    print(f"[TTS Engine] Running Whisper millisecond alignment (lang={lang})...")
    subtitles, words = align_subtitles_whisper(studio_path, lang=lang)

    total_dur = 0.0
    if subtitles:
        total_dur = subtitles[-1].get("end", 0.0)
    elif words:
        total_dur = words[-1].get("end", 0.0)

    return {
        "audioUrl": rel_audio_url,
        "subtitles": subtitles,
        "words": words,
        "totalDuration": total_dur,
        "provider": provider,
        "voiceId": voice_id,
        "emotionTone": emotion_tone
    }
