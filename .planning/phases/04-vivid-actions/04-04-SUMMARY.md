---
phase: 04-vivid-actions
plan: 04
subsystem: sidecar-audio-to-params
tags: [sidecar, dsp, neurosync, live2d, audio-processing, standalone]
dependency_graph:
  requires: [04-01]
  provides: [audio-to-params-sidecar, dsp-fallback-trajectory, arkit-live2d-mapping]
  affects: []
tech_stack:
  added: []
  patterns: [dsp-fallback, try-except-relative-import, subprocess-smoke-test]
key_files:
  created:
    - tools/__init__.py
    - tools/audio_to_params/__init__.py
    - tools/audio_to_params/pyproject.toml
    - tools/audio_to_params/.gitignore
    - tools/audio_to_params/README.md
    - tools/audio_to_params/mapping.py
    - tools/audio_to_params/adapter.py
    - tools/audio_to_params/main.py
    - tests/test_sidecar_smoke.py
  modified: []
decisions:
  - tools/__init__.py added to make tools/ a Python package for -m invocation support
  - infer_neurosync raises NotImplementedError stub (DSP fallback covers CI path)
  - try/except relative import in main.py supports both direct and -m invocation
  - ort.InferenceSession called without assignment (side-effect call before NotImplementedError) to satisfy ruff F841
metrics:
  duration: ~10 min
  completed: 2026-05-04
  tasks: 3/3
  files_created: 9
  files_modified: 0
---

# Phase 4 Plan 4: Audio-to-Params Sidecar Summary

**One-liner:** Standalone Python sidecar with DSP fallback (RMS→jaw, spectral centroid→mouth) mapping WAV+transcript to Live2D Teto parameter trajectories, plus 5-test subprocess smoke suite.

## What Was Built

### Directory Structure

```
tools/
  __init__.py                    # makes tools/ a Python package for -m invocation
  audio_to_params/
    __init__.py                  # package marker
    pyproject.toml               # standalone project metadata (numpy, scipy, loguru, pydantic)
    .gitignore                   # excludes neurosync_weights/, *.onnx, *.pth, *_traj.json
    README.md                    # install+run docs; both engines documented; CC BY-NC 4.0 note
    mapping.py                   # ARKIT_TO_LIVE2D (5 entries) + HEADPOSE_TO_LIVE2D (3 entries)
    adapter.py                   # _load_wav_mono, _neurosync_weights_present, infer_neurosync,
                                 # infer_dsp, infer() unified entry
    main.py                      # argparse CLI: --audio, --transcript, --out
tests/
  test_sidecar_smoke.py          # 5 smoke tests via subprocess
```

### Supported Live2D Parameters (7 total)

| Parameter | Source | Notes |
|-----------|--------|-------|
| ParamJawOpenIN | jawOpen ARKit idx 17 / DSP RMS | Primary mouth open |
| ParamEyeLOpen | eyeBlinkLeft ARKit idx 0 (inverted) / DSP=1.0 | Left eye open |
| ParamEyeROpen | eyeBlinkRight ARKit idx 7 (inverted) / DSP=1.0 | Right eye open |
| ParamMouthForm | mouthSmileLeft+Right ARKit idx 24+25 / DSP spectral centroid | Smile shape |
| ParamAngleXIN | head yaw ARKit idx 54 / DSP=0.0 | Head left-right |
| ParamAngleYIN | head pitch ARKit idx 53 / DSP=0.0 | Head up-down |
| ParamAngleZIN | head roll ARKit idx 52 / DSP=0.0 | Head roll |

### Sample CLI Invocation + Output

```sh
uv run python -m tools.audio_to_params.main \
    --audio tests/fixtures/sample_hello.wav \
    --transcript "hello" \
    --out /tmp/teto_traj.json
```

Output (truncated):
```json
{
  "duration_seconds": 1.0,
  "fps": 30,
  "engine": "dsp_fallback",
  "audio_path": "tests/fixtures/sample_hello.wav",
  "transcript": "hello",
  "frames": [
    {"ParamJawOpenIN": 0.069, "ParamMouthForm": 0.1197, "ParamEyeLOpen": 1.0, ...},
    ...
  ]
}
```

### License Note

NeuroSync (AnimaVR) is licensed CC BY-NC 4.0 — research/non-commercial use only.
The DSP fallback path (what runs in CI and smoke tests) uses only numpy/scipy — no license constraints.

## Test Results

```
tests/test_sidecar_smoke.py::test_sidecar_runs_on_sample_wav  PASSED
tests/test_sidecar_smoke.py::test_sidecar_output_shape        PASSED
tests/test_sidecar_smoke.py::test_sidecar_dsp_fallback_active PASSED
tests/test_sidecar_smoke.py::test_sidecar_jaw_open_varies     PASSED
tests/test_sidecar_smoke.py::test_sidecar_duration_matches_wav_length PASSED
5/5 GREEN — Full suite: 28 tests GREEN (23 prior + 5 new)
```

## D-11 Scope Guard

```
grep -r -E "from\s+src\.open_llm_vtuber|..." tools/audio_to_params/ -> NO MATCHES
```

Zero imports from `src/open_llm_vtuber` or `open_llm_vtuber`. Sidecar is fully standalone.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Direct script invocation fails due to relative imports**
- **Found during:** Task 2 smoke test
- **Issue:** `python tools/audio_to_params/main.py` fails with `ImportError: attempted relative import with no known parent package`
- **Fix:** Added try/except import fallback in `main.py` that adds repo root to sys.path for direct invocation; created `tools/__init__.py` to make `-m` invocation work
- **Files modified:** `tools/audio_to_params/main.py`, `tools/__init__.py` (new)
- **Commit:** 003b2d1

**2. [Rule 1 - Bug] Ruff F841: unused `session` variable in infer_neurosync**
- **Found during:** Task 2 ruff check
- **Issue:** `session = ort.InferenceSession(...)` assigned but never used before `raise NotImplementedError`
- **Fix:** Changed to `ort.InferenceSession(...)` (expression statement, side-effect call)
- **Files modified:** `tools/audio_to_params/adapter.py`
- **Commit:** 003b2d1

## Follow-up Work (NeuroSync Path)

`infer_neurosync()` currently raises `NotImplementedError` with a clear message. To complete the NeuroSync path:
1. Clone `https://github.com/AnimaVR/NeuroSync_Local_API`
2. Download ONNX weights from `AnimaVR/NEUROSYNC_Audio_To_Face_Blendshape` on HuggingFace
3. Place `.onnx` file in `tools/audio_to_params/neurosync_weights/`
4. Implement mel-spectrogram preprocessing and adapt `infer_neurosync()` against the API's `inference.py`
5. Calibrate blendshape index ordering (Open Q3 from RESEARCH.md — indices 52-60 for head pose)

The DSP fallback (`infer_dsp`) handles CI and all current tests without weights.

## Commits

| Task | Name | Commit | Files |
|------|------|--------|-------|
| 1 | Bootstrap sidecar skeleton | f96a583 | 5 created |
| 2 | adapter.py + main.py CLI | 003b2d1 | 3 created |
| 3 | Smoke test suite | 58b26ec | 1 created |

## Self-Check: PASSED
