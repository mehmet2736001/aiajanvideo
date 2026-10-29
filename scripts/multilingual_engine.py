"""
scripts/multilingual_engine.py
FAZ 9: Çok Dilli Küresel Dağıtım Fabrikası (Global Dubbing & RTL Engine)
Notebook Video AI Studio Pro

Enables:
1. One-click cloning of any video into 4 global languages (TR, EN, AR, ES).
2. Deep cultural translation of narration, headers, badges, cards, metrics and quotes via Gemini 3 key pool.
3. Native Edge Neural TTS dubbing in target languages with audio mastering & Whisper millisecond DTW alignment.
4. Full RTL (Right-to-Left) notebook styling, reversed spiral holes, and Arabic calligraphy typography (Amiri / Cairo).
"""

import os
import re
import json
import uuid
import copy
from typing import Dict, Any, List, Optional
from scripts.key_pool import pool, DEFAULT_MODEL
from scripts.tts_engine import generate_full_narration_pipeline

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PUBLIC_DIR = os.path.join(BASE_DIR, "public")
AUDIO_DIR = os.path.join(PUBLIC_DIR, "audio")
MULTILINGUAL_DIR = os.path.join(PUBLIC_DIR, "multilingual")

os.makedirs(AUDIO_DIR, exist_ok=True)
os.makedirs(MULTILINGUAL_DIR, exist_ok=True)

SUPPORTED_LANGUAGES = {
    "tr": {
        "code": "tr",
        "name": "Türkçe",
        "native_name": "Türkçe",
        "flag": "🇹🇷",
        "direction": "ltr",
        "default_voice": "tr-TR-AhmetNeural",
        "female_voice": "tr-TR-EmelNeural",
        "font_family": '"Kalam", "Caveat", cursive, sans-serif',
        "subtitles_font": '"Montserrat", "Inter", sans-serif',
        "social_handle_default": "@birkissa",
        "badge": "Orijinal / TR",
    },
    "en": {
        "code": "en",
        "name": "English (US)",
        "native_name": "English",
        "flag": "🇺🇸",
        "direction": "ltr",
        "default_voice": "en-US-AndrewMultilingualNeural",
        "female_voice": "en-US-AvaMultilingualNeural",
        "font_family": '"Caveat", "Kalam", cursive, sans-serif',
        "subtitles_font": '"Montserrat", "Inter", sans-serif',
        "social_handle_default": "@quickstory",
        "badge": "Global / EN",
    },
    "ar": {
        "code": "ar",
        "name": "العربية (RTL)",
        "native_name": "العربية",
        "flag": "🇸🇦",
        "direction": "rtl",
        "default_voice": "ar-SA-HamedNeural",
        "female_voice": "ar-SA-ZariyahNeural",
        "font_family": '"Amiri", "Cairo", "Scheherazade New", serif',
        "subtitles_font": '"Cairo", "Amiri", sans-serif',
        "social_handle_default": "@qissa_ar",
        "badge": "RTL / AR",
    },
    "es": {
        "code": "es",
        "name": "Español",
        "native_name": "Español",
        "flag": "🇪🇸",
        "direction": "ltr",
        "default_voice": "es-ES-AlvaroNeural",
        "female_voice": "es-ES-ElviraNeural",
        "font_family": '"Caveat", "Kalam", cursive, sans-serif',
        "subtitles_font": '"Montserrat", "Inter", sans-serif',
        "social_handle_default": "@unahistoria",
        "badge": "LatAm & ES",
    }
}


def translate_video_script(
    source_data: Dict[str, Any],
    target_lang: str,
    model: str = DEFAULT_MODEL
) -> Dict[str, Any]:
    """
    Uses Gemini 3 to translate and culturally adapt all textual fields of a video script
    into target_lang ('en', 'ar', 'es', 'tr').
    Maintains viral hook timing, punchy titles, and concise metric cards.
    """
    if target_lang not in SUPPORTED_LANGUAGES:
        raise ValueError(f"Desteklenmeyen hedef dil: {target_lang}")
    
    target_info = SUPPORTED_LANGUAGES[target_lang]
    target_name = target_info["name"]
    is_rtl = target_info["direction"] == "rtl"

    # Extract translatable payload to keep prompt focused
    translatable_payload = {
        "headerSubtitle": source_data.get("headerSubtitle", ""),
        "headerLine1": source_data.get("headerLine1", ""),
        "circledWord": source_data.get("circledWord", ""),
        "headerLine2": source_data.get("headerLine2", ""),
        "highlightedText": source_data.get("highlightedText", ""),
        "strikeWord": source_data.get("strikeWord", ""),
        "illustrationCaption": source_data.get("illustrationCaption", ""),
        "narration": source_data.get("narration", ""),
        "pipData": source_data.get("pipData", {}),
        "cards": [
            {"id": c.get("id"), "label": c.get("label", ""), "value": c.get("value", "")}
            for c in source_data.get("cards", [])
        ],
        "quoteSpotlight": source_data.get("quoteSpotlight", {}),
        "metricImpact": source_data.get("metricImpact", {}),
        "vsData": source_data.get("vsData", {}),
        "flowchartSteps": source_data.get("flowchartSteps", []),
        "triConcept": source_data.get("triConcept", {}),
        "gridExplosion": source_data.get("gridExplosion", {}),
        "timeline": source_data.get("timeline", {}),
        "viral": source_data.get("viral", {}),
    }

    # If multi-scene narrative exists, include scene texts
    scenes = source_data.get("scenes", [])
    if scenes:
        translatable_payload["scenes"] = [
            {
                "id": s.get("id"),
                "headerSubtitle": s.get("headerSubtitle", ""),
                "headerLine1": s.get("headerLine1", ""),
                "circledWord": s.get("circledWord", ""),
                "headerLine2": s.get("headerLine2", ""),
                "highlightedText": s.get("highlightedText", ""),
                "strikeWord": s.get("strikeWord", ""),
                "illustrationCaption": s.get("illustrationCaption", ""),
                "cards": [
                    {"id": c.get("id"), "label": c.get("label", ""), "value": c.get("value", "")}
                    for c in s.get("cards", [])
                ],
                "quoteSpotlight": s.get("quoteSpotlight", {}),
                "metricImpact": s.get("metricImpact", {}),
                "pipData": s.get("pipData", {}),
            }
            for s in scenes
        ]

    prompt = f"""You are an elite multilingual viral video adapter and translator specializing in YouTube Shorts and TikTok explainer videos.
You are translating and localizing a notebook explainer video into **{target_name} ({target_lang.upper()})**.

RULES FOR TRANSLATION:
1. Tone: Highly engaging, spoken-friendly, punchy, documentary-level curiosity.
2. Narration: Keep the spoken length and syllable rhythm similar to the original so the pacing fits a short-form video (approx 12-25 seconds). Do NOT make it overly long or verbose.
3. Circled Word & Highlighted Text: Must be single punchy words or short phrases in {target_name}.
4. Arabic (if target_lang is 'ar'): Use modern standard Arabic (Fusha) with majestic, natural phrasing suitable for historical/scientific reflection.
5. Numbers in Metric Cards: Keep numerals (e.g. 600+) but translate labels and takeaways authentically.
6. Hashtags & Viral Titles: Adapt to viral trending keywords in {target_name}.
7. Return strictly valid JSON with identical structure to the input payload.

INPUT PAYLOAD TO TRANSLATE:
{json.dumps(translatable_payload, ensure_ascii=False, indent=2)}

OUTPUT STRICT RAW JSON ONLY:
"""

    system_instruction = f"You are a professional video translator and cultural localizer into {target_name}. Output ONLY raw JSON without markdown code fences."
    res, key_name = pool.query_with_rotation(prompt, system_instruction, model=model)

    if not res:
        raise RuntimeError("Gemini çeviri havuzundan yanıt alınamadı.")

    cleaned = re.sub(r"```json\s*", "", res)
    cleaned = re.sub(r"```\s*", "", cleaned).strip()

    try:
        translated_payload = json.loads(cleaned)
    except Exception as e:
        print(f"[MultilingualEngine] JSON Parse error: {e}. Raw response: {res[:200]}")
        raise RuntimeError(f"Çeviri JSON formatı çözülemedi: {e}")

    # Build cloned video data with target language parameters
    cloned_data = copy.deepcopy(source_data)

    # Apply translated fields
    for field in [
        "headerSubtitle", "headerLine1", "circledWord", "headerLine2",
        "highlightedText", "strikeWord", "illustrationCaption", "narration"
    ]:
        if field in translated_payload:
            cloned_data[field] = translated_payload[field]

    if "pipData" in translated_payload and translated_payload["pipData"]:
        cloned_data["pipData"] = {**cloned_data.get("pipData", {}), **translated_payload["pipData"]}

    # Update cards
    if "cards" in translated_payload and translated_payload["cards"]:
        trans_cards = {c["id"]: c for c in translated_payload["cards"] if "id" in c}
        for c in cloned_data.get("cards", []):
            cid = c.get("id")
            if cid in trans_cards:
                c["label"] = trans_cards[cid].get("label", c.get("label"))
                c["value"] = trans_cards[cid].get("value", c.get("value"))

    # Update quoteSpotlight
    if "quoteSpotlight" in translated_payload and translated_payload["quoteSpotlight"]:
        cloned_data["quoteSpotlight"] = {**cloned_data.get("quoteSpotlight", {}), **translated_payload["quoteSpotlight"]}

    # Update metricImpact
    if "metricImpact" in translated_payload and translated_payload["metricImpact"]:
        cloned_data["metricImpact"] = {**cloned_data.get("metricImpact", {}), **translated_payload["metricImpact"]}

    # Update vsData
    if "vsData" in translated_payload and translated_payload["vsData"]:
        cloned_data["vsData"] = {**cloned_data.get("vsData", {}), **translated_payload["vsData"]}

    # Update flowchartSteps
    if "flowchartSteps" in translated_payload and translated_payload["flowchartSteps"]:
        cloned_data["flowchartSteps"] = translated_payload["flowchartSteps"]

    # Update triConcept
    if "triConcept" in translated_payload and translated_payload["triConcept"]:
        cloned_data["triConcept"] = {**cloned_data.get("triConcept", {}), **translated_payload["triConcept"]}

    # Update gridExplosion
    if "gridExplosion" in translated_payload and translated_payload["gridExplosion"]:
        cloned_data["gridExplosion"] = {**cloned_data.get("gridExplosion", {}), **translated_payload["gridExplosion"]}

    # Update timeline
    if "timeline" in translated_payload and translated_payload["timeline"]:
        cloned_data["timeline"] = {**cloned_data.get("timeline", {}), **translated_payload["timeline"]}

    # Update viral
    if "viral" in translated_payload and translated_payload["viral"]:
        cloned_data["viral"] = {**cloned_data.get("viral", {}), **translated_payload["viral"]}

    # Update scenes if multi-scene
    if "scenes" in translated_payload and "scenes" in cloned_data:
        for idx, s in enumerate(cloned_data["scenes"]):
            if idx < len(translated_payload["scenes"]):
                ts = translated_payload["scenes"][idx]
                for sf in ["headerSubtitle", "headerLine1", "circledWord", "headerLine2", "highlightedText", "strikeWord", "illustrationCaption"]:
                    if sf in ts:
                        s[sf] = ts[sf]
                if "quoteSpotlight" in ts and ts["quoteSpotlight"]:
                    s["quoteSpotlight"] = {**s.get("quoteSpotlight", {}), **ts["quoteSpotlight"]}
                if "metricImpact" in ts and ts["metricImpact"]:
                    s["metricImpact"] = {**s.get("metricImpact", {}), **ts["metricImpact"]}
                if "pipData" in ts and ts["pipData"]:
                    s["pipData"] = {**s.get("pipData", {}), **ts["pipData"]}

    # Target Language and RTL attributes
    cloned_data["language"] = target_lang
    cloned_data["direction"] = target_info["direction"]
    cloned_data["isRTL"] = is_rtl
    cloned_data["voiceId"] = target_info["default_voice"]
    cloned_data["socialHandle"] = target_info["social_handle_default"]

    return cloned_data


def dub_and_align_language(
    video_data: Dict[str, Any],
    project_id: str,
    target_lang: str,
    voice_id: Optional[str] = None,
    emotion_tone: Optional[str] = None
) -> Dict[str, Any]:
    """
    Synthesizes speech for the translated narration using native neural TTS,
    runs Whisper alignment in target language, and attaches subtitles & audio URL.
    """
    target_info = SUPPORTED_LANGUAGES.get(target_lang, SUPPORTED_LANGUAGES["en"])
    chosen_voice = voice_id or video_data.get("voiceId") or target_info["default_voice"]
    chosen_tone = emotion_tone or video_data.get("emotionTone") or "documentary"
    narration_text = video_data.get("narration", "").strip()

    if not narration_text:
        print(f"[MultilingualEngine] Warning: No narration text to dub for {target_lang}")
        return video_data

    # Generate audio filename
    audio_filename = f"audio_{project_id}_{target_lang}.mp3"
    audio_full_path = os.path.join(PUBLIC_DIR, "audio", audio_filename)
    audio_rel_url = f"audio/{audio_filename}"

    print(f"[MultilingualEngine] Dubbing {target_lang.upper()} using voice {chosen_voice} with tone {chosen_tone}...")
    
    res = generate_full_narration_pipeline(
        narration_text=narration_text,
        provider="edge_tts",
        voice_id=chosen_voice,
        emotion_tone=chosen_tone,
        lang=target_lang,
        output_studio_path=audio_full_path
    )

    subtitles = res.get("subtitles", [])
    total_dur = res.get("totalDuration", 0.0)

    video_data["audioUrl"] = audio_rel_url
    video_data["subtitles"] = subtitles
    video_data["totalDuration"] = total_dur
    video_data["voiceId"] = chosen_voice
    video_data["emotionTone"] = chosen_tone

    return video_data


def clone_project_to_all_languages(
    source_data: Dict[str, Any],
    project_id: Optional[str] = None,
    target_languages: Optional[List[str]] = None,
    model: str = DEFAULT_MODEL
) -> Dict[str, Any]:
    """
    Full Multilingual Factory:
    Clones the input video data into 4 global languages (e.g. ['tr', 'en', 'ar', 'es']),
    performs translation, neural TTS dubbing, Whisper alignment, and saves the bundle.
    """
    pid = project_id or f"nbv_{uuid.uuid4().hex[:8]}"
    targets = target_languages or ["tr", "en", "ar", "es"]
    project_bundle_dir = os.path.join(MULTILINGUAL_DIR, pid)
    os.makedirs(project_bundle_dir, exist_ok=True)

    results: Dict[str, Any] = {
        "projectId": pid,
        "createdAt": int(__import__("time").time()),
        "sourceTopic": source_data.get("headerSubtitle", "") + " " + source_data.get("headerLine1", ""),
        "languages": {},
        "summary": []
    }

    print(f"[MultilingualEngine] Starting 4-Language Factory for project {pid}...")

    for lang in targets:
        if lang not in SUPPORTED_LANGUAGES:
            continue

        print(f"\n--- [MultilingualEngine] Processing {lang.upper()} ({SUPPORTED_LANGUAGES[lang]['name']}) ---")
        
        # 1. Translation / Adaptation
        if lang == source_data.get("language", "tr") and source_data.get("audioUrl") and source_data.get("subtitles"):
            # Already primary language with audio
            lang_data = copy.deepcopy(source_data)
            lang_data["language"] = lang
            lang_data["direction"] = SUPPORTED_LANGUAGES[lang]["direction"]
            lang_data["isRTL"] = lang_data["direction"] == "rtl"
        else:
            lang_data = translate_video_script(source_data, target_lang=lang, model=model)
            # 2. Dubbing & Whisper Sync
            lang_data = dub_and_align_language(lang_data, project_id=pid, target_lang=lang)

        # 3. Save to bundle
        lang_file = os.path.join(project_bundle_dir, f"{lang}.json")
        with open(lang_file, "w", encoding="utf-8") as f:
            json.dump(lang_data, f, ensure_ascii=False, indent=2)

        results["languages"][lang] = {
            "meta": SUPPORTED_LANGUAGES[lang],
            "data": lang_data,
            "jsonPath": f"multilingual/{pid}/{lang}.json",
            "audioUrl": lang_data.get("audioUrl"),
            "subtitlesCount": len(lang_data.get("subtitles", [])),
            "isRTL": lang_data.get("isRTL", False)
        }
        results["summary"].append({
            "lang": lang,
            "name": SUPPORTED_LANGUAGES[lang]["name"],
            "flag": SUPPORTED_LANGUAGES[lang]["flag"],
            "voice": lang_data.get("voiceId"),
            "duration": lang_data.get("totalDuration", 0)
        })

    # Save meta
    meta_file = os.path.join(project_bundle_dir, "meta.json")
    with open(meta_file, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"[MultilingualEngine] Successfully cloned project {pid} into {len(results['languages'])} languages!")
    return results
