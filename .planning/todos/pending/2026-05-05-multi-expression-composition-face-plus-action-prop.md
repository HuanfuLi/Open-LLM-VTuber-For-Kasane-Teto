---
created: 2026-05-05T10:40:47.932Z
title: Multi-expression composition — face emotion + action prop simultaneously
area: general
files:
  - src/open_llm_vtuber/agent/transformers.py:91 (action-first merge order)
  - frontend-src/web/src/renderer/src/hooks/utils/use-audio-task.ts:130 (single-slot expressions[0] handler)
  - frontend-src/web/src/renderer/WebSDK/src/lappmodel.ts (setExpression / expression manager apply path)
  - live2d-models/重音テト/Expressions/ (.exp3.json files for emotion + action)
  - .planning/phases/04-vivid-actions/04-PROP-PERSISTENCE-FIX.md (documents the current single-slot tradeoff)
---

## Problem

When the LLM emits both an emotion tag and an action tag (e.g., `[joy] [hold-mic]`), only one of them visibly fires on the avatar. The Phase 4 prop-persistence fix (`3c82225`) put the action expression first in the merged list because the frontend audio handler `use-audio-task.ts:130` only applies `expressions[0]` per audio chunk:

```ts
if (lappAdapter && expressions?.[0] !== undefined) {
  setExpression(expressions[0], lappAdapter, ...);
}
```

Result: action props (mic, bread, hearts, star-eyes, chibi) take precedence and the emotion's face expression is dropped. For `[neutral] [hold-mic]` this is fine (neutral = "Remove Water Mark", no face content), but for `[joy] [hold-mic]` the joy face never shows. User flagged this during Phase 4 manual smoke on 2026-05-05: *"face expression is another layer we have not yet included in action, and currently we are only changing eyes, gestures, chibi, etc."*

A naive iteration fix (frontend iterates the whole `expressions` list and calls `setExpression` for each) doesn't work because `CubismExpressionMotionManager` auto-evicts older entries once the latest fade-in completes — pushing both Love and SV Mic in sequence converges to only SV Mic active. So multi-expression simultaneous activation requires either combining the .exp3 parameter sets at runtime or driving face params outside the Cubism expression queue entirely.

## Solution

Two viable approaches; tradeoff to evaluate before implementation.

**Option (a) — runtime-merged synthetic CubismExpressionMotion**
Build a `CubismExpressionMotion` instance at runtime from the union of two .exp3 parameter sets (e.g., Love + SV Mic), push that single synthetic motion to the expression manager. SDK's auto-eviction is happy because there's still only one entry in the queue.
- Pro: clean architecturally; SDK lifecycle (fade in/out, queue auto-cleanup) is unchanged.
- Con: requires adding a synthetic-expression builder to the bundle source. Some .exp3 entries use Add blend, others Overwrite — combining them needs careful handling so two expressions touching the same parameter (rare but possible) don't fight.

**Option (b) — apply-after-physics face overlay**
Drive emotion face params (eye/brow/mouth) directly in `lappmodel.ts update()` after physics evaluate, similar to how the TTS sway is injected. Pull face param deltas from the emotion's .exp3 file at expression-set time and write them in the update loop.
- Pro: keeps the Cubism SDK and expression queue untouched; action props stay on the existing single-slot path.
- Con: introduces a parallel face-driver alongside the SDK's expression manager. Two systems writing face params is harder to reason about. Fade in/out timing has to be re-implemented.

Recommendation lean (no commitment): start with (a) — synthetic merged expression — because it preserves the SDK's mental model. If the Add/Overwrite combination logic gets ugly, fall back to (b).

Either approach also wants the backend to send the full merged list (which it already does) — the change is on the frontend consumer side.

## Origin

User manual smoke verdict during Phase 4 closeout (2026-05-05). Phase 4 D-13 actions work for prop visibility but emotion + action composition is the missing piece that prevents the rig from feeling fully expressive. Logged here so Phase 5+ planning has the context.
