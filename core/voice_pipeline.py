import re
import asyncio
import concurrent.futures
import json
import os
import subprocess
import threading
import time
from typing import Dict, List, Optional

from core.utils import BASE_DIR, read_json

VOICE_MALE = "Charon"
VOICE_FEMALE = "Aoede"
VOICE_DEFAULT = "Charon"

_WHISPER_MODEL = None
_KEYS_FILE = os.path.join(BASE_DIR, "api_keys.json")

# --------------------------------------------------------------------------
# Gemini TTS Key Manager & Engine
# --------------------------------------------------------------------------
class GeminiKeyPool:
    def __init__(self):
        self.lock = threading.Lock()
        self.keys = []
        self.current_idx = 2
        self._load_keys()

    def _load_keys(self):
        try:
            if os.path.exists(_KEYS_FILE):
                data = read_json(_KEYS_FILE, {})
                self.keys = data.get("keys", [])
        except Exception:
            self.keys = []

    def get_client(self):
        with self.lock:
            if not self.keys:
                self._load_keys()
            if not self.keys:
                raise RuntimeError("api_keys.json içinde geçerli bir Gemini API anahtarı bulunamadı!")
            key = self.keys[self.current_idx % len(self.keys)]
            # Her istekte otomatik olarak bir sonraki anahtara geç (Round-Robin)
            self.current_idx = (self.current_idx + 1) % len(self.keys)
            from google import genai
            from google.genai import types
            return genai.Client(
                api_key=key,
                http_options=types.HttpOptions(
                    timeout=60000,
                    retry_options=types.HttpRetryOptions(attempts=1)
                )
            )

    def rotate(self):
        with self.lock:
            if self.keys:
                self.current_idx = (self.current_idx + 1) % len(self.keys)


_KEY_POOL = GeminiKeyPool()


def pick_voice(turso_meta: Optional[dict], default: str = VOICE_DEFAULT) -> str:
    """Turso ses kaydındaki API ses adını (Charon, Puck, Schedar, Aoede...) seçer."""
    if not turso_meta:
        return default
    if turso_meta.get("api_voice_name"):
        return turso_meta["api_voice_name"]
    gender = str(turso_meta.get("cinsiyet") or turso_meta.get("gender") or "").lower()
    if any(k in gender for k in ["female", "kadın", "kız", "anne", "nine"]):
        return "Aoede" if "Neural" not in default else VOICE_FEMALE
    return "Charon" if "Neural" not in default else VOICE_MALE


def default_pauses(count: int) -> List[float]:
    pauses = [0.45] * count
    if count > 3:
        pauses[3] = 0.75  # ortada dönüş es'i
    if count > 0:
        pauses[-1] = 1.20  # kapanış dinginlik payı
    return pauses


def align_script_to_whisper(
    script_words: List[str],
    whisper_words: List[Dict],
    line_duration: float,
    offset: float,
    line_idx: int,
) -> List[Dict]:
    """Metindeki kelimeleri Whisper'ın gerçek zaman damgalarına oturtur."""
    if not script_words:
        return []

    def make(k: int, s: float, e: float) -> Dict:
        return {"w": script_words[k], "s": round(offset + s, 3), "e": round(offset + e, 3), "c": line_idx}

    ww = [w for w in whisper_words if w.get("e", 0) > w.get("s", 0)]
    if not ww:
        total = sum(len(w) for w in script_words) or 1
        out, pos = [], 0.0
        for k, w in enumerate(script_words):
            s = line_duration * pos / total
            pos += len(w)
            out.append(make(k, s, line_duration * pos / total))
        return out

    anchors = []
    pos = 0
    for w in ww:
        n = max(1, len(w["w"].strip()))
        anchors.append((pos, pos + n, w["s"], w["e"]))
        pos += n
    whisper_total = pos
    script_total = sum(len(w) for w in script_words) or 1

    def time_at(x: float, side: str) -> float:
        for cs, ce, ts, te in anchors:
            inside = cs <= x < ce if side == "start" else cs < x <= ce
            if inside:
                return ts + (x - cs) / (ce - cs) * (te - ts)
        return anchors[0][2] if side == "start" else anchors[-1][3]

    out, cpos = [], 0
    for k, w in enumerate(script_words):
        a = cpos / script_total * whisper_total
        cpos += len(w)
        b = cpos / script_total * whisper_total
        s = time_at(a, "start")
        e = max(time_at(b, "end"), s + 0.05)
        out.append(make(k, s, e))
    return out


def _concat_quote(path: str) -> str:
    return path.replace("\\", "/").replace("'", "'\\''")


def _run(cmd: List[str]) -> None:
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, check=True)


def _duration(path: str) -> float:
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", path],
        stdout=subprocess.PIPE, text=True, check=True,
    ).stdout.strip()
    return float(out)


def _get_whisper():
    global _WHISPER_MODEL
    if _WHISPER_MODEL is None:
        from faster_whisper import WhisperModel
        _WHISPER_MODEL = WhisperModel("base", device="cpu", compute_type="int8")
    return _WHISPER_MODEL


def clean_for_speech(text: str) -> str:
    """Metni saf konuşma metnine dönüştürür; sahne etiketleri ve sembolleri ayıklar."""
    if not text:
        return ""
    t = re.sub(r'^(?:(?:\d+[\.\)]| Sahne\s*\d+:?| Kanca:?| Giriş:?| Bölüm\s*\d+:?)\s*)+', '', text, flags=re.IGNORECASE)
    t = re.sub(r'\[.*?\]|\(.*?\)', '', t)
    t = re.sub(r'[*_#`~]', '', t)
    t = re.sub(r'[^a-zA-Z0-9çğıöşüÇĞİÖŞÜ\s\.,;:!\?\'"«»—–-]', '', t)
    t = re.sub(r'\s+', ' ', t).strip()
    return t


def synthesize_line_gemini(text: str, voice_name: str, max_retries: int = 10) -> Optional[bytes]:
    """
    Google Gemini 3.8 Flash TTS (gemini-3.8-flash-tts) API üzerinden
    saf stüdyo kalitesinde WAV ses verisi üretir.
    """
    import base64

    VALID_VOICES = {
        "Zephyr", "Puck", "Charon", "Kore", "Fenrir", "Leda", "Orus", "Aoede",
        "Callirrhoe", "Autonoe", "Enceladus", "Iapetus", "Umbriel", "Algieba",
        "Despina", "Erinome", "Algenib", "Rasalgethi", "Laomedeia", "Achernar",
        "Alnilam", "Schedar", "Gacrux", "Pulcherrima", "Achird", "Zubenelgenubi",
        "Vindemiatrix", "Sadachbia", "Sadaltager", "Sulafat"
    }

    core_voice = voice_name if voice_name in VALID_VOICES else "Charon"

    for attempt in range(max_retries):
        try:
            client = _KEY_POOL.get_client()
            v_to_use = core_voice if attempt < 4 else ("Aoede" if core_voice in ["Kore", "Leda", "Callirrhoe", "Autonoe", "Despina", "Erinome"] else "Charon")
            
            interaction = client.interactions.create(
                model="gemini-3.8-flash-tts",
                input=[{
                    "type": "user_input",
                    "content": [{
                        "type": "text",
                        "text": text,
                    }],
                }],
                response_format={"type": "audio"},
                generation_config={
                    "speech_config": [
                        {"voice": v_to_use},
                    ]
                },
            )
            if interaction.output_audio and interaction.output_audio.data:
                return base64.b64decode(interaction.output_audio.data)
            _KEY_POOL.rotate()
        except Exception as e:
            print(f"      [Gemini TTS Retry {attempt+1}/{max_retries}] ({core_voice}): {e}")
            _KEY_POOL.rotate()
            time.sleep(0.3)

    return None


def synthesize_and_align(
    lines: list,
    output_dir: str,
    voice: str = VOICE_DEFAULT,
    pauses: Optional[list] = None,
    voice_id: Optional[str] = None,
) -> dict:
    """
    VoxAtelier v3.0 & Google Gemini TTS ile metni gerçek seçilen sesle seslendirir.
    1. Turso veritabanından veya user_settings'ten seçili ses profilini yükler.
    2. Google Gemini TTS (gemini-3.8-flash-tts) ile Charon, Puck, Schedar, Enceladus vb. seslendirir.
    3. faster-whisper ile hassas Türkçe kelime zamanlamasını çıkarır.
    4. VoxAtelier DSP parametreleri (Hz perde kaydırma, 3-bant EQ, stüdyo kompresör, -16 LUFS) uygular.
    """
    raw_lines = [l.strip() for l in lines if l and l.strip()]
    lines = []
    for l in raw_lines:
        c = clean_for_speech(l)
        if c and any(ch.isalnum() for ch in c):
            lines.append(c)
    if not lines:
        lines = ["Tefekkür ve hikmet üzerine derin bir yolculuk."]

    os.makedirs(output_dir, exist_ok=True)
    temp_dir = os.path.join(output_dir, "temp_voice")
    os.makedirs(temp_dir, exist_ok=True)

    turso_meta = None
    if voice_id:
        try:
            from core.turso_client import TursoVoiceClient
            turso_meta = TursoVoiceClient().get_voice(voice_id)
        except Exception as e:
            print(f"   ⚠️ Turso ses bilgisi alınamadı: {e}")

    # Ses kimliği tespiti
    if turso_meta:
        ses_num = str(turso_meta.get("ses_id") or "").zfill(4)
        disp_name = turso_meta.get("display_name") or voice_id
        api_voice = turso_meta.get("api_voice_name") or "Charon"
        cinsiyet = turso_meta.get("cinsiyet") or "Erkek"
        unvan = turso_meta.get("unvan") or turso_meta.get("turkish_title") or disp_name
        print(f"   🎙️ [VoxAtelier TTS] Gerçek Ses Devrede: #{ses_num} '{disp_name}' ({api_voice} · {cinsiyet})")
    else:
        api_voice = voice if voice and voice != VOICE_MALE else "Charon"
        disp_name = voice_id or api_voice
        cinsiyet = "Erkek"
        print(f"   🎙️ [Gemini TTS] Ses: {api_voice}")

    # VoxAtelier v3.0 DSP EQ & Perde Filtre Zinciri
    try:
        p_ratio = float(turso_meta.get("pitch_ratio") or 1.0) if turso_meta else 1.0
    except Exception:
        p_ratio = 1.0

    low = (turso_meta.get("ffmpeg_equalizer_low") if turso_meta else None) or "equalizer=f=160:t=q:w=1:g=1.0"
    mid = (turso_meta.get("ffmpeg_equalizer_mid") if turso_meta else None) or "equalizer=f=2800:t=q:w=1:g=1.5"
    high = (turso_meta.get("ffmpeg_equalizer_high") if turso_meta else None) or "equalizer=f=9000:t=q:w=1:g=1.0"
    comp = (turso_meta.get("ffmpeg_compressor") if turso_meta else None) or "acompressor=threshold=-18dB:ratio=2.5:attack=20:release=250"

    if abs(p_ratio - 1.0) > 0.01:
        sr = 44100
        new_sr = int(round(sr * p_ratio))
        tempo_comp = round(1.0 / p_ratio, 4)
        dsp_pitch = f"asetrate={new_sr},aresample={sr},atempo={tempo_comp}"
        master_filter = f"{dsp_pitch},{low},{mid},{high},{comp},loudnorm=I=-16:TP=-1.5:LRA=11"
    else:
        master_filter = f"{low},{mid},{high},{comp},loudnorm=I=-16:TP=-1.5:LRA=11"

    if not pauses or len(pauses) != len(lines):
        pauses = default_pauses(len(lines))

    # Adım 1: Satırları Gemini 3.8 Flash TTS ile seslendir (WAV çıktısı)
    for i, line_text in enumerate(lines):
        std_f = os.path.join(temp_dir, f"std_line_{i}.wav")
        print(f"   🎙️ Satır {i+1}/{len(lines)} seslendiriliyor ({api_voice}): «{line_text[:40]}...»")
        wav_data = synthesize_line_gemini(line_text, api_voice)

        if wav_data:
            raw_wav = os.path.join(temp_dir, f"line_{i}_raw.wav")
            with open(raw_wav, "wb") as wf:
                wf.write(wav_data)
            _run([
                "ffmpeg", "-y", "-i", raw_wav, "-ar", "44100", "-ac", "2", std_f
            ])
            if os.path.exists(raw_wav):
                os.remove(raw_wav)
            print(f"   ✓ Satır {i+1} hazır ({len(wav_data)} bayt WAV)")
        else:
            raise RuntimeError(f"Gemini TTS satır {i+1} seslendirmesini tamamlayamadı! Windows sesi engellendi.")

    # Adım 2: faster-whisper ile kelime hizalama
    model = _get_whisper()
    all_words: List[Dict] = []
    offset = 0.0
    concat_lines = []

    for i, raw_text in enumerate(lines):
        std_f = os.path.join(temp_dir, f"std_line_{i}.wav")
        sil_f = os.path.join(temp_dir, f"silence_{i}.wav")
        p_dur = pauses[i]

        _run(["ffmpeg", "-y", "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo", "-t", str(p_dur), sil_f])
        dur = _duration(std_f)

        segs, _ = model.transcribe(std_f, language="tr", word_timestamps=True)
        w_list = []
        for s in segs:
            for w in (s.words or []):
                cw = w.word.strip()
                if cw:
                    w_list.append({"w": cw, "s": w.start, "e": w.end})

        all_words.extend(align_script_to_whisper(raw_text.split(), w_list, dur, offset, i))

        concat_lines.append(f"file '{_concat_quote(os.path.abspath(std_f))}'")
        concat_lines.append(f"file '{_concat_quote(os.path.abspath(sil_f))}'")
        offset += dur + p_dur

    concat_txt = os.path.join(temp_dir, "concat.txt")
    with open(concat_txt, "w", encoding="utf-8") as f:
        f.write("\n".join(concat_lines))

    # Adım 3: FFmpeg ile birleştir ve stüdyo mastering uygula
    final_audio = os.path.join(output_dir, "ses.mp3")
    _run([
        "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", concat_txt,
        "-af", master_filter, "-c:a", "libmp3lame", "-b:a", "192k", final_audio
    ])
    total_dur = _duration(final_audio)

    kelimeler_file = os.path.join(output_dir, "kelimeler.json")
    with open(kelimeler_file, "w", encoding="utf-8") as f:
        json.dump(all_words, f, ensure_ascii=False, indent=2)

    return {
        "audio_path": final_audio,
        "kelimeler_path": kelimeler_file,
        "duration_seconds": total_dur,
        "word_count": len(all_words),
        "voice": disp_name,
        "api_voice": api_voice,
    }
