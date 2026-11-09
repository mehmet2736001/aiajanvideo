from core.voice_pipeline import align_script_to_whisper, default_pauses, pick_voice


def ww(items):
    return [{"w": w, "s": s, "e": e} for w, s, e in items]


def test_exact_words_keep_whisper_times_and_pause():
    script = ["Merhaba", "dünya", "nasılsın"]
    whisper = ww([("Merhaba", 0.0, 0.5), ("dünya", 1.5, 2.0), ("nasılsın", 2.0, 2.8)])
    out = align_script_to_whisper(script, whisper, 3.0, 10.0, 2)
    assert [w["w"] for w in out] == script
    assert all(w["c"] == 2 for w in out)
    assert out[0]["s"] == 10.0
    assert out[1]["s"] >= 11.4  # 1.5 sn'lik gerçek duraklama korunur (eşit bölme olsaydı ~10.9 olurdu)
    assert out[-1]["e"] <= 12.81


def test_times_are_monotonic_and_positive_when_counts_differ():
    script = "Beni Hûd sûresi kocattı diye buyurdu".split()
    whisper = ww([("Beni", 0.1, 0.4), ("Hud", 0.5, 0.9), ("suresi", 1.0, 1.6), ("kocatti", 1.7, 2.4)])
    out = align_script_to_whisper(script, whisper, 3.0, 0.0, 0)
    assert len(out) == len(script)
    prev_start = -1
    for w in out:
        assert w["e"] > w["s"] >= prev_start
        prev_start = w["s"]
    assert out[0]["s"] >= 0.1 - 1e-6 and out[-1]["e"] <= 2.4 + 1e-6


def test_fallback_without_whisper_words_spans_line():
    out = align_script_to_whisper(["a", "bb", "ccc"], [], 6.0, 0.0, 0)
    assert out[0]["s"] == 0.0
    assert abs(out[-1]["e"] - 6.0) < 0.01


def test_empty_script():
    assert align_script_to_whisper([], [], 1.0, 0.0, 0) == []


def test_pick_voice_and_pauses():
    assert pick_voice({"gender": "female"}, default="Aoede") == "Aoede"
    assert pick_voice({"gender": "male"}, default="Charon") == "Charon"
    assert pick_voice(None, default="Charon") == "Charon"
    p = default_pauses(6)
    assert p[3] == 0.75 and p[-1] == 1.20 and p[0] == 0.45
    assert default_pauses(0) == []
