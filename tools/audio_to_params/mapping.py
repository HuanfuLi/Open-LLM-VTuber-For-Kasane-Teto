"""ARKit blendshape index -> Live2D Teto parameter name mapping.

Source: 04-RESEARCH.md "Sidecar Adapter Survey" -> mapping sketch table.
NeuroSync outputs 61 floats per frame; indices 0-51 are ARKit standard,
indices 52-60 are head pose + emotion (calibration TBD per Open Q3).
"""

# ARKit blendshape index -> (live2d_param_name, invert_flag, scale)
# invert_flag: True means output = 1.0 - blendshape_value (eyeBlink uses this).
# scale: multiplied into the final value (clamped to [0, 1] or [-30, 30] depending on param).
ARKIT_TO_LIVE2D: dict[int, tuple[str, bool, float]] = {
    0: ("ParamEyeLOpen", True, 1.0),  # eyeBlinkLeft -> invert
    7: ("ParamEyeROpen", True, 1.0),  # eyeBlinkRight -> invert
    17: ("ParamJawOpenIN", False, 1.0),  # jawOpen -> primary mouth
    24: ("ParamMouthForm", False, 0.5),  # mouthSmileLeft (avg with 25)
    25: ("ParamMouthForm", False, 0.5),  # mouthSmileRight (avg with 24)
}

# Optional head pose mapping (indices need NeuroSync calibration — Open Q3 in RESEARCH.md)
HEADPOSE_TO_LIVE2D: dict[int, tuple[str, float]] = {
    52: ("ParamAngleZIN", 30.0),  # headRoll  (approx — calibrate)
    53: ("ParamAngleYIN", 30.0),  # headPitch (approx — calibrate)
    54: ("ParamAngleXIN", 30.0),  # headYaw   (approx — calibrate)
}


def map_blendshapes_to_params(values: list[float]) -> dict[str, float]:
    """Convert one frame of NeuroSync output (61 floats) to a Live2D
    parameter dict for that frame.

    Multiple ARKit indices may map to the same Live2D parameter
    (e.g., mouthSmileLeft + mouthSmileRight -> ParamMouthForm).
    They are summed (with their scale factors).
    """
    out: dict[str, float] = {}
    for idx, (param, invert, scale) in ARKIT_TO_LIVE2D.items():
        if idx >= len(values):
            continue
        raw = values[idx]
        v = (1.0 - raw) if invert else raw
        v *= scale
        out[param] = out.get(param, 0.0) + v
    for idx, (param, scale) in HEADPOSE_TO_LIVE2D.items():
        if idx >= len(values):
            continue
        # Head pose is signed (-1..1 -> -scale..+scale degrees)
        out[param] = values[idx] * scale
    return out


def supported_param_names() -> list[str]:
    """Returns the set of Live2D parameter names this mapping can populate."""
    names = {p for (p, _, _) in ARKIT_TO_LIVE2D.values()}
    names.update(p for (p, _) in HEADPOSE_TO_LIVE2D.values())
    return sorted(names)
