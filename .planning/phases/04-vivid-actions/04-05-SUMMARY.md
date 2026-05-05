---
phase: 04-vivid-actions
plan: 05
subsystem: frontend-rebuild-with-vtube-routing-and-tts-sway
tags: [frontend, electron-vite, cubism-sdk, vtube-studio, option-a, body-bob, tts-sway]
dependency_graph:
  requires: [04-02, 04-03]
  provides: [frontend-bundle-with-vtube-routing, tts-driven-body-sway, anyhittest-null-guard]
  affects: [04-06]
tech_stack:
  added:
    - frontend-src/web/  # full upstream Open-LLM-VTuber-Web checkout (gitignored)
    - frontend-src/patches/  # checked-in patches that re-apply on rebuild
  patterns:
    - lappmodel-vtube-routing-patch  # inputs dict + ParameterSettings forwarder
    - tts-head-in-sway-patch  # update()-time additive injection AFTER routing, BEFORE physics
    - bundle-content-regression-test  # asserts patch markers survive rebuild
key_files:
  created:
    - frontend-src/.bundle-source
    - frontend-src/patches/lappmodel-vtube-routing.patch
    - frontend-src/patches/tts-head-in-sway.patch  # replaces obsolete body-bob-extension.patch
    - frontend/.bundle-source
    - tests/test_frontend_bundle.py
  modified:
    - frontend-src/web/src/renderer/WebSDK/src/lappmodel.ts (gitignored, patches re-apply)
    - frontend/index.html
    - frontend/assets/main-*.js  # rebuilt bundle
    - live2d-models/重音テト/重音テト.model3.json  # vtube routing handoff
decisions:
  - Option A patch (face-tracker → ParamAngleXIN/YIN/ZIN twins) over Option B (rewrite VTS deformer chain)
  - TTS sway target = ParamAngleXIN/ZIN (not Talk motion3.json) — head-IN params propagate to body via physics chain
  - Sway injection happens AFTER routing pass and BEFORE physics evaluate so physics chain forwards it to ParamBodyXIN/YIN/ZIN
  - Skip-undriven-routes guard: routing for-loop only forwards inputs the routing pass actually populated this frame
  - inputs dict trimmed to face-tracker keys only (no brow/mouth/jaw/tongue) to fix mad-face from zero-pinned brow/mouth params
  - anyhitTest null-guards _modelSetting before deref (silent no-op until model loaded)
metrics:
  duration: ~3 hours over multiple iteration cycles
  completed: 2026-05-05
  files_created: 5
  files_modified: 4
  commits: 9
---

# Phase 4 Plan 5: Frontend Rebuild + Body Sway Summary

**One-liner:** Replaced the prebuilt OLVT bundle with a from-source rebuild
of upstream Open-LLM-VTuber-Web carrying the Option A vtube-routing patch
and a TTS-driven head-IN sway, plus regression tests that guard the patch
markers in the shipped bundle.

## What Was Built

### Frontend Build Scaffold (`ff7092b`)

```
frontend-src/
  .bundle-source               # tracks upstream commit + patches + build cmd + timestamp
  patches/
    lappmodel-vtube-routing.patch
    tts-head-in-sway.patch      # head-IN sway injection (replaces obsolete body-bob)
  web/                         # gitignored — full upstream checkout
```

`frontend-src/.bundle-source`:
```yaml
upstream: Open-LLM-VTuber/Open-LLM-VTuber-Web
commit: d176e7df2366952e3bacbf12cf9a8b18a4315932
patches:
  - patches/lappmodel-vtube-routing.patch
  - patches/tts-head-in-sway.patch
build_command: npm run build:web
build_output: dist/web/
built_on: 2026-05-05T10:39:56Z
```

### Option A: VTube Studio Routing Patch (`0041dcc`)

Reads `<model>.vtube.json` ParameterSettings and forwards every face-tracker
input to the rig's `*IN` twin instead of the base param the routing chain
expects. Trimmed-down inputs dict (only the keys actually driven by the
face-tracker; brow/mouth/etc. removed entirely so they don't get zero-pinned):

```ts
const inputs: Record<string, number> = {
  FaceAngleX: dx * 30,
  FaceAngleY: dy * 30,    // sign fixed in 4170924 — was -dy*30
  FaceAngleZ: 0,
  FacePositionX: dx * 0.3,
  FacePositionY: dy * 0.3,  // sign fixed in 4170924
  FacePositionZ: 0,
  EyeLeftX: dx * 0.6,
  EyeLeftY: dy * 0.6,
  EyeRightX: dx * 0.6,
  EyeRightY: dy * 0.6,
};
```

Skip-undriven-routes guard (`b0190ed`):
```ts
for (const r of routes) {
  if (!(r.input in inputs)) continue;  // don't forward what we don't drive
  ...
}
```

### TTS Head-IN Sway (`98e5429`, retuned `efd534f`)

Initial body-bob via `ParamBodyAngleX` was a no-op in this rig (the
parameter exists but isn't wired to any deformer). Switched to head-IN
injection because the rig's physics chain forwards head IN → body IN
naturally:

```ts
if (this._lipsync && this._wavFileHandler) {
  const rms = Math.min(1.0, this._wavFileHandler.getRms() * 1.5);
  this._speechRmsSmoothed = this._speechRmsSmoothed * 0.85 + rms * 0.15;
  if (this._speechRmsSmoothed > 0.005) {
    const t = this._userTimeSeconds;
    const env = this._speechRmsSmoothed;
    const swayX = (Math.sin(t * 0.35) * 0.65 + Math.sin(t * 0.18 + 1.7) * 0.45) * 60 * env;
    const swayZ = (Math.sin(t * 0.28 + 1.3) * 0.55 + Math.sin(t * 0.14 + 0.4) * 0.4) * 40 * env;
    this._model.addParameterValueById(getId("ParamAngleXIN"), swayX);
    this._model.addParameterValueById(getId("ParamAngleZIN"), swayZ);
  }
}
```

Injection timing: AFTER routing pass writes idle/cursor face values,
BEFORE physics evaluate. Physics then propagates the IN values down the
ParamBodyXINF/YINF/ZINF chain to actual body deformers.

### anyHitTest Null Guard (`e8be4f7`)

`anyhitTest` was dereferencing `_modelSetting` before model load on cold
boot, crashing the renderer. Added an early return:
```ts
if (!this._modelSetting) return null;
```

### Regression Tests (`tests/test_frontend_bundle.py`, `7a5e544`)

5 tests asserting the shipped bundle is the rebuilt one and carries the
expected patch markers:
- `test_bundle_index_html_references_built_main_js`
- `test_bundle_main_js_exists_and_nonempty`
- `test_bundle_has_vtube_routing_marker`
- `test_bundle_has_tts_head_in_sway` (formerly checked ParamBodyAngleY)
- `test_bundle_source_metadata_records_upstream_commit`

## Misdiagnosis History

The path from "body bob during TTS" to "TTS head-IN sway propagated via
physics" wasn't direct:

| Attempt | Why it failed |
|---|---|
| Drive `ParamBodyAngleX/Y/Z` directly | Param exists but isn't bound to any deformer in this rig — silent no-op |
| Retarget Talk motions to `ParamBodyAngleXIN/YIN/ZIN` | These are orphaned (not in physics input/output, not deformer-bound) — also no-op |
| Body-bob extension on lappmodel | Same orphan-param problem as above |
| Head-IN sway (final) | Head IN → body chain via physics evaluate works correctly |

The breakthrough was recognising that the rig's physics input is `*IN`
twins forwarded by routing, and the body-twin chain reads from those
same head IN values via `cubismphysics.ts` — so injecting at head IN
with the correct timing gets free body propagation.

## Bundle History

| Bundle | Commit | What changed |
|---|---|---|
| `main-DiG_7OOK.js` | `0041dcc` | Initial Option A + body-bob (orphan params, no body motion) |
| `main-DhssZ39u.js` | `4170924` | Vertical drag sign fix + body-bob gain bump |
| `main-fvckw7Y3.js` | `98e5429` | Switched body-bob → head-IN sway |
| `main-CszBi_6b.js` | `efd534f` | Trimmed inputs dict (mad-face fix) + retuned sway |

`frontend/index.html` and `frontend/.bundle-source` updated to track the
current bundle filename.

## Test Results

```
tests/test_frontend_bundle.py:
  test_bundle_index_html_references_built_main_js     PASSED
  test_bundle_main_js_exists_and_nonempty             PASSED
  test_bundle_has_vtube_routing_marker                PASSED
  test_bundle_has_tts_head_in_sway                    PASSED
  test_bundle_source_metadata_records_upstream_commit PASSED

Full suite: 36/36 GREEN
```

## Deferred to Phase 5+

- TTS sway naturalness tuning — still feels mechanical despite multi-sine
  composition. Documented at
  `.planning/todos/pending/2026-05-05-tts-body-sway-naturalness.md`.
- Multi-expression composition (face emotion + action prop simultaneously)
  — frontend `use-audio-task.ts:130` only applies `expressions[0]`.
  Documented at
  `.planning/todos/pending/2026-05-05-multi-expression-composition-face-plus-action-prop.md`.

## Commits

| Commit | Subject |
|---|---|
| `ff7092b` | feat(04-05): set up frontend-src build scaffold + patch stubs |
| `0041dcc` | feat(04-05): build + ship frontend bundle with Option A + body-bob patches |
| `7a5e544` | test(04-05): add bundle-content regression test — 5 tests GREEN |
| `4170924` | fix(04-05): correct vertical drag inversion + bump body-bob gain to 8.0 |
| `b0190ed` | fix(04-05): skip vtube.json routes for inputs we don't drive |
| `e8be4f7` | fix(frontend): null-guard anyhitTest against unloaded model |
| `98e5429` | fix(04-05): rebuild frontend bundle — TTS sway via head IN injection |
| `801c258` | fix(04-05): restore lost bundle hot-patches + bump TTS sway amplitude |
| `efd534f` | fix(04-05): trim routing inputs dict (mad-face fix) + retune TTS sway |

## Self-Check: PASSED
