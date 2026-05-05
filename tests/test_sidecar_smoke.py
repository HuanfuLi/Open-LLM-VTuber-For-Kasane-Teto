"""Phase 4 D-07 sidecar smoke test.

Exercises tools/audio_to_params/main.py against the Plan 01 sample WAV
via subprocess. Verifies the engine fallback path (no NeuroSync weights
present in CI) produces a non-trivial trajectory.
"""

import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent
SAMPLE_WAV = REPO_ROOT / "tests" / "fixtures" / "sample_hello.wav"


@pytest.fixture
def sidecar_output(tmp_path, sample_wav_path):
    out = tmp_path / "traj.json"
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "tools.audio_to_params.main",
            "--audio",
            sample_wav_path,
            "--transcript",
            "hello",
            "--out",
            str(out),
        ],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert result.returncode == 0, (
        f"sidecar failed: stdout={result.stdout!r} stderr={result.stderr!r}"
    )
    assert out.is_file(), f"output file not created at {out}"
    return json.loads(out.read_text(encoding="utf-8"))


def test_sidecar_runs_on_sample_wav(sidecar_output):
    # Existence + nonempty frames is the basic pass criterion
    assert isinstance(sidecar_output, dict)
    assert sidecar_output["frames"], "frames must be non-empty"


def test_sidecar_output_shape(sidecar_output):
    for key in (
        "duration_seconds",
        "fps",
        "engine",
        "frames",
        "audio_path",
        "transcript",
    ):
        assert key in sidecar_output, f"missing key: {key}"


def test_sidecar_dsp_fallback_active(sidecar_output):
    # CI has no NeuroSync weights -> dsp_fallback
    assert sidecar_output["engine"] == "dsp_fallback"


def test_sidecar_jaw_open_varies(sidecar_output):
    jaws = [f["ParamJawOpenIN"] for f in sidecar_output["frames"]]
    assert len(set(jaws)) >= 3, f"ParamJawOpenIN trajectory too flat: {jaws[:10]}"
    assert max(jaws) > 0.01, (
        "max ParamJawOpenIN should be > 0.01 for speech-shaped audio"
    )


def test_sidecar_duration_matches_wav_length(sidecar_output):
    # Sample WAV is 1.0 second (Plan 01 fixture)
    assert 0.85 < sidecar_output["duration_seconds"] < 1.15, (
        f"duration {sidecar_output['duration_seconds']} not ~1.0s"
    )
