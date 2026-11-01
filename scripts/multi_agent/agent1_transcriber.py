# -*- coding: utf-8 -*-
"""
Agent 1: Ses / Metin Ayrıştırma Ajanı (Transcribe & Text Parsing Agent)
Görevi:
  1. Girdi ses ise Whisper/faster-whisper ile milisaniye hassasiyetinde kelime zamanlamalarını çıkarır.
  2. Girdi metin ise metni cümle bazlı sahnelere böler ve tahmini konuşma sürelerini hesaplar.
"""
import os
import re
import subprocess
from typing import Optional, Callable, List
from .base_agent import BaseAgent
from .state import ProjectState, PipelinePhase, TranscriptionData, WordTiming, SentenceBeat


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


def estimate_turkish_text_duration(text: str) -> float:
    """
    Estimates natural Turkish speaking duration:
    Average rate: ~2.8 words/second, +0.35s punctuation pauses.
    """
    words = [w for w in text.split() if w.strip()]
    if not words:
        return 6.0
    word_count = len(words)
    comma_count = text.count(",") + text.count(";")
    period_count = text.count(".") + text.count("!") + text.count("?")
    
    base_sec = word_count / 2.7
    pause_sec = (comma_count * 0.25) + (period_count * 0.45)
    return round(max(5.0, base_sec + pause_sec), 2)


def split_text_into_sentences(text: str) -> List[str]:
    clean = re.sub(r"\s+", " ", text).strip()
    sentences = re.split(r"(?<=[.!?…])\s+", clean)
    filtered = [s.strip() for s in sentences if len(s.strip()) > 3]
    if not filtered:
        return [clean] if clean else ["Başlangıç sahnesi"]
    return filtered


class TranscribeAlignAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            agent_id=1,
            name="Ses / Metin Ayrıştırma Ajanı",
            required_phase=PipelinePhase.PHASE_0_IDLE,
            target_phase=PipelinePhase.PHASE_1_TRANSCRIBED
        )

    def _process(
        self,
        state: ProjectState,
        on_progress: Optional[Callable[[int, str, dict], None]] = None
    ) -> ProjectState:
        has_audio = bool(state.audio_file and os.path.exists(state.audio_file))
        raw_text = (state.raw_input_text or state.custom_transcript or "").strip()

        # PATH A: Audio Input provided
        if has_audio:
            state.input_type = "audio"
            total_duration = probe_audio_duration(state.audio_file)
            if on_progress:
                on_progress(self.agent_id, "running", {
                    "message": f"Ses süresi: {total_duration:.2f}s. Whisper modeli kelime zamanlamalarını çıkarıyor..."
                })

            raw_words: List[WordTiming] = []
            full_transcript = ""
            try:
                import whisper
                whisper_model = whisper.load_model("tiny")
                w_res = whisper_model.transcribe(
                    state.audio_file,
                    word_timestamps=True,
                    language="tr",
                    fp16=False
                )
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
                full_transcript = (w_res.get("text", "") or "").strip()
            except Exception as we:
                print(f"[Agent 1 Transcribe Notice] Whisper fallback: {we}")

            clean_text = raw_text if raw_text else (full_transcript or " ".join([w.word for w in raw_words]) or "Bilinmeyen ses kaydı")

            if not raw_words and clean_text:
                all_w = clean_text.split()
                w_dur = total_duration / max(1, len(all_w))
                for wi, wrd in enumerate(all_w):
                    raw_words.append(WordTiming(
                        word=wrd,
                        start=round(wi * w_dur, 2),
                        end=round((wi + 1) * w_dur, 2),
                        confidence=0.95
                    ))

            # Split into sentence beats using whisper word timestamps
            sentences = split_text_into_sentences(clean_text)
            sentence_beats: List[SentenceBeat] = []
            cur_idx = 0

            for s_idx, sent in enumerate(sentences):
                sent_words = [w.strip() for w in sent.split()]
                if not sent_words:
                    continue
                match_words = raw_words[cur_idx:cur_idx + len(sent_words)]
                if match_words:
                    s_start = match_words[0].start
                    s_end = match_words[-1].end
                    cur_idx += len(sent_words)
                else:
                    s_start = round(s_idx * (total_duration / len(sentences)), 2)
                    s_end = round((s_idx + 1) * (total_duration / len(sentences)), 2)

                sentence_beats.append(
                    SentenceBeat(
                        sentence_id=s_idx + 1,
                        text=sent,
                        start=s_start,
                        end=s_end,
                        duration=round(max(1.0, s_end - s_start), 2),
                        emphasis_words=sent_words[:2]
                    )
                )

            state.transcription = TranscriptionData(
                input_type="audio",
                raw_text=full_transcript,
                clean_text=clean_text,
                duration=total_duration,
                words=raw_words,
                sentence_beats=sentence_beats,
                language="tr"
            )

        # PATH B: Pure Text Input provided
        else:
            state.input_type = "text"
            if not raw_text:
                raw_text = "Tefekkür ve hakikat arayışında sabır ve ilmin önemi."

            total_duration = estimate_turkish_text_duration(raw_text)
            sentences = split_text_into_sentences(raw_text)

            if on_progress:
                on_progress(self.agent_id, "running", {
                    "message": f"Metin {len(sentences)} sahneye bölünüyor, tahmini konuşma süresi: {total_duration:.1f}s..."
                })

            all_words = raw_text.split()
            dur_per_word = total_duration / max(1, len(all_words))
            synth_words: List[WordTiming] = []

            for i, w in enumerate(all_words):
                st = round(i * dur_per_word, 2)
                en = round(min(total_duration, (i + 1) * dur_per_word), 2)
                synth_words.append(WordTiming(word=w, start=st, end=en, confidence=0.98))

            sentence_beats: List[SentenceBeat] = []
            dur_per_sent = total_duration / max(1, len(sentences))
            for s_idx, sent in enumerate(sentences):
                s_start = round(s_idx * dur_per_sent, 2)
                s_end = round((s_idx + 1) * dur_per_sent, 2)
                sent_words = [w.strip() for w in sent.split()]
                sentence_beats.append(
                    SentenceBeat(
                        sentence_id=s_idx + 1,
                        text=sent,
                        start=s_start,
                        end=s_end,
                        duration=round(max(1.0, s_end - s_start), 2),
                        emphasis_words=sent_words[:2]
                    )
                )

            state.transcription = TranscriptionData(
                input_type="text",
                raw_text=raw_text,
                clean_text=raw_text,
                duration=total_duration,
                words=synth_words,
                sentence_beats=sentence_beats,
                language="tr"
            )

        return state

    def _validate_contract(self, state: ProjectState) -> None:
        if not state.transcription:
            raise ValueError("TranscribeAlignAgent kontrat hatası: transcription objesi boş!")
        if state.transcription.duration <= 0:
            raise ValueError("TranscribeAlignAgent kontrat hatası: süre sıfır veya negatif!")
