"""
scripts/timeline_engine.py
Multi-Track Timeline & Scene Management Engine for Pro Video Editor
Notebook Video AI Studio Pro
"""

import os
import re
import json
import uuid
import struct
import subprocess
from typing import Dict, Any, List, Optional
from scripts.key_pool import pool, DEFAULT_MODEL
from scripts.image_engine import generate_ai_illustration

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_DIR = os.path.join(BASE_DIR, "src")
PUBLIC_DIR = os.path.join(BASE_DIR, "public")
DATA_DIR = os.path.join(BASE_DIR, "data")
GENERATED_DATA_FILE = os.path.join(SRC_DIR, "generatedData.json")


def extract_audio_waveform(audio_path: str, num_peaks: int = 100) -> List[float]:
    """
    Extracts normalized amplitude peaks (0.08 to 1.0) from an audio file using FFmpeg.
    Fast execution (<0.1s) and produces authentic waveform display for timeline track.
    """
    if not os.path.exists(audio_path):
        # Return fallback pseudo-sine peaks
        return [round(0.2 + 0.6 * abs((i % 10 - 5) / 5.0), 2) for i in range(num_peaks)]

    try:
        cmd = ["ffmpeg", "-y", "-i", audio_path, "-f", "s16le", "-ac", "1", "-ar", "8000", "-"]
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, check=True)
        raw = res.stdout
        count = len(raw) // 2
        if count == 0:
            return [0.15] * num_peaks

        samples = struct.unpack(f"{count}h", raw)
        chunk_size = max(1, count // num_peaks)
        peaks = []
        for i in range(num_peaks):
            chunk = samples[i * chunk_size : (i + 1) * chunk_size]
            if chunk:
                # RMS / Peak hybrid for punchy visualization
                peak_val = max(abs(s) for s in chunk) / 32768.0
                normalized = max(0.08, min(1.0, peak_val * 1.75))
                peaks.append(round(normalized, 3))
            else:
                peaks.append(0.08)
        return peaks
    except Exception as e:
        print(f"[TimelineEngine] Waveform extraction error: {e}")
        return [round(0.25 + 0.5 * abs((i % 12 - 6) / 6.0), 2) for i in range(num_peaks)]


def ensure_scenes_structure(video_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Ensures that video_data has a valid, properly indexed scenes array.
    If single-scene data is present, packages it into scene_1.
    """
    scenes = video_data.get("scenes", [])
    total_dur = float(video_data.get("totalDuration", 15.0) or 15.0)

    if not scenes or len(scenes) == 0:
        # Wrap root single-scene into scenes[0]
        s1 = {
            "id": "scene_1",
            "startTime": 0.0,
            "endTime": round(total_dur, 2),
            "layoutType": video_data.get("layoutType", "pip_split"),
            "headerSubtitle": video_data.get("headerSubtitle", "Kısa Kıssa"),
            "headerLine1": video_data.get("headerLine1", "NEDEN"),
            "circledWord": video_data.get("circledWord", "SIR"),
            "headerLine2": video_data.get("headerLine2", ""),
            "highlightedText": video_data.get("highlightedText", "ASIRLARIN BİLGELİĞİ"),
            "strikeWord": video_data.get("strikeWord", ""),
            "doodleType": video_data.get("doodleType", "galaxy"),
            "illustrationUrl": video_data.get("illustrationUrl", ""),
            "illustrationCaption": video_data.get("illustrationCaption", ""),
            "illustrationStyle": video_data.get("illustrationStyle", "polaroid"),
            "brollType": video_data.get("brollType", "none"),
            "brollOpacity": video_data.get("brollOpacity", 0.18),
            "cards": video_data.get("cards", []),
            "quoteSpotlight": video_data.get("quoteSpotlight", {}),
            "metricImpact": video_data.get("metricImpact", {}),
            "pipData": video_data.get("pipData", {}),
        }
        scenes = [s1]
        video_data["scenes"] = scenes

    return scenes


def delete_scene_from_timeline(video_data: Dict[str, Any], scene_id: str) -> Dict[str, Any]:
    """
    Deletes the specified scene from video_data.scenes, recalculates sequential
    timestamps without gaps, and updates src/generatedData.json.
    """
    scenes = ensure_scenes_structure(video_data)
    if len(scenes) <= 1:
        raise ValueError("En az 1 sahne kalmalıdır. Sahneyi silmek yerine içeriğini düzenleyebilirsiniz.")

    # Find and remove
    new_scenes = [s for s in scenes if s.get("id") != scene_id]
    if len(new_scenes) == len(scenes):
        raise ValueError(f"'{scene_id}' kimlikli sahne bulunamadı.")

    # Re-calculate sequential start and end times
    cur_time = 0.0
    for idx, s in enumerate(new_scenes):
        s["id"] = f"scene_{idx + 1}"
        orig_dur = s.get("endTime", 12.0) - s.get("startTime", 0.0)
        dur = max(3.0, orig_dur)
        s["startTime"] = round(cur_time, 2)
        cur_time += dur
        s["endTime"] = round(cur_time, 2)

    video_data["scenes"] = new_scenes
    video_data["totalDuration"] = round(cur_time, 2)

    # Sync root properties to scene 1
    if new_scenes:
        s0 = new_scenes[0]
        for key in ["headerSubtitle", "headerLine1", "circledWord", "headerLine2", "highlightedText", "strikeWord", "layoutType", "illustrationUrl", "illustrationCaption", "illustrationStyle"]:
            if key in s0:
                video_data[key] = s0[key]

    # Save to disk
    with open(GENERATED_DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(video_data, f, ensure_ascii=False, indent=2)

    return video_data


def regenerate_scene_with_ai(
    video_data: Dict[str, Any],
    scene_id: str,
    prompt_override: Optional[str] = None,
    layout_override: Optional[str] = None,
    illustration_style_override: Optional[str] = None,
    broll_override: Optional[str] = None,
    model: str = DEFAULT_MODEL
) -> Dict[str, Any]:
    """
    Uses Gemini 3 to regenerate content (titles, badges, cards, quote, or illustration)
    specifically for one scene in the timeline.
    """
    scenes = ensure_scenes_structure(video_data)
    target_idx = None
    for idx, s in enumerate(scenes):
        if s.get("id") == scene_id:
            target_idx = idx
            break

    if target_idx is None:
        raise ValueError(f"'{scene_id}' sahnesi bulunamadı.")

    target_scene = scenes[target_idx]
    topic_context = prompt_override or target_scene.get("headerSubtitle", "") + " " + target_scene.get("headerLine1", "")
    layout = layout_override or target_scene.get("layoutType", "pip_split")
    ill_style = illustration_style_override or target_scene.get("illustrationStyle", "polaroid")
    broll = broll_override or target_scene.get("brollType", "none")

    prompt = f"""Sen viral Shorts ve TikTok için defter kurgusu yapan bir AI Yönetmenisin.
Mevcut bir videonun **{target_idx + 1}. Sahnesini** ({target_scene.get('startTime', 0)}s - {target_scene.get('endTime', 12)}s) sıfırdan yeniden üretiyorsun.

Konu/Kanca İpuçları: '{topic_context}'
Hedef Şablon Düzeni (layoutType): '{layout}'
Görsel Tarzı: '{ill_style}'

Lütfen bu sahne için çarpıcı, merak uyandırıcı yeni başlıklar, kartlar veya alıntılar oluştur.

SADECE SAF JSON FORMATINDA YANIT VER:
{{
  "headerSubtitle": "Kısa merak uyandırıcı alt başlık",
  "headerLine1": "BÜYÜK BAŞLIK 1",
  "circledWord": "ÇEMBERLİ_KELİME",
  "headerLine2": "İkinci satır veya isim",
  "highlightedText": "FOSFORLU KALEM VURGUSU",
  "strikeWord": "ÜSTÜ_ÇİZİLECEK_KELİME",
  "illustrationPrompt": "Detaylı fotogerçekçi İngilizce prompt (ör: vintage oil painting of...)",
  "illustrationCaption": "Fotoğraf altı el yazısı açıklama",
  "quoteSpotlight": {{
    "speaker": "Konuşmacı",
    "title": "Unvan",
    "quoteText": "Çarpıcı 1 cümlelik alıntı"
  }},
  "metricImpact": {{
    "bigNumber": "300x",
    "bigLabel": "KAT DAHA HIZLI",
    "subheading": "Açıklama",
    "keyTakeaway": "Ana fikir"
  }},
  "cards": [
    {{"id": "1", "label": "Kavram", "value": "Açıklama", "color": "#1e3a8a"}},
    {{"id": "2", "label": "Neden", "value": "Çözüm", "color": "#15803d"}}
  ]
}}
"""
    system_instruction = "You are a professional video scene generator. Output ONLY raw JSON."
    res, key_name = pool.query_with_rotation(prompt, system_instruction, model=model)

    if not res:
        raise RuntimeError("Gemini havuzundan yanıt alınamadı.")

    cleaned = re.sub(r"```json\s*", "", res)
    cleaned = re.sub(r"```\s*", "", cleaned).strip()

    try:
        gen_scene = json.loads(cleaned)
    except Exception as e:
        raise RuntimeError(f"Yeniden üretilen sahne JSON ayrıştırılamadı: {e}")

    # Update scene fields
    for field in ["headerSubtitle", "headerLine1", "circledWord", "headerLine2", "highlightedText", "strikeWord", "illustrationCaption", "quoteSpotlight", "metricImpact", "cards"]:
        if field in gen_scene and gen_scene[field]:
            target_scene[field] = gen_scene[field]

    target_scene["layoutType"] = layout
    target_scene["illustrationStyle"] = ill_style
    target_scene["brollType"] = broll

    # If illustration prompt is present and pip_split is chosen, generate Flux image
    if layout == "pip_split" or ill_style in ["polaroid", "torn_paper"]:
        ill_prompt = gen_scene.get("illustrationPrompt")
        if ill_prompt:
            try:
                img_url, _ = generate_ai_illustration(
                    prompt=ill_prompt,
                    style=ill_style,
                    topic=topic_context
                )
                target_scene["illustrationUrl"] = img_url
            except Exception as ie:
                print(f"[TimelineEngine] Image generation warning: {ie}")

    # If this is scene 1, also update root properties
    if target_idx == 0:
        for k in ["headerSubtitle", "headerLine1", "circledWord", "headerLine2", "highlightedText", "strikeWord", "layoutType", "illustrationUrl", "illustrationCaption", "illustrationStyle", "brollType"]:
            if k in target_scene:
                video_data[k] = target_scene[k]

    # Save to generatedData.json
    with open(GENERATED_DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(video_data, f, ensure_ascii=False, indent=2)

    return {
        "success": True,
        "updated_scene": target_scene,
        "video_data": video_data
    }


def split_scene_on_timeline(video_data: Dict[str, Any], scene_id: str, split_time: float) -> Dict[str, Any]:
    """
    Splits an existing scene at split_time into two consecutive scenes.
    """
    scenes = ensure_scenes_structure(video_data)
    idx = None
    for i, s in enumerate(scenes):
        if s.get("id") == scene_id:
            idx = i
            break

    if idx is None:
        raise ValueError(f"'{scene_id}' bulunamadı.")

    s = scenes[idx]
    start = s.get("startTime", 0.0)
    end = s.get("endTime", 12.0)

    if split_time <= start + 1.5 or split_time >= end - 1.5:
        raise ValueError(f"Bölme zamanı ({split_time:.1f}s) sahne başlangıcından ve bitişinden en az 1.5s uzakta olmalıdır.")

    # Clone first half
    s["endTime"] = round(split_time, 2)

    # Create second half
    second_half = copy_scene_with_new_bounds(s, round(split_time, 2), end)
    scenes.insert(idx + 1, second_half)

    # Re-index ids
    for i, sc in enumerate(scenes):
        sc["id"] = f"scene_{i + 1}"

    video_data["scenes"] = scenes
    with open(GENERATED_DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(video_data, f, ensure_ascii=False, indent=2)

    return video_data


def copy_scene_with_new_bounds(scene: Dict[str, Any], start: float, end: float) -> Dict[str, Any]:
    import copy
    sc = copy.deepcopy(scene)
    sc["id"] = f"scene_{uuid.uuid4().hex[:6]}"
    sc["startTime"] = start
    sc["endTime"] = end
    sc["headerSubtitle"] = (sc.get("headerSubtitle", "") + " (Bölüm 2)").strip()
    return sc


def add_scene_to_timeline(video_data: Dict[str, Any], duration: float = 10.0) -> Dict[str, Any]:
    """
    Appends a new scene slice at the end of the timeline.
    """
    scenes = ensure_scenes_structure(video_data)
    last_end = scenes[-1].get("endTime", 0.0) if scenes else 0.0
    new_idx = len(scenes) + 1

    new_scene = {
        "id": f"scene_{new_idx}",
        "startTime": round(last_end, 2),
        "endTime": round(last_end + duration, 2),
        "layoutType": "cards",
        "headerSubtitle": f"Bölüm {new_idx}",
        "headerLine1": "YENİ",
        "circledWord": "BAŞLIK",
        "headerLine2": "",
        "highlightedText": "ÖNEMLİ NOKTA",
        "strikeWord": "",
        "doodleType": "book",
        "cards": [
            {"id": "1", "label": "Detay 1", "value": "Açıklama 1", "color": "#1e3a8a"},
            {"id": "2", "label": "Detay 2", "value": "Açıklama 2", "color": "#15803d"}
        ],
        "quoteSpotlight": {"speaker": "Yazar", "title": "Kaynak", "quoteText": "Hakikat sabır ile anlaşılır."},
        "metricImpact": {"bigNumber": "100%", "bigLabel": "ÖNEMLİ", "subheading": "Anahtar Fikir", "keyTakeaway": "Özet"},
        "pipData": {"title": "Yeni Sahne", "caption": "Detay Görseli"}
    }

    scenes.append(new_scene)
    video_data["scenes"] = scenes
    video_data["totalDuration"] = round(last_end + duration, 2)

    with open(GENERATED_DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(video_data, f, ensure_ascii=False, indent=2)

    return video_data
