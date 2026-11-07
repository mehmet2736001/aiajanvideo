import pytest

np = pytest.importorskip("numpy")

from core.vision_critic import evaluate_tiles


def tile(mean, noise=0, seed=0):
    rng = np.random.default_rng(seed)
    base = np.full((40, 24), mean, dtype=np.float32)
    if noise:
        base += rng.normal(0, noise, base.shape)
    return np.clip(base, 0, 255).astype(np.uint8)


def test_healthy_video_scores_high():
    tiles = [tile(60 + i, noise=25, seed=i) for i in range(48)]
    r = evaluate_tiles(tiles)
    assert r["score"] >= 90


def test_black_frames_and_cut_video_are_penalised():
    tiles = [tile(60, 25, i) for i in range(30)] + [tile(0) for _ in range(18)]
    r = evaluate_tiles(tiles)
    assert r["score"] < 80
    assert any("boş" in n or "siyah" in n for n in r["notes"])


def test_first_black_frame_is_allowed_fade_in():
    tiles = [tile(0)] + [tile(60 + i, 25, i) for i in range(47)]
    assert evaluate_tiles(tiles)["score"] >= 90


def test_frozen_video_penalised():
    tiles = [tile(80, 25, 1) for _ in range(48)]
    assert evaluate_tiles(tiles)["score"] < 95


def test_no_tiles():
    assert evaluate_tiles([])["score"] == 0
