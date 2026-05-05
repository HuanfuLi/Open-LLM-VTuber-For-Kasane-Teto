---
phase: 04-vivid-actions
plan: 06
subsystem: integrated-smoke-and-vibes-verdict
tags: [smoke-test, manual-verification, d-03-vibes, phase-closure]
dependency_graph:
  requires: [04-01, 04-02, 04-03, 04-04, 04-05]
  provides: [phase-4-vibes-verdict]
  affects: []
tech_stack:
  added: []
  patterns: [manual-smoke-checklist, vibes-verdict-sign-off]
key_files:
  created:
    - .planning/phases/04-vivid-actions/04-PROP-PERSISTENCE-FIX.md  # P0 post-mortem
    - .planning/todos/pending/2026-05-05-multi-expression-composition-face-plus-action-prop.md
    - .planning/todos/pending/2026-05-05-tts-body-sway-naturalness.md
  modified: []
decisions:
  - D-03 vibes verdict: PASS with two known polish items deferred to next phase
  - Phase 4 ships even though TTS sway naturalness is below ideal — rig responds visibly to speech, idle face is correct, props fire correctly, head tracking works
  - Multi-expression composition (face emo + action prop simultaneously) deferred — frontend single-slot consumer is a Phase 5+ frontend rework
metrics:
  completed: 2026-05-05
---

# Phase 4 Plan 6: Manual Smoke + Vibes Verdict Summary

**One-liner:** End-to-end manual smoke against the rebuilt bundle confirmed
the Phase 4 goal — Teto rig feels visibly closer to Neuro-sama baseline —
with two known polish items captured as deferred todos.

## Smoke Verdict (User-Reported, 2026-05-05)

The user ran an integrated smoke against the live rig and reported back
in iteration cycles. Final state after `efd534f`:

| Check | Verdict |
|---|---|
| Default rest state shows no bread, no mic | PASS |
| LLM emits `[hold-mic]` → mic appears for that response only | PASS |
| LLM emits `[bread-out]` → bread appears, mic does not | PASS |
| `[bread-out]` followed by `[neutral]` → bread vanishes | PASS |
| `[joy]` alone → joy face still works | PASS |
| Cursor head tracking activates on canvas grab | PASS |
| TTS triggers body sway via head IN propagation | PASS (mechanical-feeling, see deferred) |
| Idle face is correct (not mad/flat) | PASS (after `efd534f` inputs dict trim) |
| Lipsync works | PASS |
| 36/36 backend tests GREEN | PASS |

User verdict (verbatim, 2026-05-05):
> All good. Just body sway during TTS still not very natural. Let's defer
> to next stage. Proceed to phase 4 closure.

## D-03 Vibes Verdict: PASS

The phase goal from CONTEXT.md:
> Make the Kasane Teto rig feel visibly closer to Neuro-sama than baseline
> OLVT — bundle continuous-input liveliness (cursor/audio → params),
> authored ambient gestures, richer LLM action vocabulary, and a sidecar
> audio→param research prototype.

What landed:
- **Continuous-input liveliness:** cursor → ParamAngle*IN routing, TTS → ParamAngleXIN/ZIN sway propagated through physics
- **Authored ambient gestures:** 7 motion3.json files (Idle1/2/3, Talk1/2, Gaze1/2/3) — though Talk motions ended up no-ops (orphan body params); ambient idle motions and authored gestures via Idle group work
- **Richer LLM action vocabulary:** 6-entry actionMap (hold-mic, bread-out, hearts, star-eyes, chibi-out, big-applause) wired through extract_action → actions.expressions → frontend setExpression
- **Sidecar audio→params:** standalone tools/audio_to_params/ with DSP fallback shipped, NeuroSync ONNX path stubbed for follow-up

What didn't quite land but is acceptable:
- Talk motion3 files exist but the params they target are orphan in this
  rig — TTS sway is delivered via the head-IN injection in lappmodel.ts
  instead, which works
- TTS sway feels somewhat mechanical at current sine parameters — visible
  motion is present, but a tuning pass is wanted

## P0 Bug Discovered + Fixed Mid-Smoke

The first round of smoke surfaced a P0 bug: Teto rendered with bread + mic
visible by default and stuck across responses. Root cause was a content
convention mismatch between the original VTube Studio bundle's IDLE pins
and the Cubism Web SDK's expression overlay model — fully documented at
`.planning/phases/04-vivid-actions/04-PROP-PERSISTENCE-FIX.md`. Fixed in
commit `3c82225`.

Three SDK-source patches were attempted and reverted before the data-bug
diagnosis landed. The lesson is captured in the post-mortem.

## Deferred to Future Phases

Two polish items captured as todos for Phase 5+:

1. **Multi-expression composition** — frontend's `use-audio-task.ts:130`
   only applies `expressions[0]`, so `[joy] [hold-mic]` shows only the
   mic (action wins by intentional merge order). Two viable approaches
   outlined in the todo: synthetic merged CubismExpressionMotion vs
   apply-after-physics face overlay.
   - File: `.planning/todos/pending/2026-05-05-multi-expression-composition-face-plus-action-prop.md`

2. **TTS sway naturalness** — current two-sine composition with
   RMS-scaled amplitude works but feels mechanical. Knob inventory and
   tuning levers documented for the next pass.
   - File: `.planning/todos/pending/2026-05-05-tts-body-sway-naturalness.md`

## Test Results

```
36 passed, 6 warnings in 2.25s
```

All Phase 4 tests across plans 01–05 stay GREEN.

## Self-Check: PASSED
