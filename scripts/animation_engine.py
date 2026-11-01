import os
import sys
import uuid
import time
import json
import random
import urllib.parse
import urllib.request
import subprocess
from typing import Dict, Any, Optional

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
PUBLIC_DIR = os.path.join(BASE_DIR, "public")
VIDEOS_DIR = os.path.join(PUBLIC_DIR, "videos")
ILLUST_DIR = os.path.join(PUBLIC_DIR, "illustrations")

os.makedirs(VIDEOS_DIR, exist_ok=True)
os.makedirs(ILLUST_DIR, exist_ok=True)

# 2D Animation Style Modifiers
ANIMATION_STYLES = {
    "2d_anime": (
        "2D animated anime movie aesthetic, Studio Ghibli and Makoto Shinkai style, "
        "hand-drawn cel animation, vibrant luminous colors, atmospheric lighting, "
        "sunbeams, volumetric depth, cinematic 2D keyframe, vertical 9:16 aspect ratio, masterpiece"
    ),
    "2d_dervish_miniature": (
        "stylized Islamic miniature painting blended with modern 2D animation, "
        "rich gouache and gold leaf accents, spiritual serene atmosphere, elegant flowing outlines, "
        "traditional oriental aesthetic, vertical 9:16 aspect ratio"
    ),
    "2d_watercolor": (
        "animated watercolor illustration, warm textured paper, gentle color bleeding, "
        "dreamy atmospheric lighting, organic brushwork, peaceful 2D anime background art, vertical 9:16"
    ),
    "2d_flat_vector": (
        "modern 2D vector animation style, Kurzgesagt aesthetic, bold silhouettes, clean outlines, "
        "vibrant solid gradients, educational cinematic framing, vertical 9:16"
    ),
    "2d_comic": (
        "dynamic 2D graphic novel and comic book art, detailed crosshatch shading, "
        "dramatic rim lighting, cinematic depth, vintage animation look, vertical 9:16"
    )
}

def craft_2d_animation_prompt_with_omni(
    scene_text: str,
    style: str = "2d_anime",
    pool = None
) -> str:
    """
    Uses Gemini Omni (or pool fallback) to interpret the scene text
    and generate an ultra-detailed, evocative English visual prompt for 2D animation.
    """
    default_prompt = f"2D animated scene, {scene_text}, vertical 9:16, cinematic anime visual"

    if not pool:
        try:
            from scripts.key_pool import pool as imported_pool
            pool = imported_pool
        except Exception:
            return default_prompt

    system_instruction = (
        "You are an expert anime director and 2D visual artist at Studio Ghibli. "
        "Your task is to take a Turkish scene description and convert it into a vivid, "
        "detailed, high-end English prompt for generating a 2D animation visual. "
        "Focus on: subject action, character outfit/details, environment (mountains, trees, sun, wind), "
        "lighting (sunbeams, golden hour), and camera perspective (vertical 9:16). "
        "Output ONLY the prompt string, with NO markdown, NO quotes, NO explanation."
    )

    user_query = (
        f"Sahne Metni: '{scene_text}'\n"
        f"İstenen Stil: {style}\n"
        "Bunu derviş, tabiat, insan hareketi ve atmosfer detaylarıyla dolu, 2D animasyon için "
        "en iyi İngilizce görsel tarifine (prompt) dönüştür."
    )

    try:
        # Try with Gemini Omni models first
        omni_models = ["gemini-omni-1.1-flash", "gemini-omni-flash-preview", "gemini-3.5-flash"]
        for m in omni_models:
            res, _ = pool.query_with_rotation(user_query, system_instruction=system_instruction, model=m)
            if res and len(res.strip()) > 15:
                cleaned = res.strip().replace('"', '').replace('`', '').split('\n')[0]
                return cleaned
    except Exception as e:
        print(f"[Animation Engine] Gemini Omni prompt crafting warning: {e}")

    # Fallback contextual prompt
    if "derviş" in scene_text.lower() or "dağ" in scene_text.lower():
        return (
            "A humble Sufi dervish with green robe and wooden staff walking along a winding mountain path "
            "on a bright sunny day, majestic green mountains, sunbeams streaming down, wind blowing his robe, "
            "Studio Ghibli 2D anime aesthetic, vertical 9:16"
        )
    elif "aile" in scene_text.lower() or "yuva" in scene_text.lower():
        return (
            "A warm and peaceful traditional courtyard home, golden warm sunlight streaming through archways, "
            "olive trees, peaceful serene Islamic household atmosphere, 2D Makoto Shinkai anime style, vertical 9:16"
        )
    return f"2D animated aesthetic scene showing {scene_text}, Studio Ghibli style, vertical 9:16"


def generate_2d_keyframe_image(
    prompt: str,
    style: str = "2d_anime",
    timeout: int = 25
) -> str:
    """
    Generates a vertical 9:16 2D animation image keyframe via Pollinations Flux engine.
    """
    style_modifier = ANIMATION_STYLES.get(style, ANIMATION_STYLES["2d_anime"])
    full_prompt = f"{prompt}, {style_modifier}"
    encoded = urllib.parse.quote(full_prompt)
    seed = random.randint(100, 999999)
    url = f"https://image.pollinations.ai/prompt/{encoded}?width=720&height=1280&model=flux&nologo=true&seed={seed}"

    file_id = f"anim_key_{uuid.uuid4().hex[:8]}.jpg"
    out_path = os.path.join(ILLUST_DIR, file_id)

    print(f"[Animation Engine] Generating 2D keyframe for: {prompt[:70]}...")
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        data = resp.read()
        if len(data) > 5000:
            with open(out_path, "wb") as f:
                f.write(data)
            print(f"[Animation Engine] Keyframe saved: {file_id} ({len(data)} bytes)")
            return out_path
    raise RuntimeError("Failed to download generated 2D keyframe")


def synthesize_2d_animation_video(
    image_path: str,
    duration: float = 8.0,
    fps: int = 30
) -> str:
    """
    Converts a 2D keyframe into a smooth, dynamic 2D animation video loop
    using FFmpeg zoompan and cinematic camera motion.
    """
    total_frames = int(duration * fps)
    video_id = f"anim_vid_{uuid.uuid4().hex[:8]}.mp4"
    out_path = os.path.join(VIDEOS_DIR, video_id)

    # Dynamic Ken Burns camera motion filter
    # Smooth forward push-in with gentle upward drift
    vf_filter = (
        f"scale=720:1280:force_original_aspect_ratio=increase,"
        f"crop=720:1280,"
        f"zoompan=z='min(zoom+0.0006,1.10)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)-sin(in/25)*1.2':d={total_frames}:s=720x1280:fps={fps},"
        f"format=yuv420p"
    )

    cmd = [
        "ffmpeg", "-y", "-loop", "1", "-i", image_path,
        "-vf", vf_filter,
        "-t", str(duration),
        "-c:v", "libx264", "-preset", "ultrafast",
        "-pix_fmt", "yuv420p",
        out_path
    ]

    print(f"[Animation Engine] Synthesizing {duration}s 2D animation video with FFmpeg...")
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print(f"[Animation Engine] 2D Animation MP4 created: {video_id} ({os.path.getsize(out_path)} bytes)")
    return out_path


def create_scene_2d_animation(
    scene_text: str,
    duration: float = 8.0,
    style: str = "2d_anime",
    pool = None,
    custom_prompt: Optional[str] = None
) -> Dict[str, Any]:
    """
    Full pipeline to produce a 2D animation video using Gemini Omni and FFmpeg:
    1. Gemini Omni crafts detailed prompt
    2. 2D Anime Flux generates high-res vertical keyframe
    3. FFmpeg animates it into a 9:16 living MP4 video
    """
    if custom_prompt and custom_prompt.strip():
        final_prompt = custom_prompt.strip()
    else:
        final_prompt = craft_2d_animation_prompt_with_omni(scene_text, style=style, pool=pool)

    # Generate keyframe
    try:
        keyframe_path = generate_2d_keyframe_image(final_prompt, style=style)
    except Exception as e:
        print(f"[Animation Engine] Keyframe generation error: {e}, falling back to test dervish")
        keyframe_path = os.path.join(ILLUST_DIR, "test_dervish.jpg")

    # Synthesize video
    video_path = synthesize_2d_animation_video(keyframe_path, duration=duration)
    video_filename = os.path.basename(video_path)

    return {
        "videoUrl": f"/public/videos/{video_filename}",
        "relativeUrl": f"videos/{video_filename}",
        "prompt": final_prompt,
        "style": style,
        "duration": duration,
        "keyframeUrl": f"/public/illustrations/{os.path.basename(keyframe_path)}"
    }
