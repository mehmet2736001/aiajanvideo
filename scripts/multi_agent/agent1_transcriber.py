# -*- coding: utf-8 -*-
"""
Agent 1: Transkripsiyon ve Hizalama Ajanı (Speech & Timing Specialist)
Görevi: Sesi metne dökmek ve her kelimenin milisaniye hassasiyetindeki zaman damgalarını çıkarmak.
Girdi: Ham ses dosyası (audio_file).
Çıktı: Kelime ve cümle bazlı zaman damgası içeren TranscriptionData.
"""
import os
import subprocess
from typing import Optional, Callable
from .base_agent import BaseAgent
from .state import ProjectState, PipelinePhase, TranscriptionData, WordTiming


def probe_audio_duration(file_path: str) -> float:
    try:
        cmd = [
            "ffprobe", "-v", "error", "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1", file_path
        ]
        res = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return max(1.0, float(res.stdout.strip()))
    except Exception:
        return 15.0


class TranscribeAlignAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            agent_id=1,
            name="Transkripsiyon & Hizalama Ajanı",
            required_phase=PipelinePhase.PHASE_0_IDLE,
            target_phase=PipelinePhase.PHASE_1_TRANSCRIBED
        )

    def _process(
        self,
        state: ProjectState,
        on_progress: Optional[Callable[[int, str, dict], None]] = None
    ) -> ProjectState:
        if not os.path.exists(state.audio_file):
            raise FileNotFoundError(f"Ses dosyası bulunamadı: {state.audio_file}")

        total_duration = probe_audio_duration(state.audio_file)
        if on_progress:
            on_progress(self.agent_id, "running", {
                "message": f"Ses süresi ölçüldü: {total_duration:.2f}s. Whisper modeli yükleniyor..."
            })

        import whisper
        # Load fast & accurate whisper model
        whisper_model = whisper.load_model("tiny")

        if on_progress:
            on_progress(self.agent_id, "running", {
                "message": "Whisper milisaniye fonetik zamanlaması deşifre ediliyor..."
            })

        w_res = whisper_model.transcribe(
            state.audio_file,
            word_timestamps=True,
            language="tr",
            fp16=False
        )

        raw_words = []
        for seg in w_res.get("segments", []):
            for w in seg.get("words", []):
                w_text = w.get("word", "").strip()
                if w_text:
                    raw_words.append(
                        WordTiming(
                            word=w_text,
                            start=round(float(w.get("start", 0)), 2),
                            end=round(float(w.get("end", 0)), 2),
                            confidence=round(float(w.get("probability", 1.0)), 2)
                        )
                    )

        full_raw_text = w_res.get("text", "").strip()

        # If user passed custom transcript, use that text while maintaining acoustic anchor
        if state.custom_transcript and state.custom_transcript.strip():
            clean_text = state.custom_transcript.strip()
            # If whisper had words, retain timings; otherwise synthesize linear word timings
            if not raw_words:
                words_list = clean_text.split()
                dur_per_word = total_duration / max(1, len(words_list))
                raw_words = [
                    WordTiming(
                        word=w,
                        start=round(i * dur_per_word, 2),
                        end=round(min(total_duration, (i + 1) * dur_per_word), 2)
                    )
                    for i, w in enumerate(words_list)
                ]
        else:
            clean_text = full_raw_text or " ".join([w.word for w in raw_words])

        if not clean_text:
            clean_text = "Konuşma metni tespit edilemedi."

        # Populate state
        state.transcription = TranscriptionData(
            raw_text=full_raw_text,
            clean_text=clean_text,
            duration=round(total_duration, 2),
            words=raw_words,
            language=w_res.get("language", "tr")
        )

        return state

    def _validate_contract(self, state: ProjectState) -> None:
        if not state.transcription:
            raise ValueError("1. Ajan Kontrat Hatası: 'transcription' verisi oluşturulmadı!")
        if state.transcription.duration <= 0:
            raise ValueError("1. Ajan Kontrat Hatası: Ses süresi geçersiz (0 veya negatif)!")
        if not state.transcription.words and not state.transcription.clean_text:
            raise ValueError("1. Ajan Kontrat Hatası: Transkript kelimeleri boş olamaz!")
