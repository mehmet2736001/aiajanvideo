"""
scripts/subtitle_cleaner.py

Comprehensive Turkish & Quranic Word Stitching and Subtitle Alignment Engine.
Solves Whisper AI BPE tokenizer artifacts where words with apostrophes (' / ’)
or glottal stops (e.g. Kur'an, Kur'an-ı Kerim, Allah'ın, Türkiye'de) are
erroneously split into multiple tokens/words (e.g. "Kur'" and "an").
"""

import re
from typing import List, Dict, Any, Tuple

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
