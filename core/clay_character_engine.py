"""
Nexus AI Video Studio - 3D Clay (Vinyl) Karakter Animasyon Motoru
Saf Python (NumPy, OpenCV, Scipy, PIL) tabanlı 3D Clay Gölgelendirme ve İskelet Kinematiği.
Blender, ağır 3D motorları veya harici AI modelleri gerektirmez.
"""

import math
import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFont


def mk_lt(amb=(0.25, 0.25, 0.28), key=(1.0, 0.95, 0.85), key_dir=(0.5, -0.6, 0.6),
          rim=(0.9, 0.7, 0.3), rim_dir=(-0.6, 0.4, -0.6)):
    """Stüdyo aydınlatma parametrelerini normalleştirerek döndürür."""
    kd = np.array(key_dir, dtype=np.float32)
    kd /= (np.linalg.norm(kd) + 1e-6)
    rd = np.array(rim_dir, dtype=np.float32)
    rd /= (np.linalg.norm(rd) + 1e-6)
    return {
        "amb": np.array(amb, dtype=np.float32),
        "key": np.array(key, dtype=np.float32),
        "key_dir": kd,
        "rim": np.array(rim, dtype=np.float32),
        "rim_dir": rd,
    }


def smoothstep(edge0, edge1, x):
    """Hermite S-eğrisi yumuşatma fonksiyonu."""
    t = np.clip((x - edge0) / (edge1 - edge0 + 1e-6), 0.0, 1.0)
    return t * t * (3.0 - 2.0 * t)


def render_sphere_head(h, w, cx, cy, r, base_color=(240, 243, 246), lt=None):
    """Analitik küre normali ve Lambert + Rim gölgelendirmesi ile 3D kafa çizer."""
    if lt is None:
        lt = mk_lt()
    
    img = np.zeros((h, w, 3), dtype=np.float32)
    alpha = np.zeros((h, w), dtype=np.float32)

    y, x = np.ogrid[:h, :w]
    dx = (x - cx).astype(np.float32)
    dy = (y - cy).astype(np.float32)
    dist_sq = dx*dx + dy*dy
    r_sq = r * r

    mask = dist_sq <= r_sq
    if not np.any(mask):
        return (img * 255).astype(np.uint8), alpha

    nx = dx[mask] / r
    ny = dy[mask] / r
    nz = np.sqrt(np.maximum(0.0, 1.0 - (nx*nx + ny*ny)))
    
    # Lambert Key Light
    dot_key = np.maximum(0.0, nx * lt["key_dir"][0] + ny * lt["key_dir"][1] + nz * lt["key_dir"][2])
    # Rim Light
    dot_rim = np.maximum(0.0, nx * lt["rim_dir"][0] + ny * lt["rim_dir"][1] + nz * lt["rim_dir"][2])
    rim_factor = np.power(dot_rim, 2.5)

    base = np.array(base_color, dtype=np.float32) / 255.0
    
    shaded = (
        base * (lt["amb"] + lt["key"] * dot_key[:, None]) +
        lt["rim"] * rim_factor[:, None] * 0.75
    )
    shaded = np.clip(shaded, 0.0, 1.0)
    
    img[mask] = shaded
    alpha[mask] = 1.0
    return (img * 255).astype(np.uint8), alpha


def solve_2bone_ik(root, target, l1, l2, bend=1):
    """
    Analitik 2 kemikli Ters Kinematik (IK).
    root: (rx, ry)
    target: (tx, ty)
    l1: omuz-dirsek boyu, l2: dirsek-el boyu
    bend: +1 veya -1 (dirseğin içe/dışa bükülme yönü)
    Döndürür: dirsek (ex, ey) koordinatı
    """
    rx, ry = root
    tx, ty = target
    dx = tx - rx
    dy = ty - ry
    dist = math.hypot(dx, dy)
    
    # Ulaşılamazsa kolu hedefe doğru uzat
    if dist >= (l1 + l2):
        ratio = (l1) / (dist + 1e-6)
        return (rx + dx * ratio, ry + dy * ratio)
    if dist <= abs(l1 - l2):
        return (rx, ry + l1 * bend)

    # Kosinüs teoremi
    alpha = math.atan2(dy, dx)
    cos_angle = (l1*l1 + dist*dist - l2*l2) / (2.0 * l1 * dist)
    cos_angle = max(-1.0, min(1.0, cos_angle))
    beta = math.acos(cos_angle)

    elbow_angle = alpha + bend * beta
    ex = rx + l1 * math.cos(elbow_angle)
    ey = ry + l1 * math.sin(elbow_angle)
    return (ex, ey)
