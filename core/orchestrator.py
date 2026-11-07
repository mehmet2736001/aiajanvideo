import json
import os
import re
import shutil
import subprocess
import threading
import time
from datetime import datetime
from typing import Dict, List, Optional

from core.auto_cleanup import clean_temp_artifacts
from core.production_tracker import tracker
from core.utils import BASE_DIR, atomic_write_json, read_json, safe_join, validate_slug

BRAIN_DIR = os.path.join(BASE_DIR, "brain")
PRODUCTION_OUT = os.path.join(BASE_DIR, "out")
PUBLIC_DIR = os.path.join(BASE_DIR, "public")

GENERIC_ENTRY = "src/index.ts"
GENERIC_COMPOSITION = "TefekkurVideo"
RENDER_TIMEOUT_SEC = 30 * 60

_history_lock = threading.Lock()
_PROGRESS_RE = re.compile(r"Rendered\s+(\d+)\s*/\s*(\d+)")


class ProductionError(RuntimeError):
    pass


def resolve_render_target(project_slug: str, comp_id: Optional[str] = None) -> Dict[str, Optional[str]]:
    """Slug için hangi Remotion giriş dosyası/kompozisyonunun render edileceğini belirler.

    * `src/<slug>/index.ts` varsa (elle hazırlanmış özel video) onu kullanır.
    * Yoksa veri güdümlü genel şablonu (`TefekkurVideo`) kullanır.
    Hiçbir koşulda başka bir projenin videosuna sessizce düşmez.
    """
    validate_slug(project_slug)
    custom_index = os.path.join("src", project_slug, "index.ts")
    custom_video = os.path.join(BASE_DIR, "src", project_slug, "Video.tsx")
    if os.path.exists(os.path.join(BASE_DIR, custom_index)):
        comp = comp_id
        if not comp and os.path.exists(custom_video):
            try:
                with open(custom_video, "r", encoding="utf-8") as vf:
                    m = re.search(r'<Composition\s+id=["\']([^"\']+)["\']', vf.read())
                    comp = m.group(1) if m else None
            except OSError:
                pass
        if not comp:
            raise ProductionError(f"{custom_index} içinde <Composition id=...> bulunamadı.")
        return {"entry": custom_index.replace(os.sep, "/"), "composition": comp, "generic": False}
    return {"entry": GENERIC_ENTRY, "composition": comp_id or GENERIC_COMPOSITION, "generic": True}


def _render(entry: str, composition: str, out_path: str, props_file: Optional[str]) -> None:
    npx = shutil.which("npx.cmd" if os.name == "nt" else "npx")
    if not npx:
        raise ProductionError("npx bulunamadı. Node.js kurulu ve PATH'te olmalı (npm install de çalıştırılmış olmalı).")
    if not os.path.isdir(os.path.join(BASE_DIR, "node_modules")):
        raise ProductionError("node_modules yok. Önce proje klasöründe `npm install` çalıştırın.")

    cmd = [npx, "remotion", "render", entry, composition, out_path, "--concurrency=2"]
    if props_file:
        cmd.append(f"--props={props_file}")

    proc = subprocess.Popen(
        cmd, cwd=BASE_DIR, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        text=True, encoding="utf-8", errors="replace", bufsize=1,
    )
    deadline = time.time() + RENDER_TIMEOUT_SEC
    tail: List[str] = []
    last_pct = -1
    try:
        assert proc.stdout is not None
        for chunk in iter(lambda: proc.stdout.readline(), ""):
            tail = (tail + [chunk.rstrip()])[-15:]
            for m in _PROGRESS_RE.finditer(chunk):
                done, total = int(m.group(1)), max(1, int(m.group(2)))
                pct = 65 + int(20 * done / total)
                if pct != last_pct:
                    last_pct = pct
                    with tracker._lock:
                        tracker.progress_percent = pct
                        tracker.step_detail = f"Render: {done}/{total} kare"
            if time.time() > deadline:
                proc.kill()
                raise ProductionError(f"Render {RENDER_TIMEOUT_SEC // 60} dakikayı aştı ve durduruldu.")
        rc = proc.wait()
    finally:
        if proc.poll() is None:
            proc.kill()
    if rc != 0:
        raise ProductionError("Remotion render başarısız:\n" + "\n".join(tail[-8:]))
    if not os.path.exists(out_path):
        raise ProductionError("Render bitti ama çıktı dosyası oluşmadı.")


class StudioOrchestrator:
    """Fikirden nihai 30 FPS 1080x1920 MP4 videoya kadar tüm süreci yürütür."""

    def __init__(self):
        self.brain_memory_path = os.path.join(BRAIN_DIR, "experience_memory.json")
        self.history_path = os.path.join(BRAIN_DIR, "video_history.json")
        self.memory = read_json(self.brain_memory_path, {})

    # -- geçmiş -------------------------------------------------------------
    def _append_history(self, entry: dict) -> None:
        with _history_lock:
            hist = read_json(self.history_path, [])
            if not isinstance(hist, list):
                hist = []
            hist.append(entry)
            atomic_write_json(self.history_path, hist[-500:])

    # -- ana akış -----------------------------------------------------------
    def produce_video_from_lines(
        self,
        project_slug: str,
        title: str,
        lines: List[str],
        category: str = "İslami Tefekkür",
        comp_id: Optional[str] = None,
        voice_id: Optional[str] = None,
    ) -> dict:
        try:
            return self._produce(project_slug, title, lines, category, comp_id, voice_id)
        except Exception as e:  # tracker'ı her durumda hataya çek
            tracker.fail(str(e))
            print(f"   ✗ Üretim hatası: {e}")
            return {"status": "error", "error": str(e)}

    def _produce(self, project_slug, title, lines, category, comp_id, voice_id) -> dict:
        from core.vision_critic import generate_and_evaluate_pano
        from core.voice_pipeline import synthesize_and_align

        validate_slug(project_slug)
        lines = [l.strip() for l in (lines or []) if l and l.strip()]
        if not lines:
            raise ProductionError("En az bir senaryo satırı gerekli.")
        target = resolve_render_target(project_slug, comp_id)  # render öncesi erken doğrulama

        print(f"\n🎬 [01_basyonetmen] PRODÜKSİYON BAŞLATILDI: {title}  ({project_slug})")
        tracker.start(project_title=title, voice_name=voice_id or "dervis", total_lines=len(lines))

        proj_dir = safe_join(PRODUCTION_OUT, project_slug)
        public_dir = safe_join(PUBLIC_DIR, project_slug)
        os.makedirs(proj_dir, exist_ok=True)
        os.makedirs(public_dir, exist_ok=True)

        # 1) Ses + kelime zamanlaması
        tracker.update_step(2, "Seslendirme & Senkronizasyon",
                            f"{len(lines)} sahne seslendiriliyor ve kelime zamanları çıkarılıyor...", 30, 40)
        voice_result = synthesize_and_align(lines, public_dir, voice_id=voice_id)
        duration = voice_result["duration_seconds"]
        word_count = voice_result["word_count"]
        print(f"   ✓ Ses: {duration:.2f} sn, {word_count} kelime")

        wps = word_count / max(1.0, duration)
        pace_note = None
        if wps > 2.6:
            pace_note = f"Tempo yüksek ({wps:.2f} kelime/sn): metni kısaltmayı düşünün."
        elif wps < 1.0:
            pace_note = f"Tempo çok düşük ({wps:.2f} kelime/sn): metin uzatılabilir."
        if pace_note:
            tracker.log(pace_note)

        # 2) Render
        tracker.update_step(3, "30 FPS Remotion Dikey Render",
                            "1080x1920 sahneler derleniyor...", 65, 60)
        final_mp4 = os.path.join(proj_dir, f"{project_slug}.mp4")
        props_file = None
        if target["generic"]:
            with open(voice_result["kelimeler_path"], "r", encoding="utf-8") as f:
                words = json.load(f)
            props = {"slug": project_slug, "title": title, "words": words, "audioDurationSec": duration}
            props_file = os.path.join(proj_dir, "props.json")
            atomic_write_json(props_file, props)
        _render(target["entry"], target["composition"], final_mp4, props_file)
        size_mb = os.path.getsize(final_mp4) / 1024 / 1024
        print(f"   ✓ Video: {final_mp4} ({size_mb:.2f} MB)")

        # 3) Kalite denetimi
        tracker.update_step(4, "48-Kare Kalite Denetimi",
                            "48 kare taranıyor: boş kare, kontrast ve hareket kontrolü...", 88, 8)
        pano_path = os.path.join(proj_dir, "pano.jpg")
        critic = generate_and_evaluate_pano(final_mp4, pano_path, duration)
        score = critic.get("score") if critic.get("status") == "success" else None
        notes = critic.get("notes") or ([critic["message"]] if critic.get("message") else [])
        if pace_note:
            notes = [pace_note] + list(notes)
        if score is None:
            tracker.log(f"⚠️ Kalite denetimi yapılamadı: {critic.get('message')}")
        print(f"   🏆 Kalite puanı: {score if score is not None else 'hesaplanamadı'}")

        # 4) Hafıza + temizlik
        self._append_history({
            "id": f"vid_{int(time.time())}_{project_slug}",
            "title": title,
            "category": category,
            "duration_seconds": round(duration, 2),
            "word_count": word_count,
            "quality_score": score,
            "quality_notes": notes,
            "status": "mastered" if score is not None else "rendered",
            "created_at": datetime.now().isoformat(),
            "output_path": os.path.relpath(final_mp4, BASE_DIR).replace(os.sep, "/"),
            "pano_path": os.path.relpath(pano_path, BASE_DIR).replace(os.sep, "/"),
        })
        cleaned = clean_temp_artifacts(public_dir)
        print(f"   🧹 Temizlenen geçici dosya: {cleaned / 1024:.1f} KB")

        result_pkg = {
            "project_slug": project_slug,
            "title": title,
            "video_url": f"/out/{project_slug}/{project_slug}.mp4",
            "pano_url": f"/out/{project_slug}/pano.jpg",
            "audio_url": f"/public/{project_slug}/ses.mp3",
            "score": score,
            "notes": notes,
            "duration": duration,
            "word_count": word_count,
        }
        tracker.complete(result_pkg)
        return {
            "status": "success",
            "video_path": final_mp4,
            "pano_path": pano_path,
            "score": score,
            "notes": notes,
            "duration": duration,
            "word_count": word_count,
        }


if __name__ == "__main__":
    StudioOrchestrator()
    print("Nexus Video AI Studio Orchestrator hazır!")
