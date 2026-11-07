import os
import shutil

# Yalnızca üretimin kendi oluşturduğu geçici dosyalar silinir.
TEMP_DIR_NAMES = ("temp_voice", "temp_audio")


def clean_temp_artifacts(target_dir: str) -> int:
    """
    16. Ajan (Mühendis Demir):
    Üretim sonrası `target_dir` içindeki geçici klasörleri (temp_voice, temp_audio) ve *.tmp
    dosyalarını siler. Başka hiçbir dosyaya (ör. SFX .wav dosyaları) dokunmaz.

    `target_dir` zorunludur; boş/kök/çalışma dizini gibi tehlikeli hedefler reddedilir.
    Silinen bayt sayısını döndürür.
    """
    if not target_dir:
        raise ValueError("clean_temp_artifacts için hedef klasör zorunludur.")
    base = os.path.abspath(target_dir)
    if base in (os.path.abspath(os.sep), os.path.abspath(os.path.expanduser("~"))):
        raise ValueError(f"Güvensiz temizlik hedefi: {base}")
    if not os.path.isdir(base):
        return 0

    cleaned = 0
    for root, dirs, files in os.walk(base, topdown=True):
        if "node_modules" in dirs:
            dirs.remove("node_modules")
        for d in list(dirs):
            if d in TEMP_DIR_NAMES:
                full = os.path.join(root, d)
                cleaned += _dir_size(full)
                shutil.rmtree(full, ignore_errors=True)
                dirs.remove(d)
        for fn in files:
            if fn.endswith(".tmp"):
                full = os.path.join(root, fn)
                try:
                    cleaned += os.path.getsize(full)
                    os.remove(full)
                except OSError:
                    pass
    return cleaned


def _dir_size(path: str) -> int:
    total = 0
    for root, _dirs, files in os.walk(path):
        for fn in files:
            try:
                total += os.path.getsize(os.path.join(root, fn))
            except OSError:
                pass
    return total
