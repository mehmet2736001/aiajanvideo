import unittest
from scripts.subtitle_cleaner import (
    clean_text_apostrophes,
    fix_turkish_orthography_and_compounds,
    stitch_whisper_word_tokens,
    build_subtitle_chunks,
    align_custom_transcript_to_audio,
    is_clitic_token
)

class TestForcedAlignerAndOrthography(unittest.TestCase):

    def test_align_with_whisper_reference(self):
        user_script = "Yüce Kur'an-ı Kerim, kalplere şifa ve akıllara nur saçar. Allah'ın kelamıdır."
        whisper_words = [
            {'word': 'Yüce', 'start': 0.4, 'end': 0.8},
            {'word': 'Kur', 'start': 0.9, 'end': 1.2},
            {'word': 'an', 'start': 1.2, 'end': 1.5},
            {'word': 'kalplere', 'start': 1.8, 'end': 2.3},
            {'word': 'şifa', 'start': 2.4, 'end': 2.9},
            {'word': 'akıllara', 'start': 3.1, 'end': 3.6},
            {'word': 'nur', 'start': 3.7, 'end': 4.1},
            {'word': 'saçar', 'start': 4.2, 'end': 4.8},
            {'word': 'Allah', 'start': 5.2, 'end': 5.6},
            {'word': 'ın', 'start': 5.6, 'end': 5.9},
            {'word': 'kelamıdır', 'start': 6.0, 'end': 6.7}
        ]

        words, subtitles = align_custom_transcript_to_audio(user_script, 7.5, whisper_words)
        self.assertTrue(len(words) >= 11)
        self.assertTrue(len(subtitles) >= 3)

        # Check that user words are strictly preserved
        extracted_text = " ".join(w["text"] for w in words)
        self.assertIn("Kur'an-ı", extracted_text)
        self.assertIn("Allah'ın", extracted_text)

        # Check monotonicity
        for i in range(len(words) - 1):
            self.assertLessEqual(words[i]["start"], words[i]["end"])
            self.assertLessEqual(words[i]["end"], words[i + 1]["start"] + 0.05)

        # Check subtitles
        for sub in subtitles:
            self.assertTrue(sub["start"] < sub["end"])
            self.assertTrue(len(sub["text"]) > 0)
            self.assertNotIn("Kur' an", sub["text"])
            self.assertNotIn("Kur'  an", sub["text"])

    def test_turkish_orthography_compounds(self):
        raw = "bir kaç gün sonra her hangi bir sorun ola bilir mi? hiç bir şey baka kaldı. Kur'an da yazıyor."
        cleaned = fix_turkish_orthography_and_compounds(raw)
        self.assertIn("birkaç", cleaned)
        self.assertIn("herhangi", cleaned)
        self.assertIn("olabilir", cleaned)
        self.assertIn("hiçbir", cleaned)
        self.assertIn("bakakaldı", cleaned)
        self.assertIn("Kur'an'da", cleaned)

    def test_whisper_token_compound_stitching(self):
        raw_tokens = [
            {"word": "bir", "start": 0.0, "end": 0.3},
            {"word": "kaç", "start": 0.3, "end": 0.6},
            {"word": "sorun", "start": 0.7, "end": 1.1},
            {"word": "ola", "start": 1.2, "end": 1.5},
            {"word": "bilir", "start": 1.5, "end": 1.9},
            {"word": "mi?", "start": 1.9, "end": 2.2}
        ]
        stitched = stitch_whisper_word_tokens(raw_tokens)
        stitched_words = [w["text"] for w in stitched]
        self.assertIn("birkaç", stitched_words)
        self.assertIn("olabilir", stitched_words)
        self.assertEqual(stitched[0]["start"], 0.0)
        self.assertEqual(stitched[0]["end"], 0.6)

    def test_clitic_cohesion_no_orphans(self):
        # Scenario 1: Soru edatı "mü?" tek başına kartta kalmamalı
        words1 = [
            {"text": "Sen", "word": "Sen", "start": 0.0, "end": 0.3},
            {"text": "bunu", "word": "bunu", "start": 0.35, "end": 0.65},
            {"text": "gördün", "word": "gördün", "start": 0.7, "end": 1.1},
            {"text": "mü?", "word": "mü?", "start": 1.15, "end": 1.45}
        ]
        subs1 = build_subtitle_chunks(words1, chunk_size=3)
        self.assertEqual(len(subs1), 1)
        self.assertIn("gördün mü?", subs1[0]["text"])

        # Scenario 2: Bağlaç "de" önceki kelimeden kopmamalı, "geldi mi?" ayrılmamalı
        words2 = [
            {"text": "Ali", "word": "Ali", "start": 0.0, "end": 0.3},
            {"text": "de", "word": "de", "start": 0.35, "end": 0.55},
            {"text": "bugün", "word": "bugün", "start": 0.6, "end": 0.95},
            {"text": "geldi", "word": "geldi", "start": 1.0, "end": 1.3},
            {"text": "mi?", "word": "mi?", "start": 1.35, "end": 1.6}
        ]
        subs2 = build_subtitle_chunks(words2, chunk_size=3)
        # Check no subtitle starts with "de" or "mi?"
        for s in subs2:
            first_word = s["text"].split()[0]
            self.assertFalse(is_clitic_token(first_word), f"Subtitle started with clitic: {s['text']}")
        self.assertIn("Ali de", subs2[0]["text"])
        self.assertIn("geldi mi?", subs2[-1]["text"])

    def test_empty_user_text(self):
        words, subtitles = align_custom_transcript_to_audio("", 10.0, None)
        self.assertEqual(words, [])
        self.assertEqual(subtitles, [])

if __name__ == "__main__":
    unittest.main()
