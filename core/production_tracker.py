import os
import time
from datetime import datetime
from typing import Dict, Any, List, Optional

class ProductionTracker:
    """
    Stüdyo Prodüksiyon İlerleme ve Canlı Durum Takipçisi.
    Adım adım süreçleri, kalan süreyi, yüzdelik ilerlemeyi ve mikro logları yönetir.
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ProductionTracker, cls).__new__(cls)
            cls._instance._init_state()
        return cls._instance

    def _init_state(self):
        self.status = "IDLE"  # IDLE, PREPARING, VOICE_SYNTHESIS, REMOTION_RENDERING, QUALITY_AUDIT, COMPLETED, ERROR
        self.step = 0
        self.total_steps = 5
        self.step_title = "Stüdyo Hazır / Beklemede"
        self.step_detail = "Yönetmenden yeni bir tefekkür fikri veya senaryo onayı bekleniyor."
        self.progress_percent = 0
        self.start_time: Optional[float] = None
        self.elapsed_seconds = 0
        self.estimated_remaining_seconds = 0
        self.project_title = "Peygamberimizi Yaşlandıran Sır: Hûd 112"
        self.voice_name = "dervis (Turso #47)"
        self.total_lines = 8
        self.error_message: Optional[str] = None
        self.logs: List[Dict[str, Any]] = []
        self.result_package: Optional[Dict[str, Any]] = None

    def start(self, project_title: str, voice_name: str = "dervis", total_lines: int = 8):
        self.status = "PREPARING"
        self.step = 1
        self.step_title = "Senaryo & Kurgu Mühürlendi"
        self.step_detail = f"«{project_title}» projesi için {total_lines} sahnelik metin işleme alındı."
        self.progress_percent = 15
        self.start_time = time.time()
        self.elapsed_seconds = 0
        self.estimated_remaining_seconds = 35
        self.project_title = project_title
        self.voice_name = voice_name
        self.total_lines = total_lines
        self.error_message = None
        self.result_package = None
        self.logs = []
        self.log(f"🎬 Prodüksiyon başlatıldı: {project_title} ({total_lines} sahne)")

    def update_step(self, step_num: int, title: str, detail: str, percent: int, est_remaining: int):
        self.step = step_num
        self.step_title = title
        self.step_detail = detail
        self.progress_percent = percent
        self.estimated_remaining_seconds = max(0, est_remaining)
        if self.start_time:
            self.elapsed_seconds = int(time.time() - self.start_time)
        
        step_status_map = {
            1: "PREPARING",
            2: "VOICE_SYNTHESIS",
            3: "REMOTION_RENDERING",
            4: "QUALITY_AUDIT",
            5: "COMPLETED"
        }
        self.status = step_status_map.get(step_num, "RUNNING")
        self.log(f"[{step_num}/5] {title} — {detail}")

    def log(self, message: str):
        entry = {
            "time": datetime.now().strftime("%H:%M:%S"),
            "step": self.step,
            "message": message
        }
        self.logs.append(entry)
        if len(self.logs) > 50:
            self.logs.pop(0)

    def complete(self, package: Dict[str, Any]):
        self.status = "COMPLETED"
        self.step = 5
        self.step_title = "Master Video Yayına Hazır!"
        self.step_detail = "1080x1920 30 FPS Full HD video, Turso sesi ve 48 karelik pano ile tamamlandı."
        self.progress_percent = 100
        self.estimated_remaining_seconds = 0
        if self.start_time:
            self.elapsed_seconds = int(time.time() - self.start_time)
        self.result_package = package
        self.log("✨ Prodüksiyon %100 başarıyla tamamlandı. Oynatıcıya aktarıldı.")

    def fail(self, error_msg: str):
        self.status = "ERROR"
        self.step_title = "Prodüksiyon Hatası Oluştu"
        self.step_detail = error_msg
        self.error_message = error_msg
        self.estimated_remaining_seconds = 0
        self.log(f"⚠️ Hata: {error_msg}")

    def get_status(self) -> Dict[str, Any]:
        if self.start_time and self.status not in ["COMPLETED", "ERROR", "IDLE"]:
            self.elapsed_seconds = int(time.time() - self.start_time)
            # Kalan süreyi dinamik hafif azalt
            self.estimated_remaining_seconds = max(2, self.estimated_remaining_seconds - 1)

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
            "result_package": self.result_package
        }

    def get_director_summary(self) -> str:
        """Selim Bey'in zihnine enjekte edilecek kısa telemetri özeti."""
        if self.status == "IDLE":
            return "Stüdyo şu an beklemede. Yönetmenden yeni bir konu veya senaryo onayı bekleniyor."
        elif self.status == "COMPLETED":
            return f"«{self.project_title}» videosu başarıyla tamamlandı (%100). Master Video oynatıcıda izlenmeye hazır."
        elif self.status == "ERROR":
            return f"Prodüksiyon sırasında bir aksaklık oldu: {self.error_message}"
        else:
            return (
                f"ŞU AN CANLI ÜRETİM SÜRÜYOR: Adım {self.step}/5 ({self.step_title}). "
                f"İlerleme: %{self.progress_percent}. Geçen süre: {self.elapsed_seconds} sn. "
                f"Tahmini kalan süre: yaklaşık {self.estimated_remaining_seconds} saniye. "
                f"Yapılan işlem: {self.step_detail}."
            )

tracker = ProductionTracker()
