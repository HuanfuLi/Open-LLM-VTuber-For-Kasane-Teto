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


def test_motion_total_counts_consistent():
    for name in NEW_MOTION_FILES:
        data = _load_motion(name)
        total_points = 0
        for curve in data["Curves"]:
            # Each linear point in Segments is 3 floats: [type_prefix, time, value]
            # First point may have different shape but Cubism convention pads consistently.
            assert len(curve["Segments"]) % 3 == 0, (
                f"{name}: {curve['Id']} segments not 3-aligned"
            )
            total_points += len(curve["Segments"]) // 3
        assert data["Meta"]["TotalPointCount"] == total_points, (
            f"{name}: TotalPointCount={data['Meta']['TotalPointCount']} but sum={total_points}"
        )
        assert data["Meta"]["TotalSegmentCount"] == total_points, (
            f"{name}: TotalSegmentCount={data['Meta']['TotalSegmentCount']} but sum={total_points}"
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
    path = Path("live2d-models/重音テト/重音テト.model3.json")
    data = json.loads(path.read_text(encoding="utf-8"))
    motions = data["FileReferences"]["Motions"]
    assert len(motions["Idle"]) == 6, motions["Idle"]
    assert len(motions["Talk"]) == 2, motions["Talk"]
    idle_files = {entry["File"] for entry in motions["Idle"]}
    assert "Motions/IDLE.motion3.json" in idle_files
    assert "Motions/Breath.motion3.json" in idle_files
    talk_files = {entry["File"] for entry in motions["Talk"]}
    assert "Motions/Talk1.motion3.json" in talk_files
    assert "Motions/Talk2.motion3.json" in talk_files
