import os
import sys
import uuid
import random
import urllib.request
import urllib.parse
from typing import Dict, Any, Optional

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
PUBLIC_DIR = os.path.join(BASE_DIR, "public")
ILLUSTRATIONS_DIR = os.path.join(PUBLIC_DIR, "illustrations")
os.makedirs(ILLUSTRATIONS_DIR, exist_ok=True)

# Curated Style Enhancers
STYLE_MODIFIERS = {
    "polaroid": "vintage polaroid photograph, warm 35mm film grain, authentic analog photo, natural depth of field, masterpiece",
    "torn_paper": "vintage oil painting, parchment texture, expressive brush strokes, antique scientific illustration, warm muted colors",
    "clean_frame": "cinematic hyper-detailed digital art, dramatic lighting, volumetric glow, high contrast, 8k wallpaper",
    "sketch": "hand-drawn graphite sketch, ink crosshatch shading, rough paper texture, Leonardo da Vinci manuscript style"
}

def generate_ai_illustration(
    prompt: str,
    style: str = "polaroid",
    caption: str = "",
    timeout: int = 15
) -> Dict[str, Any]:
    """
    Generates a high-quality illustration using the Flux engine via Pollinations.ai.
    Falls back gracefully to a cached/sample illustration if network request times out.
    """
    style_modifier = STYLE_MODIFIERS.get(style, STYLE_MODIFIERS["polaroid"])
    enhanced_prompt = f"{prompt}, {style_modifier}"
    encoded_prompt = urllib.parse.quote(enhanced_prompt)
    seed = random.randint(1000, 999999)
    url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=768&height=768&model=flux&nologo=true&seed={seed}"

    file_id = f"ill_{uuid.uuid4().hex[:8]}.jpg"
    out_path = os.path.join(ILLUSTRATIONS_DIR, file_id)

    print(f"[Image Engine] Requesting illustration: {prompt[:60]}... (Style: {style})")
    success = False
    try:
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        )
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = resp.read()
            if len(data) > 5000:
                with open(out_path, "wb") as f:
                    f.write(data)
                print(f"[Image Engine] Illustration downloaded: {file_id} ({len(data)} bytes)")
                success = True
    except Exception as e:
        print(f"[Image Engine] Warning: AI image generation error or timeout: {e}")

    # Fallback if download failed
    if not success or not os.path.exists(out_path):
        sample_path = os.path.join(ILLUSTRATIONS_DIR, "test_sample.jpg")
        if os.path.exists(sample_path):
            import shutil
            shutil.copyfile(sample_path, out_path)
            print(f"[Image Engine] Used fallback sample illustration for {file_id}")
            success = True
        else:
            file_id = "illustrations/test_sample.jpg"

    return {
        "illustrationUrl": f"illustrations/{file_id}",
        "caption": caption or prompt[:40],
        "style": style,
        "prompt": prompt
    }

if __name__ == "__main__":
    res = generate_ai_illustration("Galileo Galilei looking through his antique telescope at Jupiter", style="polaroid", caption="Jüpiter'in Uyduları")
    print("Result:", res)
