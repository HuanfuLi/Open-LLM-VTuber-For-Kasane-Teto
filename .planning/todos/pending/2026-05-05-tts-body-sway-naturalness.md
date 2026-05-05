---
created: 2026-05-05T11:30:00.000Z
title: TTS body sway naturalness — feels mechanical, defer for tuning pass
area: frontend
files:
  - frontend-src/web/src/renderer/WebSDK/src/lappmodel.ts (TTS head-IN sway block in update())
  - frontend-src/patches/tts-head-in-sway.patch (current sway implementation)
---

## Problem

Phase 4 manual smoke (2026-05-05) confirmed the TTS body sway now fires
during speech (after the head-IN injection fix in `efd534f`), but it
doesn't feel natural yet. User verdict:

> Still not very natural.

Earlier rounds of feedback that shaped the current state:
- "too high frequency, too high speed, too low magnitude (angle of
  sway), not smooth all in all"
- After retune to two-sine composition with RMS-scaled amplitude
  (`swayX = (sin(t*0.35)*0.65 + sin(t*0.18+1.7)*0.45) * 60 * env`):
  better but still mechanical.

User opted to defer further tuning and proceed to Phase 4 closure.

## Current implementation (commit `efd534f`)

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

Knobs to consider in a future tuning pass:

| Knob | Current | Lever |
|---|---|---|
| Sine frequencies | 0.35 / 0.18 / 0.28 / 0.14 Hz | lower for slower, gentler arcs |
| Amplitude base | 60° X / 40° Z (× envelope) | the 60/40 caps look high but envelope crushes them — re-balance |
| RMS smoothing α | 0.85 prior / 0.15 new | higher α (e.g. 0.95) → slower envelope changes, less "pulsing" |
| Trigger threshold | env > 0.005 | tune to avoid jittery starts/stops on quiet speech |
| Number of harmonics | 2 sines | add a 3rd lower-freq sine (0.05–0.08 Hz) for breath-scale drift |
| Per-axis phase offset | 1.7 / 1.3 / 0.4 rad | randomize on TTS start for variety |
| Y axis (pitch) | not driven | adding a small pitch nod on volume peaks may feel more alive |

## Why deferred

Phase 4 D-03 vibes verdict was "good enough to ship" — the rig now
visibly responds to speech, props fire correctly, idle face is correct,
and the head-tracking + TTS sway interaction works. Tuning the sway
curve to feel "natural" is an aesthetic polish pass best done with
A/B comparison and possibly a Neuro-sama reference clip side-by-side,
not in the closing minutes of a phase that has already met its goal.

## Origin

User manual smoke verdict during Phase 4 closeout (2026-05-05) after
several rounds of TTS sway iteration. Logged here so a later phase
can pick up the tuning work with full context on what was already
tried and why the current values were chosen.
