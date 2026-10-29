import os
import subprocess
import sys

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
BROLL_DIR = os.path.join(BASE_DIR, "public", "broll")
os.makedirs(BROLL_DIR, exist_ok=True)

def generate_loop(name: str, filter_str: str, duration: int = 8):
    out_path = os.path.join(BROLL_DIR, f"{name}.mp4")
    if os.path.exists(out_path) and os.path.getsize(out_path) > 10000:
        print(f"[B-Roll] {name}.mp4 already exists ({os.path.getsize(out_path)} bytes). Skipping.")
        return

    print(f"[B-Roll] Generating {name}.mp4 ({duration}s 720x1280)...")
    cmd = [
        "ffmpeg", "-y",
        "-f", "lavfi",
        "-i", filter_str,
        "-t", str(duration),
        "-c:v", "libx264",
        "-preset", "ultrafast",
        "-pix_fmt", "yuv420p",
        out_path
    ]
    try:
        res = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        print(f"[B-Roll] Created: {name}.mp4 successfully ({os.path.getsize(out_path)} bytes)")
    except Exception as e:
        print(f"[B-Roll] Error creating {name}.mp4: {e}")

def create_all_broll():
    # 1. Cosmic Stars: Starfield noise drifting in deep indigo space
    cosmic_filter = (
        "color=c=#030614:s=720x1280:r=30,"
        "geq=r='(sin(X/35+T*0.5)*cos(Y/45-T*0.3)*60+60)':"
        "g='(sin(X/50-T*0.4)*40+40)':"
        "b='(cos(Y/40+T*0.6)*110+120)',"
        "noise=alls=15:allf=t+u"
    )
    generate_loop("cosmic", cosmic_filter, duration=6)

    # 2. Golden Sunset Clouds: Warm amber/crimson atmospheric gradients
    clouds_filter = (
        "color=c=#1a0b02:s=720x1280:r=30,"
        "geq=r='(sin(Y/120+T*0.3)*120+130)':"
        "g='(sin(Y/150+T*0.2)*70+70)':"
        "b='(cos(X/100-T*0.1)*30+30)'"
    )
    generate_loop("clouds", clouds_filter, duration=6)

    # 3. Contemplative Waves: Deep cyan and sapphire oceanic ripples
    waves_filter = (
        "color=c=#021019:s=720x1280:r=30,"
        "geq=r='(sin(X/80+T*0.8)*20+20)':"
        "g='(sin((X+Y)/90-T*0.9)*70+80)':"
        "b='(cos(Y/70+T*0.7)*100+140)'"
    )
    generate_loop("waves", waves_filter, duration=6)

    # 4. Fluid Ink Blooms: Dark organic watercolor expansion
    ink_filter = (
        "color=c=#08090f:s=720x1280:r=30,"
        "geq=r='(sin(X/55+T*0.4)*cos(Y/65+T*0.4)*70+70)':"
        "g='(sin(Y/75-T*0.3)*45+45)':"
        "b='(cos(X/65+T*0.5)*85+85)'"
    )
    generate_loop("ink", ink_filter, duration=6)

if __name__ == "__main__":
    create_all_broll()
    print("[B-Roll] All procedural B-Roll loops ready!")
