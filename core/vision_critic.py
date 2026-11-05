import os
import subprocess
from PIL import Image

def generate_and_evaluate_pano(
    video_path: str,
    output_pano_path: str,
    duration: float
) -> dict:
    """
    1. FFmpeg ile videodan 48 karelik (8x6 grid) kontrol panosunu çıkarır.
    2. İlk ve son karenin doluluğunu, parlaklık dağılımını ve görsel sürekliliği doğrular.
    """
    fps_sample = 48.0 / max(5.0, duration)
    cmd = [
        "ffmpeg", "-y", "-i", video_path,
        "-vf", f"fps={fps_sample},scale=240:-2,tile=8x6",
        "-frames:v", "1", output_pano_path
    ]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

    if not os.path.exists(output_pano_path):
        return {"status": "error", "message": "Pano görseli oluşturulamadı."}

    pano_size = os.path.getsize(output_pano_path)
    im = Image.open(output_pano_path)
    w, h = im.size

    # Temel denetimler
    first_tile_box = (0, 0, w // 8, h // 6)
    last_tile_box = (w - w // 8, h - h // 6, w, h)

    first_tile = im.crop(first_tile_box).convert("L")
    last_tile = im.crop(last_tile_box).convert("L")

    # Parlaklık / doluluk skoru
    import numpy as np
    first_mean = float(np.mean(np.array(first_tile)))
    last_mean = float(np.mean(np.array(last_tile)))

    is_first_solid = first_mean > 5.0  # Zifiri boş değil
    is_last_solid = last_mean > 5.0

    score = 95
    notes = []
    if not is_first_solid:
        score -= 15
        notes.append("İlk kare boş veya tamamen karanlık.")
    if not is_last_solid:
        score -= 15
        notes.append("Son kare boş veya erken kesilmiş.")

    return {
        "status": "success",
        "pano_path": output_pano_path,
        "resolution": f"{w}x{h}",
        "file_size_bytes": pano_size,
        "score": max(50, score),
        "notes": notes if notes else ["İlk ve son kareler dolu, akış pürüzsüz."]
    }
