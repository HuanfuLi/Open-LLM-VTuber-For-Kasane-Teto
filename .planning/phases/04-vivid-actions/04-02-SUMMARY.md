---
phase: 04-vivid-actions
plan: 02
subsystem: live2d-content
tags: [motion3json, live2d, teto, ambient-gestures, D-05, D-09, D-12, D-14]
dependency_graph:
  requires: [04-01]
  provides: [authored-ambient-motions, teto-model3-motion-groups]
  affects: [frontend-motion-playback, startRandomMotion-Talk, startRandomMotion-Idle]
tech_stack:
  added: []
  patterns: [motion3json-linear-segments, cubism-random-motion-group]
key_files:
  created:
    - live2d-models/重音テト/Motions/Talk1.motion3.json
    - live2d-models/重音テト/Motions/Talk2.motion3.json
    - live2d-models/重音テト/Motions/Breath.motion3.json
    - live2d-models/重音テト/Motions/WeightShift.motion3.json
    - live2d-models/重音テト/Motions/Gaze1.motion3.json
    - live2d-models/重音テト/Motions/Gaze2.motion3.json
    - live2d-models/重音テト/Motions/Gaze3.motion3.json
    - tests/test_motion_files.py
  modified:
    - live2d-models/重音テト/重音テト.model3.json
decisions:
  - "Linear segments (type 0) only — no bezier curves needed for small-amplitude ambient motions"
  - "Talk group uses only 2 entries (Talk1/Talk2) so the SDK alternates them on each audio message"
  - "Gaze motions are Loop:false so they play once and return to Idle group selection"
  - "FORBIDDEN_PARAM_IDS constant cross-checked against IDLE.motion3.json at runtime via test_forbidden_set_matches_idle_motion3_json"
metrics:
  duration: ~10 min
  completed: 2026-05-04
  tasks: 3/3
  files: 8 created, 1 modified
---

# Phase 4 Plan 02: Teto Motion Authoring Summary

**One-liner:** 7 authored motion3.json ambient gestures (talk loops, breath, weight shift, gaze) registered in Teto's model3.json with 7-test regression suite guarding against IDLE-pin collisions.

## What Was Built

### Motion Files (7 new files in `live2d-models/重音テト/Motions/`)

| File | Duration | Loop | Curves | Parameters Driven |
|------|----------|------|--------|-------------------|
| Talk1.motion3.json | 2.0s | true | 3 | ParamAngleXIN, ParamAngleYIN, ParamBreath |
| Talk2.motion3.json | 2.5s | true | 3 | ParamAngleXIN, ParamAngleZIN, ParamEyeBallX |
| Breath.motion3.json | 3.2s | true | 2 | ParamBreath, ParamBodyAngleY |
| WeightShift.motion3.json | 4.0s | true | 2 | ParamBodyAngleX, ParamAngleZIN |
| Gaze1.motion3.json | 1.5s | false | 2 | ParamEyeBallX (left), ParamEyeBallY |
| Gaze2.motion3.json | 1.5s | false | 2 | ParamEyeBallX (right), ParamEyeBallY |
| Gaze3.motion3.json | 2.0s | false | 3 | ParamEyeBallX, ParamEyeBallY, ParamAngleYIN |

All amplitudes are intentionally small (head angles <5 deg, eye balls in [-1, 1] range) to match Teto's small expressive rig.

### model3.json Motion Groups (updated `live2d-models/重音テト/重音テト.model3.json`)

```
Idle (6 entries): IDLE.motion3.json, Breath, WeightShift, Gaze1, Gaze2, Gaze3
Talk (2 entries): Talk1, Talk2
Sleep (1 entry): Sleep.motion3.json (unchanged)
```

The Cubism SDK's `startRandomMotion("Talk", PriorityNormal)` (called by the frontend on every audio message) now randomly selects Talk1 or Talk2. `startRandomMotion("Idle", PriorityIdle)` (called when the motion manager finishes) randomly selects from 6 idle motions. No code changes were required — only content authoring and the model3.json edit.

### Test Suite (`tests/test_motion_files.py`)

7 tests, all GREEN:
1. `test_all_new_motion_files_exist` — 7 files present on disk
2. `test_motion_schema_version_3` — Version==3 for all
3. `test_motion_curvecount_matches_curves_length` — CurveCount == len(Curves)
4. `test_motion_total_counts_consistent` — TotalSegmentCount and TotalPointCount == sum of point counts
5. `test_no_motion_animates_idle_pinned_parameters` — none of the 36 IDLE-pinned IDs appear in Curves[].Id
6. `test_forbidden_set_matches_idle_motion3_json` — FORBIDDEN_PARAM_IDS set == actual IDLE.motion3.json Curves[].Id set (drift guard)
7. `test_model3_motion_groups_updated` — Idle has 6 entries, Talk has 2 entries, correct files present

Run: `uv run pytest tests/test_motion_files.py -v`

## Deviations from Plan

None — plan executed exactly as written. All file contents, meta counts, and test cases match the plan specification verbatim.

## Known Stubs

None. All 7 motion files are fully authored with real parameter values. The model3.json references all files correctly. The test suite validates the complete set.

## Commits

| Task | Hash | Message |
|------|------|---------|
| Task 1: Author 7 motion files | 15ba817 | feat(04-02): author 7 motion3.json files for Teto ambient gestures |
| Task 2: Update model3.json | eeb0ba6 | feat(04-02): update Teto model3.json motion groups to register 7 new files |
| Task 3: Test suite | 73ae58d | test(04-02): schema + IDLE-pin-collision validation for 7 authored motion files |

## Self-Check: PASSED
