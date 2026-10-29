import os
import re
import json
import subprocess
import shutil
from typing import Dict, Any, List, Tuple

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
PUBLIC_DIR = os.path.join(BASE_DIR, "public")
SRC_DIR = os.path.join(BASE_DIR, "src")
GENERATED_DATA_FILE = os.path.join(SRC_DIR, "generatedData.json")


def detect_silences(
    audio_path: str,
    min_duration: float = 0.35,
    noise_threshold: str = "-30dB"
) -> List[Tuple[float, float, float]]:
    """
    Runs FFmpeg silencedetect to identify dead air intervals longer than min_duration.
    Returns list of (start_time, end_time, duration).
    """
    if not os.path.exists(audio_path):
        raise FileNotFoundError(f"Ses dosyası bulunamadı: {audio_path}")

    cmd = [
        "ffmpeg", "-y",
        "-i", audio_path,
        "-af", f"silencedetect=noise={noise_threshold}:d={min_duration}",
        "-f", "null", "-"
    ]
    res = subprocess.run(cmd, stderr=subprocess.PIPE, stdout=subprocess.DEVNULL, text=True)
    stderr = res.stderr

    starts = [float(x) for x in re.findall(r"silence_start:\s*(\d+\.?\d*)", stderr)]
    ends_dur = re.findall(r"silence_end:\s*(\d+\.?\d*)\s*\|\s*silence_duration:\s*(\d+\.?\d*)", stderr)

    silences: List[Tuple[float, float, float]] = []
    for s, (e_str, d_str) in zip(starts, ends_dur):
        e = float(e_str)
        d = float(d_str)
        if d >= min_duration:
            silences.append((round(s, 3), round(e, 3), round(d, 3)))

    return silences


def get_audio_duration(audio_path: str) -> float:
    """Gets exact duration of audio in seconds via ffprobe."""
    cmd = [
        "ffprobe", "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        audio_path
    ]
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)
    try:
        return float(res.stdout.strip())
    except Exception:
        return 15.0


def clean_audio_and_realign(
    audio_path: str,
    video_data: Dict[str, Any],
    min_duration: float = 0.35,
    noise_threshold: str = "-30dB",
    keep_margin: float = 0.08
) -> Dict[str, Any]:
    """
    Trims silent pauses > min_duration from audio, leaves a tight keep_margin (0.08s),
    re-encodes the audio, and smoothly shifts all subtitle and scene timestamps.
    """
    if not os.path.isabs(audio_path):
        audio_path = os.path.join(BASE_DIR, audio_path.lstrip("/\\"))

    if not os.path.exists(audio_path):
        raise FileNotFoundError(f"Ses dosyası bulunamadı: {audio_path}")

    total_orig_dur = get_audio_duration(audio_path)
    silences = detect_silences(audio_path, min_duration=min_duration, noise_threshold=noise_threshold)

    if not silences:
        return {
            "success": True,
            "modified": False,
            "message": "Seste 0.35 saniyeden uzun sessizlik bulunamadı; ses zaten akıcı ve dinamik!",
            "original_duration": total_orig_dur,
            "new_duration": total_orig_dur,
            "seconds_saved": 0.0,
            "pauses_removed": 0,
            "video_data": video_data
        }

    # Backup original audio once if not backed up
    backup_path = audio_path.replace(".mp3", "_original.mp3")
    if not os.path.exists(backup_path):
        shutil.copy2(audio_path, backup_path)

    # Determine cut regions [cut_start, cut_end]
    cuts: List[Tuple[float, float]] = []
    for s_start, s_end, s_dur in silences:
        # Keep keep_margin / 2 on both sides if duration allows
        cut_start = s_start + (keep_margin / 2.0)
        cut_end = s_end - (keep_margin / 2.0)
        if cut_end > cut_start + 0.05:
            cuts.append((round(cut_start, 3), round(cut_end, 3)))

    if not cuts:
        return {
            "success": True,
            "modified": False,
            "message": "Sessizlik aralıkları güvenlik sınırının altında.",
            "original_duration": total_orig_dur,
            "new_duration": total_orig_dur,
            "seconds_saved": 0.0,
            "pauses_removed": 0,
            "video_data": video_data
        }

    # Determine kept segments [start, end]
    kept_segments: List[Tuple[float, float]] = []
    cur_pos = 0.0
    for c_start, c_end in cuts:
        if c_start > cur_pos:
            kept_segments.append((cur_pos, c_start))
        cur_pos = c_end

    if cur_pos < total_orig_dur:
        kept_segments.append((cur_pos, total_orig_dur))

    # Time mapper function
    def map_timestamp(t: float) -> float:
        removed = 0.0
        for c_start, c_end in cuts:
            if t > c_end:
                removed += (c_end - c_start)
            elif t > c_start:
                removed += (t - c_start)
                break
        return max(0.0, t - removed)

    # Build FFmpeg complex filter to concat kept segments
    filter_parts = []
    concat_inputs = []
    for idx, (seg_s, seg_e) in enumerate(kept_segments):
        filter_parts.append(
            f"[0:a]atrim=start={seg_s:.3f}:end={seg_e:.3f},asetpts=PTS-STARTPTS[a{idx}]"
        )
        concat_inputs.append(f"[a{idx}]")

    concat_filter = f"{';'.join(filter_parts)};{''.join(concat_inputs)}concat=n={len(kept_segments)}:v=0:a=1[outa]"

    temp_out = audio_path.replace(".mp3", "_cleaned_temp.mp3")
    cmd = [
        "ffmpeg", "-y",
        "-i", audio_path,
        "-filter_complex", concat_filter,
        "-map", "[outa]",
        "-c:a", "libmp3lame",
        "-b:a", "192k",
        temp_out
    ]

    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

    # Overwrite target audio with cleaned version
    shutil.move(temp_out, audio_path)
    new_dur = get_audio_duration(audio_path)
    seconds_saved = round(total_orig_dur - new_dur, 2)

    # Re-align subtitles
    subtitles = video_data.get("subtitles", [])
    for sub in subtitles:
        if "start" in sub and "end" in sub:
            sub["start"] = round(map_timestamp(sub["start"]), 2)
            sub["end"] = round(map_timestamp(sub["end"]), 2)

    # Re-align scenes
    scenes = video_data.get("scenes", [])
    for sc in scenes:
        if "startTime" in sc:
            sc["startTime"] = round(map_timestamp(sc["startTime"]), 2)
        if "endTime" in sc:
            sc["endTime"] = round(map_timestamp(sc["endTime"]), 2)

    video_data["totalDuration"] = round(new_dur, 2)

    with open(GENERATED_DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(video_data, f, ensure_ascii=False, indent=2)

    return {
        "success": True,
        "modified": True,
        "message": f"{len(cuts)} sessizlik temizlendi. {seconds_saved}s tasarruf sağlandı (Yeni süre: {new_dur:.2f}s).",
        "original_duration": round(total_orig_dur, 2),
        "new_duration": round(new_dur, 2),
        "seconds_saved": seconds_saved,
        "pauses_removed": len(cuts),
        "video_data": video_data
    }


if __name__ == "__main__":
    audio_file = os.path.join(PUBLIC_DIR, "audio.mp3")
    if os.path.exists(audio_file) and os.path.exists(GENERATED_DATA_FILE):
        with open(GENERATED_DATA_FILE, "r", encoding="utf-8") as f:
            v_data = json.load(f)
        res = clean_audio_and_realign(audio_file, v_data)
        print("Clean result:", res["message"])
