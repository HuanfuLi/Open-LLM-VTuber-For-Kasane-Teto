"""Phase 4 D-07 sidecar adapter.

Two paths:
  * `infer_neurosync(audio_path)` — uses onnxruntime to run NeuroSync
    weights from neurosync_weights/. Outputs 61-dim per-frame vectors.
  * `infer_dsp(audio_path)` — pure DSP fallback: WAV RMS -> ParamJawOpenIN,
    spectral centroid -> ParamMouthForm bias. Lower quality, no weights
    needed, runs in CI.

The unified `infer(audio_path, transcript)` picks neurosync if weights
are present, else falls back to DSP, and tags the output JSON with
which engine ran.
"""

from __future__ import annotations

import wave
from pathlib import Path

import numpy as np
from loguru import logger

from .mapping import map_blendshapes_to_params

NEUROSYNC_WEIGHTS_DIR = Path(__file__).parent / "neurosync_weights"
SAMPLE_RATE = 16000
OUTPUT_FPS = 30


def _load_wav_mono(path: str) -> tuple[np.ndarray, int]:
    """Load a WAV file as mono float32 in [-1, 1]."""
    with wave.open(path, "rb") as w:
        sr = w.getframerate()
        nframes = w.getnframes()
        sampwidth = w.getsampwidth()
        nchan = w.getnchannels()
        raw = w.readframes(nframes)
    if sampwidth == 2:
        samples = np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768.0
    elif sampwidth == 4:
        samples = np.frombuffer(raw, dtype=np.int32).astype(np.float32) / 2147483648.0
    else:
        raise ValueError(f"unsupported sample width: {sampwidth}")
    if nchan > 1:
        samples = samples.reshape(-1, nchan).mean(axis=1)
    return samples, sr


def _neurosync_weights_present() -> bool:
    if not NEUROSYNC_WEIGHTS_DIR.is_dir():
        return False
    return any(NEUROSYNC_WEIGHTS_DIR.glob("*.onnx"))


def infer_neurosync(audio_path: str) -> list[list[float]]:
    """Run NeuroSync ONNX inference on the audio. Returns a list of
    61-dim float vectors at 60 Hz (per RESEARCH.md). The caller
    downsamples to OUTPUT_FPS.

    Raises FileNotFoundError if weights are missing.
    """
    import onnxruntime as ort  # type: ignore

    weights = next(NEUROSYNC_WEIGHTS_DIR.glob("*.onnx"))
    logger.info(f"Loading NeuroSync ONNX from {weights}")
    ort.InferenceSession(str(weights), providers=["CPUExecutionProvider"])
    # NOTE: NeuroSync_Local_API has a Python wrapper that does
    # mel-spectrogram preprocessing. For this sidecar prototype, we
    # raise NotImplementedError if reached — the user should clone
    # NeuroSync_Local_API and adapt this method per their setup.
    # The DSP fallback handles the smoke-test path.
    raise NotImplementedError(
        "NeuroSync inference requires the NeuroSync_Local_API preprocessing "
        "pipeline (mel spectrogram extraction + custom input shape). "
        "Clone https://github.com/AnimaVR/NeuroSync_Local_API and adapt "
        "this method against its inference.py. The DSP fallback runs by default."
    )


def infer_dsp(audio_path: str) -> tuple[list[dict[str, float]], float]:
    """Pure-DSP fallback. Computes RMS-per-frame and a crude spectral
    centroid, maps them onto Live2D Teto parameters.

    Returns (frames, duration_seconds) where frames is a list of
    {param_name: value} dicts at OUTPUT_FPS Hz.
    """
    samples, sr = _load_wav_mono(audio_path)
    duration = len(samples) / sr
    # Frame length = sr / OUTPUT_FPS samples per frame
    frame_len = max(1, sr // OUTPUT_FPS)
    num_frames = max(1, len(samples) // frame_len)

    frames: list[dict[str, float]] = []
    for i in range(num_frames):
        chunk = samples[i * frame_len : (i + 1) * frame_len]
        if len(chunk) == 0:
            continue
        # RMS -> jaw open
        rms = float(np.sqrt(np.mean(chunk * chunk)))
        jaw = min(1.0, rms * 4.0)  # gain
        # Spectral centroid (rough vowel proxy) -> mouth form bias
        spectrum = np.abs(np.fft.rfft(chunk))
        freqs = np.fft.rfftfreq(len(chunk), 1.0 / sr)
        total = float(spectrum.sum() + 1e-9)
        centroid = float((spectrum * freqs).sum() / total)
        # Normalize centroid to [-0.5, 0.5] around 1000 Hz neutral
        mouth_form = max(-0.5, min(0.5, (centroid - 1000.0) / 2000.0))
        # Eyes always open in DSP fallback
        frames.append(
            {
                "ParamJawOpenIN": round(jaw, 4),
                "ParamMouthForm": round(mouth_form, 4),
                "ParamEyeLOpen": 1.0,
                "ParamEyeROpen": 1.0,
                # Head pose stays neutral in DSP fallback
                "ParamAngleXIN": 0.0,
                "ParamAngleYIN": 0.0,
                "ParamAngleZIN": 0.0,
            }
        )
    return frames, duration


def infer(audio_path: str, transcript: str) -> dict:
    """Unified entry point. Picks NeuroSync if weights are present,
    else falls back to DSP. Returns the full output dict ready for
    json.dump."""
    audio_p = Path(audio_path)
    if not audio_p.is_file():
        raise FileNotFoundError(f"audio not found: {audio_path}")

    if _neurosync_weights_present():
        try:
            logger.info("NeuroSync weights detected — attempting inference")
            raw_frames = infer_neurosync(audio_path)
            # Map each 61-dim frame to a Live2D dict
            frames = [map_blendshapes_to_params(v) for v in raw_frames]
            # Estimate duration from frame count at NeuroSync's 60 Hz
            duration = len(raw_frames) / 60.0
            engine = "neurosync"
        except NotImplementedError as e:
            logger.warning(f"NeuroSync wrapper incomplete ({e}); using DSP fallback")
            frames, duration = infer_dsp(audio_path)
            engine = "dsp_fallback"
    else:
        logger.info("No NeuroSync weights at neurosync_weights/*.onnx — DSP fallback")
        frames, duration = infer_dsp(audio_path)
        engine = "dsp_fallback"

    return {
        "duration_seconds": round(duration, 4),
        "fps": OUTPUT_FPS,
        "engine": engine,
        "audio_path": str(audio_p),
        "transcript": transcript,
        "frames": frames,
    }
