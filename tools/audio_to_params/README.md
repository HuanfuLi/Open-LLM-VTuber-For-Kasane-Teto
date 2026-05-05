# audio_to_params — Phase 4 D-07 sidecar

Standalone Python CLI that takes a WAV file + transcript and emits a
JSON parameter-trajectory file for the Kasane Teto Live2D rig.

**Status:** Research-bet sidecar. NOT wired into the live OLVT WebSocket
pipeline (per 04-CONTEXT.md D-07 / D-11). Use it to iterate on
audio→param ideas without touching production.

## Engine

Primary: [NeuroSync](https://github.com/AnimaVR/NeuroSync_Local_API)
(audio → 61-dim ARKit blendshapes + head pose).
License: **CC BY-NC 4.0** — research/non-commercial use only.

Fallback (when NeuroSync is not installed): pure-DSP feature path
— audio RMS drives `ParamJawOpenIN`, spectral centroid biases
`ParamMouthForm`. Useful for CI smoke tests; quality is intentionally
low. The output JSON's `engine` field reflects which path ran.

## Install (with NeuroSync)

```sh
cd tools/audio_to_params
uv sync --extra neurosync
# Clone NeuroSync_Local_API into tools/audio_to_params/neurosync_weights/
# and download the ONNX weights from
# https://huggingface.co/AnimaVR/NEUROSYNC_Audio_To_Face_Blendshape
# (place the .onnx file in neurosync_weights/)
```

## Install (DSP-fallback only — no model download)

```sh
cd tools/audio_to_params
uv sync
```

## Run

```sh
uv run python tools/audio_to_params/main.py \
    --audio tests/fixtures/sample_hello.wav \
    --transcript "hello" \
    --out /tmp/teto_traj.json
```

Output JSON shape:

```json
{
  "duration_seconds": 1.0,
  "fps": 30,
  "engine": "neurosync" | "dsp_fallback",
  "audio_path": "...",
  "transcript": "...",
  "frames": [
    {"ParamJawOpenIN": 0.0, "ParamEyeLOpen": 1.0, ...},
    ...
  ]
}
```

## Mapping table

See `mapping.py` `ARKIT_TO_LIVE2D` for the index → Live2D-param table.
NeuroSync indices 52-60 (head pose, emotion) are approximate and need
calibration per RESEARCH.md Open Question 3.
