import os
import subprocess
from typing import Dict, List

TILE_COLS, TILE_ROWS = 8, 6
TILE_COUNT = TILE_COLS * TILE_ROWS


def evaluate_tiles(tiles: List["np.ndarray"]) -> Dict:
    """Gri tonlamalı karelerden (np.ndarray) puan ve notlar üretir. Saf fonksiyon, test edilebilir.

    Kriterler:
      - Boş/siyah kare oranı (ilk kare hariç; fade-in normal kabul edilir)
      - Ardışık kare benzerliği (donmuş/tekrarlayan görüntü)
      - Kare başına kontrast (yazı okunabilirliği için gerekli parlaklık aralığı)
      - Son karenin dolu olması (erken kesilme)
    """
    import numpy as np

    score, notes = 100, []
    n = len(tiles)
    if n == 0:
        return {"score": 0, "notes": ["Hiç kare çıkarılamadı."]}

    means = [float(t.mean()) for t in tiles]
    stds = [float(t.std()) for t in tiles]

    blank = [i for i in range(1, n) if means[i] < 5.0]
    if blank:
        pen = min(30, 4 * len(blank))
        score -= pen
        notes.append(f"{len(blank)} karede içerik yok (siyah): {blank[:6]}")

    flat = [i for i in range(n) if stds[i] < 6.0 and means[i] >= 5.0]
    if len(flat) > n * 0.25:
        score -= 10
        notes.append(f"{len(flat)} kare düz/kontrastsız görünüyor.")

    frozen = 0
    for a, b in zip(tiles, tiles[1:]):
        if a.shape == b.shape and float(np.abs(a.astype(np.int16) - b.astype(np.int16)).mean()) < 0.8:
            frozen += 1
    if frozen > n * 0.35:
        score -= 12
        notes.append(f"Ardışık {frozen} kare neredeyse aynı: hareket yetersiz olabilir.")

    if means[-1] < 5.0:
        score -= 15
        notes.append("Son kare boş: video erken kesilmiş olabilir.")

    if n < TILE_COUNT * 0.8:
        score -= 10
        notes.append(f"Pano eksik: {n}/{TILE_COUNT} kare.")

    if not notes:
        notes.append("Kareler dolu, kontrast ve hareket yeterli.")
    return {"score": max(40, score), "notes": notes}


def generate_and_evaluate_pano(video_path: str, output_pano_path: str, duration: float) -> Dict:
    """FFmpeg ile 8x6'lık 48 karelik pano üretir ve karelerini değerlendirir.

    Hata durumunda {"status": "error", ...} döner; çağıran taraf bunu başarı saymamalıdır.
    """
    try:
        import numpy as np
        from PIL import Image
    except ImportError as e:
        return {"status": "error", "message": f"Pillow/numpy eksik: {e}"}

    fps_sample = TILE_COUNT / max(5.0, duration)
    cmd = [
        "ffmpeg", "-y", "-i", video_path,
        "-vf", f"fps={fps_sample:.5f},scale=240:-2,tile={TILE_COLS}x{TILE_ROWS}",
        "-frames:v", "1", output_pano_path,
    ]
    try:
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, check=True, timeout=300)
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError) as e:
        return {"status": "error", "message": f"Pano üretilemedi: {e}"}

    if not os.path.exists(output_pano_path):
        return {"status": "error", "message": "Pano görseli oluşturulamadı."}

    im = Image.open(output_pano_path).convert("L")
    w, h = im.size
    tw, th = w // TILE_COLS, h // TILE_ROWS
    arr = np.array(im)
    tiles = []
    for r in range(TILE_ROWS):
        for c in range(TILE_COLS):
            tiles.append(arr[r * th:(r + 1) * th, c * tw:(c + 1) * tw])

    # fps yuvarlaması nedeniyle sondaki kareler boş kalabilir: tamamen siyah kuyruk karelerini at
    while tiles and float(tiles[-1].max()) == 0.0 and len(tiles) > 1:
        tiles.pop()

    res = evaluate_tiles(tiles)
    res.update({
        "status": "success",
        "pano_path": output_pano_path,
        "resolution": f"{w}x{h}",
        "file_size_bytes": os.path.getsize(output_pano_path),
        "frames_checked": len(tiles),
    })
    return res
