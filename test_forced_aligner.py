import unittest
from scripts.subtitle_cleaner import (
    clean_text_apostrophes,
    stitch_whisper_word_tokens,
    build_subtitle_chunks,
    align_custom_transcript_to_audio
)

class TestForcedAligner(unittest.TestCase):

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

    def test_align_without_whisper(self):
        user_script = "İlim öğrenmek her Müslümana farzdır."
        words, subtitles = align_custom_transcript_to_audio(user_script, 5.0, None)

        self.assertEqual(len(words), 5)
        self.assertTrue(len(subtitles) >= 2)
        self.assertEqual(words[0]["text"], "İlim")
        self.assertEqual(words[-1]["text"], "farzdır.")
        self.assertTrue(words[-1]["end"] <= 5.0)

    def test_empty_user_text(self):
        words, subtitles = align_custom_transcript_to_audio("", 10.0, None)
        self.assertEqual(words, [])
        self.assertEqual(subtitles, [])

if __name__ == "__main__":
    unittest.main()
