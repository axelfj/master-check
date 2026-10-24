"""Malformed float audio must never become an analysis verdict."""
import json
import numpy as np
import pytest
from master_check import audio, report

@pytest.mark.parametrize("bad", [float("nan"), float("inf"), float("-inf")])
@pytest.mark.parametrize("whole_file", [False, True])
def test_reject_nonfinite_audio(tmp_path, bad, whole_file):
    x = np.full((4410, 2), 0.01, dtype=np.float32)
    if whole_file:
        x[:] = bad
    else:
        x[200, 1] = bad
    path = str(tmp_path / "corrupt.wav")
    audio.write_wav_float(path, x, 44100)
    with pytest.raises(audio.AudioError, match="non-finite"):
        audio.read(path)

def test_json_refuses_nonfinite_measurements():
    with pytest.raises(ValueError):
        report.to_json([{"measurement": float("nan")}])
