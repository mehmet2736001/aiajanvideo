import os

import pytest

from core.auto_cleanup import clean_temp_artifacts


def test_only_temp_artifacts_removed(tmp_path):
    public = tmp_path / "public"
    (public / "sfx").mkdir(parents=True)
    (public / "sfx" / "pop.wav").write_bytes(b"x" * 10)
    proj = public / "proje"
    (proj / "temp_voice").mkdir(parents=True)
    (proj / "temp_voice" / "line_0.mp3").write_bytes(b"y" * 100)
    (proj / "ses.mp3").write_bytes(b"z")
    (proj / "a.tmp").write_bytes(b"t" * 5)

    cleaned = clean_temp_artifacts(str(proj))

    assert cleaned == 105
    assert not (proj / "temp_voice").exists()
    assert (proj / "ses.mp3").exists()
    assert (public / "sfx" / "pop.wav").exists()  # SFX'e dokunulmaz


def test_wav_files_are_never_deleted(tmp_path):
    (tmp_path / "keep.wav").write_bytes(b"1")
    clean_temp_artifacts(str(tmp_path))
    assert (tmp_path / "keep.wav").exists()


@pytest.mark.parametrize("bad", ["", None, os.sep])
def test_dangerous_targets_rejected(bad):
    with pytest.raises(ValueError):
        clean_temp_artifacts(bad)
