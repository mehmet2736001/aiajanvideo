import os
import sys
import json
import asyncio
import subprocess
from faster_whisper import WhisperModel
import edge_tts

VOICE_DEFAULT = "tr-TR-AhmetNeural"

def synthesize_and_align(
    lines: list,
    output_dir: str,
    voice: str = VOICE_DEFAULT,
    pauses: list = None
) -> dict:
    """
    1. Her satırı Edge-TTS ile vakur tonlama ve nefes duraklarıyla seslendirir.
    2. FFmpeg ile 44.1kHz stüdyo mastering uygular (EQ + compand + loudnorm).
    3. faster-whisper ile milisaniyelik kelime zamanlamasını (kelimeler.json) çıkarır.
    """
    os.makedirs(output_dir, exist_ok=True)
    temp_dir = os.path.join(output_dir, "temp_voice")
    os.makedirs(temp_dir, exist_ok=True)

    if not pauses or len(pauses) != len(lines):
        pauses = [0.45] * len(lines)
        if len(pauses) > 3:
            pauses[3] = 0.75  # Ortada dönüş es'i
        if len(pauses) > 0:
            pauses[-1] = 1.20 # Kapanış dinginlik payı

    # 1. Satır satır ses üret
    async def _synth():
        for i, text in enumerate(lines):
            line_out = os.path.join(temp_dir, f"line_{i}.mp3")
            comm = edge_tts.Communicate(text, voice, rate="-4%", pitch="-1Hz")
            await comm.save(line_out)

    asyncio.run(_synth())

    # 2. faster-whisper ile kelime senkronu çıkar
    model = WhisperModel("base", device="cpu", compute_type="int8")
    all_words = []
    current_offset = 0.0
    concat_lines = []

    for i, raw_text in enumerate(lines):
        line_f = os.path.join(temp_dir, f"line_{i}.mp3")
        std_line_f = os.path.join(temp_dir, f"std_line_{i}.wav")
        silence_f = os.path.join(temp_dir, f"silence_{i}.wav")
        p_dur = pauses[i]

        # Convert line to wav 44100Hz stereo
        subprocess.run(
            ["ffmpeg", "-y", "-i", line_f, "-ar", "44100", "-ac", "2", std_line_f],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True
        )

        # Generate silence wav
        subprocess.run(
            ["ffmpeg", "-y", "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo", "-t", str(p_dur), silence_f],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True
        )

        # Get line duration
        dur_cmd = ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", std_line_f]
        dur = float(subprocess.run(dur_cmd, stdout=subprocess.PIPE, text=True, check=True).stdout.strip())

        # Whisper align
        segs, _ = model.transcribe(std_line_f, language="tr", word_timestamps=True)
        w_list = []
        for s in segs:
            for w in s.words:
                clean_w = w.word.strip()
                if clean_w:
                    w_list.append({
                        "w": clean_w,
                        "s": round(current_offset + w.start, 3),
                        "e": round(current_offset + w.end, 3),
                        "c": i
                    })

        # Always match the exact script words proportionally across the spoken segment
        raw_words = raw_text.split()
        if len(w_list) > 0 and len(raw_words) > 0:
            start_t = w_list[0]["s"]
            end_t = w_list[-1]["e"]
            step = (end_t - start_t) / len(raw_words)
            matched_words = []
            for k, rw in enumerate(raw_words):
                matched_words.append({
                    "w": rw,
                    "s": round(start_t + k * step, 3),
                    "e": round(start_t + (k + 1) * step, 3),
                    "c": i
                })
            w_list = matched_words

        all_words.extend(w_list)
        abs_std = os.path.abspath(std_line_f).replace("\\", "/")
        abs_sil = os.path.abspath(silence_f).replace("\\", "/")
        concat_lines.append(f"file '{abs_std}'")
        concat_lines.append(f"file '{abs_sil}'")
        current_offset += dur + p_dur

    # 3. Concatenate and apply studio mastering
    concat_txt = os.path.join(temp_dir, "concat.txt")
    with open(concat_txt, "w", encoding="utf-8") as f:
        f.write("\n".join(concat_lines))

    final_audio = os.path.join(output_dir, "ses.mp3")
    af = (
        "equalizer=f=120:width_type=h:width=100:g=2.5,"
        "equalizer=f=3200:width_type=h:width=1200:g=1.8,"
        "compand=attacks=0.02:decays=0.2:points=-60/-60|-24/-12|0/-3:gain=2.0,"
        "loudnorm=I=-16:TP=-1.5:LRA=11"
    )

    cmd_c = [
        "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", concat_txt,
        "-af", af, "-c:a", "libmp3lame", "-b:a", "192k", final_audio
    ]
    subprocess.run(cmd_c, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

    dur_cmd = ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", final_audio]
    total_dur = float(subprocess.run(dur_cmd, stdout=subprocess.PIPE, text=True, check=True).stdout.strip())

    kelimeler_file = os.path.join(output_dir, "kelimeler.json")
    with open(kelimeler_file, "w", encoding="utf-8") as f:
        json.dump(all_words, f, ensure_ascii=False, indent=2)

    return {
        "audio_path": final_audio,
        "kelimeler_path": kelimeler_file,
        "duration_seconds": total_dur,
        "word_count": len(all_words)
    }
