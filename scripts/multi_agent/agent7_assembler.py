# -*- coding: utf-8 -*-
"""
Agent 7: Montaj ve Render Modülü (FFmpeg / Timeline Derleyici)
Görevi: 4. Ajan'dan gelen video kliplerini, 6. Ajan'dan gelen mikslenmiş sesi
ve 5. Ajan'dan gelen dinamik altyazıları birleştirip nihai MP4 videosunu render etmek.
Girdi: Doğrulanmış video klipleri, mikslenmiş ses, .ass altyazı dosyası.
Çıktı: Nihai montajlanmış MP4 video dosyası (AssemblyData).
"""
import os
import subprocess
import time
import json
from typing import Optional, Callable
from .base_agent import BaseAgent
from .state import ProjectState, PipelinePhase, AssemblyData


OUT_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "out")
PUBLIC_VIDEOS_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "public", "videos")
SRC_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "src")
os.makedirs(OUT_DIR, exist_ok=True)
os.makedirs(PUBLIC_VIDEOS_DIR, exist_ok=True)


class AssemblyAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            agent_id=7,
            name="Montaj & Render Modülü",
            required_phase=PipelinePhase.PHASE_6_AUDIO_DESIGNED,
            target_phase=PipelinePhase.PHASE_7_ASSEMBLED
        )

    def _process(
        self,
        state: ProjectState,
        on_progress: Optional[Callable[[int, str, dict], None]] = None
    ) -> ProjectState:
        t0 = time.time()
        project_id = state.project_id
        if state.selected_track == "vector_infographic" and state.vector_assets:
            media_assets = state.vector_assets.assets
        elif state.media_assets:
            media_assets = state.media_assets.assets
        elif state.vector_assets:
            media_assets = state.vector_assets.assets
        else:
            raise ValueError("Montaj için hiçbir video varlığı (medya veya vektör) bulunamadı!")

        mixed_audio = state.audio_design.mixed_audio_file
        ass_path = state.typography.ass_file_path
        total_duration = state.transcription.duration

        if on_progress:
            on_progress(self.agent_id, "running", {
                "message": f"Final montaj başlatıldı: {len(media_assets)} video sahnesi, mikslenmiş ses ve dinamik altyazılar birleştiriliyor..."
            })

        final_filename = f"final_{project_id}.mp4"
        final_video_path = os.path.join(PUBLIC_VIDEOS_DIR, final_filename)
        out_dest_path = os.path.join(OUT_DIR, "video.mp4")

        # 1. Write FFmpeg concat list
        concat_txt = os.path.join(PUBLIC_VIDEOS_DIR, f"concat_{project_id}.txt")
        with open(concat_txt, "w", encoding="utf-8") as f:
            for a in media_assets:
                # Forward slash for FFmpeg compatibility on Windows
                safe_path = a.video_file.replace("\\", "/")
                f.write(f"file '{safe_path}'\n")

        # 2. Assemble with FFmpeg
        # Format ass path safely for Windows FFmpeg
        escaped_ass_path = ass_path.replace("\\", "/").replace(":", "\\:")

        # Try rendering with ASS subtitles burned in
        # If libass fails, fallback to clean video concat
        render_success = False

        try:
            cmd = [
                "ffmpeg", "-y",
                "-f", "concat", "-safe", "0", "-i", concat_txt,
                "-i", mixed_audio,
                "-vf", f"ass='{escaped_ass_path}'",
                "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
                "-c:a", "aac", "-b:a", "192k",
                "-pix_fmt", "yuv420p",
                "-shortest",
                final_video_path
            ]
            subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
            render_success = True
        except Exception as e:
            print(f"[Assembly Agent] Burn-in subtitle attempt notice: {e}, falling back to video concat without burn-in...")
            try:
                cmd_fallback = [
                    "ffmpeg", "-y",
                    "-f", "concat", "-safe", "0", "-i", concat_txt,
                    "-i", mixed_audio,
                    "-c:v", "libx264", "-preset", "ultrafast",
                    "-c:a", "aac", "-b:a", "192k",
                    "-pix_fmt", "yuv420p",
                    "-shortest",
                    final_video_path
                ]
                subprocess.run(cmd_fallback, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
                render_success = True
            except Exception as e2:
                print(f"[Assembly Agent] Concat fallback failed: {e2}")

        # Clean up temporary concat list
        if os.path.exists(concat_txt):
            try:
                os.remove(concat_txt)
            except Exception:
                pass

        if not os.path.exists(final_video_path) or os.path.getsize(final_video_path) < 10000:
            raise RuntimeError(f"Final video derlenemedi veya dosya boyutu yetersiz ({final_video_path})")

        # Copy to out/video.mp4 for default viewer
        try:
            import shutil
            shutil.copyfile(final_video_path, out_dest_path)
        except Exception:
            pass

        render_time = round(time.time() - t0, 2)
        file_size = os.path.getsize(final_video_path)

        state.assembly = AssemblyData(
            final_video_file=final_video_path,
            final_video_url=f"/public/videos/{final_filename}",
            duration=total_duration,
            file_size_bytes=file_size,
            resolution="720x1280",
            render_time_sec=render_time
        )

        # 3. Synchronize with src/generatedData.json for Timeline & Studio View
        self._sync_to_studio_timeline(state)

        return state

    def _sync_to_studio_timeline(self, state: ProjectState) -> None:
        """Updates src/generatedData.json so the browser timeline and preview canvas load the result."""
        data_file = os.path.join(SRC_DIR, "generatedData.json")
        scenes_data = []

        active_assets = []
        if state.selected_track == "vector_infographic" and state.vector_assets:
            active_assets = state.vector_assets.assets
        elif state.media_assets:
            active_assets = state.media_assets.assets
        elif state.vector_assets:
            active_assets = state.vector_assets.assets

        for idx, sc in enumerate(state.storyboard.scenes):
            media = active_assets[idx] if idx < len(active_assets) else None
            vid_url = media.video_url if media else "/public/videos/test_dervish_anim.mp4"

            scenes_data.append({
                "id": f"scene_{sc.scene_id}",
                "startTime": sc.start,
                "endTime": sc.end,
                "duration": sc.duration,
                "headerSubtitle": sc.concept[:30],
                "headerLine1": sc.concept.split(",")[0][:25],
                "highlightedText": " ".join(sc.emphasis_keywords) or "HİKMET",
                "layoutType": sc.layout_type,
                "videoUrl": vid_url,
                "animationVideoUrl": vid_url,
                "brollType": "vector_infographic" if state.selected_track == "vector_infographic" else "cinematic_documentary",
                "spokenText": sc.spoken_text,
                "narration": sc.spoken_text
            })

        new_data = {
            "topic": f"🎬 Çoklu Ajan: {scenes_data[0]['headerLine1'] if scenes_data else 'Yeni Video'}",
            "theme": "dark_minimalist",
            "format": state.aspect_ratio or "9:16",
            "is_empty": False,
            "narration": state.transcription.clean_text,
            "audioUrl": state.audio_design.mixed_audio_url if state.audio_design else "/public/audio.mp3",
            "totalDuration": state.transcription.duration,
            "scenes": scenes_data,
            "subtitles": state.typography.subtitle_chunks if state.typography else [],
            "words": [w.dict() for w in state.transcription.words] if state.transcription else [],
            "brollType": "2d_animation",
            "finalVideoUrl": state.assembly.final_video_url,
            "created_at": time.strftime("%Y-%m-%d %H:%M:%S")
        }

        try:
            with open(data_file, "w", encoding="utf-8") as f:
                json.dump(new_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[Assembly Agent] generatedData.json sync error: {e}")

    def _validate_contract(self, state: ProjectState) -> None:
        if not state.assembly:
            raise ValueError("7. Ajan Kontrat Hatası: 'assembly' verisi oluşturulmadı!")
        if not os.path.exists(state.assembly.final_video_file):
            raise ValueError(f"7. Ajan Kontrat Hatası: Final video dosyası mevcut değil ({state.assembly.final_video_file})!")
        if state.assembly.file_size_bytes < 10000:
            raise ValueError("7. Ajan Kontrat Hatası: Final video boyutu bozuk veya 0 byte!")
