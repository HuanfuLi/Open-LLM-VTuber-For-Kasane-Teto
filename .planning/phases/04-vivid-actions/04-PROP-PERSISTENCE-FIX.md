---
phase: 04-vivid-actions
type: post-execution-bugfix
severity: P0
fixes: [04-02, 04-03]
tags: [live2d, expression-stacking, idle-motion, vtube-studio, cubism-sdk]
key_files:
  modified:
    - live2d-models/重音テト/Motions/IDLE.motion3.json
    - src/open_llm_vtuber/agent/transformers.py
    - tests/test_motion_files.py
    - tests/test_actions_extractor.py
commit: 3c82225
completed: 2026-05-05
---

# Phase 4 P0 Bug — Prop Persistence

## Symptom

After Phase 4 plans 02–05 landed, Teto rendered with **bread *and* mic
visible at all times** in the rest pose, regardless of which action tags
the LLM emitted. Subsequent responses could not turn the props off,
even when the LLM emitted `[neutral]` or no action tag at all.

User report (paraphrased):
- "Teto is always in [bread-out] gesture"
- "I even triggered a state that Teto is holding bread and mic at the
  same time"
- "It's a state issue not a prompt issue, and it is a regression"

## Misdiagnosis history

The bug *looked* like a Cubism Web SDK queue problem — multiple
expressions stacking in `CubismExpressionMotionManager` and never being
evicted. Several attempts to clear the queue from the bundle (commits
that no longer exist in main; reset to `5521b7f` discarded them) all
failed:

| Attempted fix | Why it didn't work |
|---|---|
| `lappAdapter.resetExpression()` before `setExpression(...)` | Method does not exist on `LAppLive2DManager` — silent no-op. |
| `_expressionManager.stopAllMotions()` before push | Clears `_motions` but leaves `_expressionParameterValues` populated — params stay set. |
| `popBack()` loop on `_motions` and `_fadeWeights` | Infinite-looped (likely against a wrapped getter) and froze the JS thread → no audio, no lipsync, no talk. |

After the third regression broke playback entirely, the branch was
reset to `5521b7f` (which had already shipped a working bundle with
cursor head-tracking, body-bob, Option A vtube routing).

## Actual root cause

The bug had two distinct halves, neither in the SDK:

### Cause A — IDLE.motion3.json pin convention (data bug)

The original VTube Studio bundle's `IDLE.motion3.json` (committed in
`a21b5bf`, untouched by Phase 4) pins **36 parameters every frame** to
provide a stable rest pose. Two of those pins were:

```json
{ "Id": "ParamBHandIN",  "Segments": [0, 1.0, 0, 1.0, 1.0] }
{ "Id": "ParamSVMCON",   "Segments": [0, 1.0, 0, 1.0, 1.0] }
```

In this rig's parameter convention, those values mean **bread visible**
and **mic visible**. The action expression files Add `+1` to the same
parameters, taking the value from `1.0` to `2.0` — at or above the
parameter's max — producing **no visible change**.

Net effect: the rig was permanently stuck in "bread + mic ON" because
the IDLE motion drove the params to the visible state every frame,
and the action expressions could not overcome it.

This was *not* an SDK queue bug. It was a content-convention bug.

Heart / Star Eye / Chibi pins also sit at `1.0` in IDLE, but those
expressions Add `-1.0` (or use Paramchibi's much larger range), so for
them `1.0` correctly means "off". The convention is inverted between
the two prop families.

### Cause B — `use-audio-task.ts` only reads `expressions[0]`

The frontend audio handler (`frontend-src/web/src/renderer/src/hooks/utils/use-audio-task.ts`,
line 130) applies only the first element of the `expressions` array:

```ts
if (lappAdapter && expressions?.[0] !== undefined) {
  setExpression(expressions[0], lappAdapter, ...);
}
```

The Phase 4 D-06 backend merge in `actions_extractor` was emotion-first:
```python
merged = (expressions or []) + (action_expressions or [])
```

So `[neutral] [hold-mic]` became `[0, "SV Mic"]` on the wire. The
frontend ran `setExpression(0)` (= "Remove Water Mark", a watermark
cosmetic), and the action expression at index 1 was silently dropped.
**Action props never fired.**

Combined with Cause A, the user saw bread + mic visible by default
*and* could not affect them with action tags — exactly matching the
"always in [bread-out] gesture" complaint.

## The fix (commit `3c82225`)

Two minimal changes, no SDK-source patches, no bundle hot-patches:

### Fix A — flip IDLE pins to OFF

`live2d-models/重音テト/Motions/IDLE.motion3.json`:

```diff
- "ParamBHandIN":  Segments [0, 1.0, 0, 1.0, 1.0]
+ "ParamBHandIN":  Segments [0, 0.0, 0, 1.0, 0.0]
- "ParamSVMCON":   Segments [0, 1.0, 0, 1.0, 1.0]
+ "ParamSVMCON":   Segments [0, 0.0, 0, 1.0, 0.0]
```

Now rest = hidden. Action expression `Add +1` takes the value to `1.0`
= visible. When the expression is auto-evicted from the Cubism queue,
`_expressionParameterValues.overwriteValue` (captured first frame at
the IDLE pin = `0.0`) reverts the parameter to `0.0` = hidden. The
SDK's existing eviction logic now produces the correct behaviour
because the data convention finally matches what the SDK assumes.

Heart / Star / Chibi pins are NOT touched — their convention is
inverted and `1.0` is correct for them.

### Fix B — action-first merge order

`src/open_llm_vtuber/agent/transformers.py`:

```diff
- merged = (expressions or []) + (action_expressions or [])
+ merged = (action_expressions or []) + (expressions or [])
```

Now `expressions[0]` is the action when one is present, and the
frontend's single-slot `setExpression(expressions[0])` fires the prop.
Emotion remains as fallback when no action tag is emitted.

### Tradeoff

When both an emotion *and* an action tag are present, the emotion
expression is dropped (frontend takes only `[0]`). For the persona-
required `[neutral]` prefix this is a no-op (Remove Water Mark has no
face content). For `[joy] [hold-mic]`, joy's Love face is dropped in
favour of the mic prop — strictly better than the prior state, where
the mic never appeared at all.

Multi-expression simultaneous activation (face *and* prop on the same
response) is a separate Phase 5+ enhancement. It requires either
combining .exp3 parameter sets at runtime or modifying the Cubism
auto-eviction — out of scope for this P0 fix.

## Tests added

| Test | What it locks in |
|---|---|
| `test_idle_action_prop_pins_are_off` (test_motion_files.py) | `ParamBHandIN` and `ParamSVMCON` in IDLE pinned at `0.0`. |
| `test_decorator_orders_action_before_emotion` (test_actions_extractor.py) | `[joy] [hold-mic]` produces `expressions == ["SV Mic", 3]` — action leads. |

35 / 35 tests passing post-fix.

## Verification checklist (manual smoke)

After hard-reload of the frontend:

- [x] Default rest state: **no bread, no mic** visible
- [x] LLM emits `[hold-mic]`: mic appears for that response only
- [x] LLM emits `[bread-out]`: bread appears, mic does not
- [x] `[bread-out]` followed by `[neutral]` next response: bread vanishes
- [x] `[joy]` alone (no action tag): joy face still works
- [ ] `[joy] [hold-mic]`: mic appears, joy face dropped (documented tradeoff)

## Lesson

When a symptom looks like an SDK or framework bug, verify the *data*
the SDK is consuming before patching the SDK. The IDLE pin values
were the original VTube Studio bundle's choice — designed for
VTube Studio's hotkey-toggle expression model, not the Cubism Web
SDK's continuous-overlay model. Three failed bundle hot-patches
chased a queue-management hypothesis that was never the real bug.

The investigation that finally solved it followed the data path
end-to-end: `extract_action` → `actions.expressions` → wire →
`use-audio-task.ts` → `setExpression` → `CubismExpressionMotionManager`
→ `setParameterValueById` → `IDLE.motion3.json` keyframes. The IDLE
pins were the *first* thing in that chain that wasn't unit-tested,
and that is where the bug was.
