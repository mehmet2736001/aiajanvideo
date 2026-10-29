import os
import json
import time
import uuid
import threading
import datetime
from typing import List, Dict, Any, Optional
import schedule

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
JOBS_FILE = os.path.join(DATA_DIR, "autopilot_jobs.json")
HISTORY_FILE = os.path.join(DATA_DIR, "autopilot_history.json")

VIRAL_BANK = [
    {"topic": "İbn-i Sina Aristo'nun Metafizik kitabını neden 40 kez okudu?", "layout": "flowchart", "theme": "notebook"},
    {"topic": "Zaman dağlarda deniz seviyesine göre neden daha hızlı akar?", "layout": "metric_impact", "theme": "blueprint"},
    {"topic": "Kâinat neden bir anda değil de 6 evrede yaratıldı?", "layout": "cards", "theme": "notebook"},
    {"topic": "Karadeliklerin olay ufkunu geçersek gerçekte ne görürüz?", "layout": "flowchart", "theme": "chalkboard"},
    {"topic": "Stoacılık vs Modern Telaş: Kontrol edemediğin şeyleri dert etme!", "layout": "vs_split", "theme": "chalkboard"},
    {"topic": "Mimar Sinan'ın Süleymaniye'deki kandil isi ve devekuşu yumurtası sırrı", "layout": "flowchart", "theme": "parchment"},
    {"topic": "Prokrastinasyon: İnsan neden en çok sevdiği şeyleri erteler?", "layout": "cards", "theme": "kraft"},
    {"topic": "Işık hızına yaklaştıkça kütle neden sonsuza gider?", "layout": "metric_impact", "theme": "blueprint"}
]

class AutopilotScheduler:
    def __init__(self):
        self.jobs: List[Dict[str, Any]] = []
        self.history: List[Dict[str, Any]] = []
        self.is_running = False
        self.worker_thread: Optional[threading.Thread] = None
        self.active_execution: Optional[Dict[str, Any]] = None
        self.load_data()

    def load_data(self):
        os.makedirs(DATA_DIR, exist_ok=True)
        if os.path.exists(JOBS_FILE):
            try:
                with open(JOBS_FILE, "r", encoding="utf-8") as f:
                    self.jobs = json.load(f)
            except Exception:
                self.jobs = []
        else:
            # Seed with a default paused sample job so user immediately sees how it works
            self.jobs = [
                {
                    "id": "job_sample_1",
                    "title": "Akşam Bülteni (Viral Bilim & Hikmet)",
                    "enabled": False,
                    "frequency": "daily",
                    "time": "19:00",
                    "topic_source": "bank",
                    "theme": "random",
                    "layout": "auto",
                    "auto_upload": True,
                    "privacy": "private",
                    "webhook_url": "",
                    "created_at": time.strftime("%Y-%m-%d %H:%M"),
                    "last_run": None,
                    "run_count": 0
                }
            ]
            self.save_jobs()

        if os.path.exists(HISTORY_FILE):
            try:
                with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                    self.history = json.load(f)
            except Exception:
                self.history = []

    def save_jobs(self):
        with open(JOBS_FILE, "w", encoding="utf-8") as f:
            json.dump(self.jobs, f, ensure_ascii=False, indent=2)

    def save_history(self):
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(self.history[:50], f, ensure_ascii=False, indent=2)

    def add_job(self, job_data: Dict[str, Any]) -> Dict[str, Any]:
        job_id = f"job_{str(uuid.uuid4())[:8]}"
        new_job = {
            "id": job_id,
            "title": job_data.get("title", "Otomatik Video Görevi"),
            "enabled": job_data.get("enabled", True),
            "frequency": job_data.get("frequency", "daily"),  # daily, interval_hours, once
            "time": job_data.get("time", "18:00"),
            "interval_hours": job_data.get("interval_hours", 6),
            "topic_source": job_data.get("topic_source", "bank"),  # bank, custom
            "custom_topics": job_data.get("custom_topics", []),
            "theme": job_data.get("theme", "random"),
            "layout": job_data.get("layout", "auto"),
            "auto_upload": job_data.get("auto_upload", False),
            "privacy": job_data.get("privacy", "private"),
            "webhook_url": job_data.get("webhook_url", ""),
            "created_at": time.strftime("%Y-%m-%d %H:%M"),
            "last_run": None,
            "run_count": 0
        }
        self.jobs.append(new_job)
        self.save_jobs()
        return new_job

    def update_job(self, job_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        target = next((j for j in self.jobs if j["id"] == job_id), None)
        if not target:
            return None
        target.update(updates)
        self.save_jobs()
        return target

    def delete_job(self, job_id: str) -> bool:
        before = len(self.jobs)
        self.jobs = [j for j in self.jobs if j["id"] != job_id]
        if len(self.jobs) < before:
            self.save_jobs()
            return True
        return False

    def trigger_job_execution(self, job_id: str, execute_fn) -> Dict[str, Any]:
        """Executes a job immediately in a dedicated background task."""
        target = next((j for j in self.jobs if j["id"] == job_id), None)
        if not target:
            return {"success": False, "error": "Görev bulunamadı"}

        if self.active_execution:
            return {"success": False, "error": "Zaten aktif çalışan bir otopilot görevi var."}

        # Run via thread
        t = threading.Thread(target=self._run_job_worker, args=(target, execute_fn))
        t.daemon = True
        t.start()

        return {"success": True, "message": f"'{target['title']}' görevi başlatıldı."}

    def _run_job_worker(self, job: Dict[str, Any], execute_fn):
        self.active_execution = {
            "job_id": job["id"],
            "title": job["title"],
            "started_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "stage": "İçerik Şablonu Üretiliyor..."
        }
        t0 = time.time()
        try:
            # 1. Pick Topic
            import random
            if job.get("topic_source") == "custom" and job.get("custom_topics"):
                topic_item = random.choice(job["custom_topics"])
                topic = topic_item if isinstance(topic_item, str) else topic_item.get("topic")
                layout = job.get("layout", "cards")
                theme = job.get("theme", "notebook")
            else:
                entry = random.choice(VIRAL_BANK)
                topic = entry["topic"]
                layout = entry["layout"] if job.get("layout") == "auto" else job.get("layout")
                theme = entry["theme"] if job.get("theme") == "random" else job.get("theme")

            self.active_execution["stage"] = f"Yapay Zekâ ile Senaryo ve Ses Hazırlanıyor: '{topic[:40]}...'"
            
            # 2. Invoke generator & render
            run_result = execute_fn(topic=topic, layout=layout, theme=theme, job=job)

            # Update job state
            job["last_run"] = time.strftime("%Y-%m-%d %H:%M")
            job["run_count"] = job.get("run_count", 0) + 1
            self.save_jobs()

            duration_sec = int(time.time() - t0)
            hist_item = {
                "id": str(uuid.uuid4())[:8],
                "job_id": job["id"],
                "job_title": job["title"],
                "topic": topic,
                "timestamp": time.strftime("%Y-%m-%d %H:%M"),
                "status": "success",
                "duration_sec": duration_sec,
                "video_url": run_result.get("video_url", ""),
                "youtube_url": run_result.get("youtube_url", "")
            }
            self.history.insert(0, hist_item)
            self.save_history()

        except Exception as e:
            job["last_error"] = str(e)
            self.save_jobs()
            hist_item = {
                "id": str(uuid.uuid4())[:8],
                "job_id": job["id"],
                "job_title": job["title"],
                "topic": "Hata",
                "timestamp": time.strftime("%Y-%m-%d %H:%M"),
                "status": "failed",
                "error": str(e)
            }
            self.history.insert(0, hist_item)
            self.save_history()
        finally:
            self.active_execution = None

    def start_scheduler_loop(self, execute_fn):
        """Starts the background ticker thread."""
        if self.is_running:
            return
        self.is_running = True

        def loop():
            while self.is_running:
                try:
                    now_str = time.strftime("%H:%M")
                    for job in self.jobs:
                        if not job.get("enabled", True):
                            continue
                        
                        freq = job.get("frequency", "daily")
                        target_time = job.get("time", "18:00")
                        
                        # Match current minute
                        if freq == "daily" and now_str == target_time:
                            last_run = job.get("last_run", "")
                            today_prefix = time.strftime("%Y-%m-%d")
                            if not last_run or not last_run.startswith(today_prefix):
                                if not self.active_execution:
                                    self._run_job_worker(job, execute_fn)
                except Exception as e:
                    print(f"Autopilot ticker error: {e}")
                time.sleep(30)

        self.worker_thread = threading.Thread(target=loop)
        self.worker_thread.daemon = True
        self.worker_thread.start()

scheduler = AutopilotScheduler()
