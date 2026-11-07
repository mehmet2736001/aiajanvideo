import asyncio
import concurrent.futures
import json
import os
import subprocess
from typing import Dict, List, Optional

VOICE_MALE = "tr-TR-AhmetNeural"
VOICE_FEMALE = "tr-TR-EmelNeural"
VOICE_DEFAULT = VOICE_MALE

_WHISPER_MODEL = None


# --------------------------------------------------------------------------
# Saf (bağımlılıksız) yardımcılar — test edilebilir
# --------------------------------------------------------------------------
def pick_voice(turso_meta: Optional[dict], default: str = VOICE_DEFAULT) -> str:
    """Turso ses kaydındaki cinsiyete göre edge-tts sesini seçer.

    edge-tts'te Türkçe için yalnızca iki ses (Ahmet/Emel) vardır; Turso'daki
    kayıtlar ses *karakterini* değil yalnızca cinsiyet seçimini etkiler.
    """
    if turso_meta and str(turso_meta.get("gender", "")).lower() == "female":
        return VOICE_FEMALE
    return default


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
    """Metindeki kelimeleri Whisper'ın gerçek zaman damgalarına oturtur.

    Whisper kelime sayısı metinle birebir tutmasa bile, karakter uzunluğuna göre
    piecewise-lineer bir eşleme yapılır; böylece gerçek duraklamalar korunur
    (eşit aralığa bölmek yerine).
    """
    if not script_words:
        return []

    def make(k: int, s: float, e: float) -> Dict:
        return {"w": script_words[k], "s": round(offset + s, 3), "e": round(offset + e, 3), "c": line_idx}

    ww = [w for w in whisper_words if w.get("e", 0) > w.get("s", 0)]
    if not ww:
        # Whisper hiçbir şey bulamadı: karakter ağırlıklı eşit dağılım
        total = sum(len(w) for w in script_words) or 1
        out, pos = [], 0.0
        for k, w in enumerate(script_words):
            s = line_duration * pos / total
            pos += len(w)
            out.append(make(k, s, line_duration * pos / total))
        return out

    # Whisper tarafında kümülatif karakter ekseni
    anchors = []  # (char_start, char_end, t_start, t_end)
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


# --------------------------------------------------------------------------
# FFmpeg / ffprobe
# --------------------------------------------------------------------------
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
        from faster_whisper import WhisperModel  # tembel import
        _WHISPER_MODEL = WhisperModel("base", device="cpu", compute_type="int8")
    return _WHISPER_MODEL


async def _synth_all(lines: List[str], temp_dir: str, voice: str) -> None:
    import edge_tts  # tembel import
    sem = asyncio.Semaphore(3)

    async def one(i: int, text: str):
        async with sem:
            out = os.path.join(temp_dir, f"line_{i}.mp3")
            await edge_tts.Communicate(text, voice, rate="-4%", pitch="-1Hz").save(out)

    await asyncio.gather(*(one(i, t) for i, t in enumerate(lines)))


def _run_async(coro_factory):
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(coro_factory())
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as ex:
        return ex.submit(lambda: asyncio.run(coro_factory())).result()


# --------------------------------------------------------------------------
# Ana akış
# --------------------------------------------------------------------------
MASTER_FILTER = (
    "equalizer=f=120:width_type=h:width=100:g=2.5,"
    "equalizer=f=3200:width_type=h:width=1200:g=1.8,"
    "compand=attacks=0.02:decays=0.2:points=-60/-60|-24/-12|0/-3:gain=2.0,"
    "loudnorm=I=-16:TP=-1.5:LRA=11"
)


def synthesize_and_align(
    lines: list,
    output_dir: str,
    voice: str = VOICE_DEFAULT,
    pauses: Optional[list] = None,
    voice_id: Optional[str] = None,
) -> dict:
    """
    1. (Varsa) Turso'dan ses kaydını çekip cinsiyete göre edge-tts sesini seçer.
    2. Her satırı edge-tts ile seslendirir.
    3. faster-whisper ile gerçek kelime zamanlarını çıkarıp metin kelimelerine oturtur.
    4. FFmpeg ile satırları birleştirir ve stüdyo mastering uygular (EQ + compand + loudnorm -16 LUFS).
    """
    lines = [l.strip() for l in lines if l and l.strip()]
    if not lines:
        raise ValueError("Seslendirilecek en az bir satır gerekli.")

    os.makedirs(output_dir, exist_ok=True)
    temp_dir = os.path.join(output_dir, "temp_voice")
    os.makedirs(temp_dir, exist_ok=True)

    turso_meta = None
    if voice_id:
        try:
            from core.turso_client import TursoVoiceClient
            turso_meta = TursoVoiceClient().get_voice(voice_id)
            if turso_meta:
                print(f"   ✓ Turso sesi yüklendi: {turso_meta.get('turkish_title') or voice_id}")
        except Exception as e:  # ağ yoksa üretim yine de sürsün
            print(f"   ⚠️ Turso ses bilgisi alınamadı, varsayılan ses kullanılacak: {e}")
    voice = pick_voice(turso_meta, voice)

    if not pauses or len(pauses) != len(lines):
        pauses = default_pauses(len(lines))

    _run_async(lambda: _synth_all(lines, temp_dir, voice))

    model = _get_whisper()
    all_words: List[Dict] = []
    offset = 0.0
    concat_lines = []

    for i, raw_text in enumerate(lines):
        line_f = os.path.join(temp_dir, f"line_{i}.mp3")
        std_f = os.path.join(temp_dir, f"std_line_{i}.wav")
        sil_f = os.path.join(temp_dir, f"silence_{i}.wav")
        p_dur = pauses[i]

        _run(["ffmpeg", "-y", "-i", line_f, "-ar", "44100", "-ac", "2", std_f])
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

    final_audio = os.path.join(output_dir, "ses.mp3")
    _run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", concat_txt,
          "-af", MASTER_FILTER, "-c:a", "libmp3lame", "-b:a", "192k", final_audio])
    total_dur = _duration(final_audio)

    kelimeler_file = os.path.join(output_dir, "kelimeler.json")
    with open(kelimeler_file, "w", encoding="utf-8") as f:
        json.dump(all_words, f, ensure_ascii=False, indent=2)

    return {
        "audio_path": final_audio,
        "kelimeler_path": kelimeler_file,
        "duration_seconds": total_dur,
        "word_count": len(all_words),
        "voice": voice,
    }
