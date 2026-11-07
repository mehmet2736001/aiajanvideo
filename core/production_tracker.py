import threading
import time
from datetime import datetime
from typing import Any, Dict, List, Optional

STEP_STATUS = {
    1: "PREPARING",
    2: "VOICE_SYNTHESIS",
    3: "REMOTION_RENDERING",
    4: "QUALITY_AUDIT",
    5: "COMPLETED",
}


class ProductionTracker:
    """
    Stüdyo prodüksiyon ilerleme takipçisi (thread-safe tekil nesne).
    Kalan süre, adım başına sabit tahmin ve geçen süreden hesaplanır
    (sorgu sayısına bağlı değildir).
    """
    _instance = None
    _guard = threading.Lock()

    def __new__(cls):
        with cls._guard:
            if cls._instance is None:
                inst = super().__new__(cls)
                inst._lock = threading.RLock()
                inst._init_state()
                cls._instance = inst
        return cls._instance

    def _init_state(self):
        with self._lock:
            self.status = "IDLE"
            self.step = 0
            self.total_steps = 5
            self.step_title = "Stüdyo Hazır / Beklemede"
            self.step_detail = "Yönetmenden yeni bir tefekkür fikri veya senaryo onayı bekleniyor."
            self.progress_percent = 0
            self.start_time: Optional[float] = None
            self.step_started: Optional[float] = None
            self.step_est_seconds = 0
            self.elapsed_seconds = 0
            self.estimated_remaining_seconds = 0
            self.project_title = ""
            self.voice_name = ""
            self.total_lines = 0
            self.error_message: Optional[str] = None
            self.logs: List[Dict[str, Any]] = []
            self.result_package: Optional[Dict[str, Any]] = None

    def reset(self):
        self._init_state()

    @property
    def busy(self) -> bool:
        return self.status not in ("IDLE", "COMPLETED", "ERROR")

    def start(self, project_title: str, voice_name: str = "dervis", total_lines: int = 8):
        with self._lock:
            self._init_state()
            now = time.time()
            self.status = "PREPARING"
            self.step = 1
            self.step_title = "Senaryo & Kurgu Mühürlendi"
            self.step_detail = f"«{project_title}» projesi için {total_lines} sahnelik metin işleme alındı."
            self.progress_percent = 10
            self.start_time = now
            self.step_started = now
            self.step_est_seconds = 5
            self.estimated_remaining_seconds = 60
            self.project_title = project_title
            self.voice_name = voice_name
            self.total_lines = total_lines
            self.log(f"🎬 Prodüksiyon başlatıldı: {project_title} ({total_lines} sahne)")

    def update_step(self, step_num: int, title: str, detail: str, percent: int, est_remaining: int):
        with self._lock:
            self.step = step_num
            self.step_title = title
            self.step_detail = detail
            self.progress_percent = percent
            self.step_started = time.time()
            self.step_est_seconds = max(0, est_remaining)
            self.estimated_remaining_seconds = max(0, est_remaining)
            if self.start_time:
                self.elapsed_seconds = int(time.time() - self.start_time)
            self.status = STEP_STATUS.get(step_num, "RUNNING")
            self.log(f"[{step_num}/5] {title} — {detail}")

    def log(self, message: str):
        with self._lock:
            self.logs.append({"time": datetime.now().strftime("%H:%M:%S"), "step": self.step, "message": message})
            if len(self.logs) > 50:
                self.logs.pop(0)

    def complete(self, package: Dict[str, Any]):
        with self._lock:
            self.status = "COMPLETED"
            self.step = 5
            self.step_title = "Master Video Yayına Hazır!"
            self.step_detail = "1080x1920 30 FPS video, ses ve 48 karelik pano ile tamamlandı."
            self.progress_percent = 100
            self.estimated_remaining_seconds = 0
            if self.start_time:
                self.elapsed_seconds = int(time.time() - self.start_time)
            self.result_package = package
            self.log("✨ Prodüksiyon %100 tamamlandı.")

    def fail(self, error_msg: str):
        with self._lock:
            self.status = "ERROR"
            self.step_title = "Prodüksiyon Hatası Oluştu"
            self.step_detail = error_msg
            self.error_message = error_msg
            self.estimated_remaining_seconds = 0
            if self.start_time:
                self.elapsed_seconds = int(time.time() - self.start_time)
            self.log(f"⚠️ Hata: {error_msg}")

    def get_status(self) -> Dict[str, Any]:
        with self._lock:
            if self.start_time and self.busy:
                now = time.time()
                self.elapsed_seconds = int(now - self.start_time)
                in_step = now - (self.step_started or now)
                self.estimated_remaining_seconds = max(2, int(self.step_est_seconds - in_step))
            return {
                "status": self.status,
                "step": self.step,
                "total_steps": self.total_steps,
                "step_title": self.step_title,
                "step_detail": self.step_detail,
                "progress_percent": self.progress_percent,
                "elapsed_seconds": self.elapsed_seconds,
                "estimated_remaining_seconds": self.estimated_remaining_seconds,
                "project_title": self.project_title,
                "voice_name": self.voice_name,
                "total_lines": self.total_lines,
                "error_message": self.error_message,
                "recent_logs": self.logs[-8:],
                "result_package": self.result_package,
            }

    def get_director_summary(self) -> str:
        """Selim Bey'in zihnine enjekte edilecek kısa telemetri özeti."""
        s = self.get_status()
        if s["status"] == "IDLE":
            return "Stüdyo şu an beklemede. Yönetmenden yeni bir konu veya senaryo onayı bekleniyor."
        if s["status"] == "COMPLETED":
            return f"«{s['project_title']}» videosu başarıyla tamamlandı (%100). Master Video oynatıcıda izlenmeye hazır."
        if s["status"] == "ERROR":
            return f"Prodüksiyon sırasında bir aksaklık oldu: {s['error_message']}"
        return (
            f"ŞU AN CANLI ÜRETİM SÜRÜYOR: Adım {s['step']}/5 ({s['step_title']}). "
            f"İlerleme: %{s['progress_percent']}. Geçen süre: {s['elapsed_seconds']} sn. "
            f"Tahmini kalan süre: yaklaşık {s['estimated_remaining_seconds']} saniye. "
            f"Yapılan işlem: {s['step_detail']}."
        )


tracker = ProductionTracker()
