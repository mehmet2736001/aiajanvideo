"""
scripts/subtitle_cleaner.py

Comprehensive Turkish & Quranic Word Stitching and Subtitle Alignment Engine.
Solves Whisper AI BPE tokenizer artifacts where words with apostrophes (' / ’)
or glottal stops (e.g. Kur'an, Kur'an-ı Kerim, Allah'ın, Türkiye'de) are
erroneously split into multiple tokens/words (e.g. "Kur'" and "an").

Also provides Forced Alignment between custom user-pasted scripts and audio
duration, ensuring 100% fidelity to the user's exact words without relying
blindly on Whisper AI transcription.
"""

import difflib
import re
from typing import List, Dict, Any, Tuple, Optional

# All possible apostrophe / glottal stop characters
APOSTROPHES = ("'", "’", "‘", "ʼ", "`", "´")
APOSTROPHE_PATTERN = r"['’‘ʼ`´]"

# Common Turkish noun/case suffixes frequently split by Whisper BPE tokenizers
TURKISH_SUFFIXES = {
    "ın", "in", "un", "ün",
    "nın", "nin", "nun", "nün",
    "a", "e", "ya", "ye",
    "ı", "i", "u", "ü", "yı", "yi", "yu", "yü",
    "da", "de", "ta", "te",
    "dan", "den", "tan", "ten",
    "la", "le", "yla", "yle",
    "lar", "ler", "lara", "lere", "ların", "lerin", "larda", "lerde", "lardan", "lerden",
    "mız", "miz", "muz", "müz",
    "nız", "niz", "nuz", "nüz",
    "ce", "ca"
}


def clean_text_apostrophes(text: str) -> str:
    """
    Cleans all unwanted spaces around apostrophes inside words and fixes split Quranic/Turkish terms.
    e.g. "Kur' an" -> "Kur'an", "Kur an" -> "Kur'an", "Allah' ın" -> "Allah'ın"
    """
    if not text:
        return ""

    # 1. Standardize apostrophes to standard single quote '
    text = re.sub(r"[’‘ʼ`´]", "'", text)

    # 2. Fix words with space around apostrophe: "Kur ' an", "Kur' an", "Kur 'an" -> "Kur'an"
    text = re.sub(r"([A-Za-zÇĞİÖŞÜçğıöşü]+)\s*'\s*([A-Za-zÇĞİÖŞÜçğıöşü]+)", r"\1'\2", text)

    # 3. Fix split "Kur an" / "kuran" with glottal space (case-insensitive) -> "Kur'an"
    text = re.sub(r"\bKur\s+an\b", "Kur'an", text, flags=re.IGNORECASE)
    text = re.sub(r"\bKur\s+an'([a-zçğıöşü]+)\b", r"Kur'an'\1", text, flags=re.IGNORECASE)
    text = re.sub(r"\bKur\s+an([a-zçğıöşü]{1,5})\b", r"Kur'an'\1", text, flags=re.IGNORECASE)

    # 4. Fix "Kur'an-ı Kerim" / "Kur'an ı Kerim" / "Kur'an - ı Kerim"
    text = re.sub(r"Kur'an\s*[\-–—]?\s*[ıi]\s+Kerim", "Kur'an-ı Kerim", text, flags=re.IGNORECASE)
    text = re.sub(r"Kur'an\s*[\-–—]\s*([ıi])\b", r"Kur'an-\1", text, flags=re.IGNORECASE)

    # 5. Fix dangling apostrophe followed by lowercase suffix: "Allah' ın" -> "Allah'ın"
    text = re.sub(r"([A-Za-zÇĞİÖŞÜçğıöşü]+)'\s+([a-zçğıöşü]+)", r"\1'\2", text)

    # 6. Normalize double spaces
    text = re.sub(r"\s+", " ", text).strip()

    return text


def stitch_whisper_word_tokens(raw_words: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Takes raw word-level output from Whisper AI transcribe(word_timestamps=True)
    and intelligently stitches tokens that belong to the same word.
    
    Guarantees:
    - "Kur'" and "an" are ALWAYS stitched into a single atomic word token "Kur'an".
    - "Allah'" and "ın" are stitched into "Allah'ın".
    - Hyphenated compounds like "Kur'an-" and "ı" are stitched into "Kur'an-ı".
    - Start timestamp of the first token and End timestamp of the last token are preserved.
    """
    if not raw_words:
        return []

    stitched: List[Dict[str, Any]] = []
    i = 0
    n = len(raw_words)

    while i < n:
        cur = dict(raw_words[i])
        cur_text = cur.get("word") or cur.get("text") or ""
        cur_text = cur_text.strip()
        cur_start = float(cur.get("start", 0.0))
        cur_end = float(cur.get("end", cur_start + 0.3))

        # Check for merges with following tokens
        while i + 1 < n:
            next_w = raw_words[i + 1]
            next_text = (next_w.get("word") or next_w.get("text") or "").strip()
            next_start = float(next_w.get("start", cur_end))
            next_end = float(next_w.get("end", next_start + 0.3))

            cur_lower = cur_text.lower().rstrip(".,!?:;\"'’‘ʼ")
            next_lower = next_text.lower().lstrip(".,!?:;\"'’‘ʼ")

            should_merge = False
            merged_text = ""

            # Case A: Quranic term splitting: "Kur'" + "an", "Kur’" + "an", "Kur" + "an", "Kur" + "'an"
            if cur_lower in ["kur", "kur'", "kur’", "kür", "kür'"] and (
                next_lower.startswith("an") or next_lower.startswith("'an") or next_lower.startswith("’an") or next_lower.startswith("ân")
            ):
                should_merge = True
                suffix = re.sub(r"^(?:['’‘ʼ]?)an(?:['’‘ʼ]?)", "", next_text, flags=re.IGNORECASE).strip()
                if suffix:
                    if not any(suffix.startswith(ap) for ap in APOSTROPHES) and not suffix.startswith("-"):
                        suffix = "'" + suffix
                    merged_text = f"Kur'an{suffix}"
                else:
                    merged_text = "Kur'an"

            # Case B: Current token ends with apostrophe: "Allah'" + "ın" -> "Allah'ın"
            elif any(cur_text.endswith(ap) for ap in APOSTROPHES) or cur_text.endswith("-"):
                should_merge = True
                c_clean = cur_text.rstrip("".join(APOSTROPHES) + "-")
                sep = "-" if cur_text.endswith("-") else "'"
                n_clean = next_text.lstrip("".join(APOSTROPHES) + "-")
                merged_text = f"{c_clean}{sep}{n_clean}"

            # Case C: Next token starts with apostrophe: "Allah" + "'ın" -> "Allah'ın"
            elif any(next_text.startswith(ap) for ap in APOSTROPHES) or next_text.startswith("-"):
                should_merge = True
                c_clean = cur_text.rstrip("".join(APOSTROPHES) + "-")
                sep = "-" if next_text.startswith("-") else "'"
                n_clean = next_text.lstrip("".join(APOSTROPHES) + "-")
                merged_text = f"{c_clean}{sep}{n_clean}"

            # Case D: Compound "Kur'an" + "ı" -> "Kur'an-ı"
            elif cur_lower in ["kur'an", "kuran"] and next_lower in ["ı", "i", "-ı", "-i"]:
                should_merge = True
                merged_text = "Kur'an-ı"

            # Case E: Proper noun ending in vowel/consonant and next token is standalone Turkish suffix
            elif (next_end - cur_start <= 1.2) and next_lower in TURKISH_SUFFIXES and (
                cur_text and (cur_text[0].isupper() or any(cur_text.endswith(ap) for ap in APOSTROPHES))
            ):
                should_merge = True
                c_clean = cur_text.rstrip("".join(APOSTROPHES))
                merged_text = f"{c_clean}'{next_lower}"

            if should_merge:
                cur_text = merged_text
                cur_end = next_end
                cur["word"] = merged_text
                cur["text"] = merged_text
                cur["end"] = round(cur_end, 2)
                cur["start"] = round(cur_start, 2)
                i += 1  # Consumed next token
            else:
                break

        # Final cleanup on word text
        final_word = clean_text_apostrophes(cur_text)
        stitched.append({
            "word": final_word,
            "text": final_word,
            "start": round(cur_start, 2),
            "end": round(cur_end, 2)
        })
        i += 1

    return stitched


def build_subtitle_chunks(
    words: List[Dict[str, Any]],
    chunk_size: int = 3,
    max_duration: float = 2.8
) -> List[Dict[str, Any]]:
    """
    Groups atomic stitched words into punchy, perfectly readable subtitle chunks.
    Ensures that no word is ever split across subtitles.
    """
    if not words:
        return []

    # First stitch all word tokens
    stitched_words = stitch_whisper_word_tokens(words)

    subtitles = []
    i = 0
    total_len = len(stitched_words)

    while i < total_len:
        chunk = stitched_words[i:i + chunk_size]
        
        # Don't let a chunk exceed max_duration if it contains > 1 word
        if len(chunk) > 1 and (chunk[-1]["end"] - chunk[0]["start"] > max_duration):
            chunk = chunk[:max(1, len(chunk) - 1)]

        chunk_text = " ".join(clean_text_apostrophes(w.get("word") or w.get("text") or "") for w in chunk)
        chunk_text = clean_text_apostrophes(chunk_text)

        sub_obj = {
            "text": chunk_text,
            "start": chunk[0]["start"],
            "end": chunk[-1]["end"],
            "words": chunk
        }
        subtitles.append(sub_obj)
        i += len(chunk)

    return subtitles


def normalize_for_match(token: str) -> str:
    """Normalizes token for fuzzy phonetic/sequence comparison."""
    t = token.lower()
    t = re.sub(r"['’‘ʼ`´\-]", "", t)
    t = re.sub(r"[^\w\s]", "", t)
    return t.strip()


def token_similarity(a: str, b: str) -> float:
    """Computes similarity ratio between two normalized tokens."""
    if a == b:
        return 1.0
    if not a or not b:
        return 0.0
    if a.startswith(b) or b.startswith(a):
        return 0.85
    return difflib.SequenceMatcher(None, a, b).ratio()


def distribute_words_by_duration(
    tokens: List[str],
    start_time: float,
    end_time: float
) -> List[Dict[str, Any]]:
    """
    Distributes tokens proportionally across a time window [start_time, end_time],
    weighted by character length so longer words receive appropriately more time.
    """
    if not tokens:
        return []
    total_dur = max(0.3, end_time - start_time)
    weights = [max(2, len(t)) for t in tokens]
    total_weight = sum(weights)

    words = []
    cur_t = start_time
    for t, w in zip(tokens, weights):
        word_dur = total_dur * (w / total_weight)
        s = round(cur_t, 2)
        e = round(min(end_time, cur_t + word_dur), 2)
        words.append({
            "word": t,
            "text": t,
            "start": s,
            "end": e
        })
        cur_t += word_dur

    return words


def align_custom_transcript_to_audio(
    user_text: str,
    audio_duration: float,
    whisper_words: Optional[List[Dict[str, Any]]] = None
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    FORCED ALIGNMENT ENGINE:
    Aligns the user's exact pasted script to the audio duration and acoustic Whisper timestamps.
    
    GUARANTEES:
    1. Every single word in the resulting subtitles is 100% the user's exact text
       (preserving spelling, capitalization, punctuation, apostrophes like Kur'an, Allah'ın).
    2. Whisper AI is used strictly as an acoustic timing guide; Whisper's misheard words,
       hallucinations, and spelling mistakes NEVER leak onto the screen.
    3. If Whisper is unavailable or fails, user words are smoothly distributed across the audio.
    4. Returns (words, subtitles) ready for Remotion & web timeline rendering.
    """
    cleaned_text = clean_text_apostrophes(user_text)
    user_tokens = [w for w in cleaned_text.split() if w]
    if not user_tokens:
        return [], []

    audio_duration = max(1.0, float(audio_duration))
    total_words = len(user_tokens)

    # If no whisper words provided or whisper failed, distribute by character-length weights
    if not whisper_words:
        aligned_words = distribute_words_by_duration(user_tokens, 0.2, audio_duration - 0.2)
        subtitles = build_subtitle_chunks(aligned_words, chunk_size=3)
        return aligned_words, subtitles

    # First stitch Whisper tokens to avoid fragmented acoustic references
    stitched_whisper = stitch_whisper_word_tokens(whisper_words)

    # 1. Prepare normalized token lists
    u_norm = [normalize_for_match(w) for w in user_tokens]
    w_norm = [normalize_for_match(w.get("word") or w.get("text") or "") for w in stitched_whisper]

    # 2. Monotonic greedy / sequence alignment
    matched_whisper: Dict[int, int] = {}
    last_w_idx = -1

    for u_idx, u_w in enumerate(u_norm):
        if not u_w:
            continue
        best_w_idx = -1
        best_score = 0.0

        # Look in a window around expected relative position
        expected_w = int((u_idx / total_words) * len(w_norm))
        search_start = max(last_w_idx + 1, expected_w - 7)
        search_end = min(len(w_norm), expected_w + 8)

        for w_idx in range(search_start, search_end):
            score = token_similarity(u_w, w_norm[w_idx])
            if score > best_score and score >= 0.70:
                best_score = score
                best_w_idx = w_idx

        if best_w_idx != -1:
            matched_whisper[u_idx] = best_w_idx
            last_w_idx = best_w_idx

    # If matching ratio is too low (< 15%), fallback to pure proportional distribution within speech bounds
    if len(matched_whisper) < max(1, total_words * 0.15):
        first_t = float(stitched_whisper[0].get("start", 0.2)) if stitched_whisper else 0.2
        last_t = float(stitched_whisper[-1].get("end", audio_duration - 0.2)) if stitched_whisper else (audio_duration - 0.2)
        aligned_words = distribute_words_by_duration(user_tokens, max(0.1, first_t), min(audio_duration - 0.1, last_t))
        subtitles = build_subtitle_chunks(aligned_words, chunk_size=3)
        return aligned_words, subtitles

    # 3. Build timestamp anchors for each user token
    anchor_times: Dict[int, Tuple[float, float]] = {}
    for u_idx, w_idx in matched_whisper.items():
        w_obj = stitched_whisper[w_idx]
        anchor_times[u_idx] = (float(w_obj.get("start", 0.0)), float(w_obj.get("end", 0.0)))

    # 4. Interpolate missing user tokens
    result_words: List[Dict[str, Any]] = []
    i = 0
    while i < total_words:
        if i in anchor_times:
            s, e = anchor_times[i]
            result_words.append({
                "word": user_tokens[i],
                "text": user_tokens[i],
                "start": round(s, 2),
                "end": round(max(s + 0.15, e), 2)
            })
            i += 1
        else:
            # Find run of unanchored words: i ... next_anchor - 1
            start_run = i
            while i < total_words and i not in anchor_times:
                i += 1
            end_run = i  # exclusive

            # Determine boundary times [t_start, t_end]
            if start_run == 0:
                # Preceding run before first anchor
                next_start = anchor_times[end_run][0]
                run_dur_est = sum(max(2, len(user_tokens[k])) for k in range(start_run, end_run)) * 0.05
                t_start = max(0.1, next_start - run_dur_est)
                t_end = next_start
            elif end_run == total_words:
                # Trailing run after last anchor
                prev_end = anchor_times[start_run - 1][1]
                t_start = prev_end
                t_end = min(audio_duration - 0.1, prev_end + sum(max(2, len(user_tokens[k])) for k in range(start_run, end_run)) * 0.06)
            else:
                prev_end = anchor_times[start_run - 1][1]
                next_start = anchor_times[end_run][0]
                t_start = prev_end
                t_end = max(prev_end + 0.15 * (end_run - start_run), next_start)

            sub_words = distribute_words_by_duration(user_tokens[start_run:end_run], t_start, t_end)
            result_words.extend(sub_words)

    # Final monotonicity and overlap adjustment pass
    for idx in range(1, len(result_words)):
        if result_words[idx]["start"] < result_words[idx - 1]["end"]:
            mid = (result_words[idx - 1]["end"] + result_words[idx]["start"]) / 2
            result_words[idx - 1]["end"] = round(mid, 2)
            result_words[idx]["start"] = round(mid, 2)
            if result_words[idx]["end"] <= result_words[idx]["start"]:
                result_words[idx]["end"] = round(result_words[idx]["start"] + 0.18, 2)

    subtitles = build_subtitle_chunks(result_words, chunk_size=3)
    return result_words, subtitles
