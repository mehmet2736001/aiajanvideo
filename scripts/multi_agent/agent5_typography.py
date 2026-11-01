# -*- coding: utf-8 -*-
"""
Agent 5: Dinamik Tipografi ve Altyazı Ajanı (Motion Subtitle Specialist)
Görevi: 1. Ajan'dan gelen kelime bazlı zaman damgalarını modern sosyal medya tarzı
vurgulu altyazılara (.ass dosyası ve zaman tüneli JSON katmanı) dönüştürmek.
Girdi: 1. Ajan'dan gelen TranscriptionData kelime zamanlamaları.
Çıktı: Doğrulanmış .ass altyazı dosyası ve JSON chunk'ları (TypographyData).
"""
import os
import math
from typing import Optional, Callable, List, Dict, Any
from .base_agent import BaseAgent
from .state import ProjectState, PipelinePhase, TypographyData, WordTiming


SUBTITLES_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "public", "subtitles")
os.makedirs(SUBTITLES_DIR, exist_ok=True)


def format_ass_time(seconds: float) -> str:
    """Formats float seconds into ASS time format: H:MM:SS.cc"""
    hrs = int(seconds // 3600)
    mins = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    centis = int(round((seconds - int(seconds)) * 100))
    if centis >= 100:
        centis = 99
    return f"{hrs}:{mins:02d}:{secs:02d}.{centis:02d}"


class TypographyAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            agent_id=5,
            name="Dinamik Tipografi & Altyazı Ajanı",
            required_phase=PipelinePhase.PHASE_4_ASSETS_GENERATED,
            target_phase=PipelinePhase.PHASE_5_SUBTITLES_COMPOSED
        )

    def can_execute(self, state: ProjectState):
        valid_phases = [
            PipelinePhase.PHASE_4_ASSETS_GENERATED,
            PipelinePhase.PHASE_4A_DIFFUSION_RENDERED,
            PipelinePhase.PHASE_4B_REMOTION_RENDERED
        ]
        if state.current_phase not in valid_phases:
            return (
                False,
                f"Kural İhlali: [{self.agent_id}. {self.name}] çalıştırılamaz! "
                f"Gerekli Aşama: 4A (Difüzyon) veya 4B (Remotion), Mevcut Aşama: '{state.current_phase.value}'."
            )
        return True, "Geçerli"

    def _process(
        self,
        state: ProjectState,
        on_progress: Optional[Callable[[int, str, dict], None]] = None
    ) -> ProjectState:
        words = state.transcription.words
        total_dur = state.transcription.duration

        if on_progress:
            on_progress(self.agent_id, "running", {
                "message": f"Dinamik tipografi üretiliyor: {len(words)} kelime viral altyazı formatına işleniyor..."
            })

        project_id = state.project_id
        ass_filename = f"subtitles_{project_id}.ass"
        ass_path = os.path.join(SUBTITLES_DIR, ass_filename)

        # Generate 2 to 3 word chunks for fast modern cadence
        chunks = self._build_word_chunks(words, total_dur, chunk_size=3)

        # Generate ASS subtitle script with dynamic karaoke color highlights
        self._write_ass_file(ass_path, chunks)

        state.typography = TypographyData(
            ass_file_path=ass_path,
            ass_url=f"/public/subtitles/{ass_filename}",
            subtitle_chunks=chunks,
            style_name="TikTok_Gold_Pop",
            font_name="Arial",
            primary_color="&H00FFFFFF",
            highlight_color="&H0000D7FF"
        )

        return state

    def _build_word_chunks(
        self,
        words: List[WordTiming],
        total_duration: float,
        chunk_size: int = 3
    ) -> List[Dict[str, Any]]:
        chunks = []
        if not words:
            return chunks

        for i in range(0, len(words), chunk_size):
            group = words[i: i + chunk_size]
            if not group:
                continue
            st = group[0].start
            en = group[-1].end
            text = " ".join([w.word for w in group])

            chunks.append({
                "start": st,
                "end": max(st + 0.4, en),
                "text": text,
                "words": [{"word": w.word, "start": w.start, "end": w.end} for w in group]
            })

        return chunks

    def _write_ass_file(self, filepath: str, chunks: List[Dict[str, Any]]) -> None:
        """Writes stylized ASS subtitle file with bold typography and active word highlights."""
        ass_content = [
            "[Script Info]",
            "Title: Dynamic Motion Viral Subtitles",
            "ScriptType: v4.00+",
            "WrapStyle: 0",
            "ScaledBorderAndShadow: yes",
            "PlayResX: 720",
            "PlayResY: 1280",
            "",
            "[V4+ Styles]",
            "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
            "Style: KineticGold,Arial,48,&H00FFFFFF,&H000000FF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,3.5,2.0,2,40,40,160,1",
            "",
            "[Events]",
            "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text"
        ]

        for chunk in chunks:
            group_words = chunk.get("words", [])
            c_start = format_ass_time(chunk["start"])
            c_end = format_ass_time(chunk["end"])

            # Highlight each word dynamically during its active timestamp window
            if len(group_words) > 1:
                for idx, w in enumerate(group_words):
                    w_st = format_ass_time(w["start"])
                    w_en = format_ass_time(w["end"])

                    # Reconstruct line with word 'idx' highlighted in gold (&H0000D7FF)
                    line_parts = []
                    for j, other_w in enumerate(group_words):
                        if j == idx:
                            line_parts.append(r"{\c&H0000D7FF\b1}" + other_w["word"] + r"{\c&H00FFFFFF\b0}")
                        else:
                            line_parts.append(other_w["word"])

                    dialogue_text = " ".join(line_parts)
                    ass_content.append(f"Dialogue: 0,{w_st},{w_en},KineticGold,,0,0,0,,{dialogue_text}")
            else:
                raw_text = r"{\c&H0000D7FF\b1}" + chunk["text"] + r"{\c&H00FFFFFF\b0}"
                ass_content.append(f"Dialogue: 0,{c_start},{c_end},KineticGold,,0,0,0,,{raw_text}")

        with open(filepath, "w", encoding="utf-8") as f:
            f.write("\n".join(ass_content))

    def _validate_contract(self, state: ProjectState) -> None:
        if not state.typography:
            raise ValueError("5. Ajan Kontrat Hatası: 'typography' verisi oluşturulmadı!")
        if not os.path.exists(state.typography.ass_file_path):
            raise ValueError(f"5. Ajan Kontrat Hatası: .ass altyazı dosyası fiziksel olarak bulunamadı ({state.typography.ass_file_path})!")
        if not state.typography.subtitle_chunks:
            raise ValueError("5. Ajan Kontrat Hatası: Altyazı chunk listesi boş!")
