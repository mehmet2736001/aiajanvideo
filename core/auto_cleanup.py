import os
import shutil
import glob

def clean_temp_artifacts(target_dir: str = None) -> int:
    """
    16. Ajan (Mühendis Demir):
    Render tamamlandıktan sonra diskte biriken ara wav/mp3 ve temp klasörlerini temizler.
    """
    cleaned_bytes = 0
    patterns = [
        "**/temp_voice",
        "**/temp_audio",
        "**/*.wav",
        "**/*.tmp"
    ]

    base = target_dir or os.path.abspath(".")
    for p in patterns:
        for f in glob.glob(os.path.join(base, p), recursive=True):
            if "node_modules" in f:
                continue
            try:
                if os.path.isdir(f):
                    for root, dirs, files in os.walk(f):
                        for file in files:
                            cleaned_bytes += os.path.getsize(os.path.join(root, file))
                    shutil.rmtree(f, ignore_errors=True)
                elif os.path.isfile(f):
                    cleaned_bytes += os.path.getsize(f)
                    os.remove(f)
            except Exception:
                pass

    return cleaned_bytes
