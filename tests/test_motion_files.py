"""Schema + IDLE-pin-collision tests for Phase 4 D-05 authored motions."""

import json
from pathlib import Path

MOTIONS_DIR = Path("live2d-models/重音テト/Motions")
NEW_MOTION_FILES = [
    "Talk1.motion3.json",
    "Talk2.motion3.json",
    "Breath.motion3.json",
    "WeightShift.motion3.json",
    "Gaze1.motion3.json",
    "Gaze2.motion3.json",
    "Gaze3.motion3.json",
]

# ENUMERATED VERBATIM from live2d-models/重音テト/Motions/IDLE.motion3.json Curves[].Id.
# IDLE.motion3.json pins these 36 parameters to neutral/off — new Talk/Idle motions
# MUST NOT touch them or watermark/props will flicker. Count = 36 = IDLE Meta.CurveCount.
FORBIDDEN_PARAM_IDS = {
    # Watermark + emotion-state pins (lines 17-133 of IDLE.motion3.json):
    "ParamWatermarkOFF",
    "PramaAngry2",
    "ParamHeartEYEON",
    "ParamBlankEYEON",
    "ParamTearON",
    "ParamStarEYE",
    "ParamEYEClosed2ON",
    "ParamCircleEYEON",
    "ParamBlush",
    # Prop pins:
    "ParamMicON",
    "ParamSVMCON",
    "ParamKnifeHandsON",
    "ParamBHandsON",
    "ParamBHandIN",
    # Chibi state:
    "Paramchibi",
    "Paramchibi2",
    # Cry/sweat overlays:
    "ParamCRY",
    "ParamCRY2",
    "ParamSweat1",
    "ParamSweat2",
    "ParamSweat3",
    "ParamSweat4",
    # Eye-state pins:
    "ParamBlackEYE",
    "ParamCryEye",
    "ParamTearEye1",
    "ParamTearEye2",
    # Physics-driven cry-eye pins (10 total — verbatim from IDLE.motion3.json):
    "ParamPhyCryEyeINR",
    "ParamPhyCryEyeR1",
    "ParamPhyCryEyeR2",
    "ParamPhyCryEyeR3",
    "ParamPhyCryEyeR4",
    "ParamPhyCryEyeIN",
    "ParamPhyCryEyeL",
    "ParamPhyCryEyeL2",
    "ParamPhyCryEyeL3",
    "ParamPhyCryEyeL5",
}
assert len(FORBIDDEN_PARAM_IDS) == 36, (
    f"FORBIDDEN_PARAM_IDS must enumerate all 36 IDLE pins; got {len(FORBIDDEN_PARAM_IDS)}"
)


def _load_motion(name):
    return json.loads((MOTIONS_DIR / name).read_text(encoding="utf-8"))


def test_all_new_motion_files_exist():
    for name in NEW_MOTION_FILES:
        assert (MOTIONS_DIR / name).is_file(), f"missing: {name}"


def test_motion_schema_version_3():
    for name in NEW_MOTION_FILES:
        assert _load_motion(name)["Version"] == 3, name


def test_motion_curvecount_matches_curves_length():
    for name in NEW_MOTION_FILES:
        data = _load_motion(name)
        assert data["Meta"]["CurveCount"] == len(data["Curves"]), name


def test_motion_segments_match_cubism_format():
    """Validate Cubism motion3.json segment encoding by walking each curve.

    Cubism format (verified against Sleep.motion3.json + IDLE.motion3.json):
      - Initial point: 2 floats [time, value]
      - Each subsequent segment: 3 floats [type, time, value]
        where type ∈ {0=Linear, 1=Bezier, 2=Stepped, 3=InverseStepped}
        Bezier (type=1) actually takes 6 floats (2 control + endpoint), not 2.
      - Total floats per curve: 2 + Σ(per-segment floats)

    Earlier iteration of this test only checked `len % 3 == 0`, which permitted
    a malformed format where the initial point was encoded as a phantom
    [type=0, time, value] segment. Cubism's WebSDK rejected those files at
    runtime with `basePointIndex undefined`. This stricter test walks the
    segment array exactly the way the SDK does.

    Also verifies Meta.TotalSegmentCount and Meta.TotalPointCount equal the
    walked counts.
    """
    VALID_TYPES = {0, 1, 2, 3}
    for name in NEW_MOTION_FILES:
        data = _load_motion(name)
        total_segments = 0
        total_points = 0
        for curve in data["Curves"]:
            seg = curve["Segments"]
            assert len(seg) >= 2, f"{name}::{curve['Id']} too short: {seg!r}"

            # Initial point — 2 floats
            n_segs = 0
            n_pts = 1  # initial point itself
            i = 2
            while i < len(seg):
                t = seg[i]
                assert t in VALID_TYPES, (
                    f"{name}::{curve['Id']} segment type {t!r} at index {i} "
                    f"not in {VALID_TYPES}; full segments: {seg!r}"
                )
                if t == 1:  # Bezier — 6 floats follow (2 control + endpoint)
                    i += 1 + 6
                else:  # Linear, Stepped, InverseStepped — 2 floats follow
                    i += 1 + 2
                n_segs += 1
                n_pts += 1
            assert i == len(seg), (
                f"{name}::{curve['Id']} segment walk overran/underran "
                f"(stopped at {i}, len={len(seg)})"
            )
            total_segments += n_segs
            total_points += n_pts

        assert data["Meta"]["TotalSegmentCount"] == total_segments, (
            f"{name}: Meta.TotalSegmentCount={data['Meta']['TotalSegmentCount']} "
            f"but walked {total_segments}"
        )
        assert data["Meta"]["TotalPointCount"] == total_points, (
            f"{name}: Meta.TotalPointCount={data['Meta']['TotalPointCount']} "
            f"but walked {total_points}"
        )


def test_no_motion_animates_idle_pinned_parameters():
    for name in NEW_MOTION_FILES:
        data = _load_motion(name)
        for curve in data["Curves"]:
            assert curve["Id"] not in FORBIDDEN_PARAM_IDS, (
                f"{name}: animates IDLE-pinned parameter {curve['Id']!r} — "
                f"this will fight the watermark/expression-state reset"
            )


def test_forbidden_set_matches_idle_motion3_json():
    """Cross-check: FORBIDDEN_PARAM_IDS must equal the actual IDLE pin set.

    Catches regressions where the constant drifts from the source of truth
    (live2d-models/重音テト/Motions/IDLE.motion3.json). If IDLE ever gains
    a new pin, this test fails until FORBIDDEN_PARAM_IDS is updated.
    """
    idle_path = MOTIONS_DIR / "IDLE.motion3.json"
    idle_data = json.loads(idle_path.read_text(encoding="utf-8"))
    actual_ids = {curve["Id"] for curve in idle_data["Curves"]}
    assert actual_ids == FORBIDDEN_PARAM_IDS, (
        f"FORBIDDEN_PARAM_IDS drift from IDLE.motion3.json:\n"
        f"  in IDLE only: {actual_ids - FORBIDDEN_PARAM_IDS}\n"
        f"  in constant only: {FORBIDDEN_PARAM_IDS - actual_ids}"
    )


def test_model3_motion_groups_updated():
    """The Idle group must contain ONLY IDLE.motion3.json.

    IDLE.motion3.json pins 36 expression-state parameters (watermark, anger,
    heart-eye, prop overlays, cry overlays, etc.) to neutral. If we add other
    motions to the Idle group, the SDK randomly picks one each cycle, and 5/6
    of the time those pins don't apply — parameters drift to MOC defaults
    and the angry/cry/etc. overlays become visible.

    The 5 ambient gesture motion files (Breath, WeightShift, Gaze1-3) remain
    in the repo as content but are NOT registered. Future work: replicate
    IDLE's 36 pins inside each ambient motion (or add a second motion manager
    to the bundle for layered playback).
    """
    path = Path("live2d-models/重音テト/重音テト.model3.json")
    data = json.loads(path.read_text(encoding="utf-8"))
    motions = data["FileReferences"]["Motions"]
    assert motions["Idle"] == [{"File": "Motions/IDLE.motion3.json"}], (
        f"Idle group must contain only IDLE.motion3.json; got {motions['Idle']}"
    )
    assert len(motions["Talk"]) == 2, motions["Talk"]
    talk_files = {entry["File"] for entry in motions["Talk"]}
    assert "Motions/Talk1.motion3.json" in talk_files
    assert "Motions/Talk2.motion3.json" in talk_files
