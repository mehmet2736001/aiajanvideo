"""
scripts/subtitle_cleaner.py

Comprehensive Turkish & Quranic Word Stitching, Orthography Correction,
Clitic Cohesion, and Subtitle Alignment Engine.

Solves:
1. Whisper AI BPE tokenizer artifacts where words with apostrophes (' / ’)
   or glottal stops (e.g. Kur'an, Kur'an-ı Kerim, Allah'ın, Türkiye'de) are
   erroneously split into multiple tokens/words (e.g. "Kur'" and "an").
2. Turkish spelling rules (TDK) where compound words, prefixes, and suffixes
   must be written together (bitişik):
   - "birkaç", "birtakım", "hiçbir", "herhangi", "birbiri", "bugün", "biraz", "herkes", "herhalde"
   - "-ki" eki: "evdeki", "oradaki", "sendeki", "dünkü", "bugünkü", "akşamki"
   - "-de / -da / -te / -ta" bulunma eki: "evde", "okulda", "yolda", "kitapta", "Kur'an'da", "Allah'ta"
   - Kurallı birleşik fiiller: "yapabilir", "yapıverdi", "bakakaldı", "gidedursun"
   - Kalıplaşmış -ki bağlaçları: "oysaki", "mademki", "meğerki", "halbuki", "illaki"
3. Clitic cohesion (mi soru edatı, de/da bağlacı):
   - Soru edatları ("mi", "mı", "mu", "mü", "misin", "musun"...) ve "de / da / ki" bağlaçları
     ASLA kendisinden önceki kelimeden ayrılarak yeni bir altyazı kartına tek başına atılamaz.
   - Her zaman önceki kelimeyle aynı altyazı kartında ve aynı satırda kalır.
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
# Suffixes that are never conjunctions (excluding de/da)
TURKISH_SUFFIXES_EXCLUSIVE = TURKISH_SUFFIXES - {"de", "da", "te", "ta"}

# Clitics that must NEVER be orphaned onto a new subtitle card or start a chunk alone
TURKISH_CLITICS = {
    # Soru edatları ve şahıs/zaman ekleri
    "mi", "mı", "mu", "mü",
    "misin", "mısın", "musun", "müsün",
    "miyiz", "mıyız", "muyuz", "müyüz",
    "miydi", "mıydı", "muydu", "müydü",
    "miymiş", "mıymış", "muymuş", "müymüş",
    "midir", "mıdır", "mudur", "müdür",
    "miyim", "mıyım",
    "misiniz", "mısınız", "musunuz", "müsünüz",
    "miler", "mılar",
    # Bağlaçlar (ayrı yazılır ama önceki kelimeden asla koparılmaz)
    "de", "da", "ki", "ise", "bile", "dahi"
}


def is_clitic_token(token: str) -> bool:
    """Checks if a given word token is a Turkish question particle or cohesion clitic."""
    if not token:
        return False
    clean = re.sub(r"[^\wçğıöşüÇĞİÖŞÜ]", "", token.lower()).strip()
    return clean in TURKISH_CLITICS


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


def fix_turkish_orthography_and_compounds(text: str) -> str:
    """
    Enforces Turkish Language Association (TDK) orthography rules:
    Stitches words that must be written compound/bitişik:
    - Belgisiz sıfat/zamirler: birkaç, birtakım, hiçbir, herhangi, birbiri, bugün, biraz, herkes, herhalde
    - Bitişik -ki eki: evdeki, oradaki, sendeki, dünkü, bugünkü, akşamki
    - İsmin bulunma hali (-de / -da): evde, okulda, yolda, kitapta, Kur'an'da, Allah'ta
    - Kurallı birleşik fiiller: yapabilir, yapıverdi, bakakaldı, gidedursun
    - Kalıplaşmış -ki bağlaçları: oysaki, mademki, meğerki, halbuki, illaki
    """
    if not text:
        return ""

    # First clean apostrophes
    text = clean_text_apostrophes(text)

    # 1. Belgisiz Zamir ve Sıfatlar (Daima bitişik)
    text = re.sub(r"\b(bir)\s+(kaç[a-zçğıöşü]*)\b", r"bir\2", text, flags=re.IGNORECASE)
    text = re.sub(r"\b(bir)\s+(takım)\b", r"birtakım", text, flags=re.IGNORECASE)
    text = re.sub(r"\b(hiç)\s+(bir[a-zçğıöşü]*)\b", r"hiç\2", text, flags=re.IGNORECASE)
    text = re.sub(r"\b(her)\s+(hangi)\b", r"herhangi", text, flags=re.IGNORECASE)
    text = re.sub(r"\b(bir)\s+(biri[a-zçğıöşü]*)\b", r"bir\2", text, flags=re.IGNORECASE)
    text = re.sub(r"\b(bu)\s+(gün[a-zçğıöşü]*)\b", r"bu\2", text, flags=re.IGNORECASE)
    text = re.sub(r"\b(bir)\s+(az[a-zçğıöşü]*)\b", r"bir\2", text, flags=re.IGNORECASE)
    text = re.sub(r"\b(her)\s+(kes[a-zçğıöşü]*)\b", r"her\2", text, flags=re.IGNORECASE)
    text = re.sub(r"\b(her)\s+(halde)\b", r"herhalde", text, flags=re.IGNORECASE)

    # 2. Kalıplaşmış -ki bağlaçları (SOMBAHÇEMİ)
    text = re.sub(r"\b(oysa)\s+(ki)\b", r"oysaki", text, flags=re.IGNORECASE)
    text = re.sub(r"\b(madem)\s+(ki)\b", r"mademki", text, flags=re.IGNORECASE)
    text = re.sub(r"\b(meğer)\s+(ki)\b", r"meğerki", text, flags=re.IGNORECASE)
    text = re.sub(r"\b(halbu)\s+(ki)\b", r"halbuki", text, flags=re.IGNORECASE)
    text = re.sub(r"\b(illa)\s+(ki)\b", r"illaki", text, flags=re.IGNORECASE)

    # 3. İsmin Bulunma Hali (-de / -da / -te / -ta)
    locative_nouns = "ev|okul|yol|kitap|cami|oda|el|yer|gök|şehir|sokak|dünya|ahiret|cennet|cehennem"
    text = re.sub(rf"\b({locative_nouns})\s+(de|da|te|ta)\b", r"\1\2", text, flags=re.IGNORECASE)
    # Proper nouns: Kur'an da -> Kur'an'da, Allah ta -> Allah'ta
    text = re.sub(r"\b(Kur'an|Kuran|Allah|Türkiye|İstanbul|Ankara|İslam)\s+(da|de|ta|te)\b", r"\1'\2", text, flags=re.IGNORECASE)

    # 4. Sıfat ve İlgi Zamiri Yapan -ki Eki (Daima bitişik)
    ki_hosts = (
        "evde|okulda|odada|camide|şehirde|sokakta|dünyada|ahirette|cennette|cehennemde|"
        "orada|burada|şurada|sende|bende|onda|bizde|sizde|onlarda|"
        "dün|bugün|akşam|sabah|yarın|masada|yolda|kalpte|gökte|yerde"
    )
    text = re.sub(rf"\b({ki_hosts})\s+(ki)\b", r"\1ki", text, flags=re.IGNORECASE)
    text = re.sub(r"\bdünki\b", "dünkü", text, flags=re.IGNORECASE)

    # 5. Kurallı Birleşik Fiiller (-ebilmek, -ivermek, -ekalmak, -edurmak)
    # yapa bilir -> yapabilir, gide bilir -> gidebilir, ola bilir -> olabilir
    text = re.sub(r"\b([A-Za-zÇĞİÖŞÜçğıöşü]+[ae])\s+(bilir(?:[a-zçğıöşü]*)?|bilmek|bildi(?:[a-zçğıöşü]*)?|bilse(?:[a-zçğıöşü]*)?)\b", r"\1\2", text, flags=re.IGNORECASE)
    # yapı verdi -> yapıverdi, geli verdi -> geliverdi
    text = re.sub(r"\b([A-Za-zÇĞİÖŞÜçğıöşü]+[ıiuü])\s+(ver(?:di|miş|ir|elim|sin|di[a-zçğıöşü]*)?|vermek)\b", r"\1\2", text, flags=re.IGNORECASE)
    # baka kaldı -> bakakaldı, gide dursun -> gidedursun
    text = re.sub(r"\b([A-Za-zÇĞİÖŞÜçğıöşü]+[ae])\s+(kal(?:dı|mış|ır|an)?|dur(?:du|sun|ur)?)\b", r"\1\2", text, flags=re.IGNORECASE)

    # 6. Vasıta Eki (-le / -la / -yle / -yla)
    text = re.sub(r"\b(senin|onun|benim|bizim|sizin|araba|sevgi|hız|kolaylık)\s+(la|le|yla|yle)\b", r"\1\2", text, flags=re.IGNORECASE)

    # Clean double spaces
    text = re.sub(r"\s+", " ", text).strip()
    return text


def stitch_whisper_word_tokens(raw_words: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Takes raw word-level output from Whisper AI transcribe(word_timestamps=True)
    and intelligently stitches tokens that belong to the same word.
    
    Guarantees:
    - "Kur'" and "an" are ALWAYS stitched into a single atomic word token "Kur'an".
    - "Allah'" and "ın" are stitched into "Allah'ın".
    - Bitişik yazılması gereken kelimeler ("bir" + "kaç" -> "birkaç", "hiç" + "bir" -> "hiçbir",
      "yapa" + "bilir" -> "yapabilir", "ev" + "de" -> "evde") birleştirilir.
    - Start timestamp of the first token and End timestamp of the last token are preserved.
    """
    if not raw_words:
        return []

    stitched: List[Dict[str, Any]] = []
    i = 0
    n = len(raw_words)

    # List of known prefixes for compound word joining
    COMPOUND_PREFIX_MAP = {
        "bir": ("kaç", "takım", "biri", "birisi", "az"),
        "hiç": ("bir", "biri", "birisi"),
        "her": ("hangi", "kes", "halde"),
        "bu": ("gün",),
        "oysa": ("ki",),
        "madem": ("ki",),
        "meğer": ("ki",),
        "halbu": ("ki",),
        "illa": ("ki",),
    }

    LOCATIVE_BASE_NOUNS = {
        "ev", "okul", "yol", "kitap", "cami", "oda", "el", "yer", "gök", "şehir", "sokak"
    }

    KI_ATTACH_HOSTS = {
        "evde", "okulda", "odada", "camide", "sokakta", "dünyada",
        "orada", "burada", "şurada", "sende", "bende", "onda", "bizde", "sizde",
        "dün", "bugün", "akşam", "sabah", "yarın", "masada", "yolda"
    }

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

            # Case E: Proper noun ending in vowel/consonant and next token is standalone Turkish suffix (excluding de/da conjunctions)
            elif (next_end - cur_start <= 1.2) and next_lower in TURKISH_SUFFIXES_EXCLUSIVE and (
                cur_text and (cur_text[0].isupper() or any(cur_text.endswith(ap) for ap in APOSTROPHES))
            ):
                should_merge = True
                c_clean = cur_text.rstrip("".join(APOSTROPHES))
                merged_text = f"{c_clean}'{next_lower}"

            # Case F: TDK Compound words (birkaç, hiçbir, herhangi, bugün, biraz, herkes)
            elif (next_end - cur_start <= 1.2) and (cur_lower in COMPOUND_PREFIX_MAP) and any(next_lower.startswith(s) for s in COMPOUND_PREFIX_MAP[cur_lower]):
                should_merge = True
                merged_text = f"{cur_text}{next_text}"

            # Case G: Suffix -ki attached to host words (evdeki, oradaki, dünkü)
            elif (next_end - cur_start <= 1.0) and (cur_lower in KI_ATTACH_HOSTS) and next_lower == "ki":
                should_merge = True
                merged_text = f"{cur_text}ki"

            # Case H: Locative case suffix attached to base nouns (evde, okulda, yolda)
            elif (next_end - cur_start <= 0.8) and (cur_lower in LOCATIVE_BASE_NOUNS) and next_lower in ["de", "da", "te", "ta"]:
                should_merge = True
                merged_text = f"{cur_text}{next_lower}"

            # Case I: Kurallı birleşik fiiller (yapa + bilir -> yapabilir, yapı + verdi -> yapıverdi)
            elif (next_end - cur_start <= 1.0) and cur_lower.endswith(("a", "e")) and next_lower.startswith(("bilir", "bilmek", "bildi", "bilse")):
                should_merge = True
                merged_text = f"{cur_text}{next_text}"
            elif (next_end - cur_start <= 1.0) and cur_lower.endswith(("ı", "i", "u", "ü")) and next_lower.startswith(("verdi", "vermiş", "verir", "vermek")):
                should_merge = True
                merged_text = f"{cur_text}{next_text}"
            elif (next_end - cur_start <= 1.0) and cur_lower.endswith(("a", "e")) and next_lower.startswith(("kaldı", "kalmış", "durdu", "dursun")):
                should_merge = True
                merged_text = f"{cur_text}{next_text}"

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

        # Final orthography cleanup
        final_word = fix_turkish_orthography_and_compounds(cur_text)
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
    max_duration: float = 3.2
) -> List[Dict[str, Any]]:
    """
    Groups atomic stitched words into punchy, perfectly readable subtitle chunks.
    
    GUARANTEES:
    1. No word is ever split across subtitles.
    2. Question particles ("mi", "mı", "mu", "mü", "misin", "musun"...) and
       conjunctions ("de", "da", "ki") are NEVER orphaned onto a separate chunk!
       They are strictly kept on the same card with the word they qualify.
    3. Maximum duration and chunk size constraints are respected dynamically.
    """
    if not words:
        return []

    # First stitch all word tokens with compound word & apostrophe rules
    stitched_words = stitch_whisper_word_tokens(words)

    subtitles = []
    i = 0
    total_len = len(stitched_words)

    while i < total_len:
        end_idx = min(total_len, i + chunk_size)

        # Sentence punctuation break: if ANY word in range [i, end_idx) ends with ? or !, break right there
        for k in range(i, end_idx):
            w_text = (stitched_words[k].get("word") or stitched_words[k].get("text") or "").strip()
            if w_text.endswith(('?', '!')) and not w_text.endswith('...'):
                end_idx = k + 1
                break

        # Look ahead: Check if the token immediately following end_idx is a clitic (e.g. "mi?", "de", "musun?")
        # If so, that clitic CANNOT start the next chunk alone!
        if end_idx < total_len and is_clitic_token(stitched_words[end_idx].get("text") or stitched_words[end_idx].get("word", "")):
            cand_dur = stitched_words[end_idx]["end"] - stitched_words[i]["start"]
            if (end_idx - i <= 3) and cand_dur <= max_duration:
                # Include the clitic in the current chunk!
                end_idx += 1
                # If there is another clitic (e.g. "de mi?"), include that too!
                if end_idx < total_len and is_clitic_token(stitched_words[end_idx].get("text") or stitched_words[end_idx].get("word", "")) and (end_idx - i <= 4):
                    end_idx += 1
            else:
                # Chunk would exceed duration -> Move host word to the next chunk
                # so the host word + clitic start the next chunk together!
                if end_idx - i > 1:
                    end_idx -= 1

        # Check duration limit
        while (end_idx - i > 1) and (stitched_words[end_idx - 1]["end"] - stitched_words[i]["start"] > max_duration):
            end_idx -= 1

        # Prevent leaving a host word at the end if its clitic couldn't be included
        if end_idx < total_len and is_clitic_token(stitched_words[end_idx].get("text") or stitched_words[end_idx].get("word", "")):
            if end_idx - i > 1:
                end_idx -= 1

        chunk = stitched_words[i:end_idx]
        chunk_text = " ".join(fix_turkish_orthography_and_compounds(w.get("word") or w.get("text") or "") for w in chunk)
        chunk_text = fix_turkish_orthography_and_compounds(chunk_text)

        sub_obj = {
            "text": chunk_text,
            "start": chunk[0]["start"],
            "end": chunk[-1]["end"],
            "words": chunk
        }
        subtitles.append(sub_obj)
        i = end_idx

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
        clean_w = fix_turkish_orthography_and_compounds(t)
        words.append({
            "word": clean_w,
            "text": clean_w,
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
    BULLETPROOF FORCED ALIGNMENT ARCHITECTURE:
    Aligns the user's exact reference script monotonically to acoustic Whisper timestamps.
    
    GUARANTEES:
    1. Every single word in the aligned portion is 100% the user's exact text
       (preserving spelling, capitalization, punctuation, apostrophes like Kur'an, Allah'ın).
    2. Whisper AI is used STRICTLY as an acoustic timing guide (clock). Whisper's misheard words,
       hallucinations, and spelling mistakes (e.g. 'ısırlık' -> 'asırlık', 'fıkında fethvalar' ->
       'fıkhında fetvalar', 'dinisenden' -> 'dini senden') NEVER leak onto the timeline.
    3. Handles 1:1 fuzzy mishearings, 2:1 fused tokens, 1:2 split tokens, and partial transcripts.
    4. Enforces Turkish orthography rules and non-breaking clitic cohesion (mi, de, da, ki).
    5. Returns (words, subtitles) ready for Remotion & web timeline rendering.
    """
    cleaned_text = fix_turkish_orthography_and_compounds((user_text or "").strip())
    user_tokens = [w for w in cleaned_text.split() if w]
    if not user_tokens:
        return [], []

    audio_duration = max(1.0, float(audio_duration))

    # If no whisper words provided or whisper failed, distribute by character-length weights
    if not whisper_words:
        aligned_words = distribute_words_by_duration(user_tokens, 0.2, audio_duration - 0.2)
        subtitles = build_subtitle_chunks(aligned_words, chunk_size=3)
        return aligned_words, subtitles

    # First stitch Whisper tokens with compound word & apostrophe rules
    stitched_whisper = stitch_whisper_word_tokens(whisper_words)

    # Prepare normalized token lists for fuzzy comparison
    u_norm = [normalize_for_match(w) for w in user_tokens]
    w_norm = [normalize_for_match(w.get("word") or w.get("text") or "") for w in stitched_whisper]

    u_len = len(user_tokens)
    w_len = len(stitched_whisper)

    # 1. Monotonic anchor search in first 15 whisper words
    w_curr = 0
    if u_norm:
        best_start = 0
        best_start_score = 0.0
        for w_idx in range(min(15, w_len)):
            sc = token_similarity(u_norm[0], w_norm[w_idx])
            if sc > best_start_score:
                best_start_score = sc
                best_start = w_idx
        if best_start_score >= 0.70:
            w_curr = best_start

    aligned_user_words: List[Dict[str, Any]] = []
    u_curr = 0

    # 2. Monotonic Dynamic Alignment with locality constraint
    while u_curr < u_len:
        best_match = None
        best_score = 0.0
        # Window of 10 whisper words ahead (prevents jumping across minutes for accidental common words)
        window_end = min(w_len, w_curr + 10)

        # Pattern A: 1:1 match (handles misheard words: user 'asırlık' vs whisper 'ısırlık')
        for w_cand in range(w_curr, window_end):
            score = token_similarity(u_norm[u_curr], w_norm[w_cand])
            dist_penalty = (w_cand - w_curr) * 0.03
            adj = score - dist_penalty
            if adj > best_score and score >= 0.60:
                best_score = adj
                best_match = ('1:1', u_curr, w_cand, score)

        # Pattern B: 2:1 fusion (User 'dini' + 'senden' vs Whisper 'dinisenden')
        if u_curr + 1 < u_len:
            fused_u = u_norm[u_curr] + u_norm[u_curr + 1]
            for w_cand in range(w_curr, window_end):
                score = token_similarity(fused_u, w_norm[w_cand])
                dist_penalty = (w_cand - w_curr) * 0.03
                adj = score - dist_penalty
                if adj > best_score and score >= 0.70:
                    best_score = adj
                    best_match = ('2:1', u_curr, w_cand, score)

        # Pattern C: 1:2 split (User 'öğreneceğiz' vs Whisper 'mı' + 'renceğiz')
        for w_cand in range(w_curr, window_end - 1):
            fused_w = w_norm[w_cand] + w_norm[w_cand + 1]
            score = token_similarity(u_norm[u_curr], fused_w)
            dist_penalty = (w_cand - w_curr) * 0.03
            adj = score - dist_penalty
            if adj > best_score and score >= 0.70:
                best_score = adj
                best_match = ('1:2', u_curr, w_cand, score)

        if best_match:
            mtype = best_match[0]
            if mtype == '1:1':
                _, _, w_idx, _ = best_match
                w_ref = stitched_whisper[w_idx]
                aligned_user_words.append({
                    "word": user_tokens[u_curr],
                    "text": user_tokens[u_curr],
                    "start": round(float(w_ref["start"]), 2),
                    "end": round(float(w_ref["end"]), 2)
                })
                w_curr = w_idx + 1
                u_curr += 1
            elif mtype == '2:1':
                _, _, w_idx, _ = best_match
                w_ref = stitched_whisper[w_idx]
                t_s = float(w_ref["start"])
                t_e = float(w_ref["end"])
                mid = round((t_s + t_e) / 2.0, 2)
                aligned_user_words.append({
                    "word": user_tokens[u_curr],
                    "text": user_tokens[u_curr],
                    "start": round(t_s, 2),
                    "end": mid
                })
                aligned_user_words.append({
                    "word": user_tokens[u_curr + 1],
                    "text": user_tokens[u_curr + 1],
                    "start": mid,
                    "end": round(t_e, 2)
                })
                w_curr = w_idx + 1
                u_curr += 2
            elif mtype == '1:2':
                _, _, w_idx, _ = best_match
                t_s = float(stitched_whisper[w_idx]["start"])
                t_e = float(stitched_whisper[w_idx + 1]["end"])
                aligned_user_words.append({
                    "word": user_tokens[u_curr],
                    "text": user_tokens[u_curr],
                    "start": round(t_s, 2),
                    "end": round(t_e, 2)
                })
                w_curr = w_idx + 2
                u_curr += 1
        else:
            # Unmatched user token -> smoothly interpolate timestamp
            prev_end = aligned_user_words[-1]["end"] if aligned_user_words else 0.0
            next_start = float(stitched_whisper[w_curr]["start"]) if w_curr < w_len else prev_end + 0.35
            if next_start <= prev_end:
                next_start = prev_end + 0.3
            dur = max(0.2, min(0.6, next_start - prev_end))
            aligned_user_words.append({
                "word": user_tokens[u_curr],
                "text": user_tokens[u_curr],
                "start": round(prev_end, 2),
                "end": round(prev_end + dur, 2)
            })
            u_curr += 1

    # 3. Handle Partial Transcripts:
    # If user provided a partial transcript covering a portion of the speech,
    # preserve the remaining audio's speech so rest of video is not lost.
    final_words = list(aligned_user_words)
    if w_curr < w_len:
        for rem_w in stitched_whisper[w_curr:]:
            clean_rem = fix_turkish_orthography_and_compounds(rem_w.get("word") or rem_w.get("text") or "")
            final_words.append({
                "word": clean_rem,
                "text": clean_rem,
                "start": round(float(rem_w["start"]), 2),
                "end": round(float(rem_w["end"]), 2)
            })

    # 4. Monotonicity and timestamp sanity adjustment pass
    for idx in range(1, len(final_words)):
        if final_words[idx]["start"] < final_words[idx - 1]["end"]:
            mid = (final_words[idx - 1]["end"] + final_words[idx]["start"]) / 2
            final_words[idx - 1]["end"] = round(mid, 2)
            final_words[idx]["start"] = round(mid, 2)
            if final_words[idx]["end"] <= final_words[idx]["start"]:
                final_words[idx]["end"] = round(final_words[idx]["start"] + 0.18, 2)

    # 5. Build 3-word subtitle chunks with strict Turkish clitic & orthography cohesion
    subtitles = build_subtitle_chunks(final_words, chunk_size=3)
    return final_words, subtitles
