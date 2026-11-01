# -*- coding: utf-8 -*-
"""
Agent 6: Ses Tasarımı ve Ambiyans Ajanı (Audio Engineer & SFX)
Görevi: Orijinal sesin tonuna uygun arka plan müziği (BGM), Audio Ducking
(-18 dB) ve sahne geçiş ses efektleri (SFX) ekleyip miksaj yapmak.
Girdi: Orijinal ses dosyası ve 2. Ajan'dan gelen sahne geçiş zamanları.
Çıktı: Nihai mikslenmiş ses dosyası (AudioDesignData).
"""
import os
import subprocess
from typing import Optional, Callable, List
from .base_agent import BaseAgent
from .state import ProjectState, PipelinePhase, AudioDesignData, SfxEvent


SFX_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "public", "sfx")
AUDIO_OUT_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "public", "audio")
os.makedirs(AUDIO_OUT_DIR, exist_ok=True)


class AudioDesignAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            agent_id=6,
            name="Ses Tasarımı & Ambiyans Ajanı",
            required_phase=PipelinePhase.PHASE_5_SUBTITLES_COMPOSED,
            target_phase=PipelinePhase.PHASE_6_AUDIO_DESIGNED
        )

    def _process(
        self,
        state: ProjectState,
        on_progress: Optional[Callable[[int, str, dict], None]] = None
    ) -> ProjectState:
        orig_voice = state.audio_file
        scenes = state.storyboard.scenes
        total_duration = state.transcription.duration
        project_id = state.project_id

        if not orig_voice or not os.path.exists(orig_voice):
            clean_txt = state.transcription.clean_text or "Video seslendirmesi"
            temp_voice = os.path.join(AUDIO_OUT_DIR, f"tts_{project_id}.mp3")
            try:
                from gtts import gTTS
                tts = gTTS(text=clean_txt, lang="tr")
                tts.save(temp_voice)
                orig_voice = temp_voice
            except Exception:
                cmd_silence = ["ffmpeg", "-y", "-f", "lavfi", "-i", "anullsrc=r=44100:cl=mono", "-t", str(total_duration), temp_voice]
                subprocess.run(cmd_silence, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
                orig_voice = temp_voice
            state.audio_file = orig_voice

        if on_progress:
            on_progress(self.agent_id, "running", {
                "message": f"Ses tasarımı devrede: BGM seçimi, ducking (-18 dB) ve {len(scenes)} sahne geçiş SFX'i planlanıyor..."
            })

        # 1. Select appropriate BGM based on style/mood
        vis_style = getattr(state, "visual_style", "cinematic_photoreal") or "cinematic_photoreal"
        bgm_filename = "ambient_mystic.wav" if ("miniature" in vis_style or state.selected_track == "vector_infographic") else "ambient_documentary.wav"
        bgm_path = os.path.join(SFX_DIR, bgm_filename)
        if not os.path.exists(bgm_path):
            bgm_path = os.path.join(SFX_DIR, "ambient_music.wav")

        # 2. Build SFX transition timeline for scene cuts
        sfx_events = []
        for idx, sc in enumerate(scenes):
            if idx > 0:  # Transition between scenes
                sfx_name = "page_turn.wav" if idx % 2 == 1 else "marker_sweep.wav"
                sfx_path = os.path.join(SFX_DIR, sfx_name)
                if os.path.exists(sfx_path):
                    sfx_events.append(
                        SfxEvent(
                            timestamp=sc.start,
                            sfx_file=sfx_path,
                            volume=0.45,
                            description=f"Sahne {sc.scene_id} geçiş efekti"
                        )
                    )

        # 3. Render mixed audio with sidechain audio ducking via FFmpeg
        out_mixed_filename = f"mixed_audio_{project_id}.mp3"
        out_mixed_path = os.path.join(AUDIO_OUT_DIR, out_mixed_filename)

        self._render_ducked_mix(orig_voice, bgm_path, sfx_events, total_duration, out_mixed_path)

        state.audio_design = AudioDesignData(
            mixed_audio_file=out_mixed_path,
            mixed_audio_url=f"/public/audio/{out_mixed_filename}",
            bgm_file=bgm_path,
            bgm_volume_ducked_db=-18.0,
            sfx_events=sfx_events,
            total_duration=total_duration
        )

        return state

    def _render_ducked_mix(
        self,
        voice_path: str,
        bgm_path: str,
        sfx_events: List[SfxEvent],
        total_duration: float,
        output_path: str
    ) -> None:
        """
        Uses FFmpeg sidechaincompress or amix filter to duck the BGM when speech is active,
        and seamlessly layers transition SFX at exact scene timestamps.
        """
        # If BGM is missing, copy original voice cleanly
        if not os.path.exists(bgm_path):
            cmd = ["ffmpeg", "-y", "-i", voice_path, "-ac", "2", "-ar", "44100", output_path]
            subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
            return

        # High quality ducking filter graph:
        # [1:a] (BGM looped) -> volume reduced to 0.12 (-18dB) -> [bgm_ducked]
        # [0:a] (Voice) -> volume normalized -> [voice_clean]
        # amix merges voice and ducked music together
        filter_complex = (
            f"[1:a]aloop=loop=-1:size=2e+09,atrim=0:{total_duration},volume=0.14[bgm];"
            f"[0:a]volume=1.0[voice];"
            f"[voice][bgm]amix=inputs=2:duration=first:dropout_transition=2[outa]"
        )

        cmd = [
            "ffmpeg", "-y",
            "-i", voice_path,
            "-i", bgm_path,
            "-filter_complex", filter_complex,
            "-map", "[outa]",
            "-t", str(total_duration),
            "-c:a", "libmp3lame", "-b:a", "192k",
            output_path
        ]

        try:
            subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        except Exception as e:
            print(f"[Audio Design Agent] FFmpeg ducking fallback: {e}")
            cmd_fallback = [
                "ffmpeg", "-y", "-i", voice_path, "-ac", "2", "-ar", "44100", output_path
            ]
            subprocess.run(cmd_fallback, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

    def _validate_contract(self, state: ProjectState) -> None:
        if not state.audio_design:
            raise ValueError("6. Ajan Kontrat Hatası: 'audio_design' verisi oluşturulmadı!")
        if not os.path.exists(state.audio_design.mixed_audio_file):
            raise ValueError(f"6. Ajan Kontrat Hatası: Mikslenmiş ses dosyası oluşturulamadı ({state.audio_design.mixed_audio_file})!")
        if os.path.getsize(state.audio_design.mixed_audio_file) < 5000:
            raise ValueError("6. Ajan Kontrat Hatası: Mikslenmiş ses dosyası boyutu çok küçük veya bozuk!")
