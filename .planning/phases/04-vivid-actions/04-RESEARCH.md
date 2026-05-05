# Phase 4: Vivid Actions - Research

**Researched:** 2026-05-04
**Domain:** Live2D Cubism Web SDK, motion3.json authoring, audio-RMS routing, LLM action vocabulary, audio-to-parameter models
**Confidence:** HIGH (core stack fully verified); MEDIUM (sidecar adapter landscape); HIGH (Phase 1-3 surface area predicted from source)

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- **D-01:** Bundle all three liveliness levers in one phase (continuous-input params + richer vocabulary + ambient gestures).
- **D-02:** Production-ish ambition for the three levers, plus a side research bet on a text/audio → continuous-parameter adapter built as a sidecar prototype.
- **D-03:** Success is vibes-graded: "Watching Teto idle, talk, and react feels visibly closer to Neuro-sama than baseline OLVT."
- **D-04:** Continuous-param routing lives in the frontend. Apply the documented Option A patch from `patches/lappmodel-vtube-routing.md` to `lappmodel.ts`, AND extend it with TTS-audio-RMS routing for body bob. Frontend rebuild required (not bundle hot-patch).
- **D-05:** Ambient idle gestures driven by authored motion content, not code-side noise generator. Author additional `motion3.json` files for Teto (talk loops, breath, weight shift, gaze variants) and let the existing motion system play them probabilistically.
- **D-06:** Richer-vocabulary actions reuse Phase 1-3 plumbing. Extend `motionMap` / new `actionMap` entries in `model_dict.json`. No new action channel on the wire.
- **D-07:** Research-bet adapter ships as a sidecar standalone Python tool that takes TTS audio + transcript and emits a parameter-trajectory file. Not wired into the live WebSocket loop.
- **D-08:** Flat tag schema only. `[hold-mic]`, `[bread-out]`, `[lean-left]`. No parameterized tags.
- **D-09:** Ambient gestures are system-only and invisible to the LLM. They fire on a timer regardless of LLM output.
- **D-10:** The LLM learns the new vocabulary via an auto-generated list, mirroring the `emo_str` pattern at `live2d_model.py:51`. Adding an action = JSON edit, no prompt-template edits.
- **D-11:** Typed JSON action protocol deferred to a future phase.
- **D-12:** Phase 4 is explicitly Teto-first. Generic rig story is a later phase.
- **D-13:** Teto's quirky variants get exposed as LLM actions: `SV Mic`, `Utau Mic`, `SV Baguette`, `chibi`, `Heart`, `Star Eye`.
- **D-14:** Authored Talk motions are Teto-only.
- **D-15:** Phase 4 work is fork-only. No PR back to upstream OLVT.

### Claude's Discretion
- Exact motion-file naming and on-disk layout for D-05 (Teto's existing convention is `Motions/IDLE.motion3.json` — match it).
- Audio-RMS smoothing window and gain for body-bob routing in D-04.
- Ambient gesture timing distribution (Poisson vs uniform vs weighted-random) for D-05/D-09.
- Sidecar adapter input/output format details for D-07 (probably JSON or CSV trajectory).
- Tag casing convention (`[hold-mic]` vs `[hold_mic]`) — pick whatever matches Phase 1-3's choice.
- Whether to drop or rewrite the broken `tapMotions` references in `model_dict.json`.

### Deferred Ideas (OUT OF SCOPE)
- Typed JSON action protocol (neuro-sdk style).
- Live-pipeline integration of the research-bet adapter.
- Generic-model parity (mao_pro, shizuku) for D-04/D-05/D-13 work.
- Upstream-PR readiness for generic pieces.
- Authored Talk motions for default models.
</user_constraints>

---

## Summary

Phase 4 has four workstreams with distinct technical surfaces. Research fully resolves the critical unknowns in each.

**Workstream A (Frontend rebuild):** The Open-LLM-VTuber-Web repo is an Electron + Vite + React + TypeScript project. The web renderer bundles to `out/renderer/` via `electron-vite`. For in-tree use, the build output (`index.html` + hashed asset files) is copied into the `frontend/` directory. The existing bundle already handles audio as base64 WAV via `new Audio(dataUrl)` and drives lipsync through `LAppWavFileHandler.start(url)`. The pre-computed `volumes` array sent by the backend (20 ms RMS chunks via `_get_volume_by_chunks`) is currently passed to the React layer but not used for body-bob — it is the ideal hook point for D-04's body-bob extension. No new backend signal is needed.

**Workstream B (Authored motions):** Teto's IDLE.motion3.json is a 1-second looping file at 30 FPS with 36 curves that pin prop-state and effect-toggle parameters to their "clear" values. It does NOT animate head, body, breath, or eye-ball parameters — those are left for VTube routing (ParamAngleXIN etc) and SDK breath. Talk-loop motions MUST NOT touch any of the 36 IDLE-pinned parameters or they will fight the watermark-and-prop-reset logic. Sleep.motion3.json (6.8 s, 60 FPS, 7 curves) animates ParamAngleXIN/YIN/ZIN, eye open, mouth shape — it demonstrates the schema for head-pose motions.

**Workstream C (Action vocabulary):** The `actions.expressions` field is already in the wire payload and handled by the frontend. Phase 1-3 must add `actions.motions`. Phase 4's `actionMap` in `model_dict.json` can route expression-file names to flat tags and reuse the same `expressions` dispatch on the frontend side (expressions API accepts expression names as strings). No new frontend field needed for Teto's prop/variant expressions. For Teto's unique expressions, the frontend already resolves expressions by string name via `LAppAdapter.setExpression(name)`.

**Workstream D (Sidecar):** NeuroSync (AnimaVR) is the strongest candidate — it outputs 52 ARKit blendshape weights at 60 fps from audio-only input, has a local inference API, and blendshapes map straightforwardly to Live2D parameters (jawOpen→ParamJawOpenIN, eyeBlink→ParamEyeLOpen/R, headRoll→ParamAngleZIN, etc.). License is CC BY-NC 4.0 (research use acceptable). NVIDIA Audio2Face-3D is higher quality but requires a NIM container and NVIDIA Open Model License — practical only if a GPU is available. SadTalker, EchoMimic, JoyVASA, and AniPortrait all output video frames, not parameter streams — they are not useful as-is for a trajectory file.

**Primary recommendation:** Build the frontend in-tree from the upstream Web repo source with the Option A patch applied. Use the existing `volumes` array (already sent by backend) as the RMS source for body-bob in the patched `update()`. Author new motion3.json files that animate only the 7 parameters Sleep.motion3.json touches (head pose, eye open, mouth). Wire `actionMap` tag → expression file name; reuse the existing `expressions` dispatch path. Use NeuroSync Local API for the sidecar.

---

## Standard Stack

### Core (frontend rebuild)
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| Node.js | 22.x (available) | Build runtime | Already installed |
| npm | 10.9 (available) | Package manager | Upstream uses npm |
| electron-vite | As upstream | Vite config wrapper | Upstream uses this |
| TypeScript | As upstream | Language | Upstream repo |
| React 18 | As upstream | UI layer | Upstream repo |
| Cubism SDK for Web | Bundled in WebSDK/ | Live2D rendering | Part of upstream |

### Core (sidecar)
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| Python | 3.10.19 (available) | Runtime | Already installed |
| uv | 0.10.4 (available) | Package manager | Project standard (CLAUDE.md) |
| NeuroSync_Local_API | latest | Audio→blendshape transformer | Only OSS local audio-to-face param model |
| librosa or scipy | latest stable | WAV loading / feature extraction | Standard audio processing |
| numpy | latest stable | Array math | Ubiquitous |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| pydub | already in project | WAV RMS chunking | Reuse existing audio util |
| loguru | already in project | Logging in sidecar | Project standard |
| Pydantic v2 | already in project | Sidecar config validation | Project standard |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| NeuroSync (sidecar) | NVIDIA Audio2Face-3D | A2F-3D has better quality but requires NIM container + GPU + NVIDIA license; NeuroSync runs on CPU locally with CC BY-NC 4.0 |
| authored motion3.json | code-side noise generator | D-05 locked authored content; generator was explicitly rejected |
| actionMap via expressions | new wire field for motions | Expressions API already handles string-named expressions; no new wire needed for Teto prop variants |

**Frontend build install:**
```bash
cd path/to/Open-LLM-VTuber-Web
npm install
npm run build       # produces out/renderer/
# Copy out/renderer/* into fork's frontend/
```

**Sidecar install:**
```bash
cd tools/audio_to_params
uv init --no-readme
uv add numpy scipy loguru pydantic
# NeuroSync_Local_API: clone and install as editable
```

**Version verification:** Node 22.19.0 and npm 10.9.3 confirmed present. Python 3.10.19 confirmed present. uv 0.10.4 confirmed present.

---

## Architecture Patterns

### A. Frontend Rebuild Pipeline

The upstream Open-LLM-VTuber-Web repo is a standard Electron + Vite project with `electron.vite.config.ts` as the build config. The renderer output lives at `out/renderer/` (Electron default for electron-vite). The file that concerns Phase 4 is `src/renderer/WebSDK/src/lappmodel.ts`.

**In-tree strategy (D-04, D-15: fork-only, no submodule):**
1. Clone Open-LLM-VTuber-Web source into `frontend-src/` (NOT tracked as submodule — it is a build-time dependency).
2. Apply the four hunks from `patches/lappmodel-vtube-routing.md` to `frontend-src/src/renderer/WebSDK/src/lappmodel.ts`.
3. Extend the same file with body-bob RMS routing (see Pattern B below).
4. `npm install && npm run build` in `frontend-src/`.
5. Copy `frontend-src/out/renderer/` → replace `frontend/` contents.
6. Commit the new bundle to `frontend/` (same pattern as the existing "vendor frontend bundle" commit).

**The `frontend/` directory is the single build artifact** — it is not a submodule. The `frontend-src/` directory is gitignored or added to `.gitignore` with a note in the commit message.

### B. Body-Bob RMS Extension (D-04 extension to Option A)

The backend already computes `volumes` — a list of normalized RMS values at 20 ms intervals — and sends them in the `audio` WebSocket message alongside `audio` (base64 WAV). The frontend receives this as `Gt.volumes`.

**Current frontend path (from bundle analysis):**
```
WebSocket message "audio"
  → ct({ audioBase64, volumes, sliceLength, displayText, expressions, forwarded })
  → addAudioTask(rt) → et(rt) [Promise]
    → new Audio(dataUrl)
    → wt._wavFileHandler.start(dataUrl)  // drives lipsync via getRms()
    → wt.startRandomMotion("Talk", PriorityNormal)
    → Ct.setExpression(expressions[0])   // if expressions present
    → audio.play()
```

The `volumes` array is passed but not used for body-bob today. The cleanest hook point is inside `lappmodel.ts`'s `update()` method, where `_wavFileHandler.getRms()` already drives `ParamMouthOpenY`. A parallel read of the same RMS value (or the volumes-backed equivalent) can drive a body-bob parameter.

**Option A patch already synthesizes `MouthOpen` as 0 in the inputs dict** — meaning `ParamJawOpenIN` gets no audio-driven signal from the cursor inputs. The body-bob extension should drive a body sway parameter (e.g., `ParamBodyAngleX` or `ParamBodyAngleY`) proportional to `_wavFileHandler.getRms()`. Smoothing: use an exponential moving average with alpha ~0.15 to avoid jitter.

```typescript
// In update(), after Option A routing block:
if (this._lipsync && this._wavFileHandler) {
  const rms = Math.min(1.0, this._wavFileHandler.getRms() * 1.5);
  // Body bob: small Y sway proportional to speech volume
  this._speechRmsSmoothed = (this._speechRmsSmoothed ?? 0) * 0.85 + rms * 0.15;
  this._model.addParameterValueById(
    CubismFramework.getIdManager().getId("ParamBodyAngleY"),
    this._speechRmsSmoothed * 3.0  // max 3 degrees of sway
  );
}
```

Add `_speechRmsSmoothed: number = 0;` to field declarations.

**Note:** `ParamBodyAngleY` is a standard Cubism ID, not an IN-suffix ID. Teto's vtube.json does NOT route a body-Y parameter, so this goes directly to the standard Live2D parameter which is bound to body sway in the rig.

### C. motion3.json Authoring (D-05)

**Schema (confirmed from spec and Teto's existing files):**

```json
{
  "Version": 3,
  "Meta": {
    "Duration": <float_seconds>,
    "Fps": 30.0,
    "Loop": true,
    "AreBeziersRestricted": false,
    "FadeInTime": 0.5,
    "FadeOutTime": 0.5,
    "CurveCount": <N>,
    "TotalSegmentCount": <sum_of_segments_per_curve>,
    "TotalPointCount": <sum_of_points_per_curve>
  },
  "Curves": [
    {
      "Target": "Parameter",
      "Id": "<Live2D_parameter_id>",
      "FadeInTime": 0.0,
      "FadeOutTime": 0.0,
      "Segments": [
        0, <value_at_t0>,    // t=0, value (linear start)
        0, <value_at_t1>,    // segment type 0=linear, then t=?, val
        ...
      ]
    }
  ]
}
```

**Segment encoding:** Flat array. Each point is `[time, value]`. Segment type prefix: `0` = linear, `1` = cubic bezier (adds 2 control points = 4 extra floats), `2` = stepped, `3` = inverse-stepped. For simple talk-loop motions, linear segments (type 0) are sufficient.

**Minimal looping motion example (2-second talk loop):**
```json
{
  "Version": 3,
  "Meta": {
    "Duration": 2.0, "Fps": 30.0, "Loop": true,
    "AreBeziersRestricted": false, "FadeInTime": 0.3, "FadeOutTime": 0.3,
    "CurveCount": 3, "TotalSegmentCount": 9, "TotalPointCount": 18
  },
  "Curves": [
    {
      "Target": "Parameter", "Id": "ParamAngleXIN",
      "Segments": [0, 0.0, 0, 0.5, -3.0, 0, 1.0, 0.0, 0, 1.5, 3.0, 0, 2.0, 0.0]
    },
    {
      "Target": "Parameter", "Id": "ParamAngleYIN",
      "Segments": [0, 0.0, 0, 1.0, -2.0, 0, 2.0, 0.0]
    },
    {
      "Target": "Parameter", "Id": "ParamBreath",
      "Segments": [0, 0.5, 0, 1.0, 1.0, 0, 2.0, 0.5]
    }
  ]
}
```

**Parameters safe to animate (not in IDLE's 36-curve pin list):**
- `ParamAngleXIN`, `ParamAngleYIN`, `ParamAngleZIN` — head pose (only in Sleep.motion3.json, not IDLE)
- `ParamEyeLOpen`, `ParamEyeROpen` — eye open (only in Sleep)
- `ParamMouthFormP`, `ParamMouthOpenY` — mouth shape (only in Sleep)
- `ParamBreath` — breath (handled by SDK auto-breath in vtube.json but safe to author over)
- `ParamBodyAngleX`, `ParamBodyAngleY` — body tilt (not in either existing motion)
- `ParamEyeBallX`, `ParamEyeBallY` — gaze direction (not in either existing motion)

**Parameters MUST NOT animate (IDLE pins them to neutral/off):**
All 36 parameters from the IDLE motion — including `ParamWatermarkOFF`, `PramaAngry2`, `ParamHeartEYEON`, `ParamBlankEYEON`, `ParamTearON`, `ParamStarEYE`, `ParamEYEClosed2ON`, `ParamCircleEYEON`, `ParamBlush`, `ParamMicON`, `ParamSVMCON`, `ParamKnifeHandsON`, `ParamBHandsON`, `ParamBHandIN`, `Paramchibi`, `Paramchibi2`, `ParamCRY`, `ParamCRY2`, `ParamSweat1-4`, `ParamBlackEYE`, `ParamCryEye`, `ParamTearEye1/2`, and all `ParamPhyCryEye*` variants. IDLE resets these to 0 (or -5.2 for cry/sweat params). Talk-loop motions that touch these will fight the watermark and prop-state reset.

**Recommended authored files for D-05:**

| File | Duration | FPS | Params driven | Purpose |
|------|----------|-----|---------------|---------|
| `Motions/Talk1.motion3.json` | 2.0 s | 30 | AngleXIN, AngleYIN, Breath | Primary talk loop — small head wag |
| `Motions/Talk2.motion3.json` | 2.5 s | 30 | AngleXIN, AngleZIN, EyeBallX | Secondary talk loop — head tilt + gaze |
| `Motions/Breath.motion3.json` | 3.2 s | 30 | Breath, BodyAngleY | Idle breath cycle |
| `Motions/WeightShift.motion3.json` | 4.0 s | 30 | BodyAngleX, AngleZIN | Weight-shift side sway |
| `Motions/Gaze1.motion3.json` | 1.5 s | 30 | EyeBallX, EyeBallY | Brief gaze drift left |
| `Motions/Gaze2.motion3.json` | 1.5 s | 30 | EyeBallX, EyeBallY | Brief gaze drift right |
| `Motions/Gaze3.motion3.json` | 2.0 s | 30 | EyeBallX, EyeBallY, AngleYIN | Gaze-up-and-away |

**model3.json update** — extend the `Motions` block:
```json
"Talk": [
  { "File": "Motions/Talk1.motion3.json" },
  { "File": "Motions/Talk2.motion3.json" }
],
"Idle": [
  { "File": "Motions/IDLE.motion3.json" },
  { "File": "Motions/Breath.motion3.json" },
  { "File": "Motions/WeightShift.motion3.json" },
  { "File": "Motions/Gaze1.motion3.json" },
  { "File": "Motions/Gaze2.motion3.json" },
  { "File": "Motions/Gaze3.motion3.json" }
]
```

`startRandomMotion("Talk", PriorityNormal)` (already called by the frontend on every audio message) will randomly select from the Talk group. `startRandomMotion("Idle", PriorityIdle)` (called when motionManager.isFinished()) will randomly select from the Idle group. No code change is required on the frontend — only content authoring and model3.json edits.

### D. Phase 1-3 Surface Area (predicted shape for Phase 4 integration)

From reading the current source files:

**`Actions` dataclass** (`output_types.py`) currently has:
- `expressions: Optional[List[str] | List[int]]`
- `pictures: Optional[List[str]]`
- `sounds: Optional[List[str]]`

Phase 1-3 task 1.1 adds: `motions: Optional[List[str]]`

After Phase 1-3, `Actions.to_dict()` will include `motions` when present. The wire payload will have `actions: { expressions: [...], motions: [...] }`.

**`Live2dModel`** (`live2d_model.py`) currently reads `emotionMap` from model_dict.json. Phase 1-3 tasks 1.2 and 2.1 add `motionMap` reading and `extract_motion` / `remove_emotion_keywords` generalization.

**`actions_extractor` decorator** (`transformers.py`) currently only extracts emotions and populates `actions.expressions`. Phase 1-3 task 1.3 extends it to also extract motion tags (from `motionMap` keys) and populate `actions.motions`.

**Frontend** currently reads `Gt.actions.expressions` and calls `Ct.setExpression(expressions[0])`. Phase 1-3 (or Phase 4's frontend rebuild) must also read `Gt.actions.motions` and call `wt.startMotion(groupName, index, PriorityNormal)` or equivalent.

**Phase 4 integration confidence:** The Phase 4 action vocabulary (D-13 expressions like `[hold-mic]`, `[bread-out]`) routes to expression files. These use the `expressions` field already established by Phase 1-3 (string expression names). Phase 4 only needs to add `actionMap` entries to `model_dict.json` and extend `emo_str` → `action_str` to include them. No new wire field needed for Teto's expression-based actions.

### E. Action Prompt Injection (D-10)

**Current emo_str injection path:**
1. `live2d_model.py:51` — `self.emo_str = " ".join([f"[{key}]," for key in self.emo_map.keys()])`
2. Used via template variable `<insert_emomap_keys>` in `prompts/utils/live2d_expression_prompt.txt`
3. Injected into the system prompt at character-config load time (searched `service_context.py` for prompt construction — pattern is load prompt template, substitute `emo_str`)

**Phase 4 `action_str` pattern:**
```python
# In Live2dModel.set_model(), after emo_str is built:
action_map = self.model_info.get("actionMap", {})
self.action_str = " ".join([f"[{key}]," for key in action_map.keys()])
# Combined prompt string:
self.full_action_str = self.emo_str + " " + self.action_str
```

The prompt template `live2d_expression_prompt.txt` currently uses `<insert_emomap_keys>`. Phase 4 can either:
- Replace the placeholder with `<insert_action_keys>` and substitute `full_action_str`, OR
- Add a second placeholder `<insert_actionmap_keys>` with a separate section explaining prop/variant actions

The CONTEXT.md locked decision D-10 says "Adding an action = JSON edit, no prompt-template edits." This favors option 1: a single combined placeholder that the auto-generated string fills in. The existing prompt template already calls them "expressions or actions," so no semantic change is needed.

**Precise recommendation:** Add `actionMap` keys into `emo_str` by merging both maps before building the string. Rename `emo_str` to `action_str` or build `action_str` as the union. Update `live2d_expression_prompt.txt` placeholder name once (from `<insert_emomap_keys>` to `<insert_action_keys>`). After this one-time template edit, every new action added to `actionMap` auto-appears in the prompt.

### F. Teto Expression ActionMap Design (D-13)

**Expression files confirmed present** in `live2d-models/重音テト/Expressions/`:
- `【SV】Mic.exp3.json` — sets `ParamSVMCON=1` (Add blend). Tag: `[hold-mic]`
- `【Utau】Mic.exp3.json` — sets `ParamMicON=-1` (Add blend). Tag: `[utau-mic]`
- `【SV】Baguette.exp3.json` — sets `ParamBHandIN=1` (Add blend). Tag: `[bread-out]`
- `chibi.exp3.json` — sets `Paramchibi=10` (Add blend). Tag: `[chibi]`
- `Love.exp3.json` — heart expression. Tag: `[hearts]`
- `Star Eye.exp3.json` — sets `ParamStarEYE`. Tag: `[star-eyes]`

Note: All expression files have `FadeInTime: 0.0, FadeOutTime: 0.0`. They snap instantly. The existing `expressions` dispatch path calls `model.setExpression(name)` by the string name from the manifest — "SV Mic", "chibi", etc. The actionMap should use these exact manifest names as values.

**Proposed `actionMap` in `model_dict.json` for Teto:**
```json
"actionMap": {
  "hold-mic":  "SV Mic",
  "utau-mic":  "Utau Mic",
  "bread-out": "SV Baguette",
  "chibi":     "chibi",
  "hearts":    "Heart",
  "star-eyes": "Star Eye"
}
```

The values are the expression `Name` fields from `重音テト.model3.json` (e.g., `"Name": "SV Mic"`). The LAppModel `setExpression(name)` call resolves these by string lookup. Phase 4 backend reads actionMap tags from LLM output, puts them in `actions.expressions`, and the existing frontend dispatch handles them.

**Broken tapMotions (D-15 discretion):** `model_dict.json` Teto entry has `tapMotions` pointing to `tap_body`, `shake`, `pinch_in`, `flick_head` etc. which do not exist as motion files. Recommendation: drop the `tapMotions` block entirely and replace with the new `actionMap` block. The tap interaction is not a core feature of this phase.

### G. VTube Routing — Confirmed Parameter Map

From `重音テト.vtube.json` (22 ParameterSettings entries), the routes Phase 4's Option A patch will activate:

| VTS Input | Live2D Output | Notes |
|-----------|--------------|-------|
| FaceAngleX | ParamAngleXIN | head left-right |
| FaceAngleY | ParamAngleYIN | head up-down |
| FaceAngleZ | ParamAngleZIN | head roll |
| EyeOpenLeft | ParamEyeLOpen | left eye open |
| EyeOpenRight | ParamEyeROpen | right eye open |
| MouthSmile | ParamEyeLSmile, ParamEyeRSmile, ParamMouthForm | smile |
| BrowLeftY | ParamBrowLYIN | left brow |
| BrowRightY | ParamBrowRYIN | right brow |
| (auto-breath) | ParamBreath | UseBreathing=true |
| JawOpen | ParamJawOpenIN | jaw |
| MouthShrug | ParamMouthShrugIN | mouth shrug |
| MouthX | ParamMouthXIN | mouth left-right |
| EyeLeftX | ParamEyeBallX | eye gaze X |
| EyeRightY | ParamEyeBallY | eye gaze Y |
| CheekPuff | ParamCheekPuffIN | cheek puff |
| MouthPucker | ParamMouthPuckerIN | pucker |
| MouthFunnel | ParamMouthFunnel | funnel |
| MouthPressLipOpen | ParamLipPress | lip press |
| FacePositionZ | ParamFacePositionZIN | face depth |

The patch synthesizes FaceAngleX/Y/Z from `_dragX` / `_dragY`. EyeOpen defaults to 1 (eyes open). All other inputs default to 0. This means cursor drag immediately drives head pose through Teto's IN-suffix twins.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Audio→face blendshape model | Custom neural network | NeuroSync Local API | Pre-trained transformer, runs locally, CC BY-NC 4.0 |
| WAV feature extraction | Manual FFT | scipy.signal / librosa | Mel spectrogram extraction is non-trivial |
| motion3.json generation | Runtime code generator | Hand-authored JSON files | D-05 explicitly requires authored content; code generators produce mechanical-looking motion |
| VTube parameter routing | Custom mapping table | Parse existing `.vtube.json` | Option A patch already does this; don't duplicate |
| LLM action dispatch | New WebSocket channel | Extend existing `expressions` field | D-06 locked: reuse existing plumbing |
| Ambient gesture timer | Complex scheduler | `startRandomMotion` already in SDK | Cubism SDK's random-selection from motion group is exactly this feature |

**Key insight:** The Cubism SDK's `startRandomMotion(group, priority)` is already the ambient-gesture system. Adding motion files to the Idle/Talk motion groups in `model3.json` is all that is needed — no backend code, no timers, no scheduler.

---

## Common Pitfalls

### Pitfall 1: motion3.json touching IDLE-pinned parameters
**What goes wrong:** A talk-loop motion that animates `ParamWatermarkOFF` or `ParamMicON` will fight the IDLE motion's constant-value pins. When the talk motion ends and IDLE resumes, parameters snap back. Worse, while the talk motion plays, props may disappear or the watermark may reappear.
**Why it happens:** IDLE.motion3.json pins 36 parameters at specific values every frame. Any motion in the Talk/Idle groups that writes those same parameters creates a race between the two motion layers.
**How to avoid:** Only animate the 7 "safe" parameters confirmed from the Sleep motion: AngleXIN, AngleYIN, AngleZIN, EyeLOpen, EyeROpen, MouthFormP, MouthOpenY — plus BodyAngleX/Y and EyeBallX/Y which neither existing motion touches.
**Warning signs:** During talk, props (mic, baguette) disappear or the watermark flickers.

### Pitfall 2: Frontend build output path mismatch
**What goes wrong:** `npm run build` in the Electron-Vite project produces output in `out/renderer/` (for desktop app mode). If the planner copies the wrong directory, the `index.html` will reference incorrect asset paths or miss the Cubism SDK libs.
**Why it happens:** electron-vite separates main/preload/renderer outputs. Only the renderer output is relevant for the browser/WebSocket server use case.
**How to avoid:** Copy `out/renderer/` (contains `index.html` and `assets/`) to `frontend/`. Verify `frontend/index.html` references the new asset hash, and that `frontend/libs/` still contains Cubism libs (they should be copied by Vite's static copy plugin, but verify).
**Warning signs:** Browser console shows 404 for `.js` assets or `live2dcubismcore.min.js`.

### Pitfall 3: `createRenderer(o=4)` hot-patch lost after rebuild
**What goes wrong:** The current bundle has a one-line hot-patch `createRenderer(o=4)` that increases WebGL vertex buffer size. This patch was applied to the minified bundle. A fresh build from upstream source may not have this patch.
**Why it happens:** The upstream source code's `createRenderer()` may default to a smaller value. The minified bundle was manually edited.
**How to avoid:** Before building the frontend, locate `createRenderer` in `lappmodel.ts` (it's the `CubismUserModel.createRenderer` call) and verify the `o` argument. If needed, patch it in the source file before building — not in the bundle.
**Warning signs:** Teto rig renders with clipped/missing body parts after the rebuild.

### Pitfall 4: `action_str` prompt injection not connected
**What goes wrong:** The new `actionMap` tags (`[hold-mic]`, etc.) are in `model_dict.json` but not in the LLM's system prompt. The LLM invents its own tags or never uses the new vocabulary.
**Why it happens:** The `emo_str` only builds from `emotionMap` keys. If `action_str` isn't also injected, the LLM doesn't know the action vocabulary exists.
**How to avoid:** Verify the prompt template substitution includes both `emo_str` and `action_str` (or the merged `full_action_str`). Add an integration test that instantiates `Live2dModel("重音テト")` and checks that `[hold-mic]` appears in the injected prompt.
**Warning signs:** LLM never outputs `[hold-mic]` or outputs it in wrong format; testing conversation about mics doesn't trigger prop.

### Pitfall 5: NeuroSync output not at 52 ARKit standard order
**What goes wrong:** NeuroSync's ONNX model outputs 61 or 68 values. The first 52 are ARKit blendshapes but the mapping order is not documented in the README. Indices 52-68 are head pose and emotion dims — but their exact semantics are unclear from current docs.
**Why it happens:** The NeuroSync forum thread from 2025 specifically asks about this and no official answer was found. The convaitech fork on Hugging Face may have different output dims.
**How to avoid:** Use the NeuroSync_Local_API repo (not the convaitech fork) — it has Python inference code that names the outputs. Probe the model with a short silent audio clip and log all 61 values to determine live ranges. Map jawOpen (ARKit index 17) → ParamJawOpenIN, eyeBlinkLeft (0) → ParamEyeLOpen, etc.
**Warning signs:** Sidecar trajectory file has all-zero or out-of-range values; jaw param is clearly wrong.

### Pitfall 6: Expression name vs index mismatch in actionMap dispatch
**What goes wrong:** `model_dict.json` uses expression names (e.g., `"SV Mic"`) but the existing frontend's expression dispatch path also accepts numeric indices (from the current `emotionMap` which maps to integers like `0, 1, 2, 3`). If Phase 1-3 hardcodes integer dispatch, actionMap string names won't resolve.
**Why it happens:** The current `emo_map` stores `{"neutral": 0, "anger": 2, ...}` — integer indices. But the existing bundle code (`Ct.setExpression(s)`) already handles both: `if (typeof s == "string") a.setExpression(s); else if (typeof s == "number") { name = a.getExpressionName(s); a.setExpression(name); }`.
**How to avoid:** Ensure Phase 1-3's `extract_emotion` for motions uses string names (from `motionMap`/`actionMap` keys → string expression names as values), not integer indices. The frontend already handles strings correctly.
**Warning signs:** Expression snap produces wrong expression or a console error "expression[hold-mic] is null".

---

## Runtime State Inventory

No rename or migration is involved in Phase 4. This section is not applicable.

---

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| pixi-live2d-display-lipsync | Official Cubism Web SDK | OLVT v2 migration | Cubism 5 support, but removed Cubism 2 support |
| VTube Studio for all animation | Direct Cubism SDK in browser | OLVT v2 | Self-hosted, no VTS dependency |
| Bundle hot-patch for small fixes | In-tree frontend build | Phase 4 (this phase) | Scales to multi-hundred-line patches |
| Audio2Face / SadTalker (video out) | NeuroSync (blendshape stream) | 2024 | First real-time local audio→param model |

**Deprecated/outdated:**
- The `tapMotions` block in Teto's `model_dict.json` entry references non-existent motion files (`tap_body`, `flick_head`). These should be dropped.
- Single motion per group in `model3.json` (Teto currently has 1 motion per group). Extended to multiple files for probabilistic selection.

---

## Open Questions

1. **electron-vite renderer output path for web-only builds**
   - What we know: electron-vite default output is `out/renderer/`. The `out/renderer/index.html` is designed for Electron's `loadFile()`.
   - What's unclear: Whether the built `index.html` uses absolute paths (breaking browser loading) or relative paths (fine). The current vendored `frontend/index.html` uses `./assets/main-CKgUHFa9.js` (relative) — we need the rebuild to match.
   - Recommendation: Inspect `electron.vite.config.ts` `base` option. If it's `/`, switch to `'./'` for the renderer build or add a `vite.config.ts` override. Alternatively, verify by running `npm run build` on a test clone before the implementation task.

2. **Phase 1-3 tag casing convention for motions**
   - What we know: CONTEXT.md says Phase 4 should match whatever Phase 1-3 chose. Phase 1-3 is not yet implemented.
   - What's unclear: Whether Phase 1-3 uses `[wave]` (lowercase-hyphenated) or `[Wave]` (title case).
   - Recommendation: Phase 4 planner should explicitly lock `kebab-case-lowercase` as the tag convention for both motions and actions. The extraction code in `extract_emotion` already lowercases the input, so any casing in LLM output will match.

3. **NeuroSync blendshape index ordering (indices 0-51)**
   - What we know: NeuroSync outputs 52 ARKit blendshapes plus head/emotion dims. ARKit order is known (jawOpen=17, eyeBlinkLeft=0, etc.).
   - What's unclear: Whether AnimaVR's model follows the exact standard ARKit 52 order or a custom order.
   - Recommendation: The sidecar task should include a calibration step that logs all 61 output values for a "ahh" audio clip and a "blink" audio clip to verify index assignments before building the mapping.

---

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Node.js | Frontend rebuild (D-04) | Yes | 22.19.0 | — |
| npm | Frontend rebuild (D-04) | Yes | 10.9.3 | — |
| Python | Sidecar (D-07) | Yes | 3.10.19 | — |
| uv | Sidecar (D-07) | Yes | 0.10.4 | — |
| git | Source management | Yes | (git repo confirmed) | — |
| NeuroSync Local API | Sidecar (D-07) | Not yet installed | — | Download from GitHub: AnimaVR/NeuroSync_Local_API |
| NeuroSync ONNX model weights | Sidecar (D-07) | Not yet downloaded | — | HuggingFace: AnimaVR/NEUROSYNC_Audio_To_Face_Blendshape |
| NVIDIA GPU | A2F-3D alternative sidecar | Unknown | — | Use NeuroSync (CPU-capable) |

**Missing dependencies with no fallback:** None — NeuroSync works on CPU.

**Missing dependencies with fallback:**
- NeuroSync weights: Download task in Wave 0. License (CC BY-NC 4.0) permits research use. No GPU required.

---

## Validation Architecture

`workflow.nyquist_validation` key is absent from `.planning/config.json` — treated as enabled.

### Test Framework
| Property | Value |
|----------|-------|
| Framework | None configured (project uses manual testing + ruff) |
| Config file | None |
| Quick run command | `ruff check . && ruff format --check .` |
| Full suite command | Manual browser smoke test (described below) |

No automated test framework (pytest, jest, vitest) is currently configured for this project. Per CLAUDE.md: "Manual testing through web interface and desktop client." The Nyquist validation for Phase 4 is therefore manual smoke tests, supplemented by one lightweight Python unit test for the backend action extraction.

### Phase Requirements → Test Map

| Req | Behavior | Test Type | Command / Protocol | File Exists? |
|-----|----------|-----------|-------------------|-------------|
| D-04 (cursor head) | Mouse drag moves Teto's head in browser | Manual visual smoke | Open browser, drag on canvas, verify head follows | N/A |
| D-04 (audio bob) | Body bobs slightly during TTS speech | Manual visual smoke | Send "count to five" prompt, watch body Y parameter | N/A |
| D-05 (talk variety) | Talk motion varies across multiple responses | Manual visual smoke | Send 5 consecutive prompts, verify motions differ | N/A |
| D-05 (idle variety) | Idle motion varies during 60s of silence | Manual visual smoke | Leave running idle for 60s, verify non-repetitive motion | N/A |
| D-05 (no param collision) | Props don't disappear during talk motions | Manual visual smoke | With `[hold-mic]` expression active, send a prompt, verify mic stays | N/A |
| D-06 (action dispatch) | `[hold-mic]` in LLM output triggers SV Mic expression | Python unit test | `pytest tests/test_action_extraction.py -x` | No — Wave 0 |
| D-06 (prompt injection) | action_str contains `[hold-mic]` etc. | Python unit test | Check `live2d_model.action_str` after loading Teto | No — Wave 0 |
| D-07 (sidecar output) | sidecar produces non-trivial trajectory for "hello" WAV | Manual inspection | `uv run tools/audio_to_params/main.py --audio sample.wav` produces nonzero jawOpen values | N/A |

### Sampling Rate
- **Per task commit:** `ruff check . && ruff format --check .` (Python backend changes only)
- **Per wave merge:** Full manual smoke test: cursor → head, audio → bob, talk → varied motion, `[hold-mic]` → prop visible
- **Phase gate:** All manual smoke tests pass + unit tests green before `/gsd:verify-work`

### Wave 0 Gaps
- [ ] `tests/test_action_extraction.py` — unit test for actionMap tag extraction and action_str prompt injection
- [ ] `tests/conftest.py` — shared fixtures (Live2dModel instantiation with test model_dict)
- [ ] Framework install: `uv add pytest` (if pytest not already in dev deps)

---

## Sidecar Adapter Survey (D-07)

Research question E asked for a survey of real available models. Findings:

| Model | Input | Output | License | Usable for Sidecar? |
|-------|-------|--------|---------|---------------------|
| NeuroSync (AnimaVR) | WAV audio only | 61 values: 52 ARKit blendshapes + head pose + emotion | CC BY-NC 4.0 | **Yes — recommended** |
| NVIDIA Audio2Face-3D | WAV via gRPC | 52-68 ARKit blendshapes at real-time | NVIDIA Open Model License | Possible if GPU available; NIM container required |
| SadTalker | portrait image + audio | MP4 video | Apache 2.0 | No — video output, not params |
| EchoMimic / EchoMimicV2 | audio + (optional landmarks) | MP4 video | Apache 2.0 | No — video output |
| JoyVASA | audio + reference image | Video (keypoints internally) | Unknown (check repo) | No — video output |
| AniPortrait | audio + reference image | 2D facial landmarks → video | Unknown | No — video output |
| kimjammer/Neuro | delegates to VTube Studio | VTS mic → lipsync only | MIT | No — architecture, not a model |

**NeuroSync Local API architecture:**
- Input: audio bytes (WAV, 16 kHz recommended)
- Processing: Mel spectrogram → transformer encoder-decoder → 61 blendshape values per frame at ~60 fps
- Output: sequence of float vectors `[frame_count, 61]`
- Frames 0-51: ARKit blendshapes in standard order (jawOpen at 17, eyeBlinkLeft at 0)
- Frames 52-60: head pose and emotion dims (exact mapping needs calibration — see Open Question 3)

**ARKit → Live2D Teto parameter mapping sketch:**

| ARKit blendshape | Live2D parameter | Notes |
|-----------------|-----------------|-------|
| jawOpen (17) | ParamJawOpenIN | Primary mouth open |
| mouthSmileLeft (24) + mouthSmileRight (25) | ParamMouthForm | average |
| eyeBlinkLeft (0) | ParamEyeLOpen | invert: blink=1 → open=0 |
| eyeBlinkRight (7) | ParamEyeROpen | invert |
| headRoll (52?) | ParamAngleZIN | head rotation Z (needs calibration) |
| headPitch (53?) | ParamAngleYIN | head up-down |
| headYaw (54?) | ParamAngleXIN | head left-right |

**Sidecar output format (D-07 recommendation):** JSON file with `frames` array, each frame a dict of `{param_id: float, ...}` at 30 Hz, plus a `duration_seconds` field. This matches the conceptual structure of a motion3.json but is easier to process than the Cubism segment format.

```json
{
  "duration_seconds": 2.1,
  "fps": 30,
  "frames": [
    {"ParamJawOpenIN": 0.0, "ParamEyeLOpen": 1.0, ...},
    {"ParamJawOpenIN": 0.3, "ParamEyeLOpen": 0.95, ...},
    ...
  ]
}
```

---

## Code Examples

### Verified Pattern 1: motion3.json minimal loop (from spec + IDLE analysis)
```json
{
  "Version": 3,
  "Meta": {
    "Duration": 2.0,
    "Fps": 30.0,
    "Loop": true,
    "AreBeziersRestricted": false,
    "FadeInTime": 0.5,
    "FadeOutTime": 0.5,
    "CurveCount": 2,
    "TotalSegmentCount": 8,
    "TotalPointCount": 16
  },
  "Curves": [
    {
      "Target": "Parameter",
      "Id": "ParamAngleXIN",
      "FadeInTime": 0.0,
      "FadeOutTime": 0.0,
      "Segments": [
        0, 0.0,
        0, 0.5, -4.0,
        0, 1.0, 0.0,
        0, 1.5, 4.0,
        0, 2.0, 0.0
      ]
    },
    {
      "Target": "Parameter",
      "Id": "ParamBreath",
      "FadeInTime": 0.0,
      "FadeOutTime": 0.0,
      "Segments": [
        0, 0.5,
        0, 1.0, 1.0,
        0, 2.0, 0.5
      ]
    }
  ]
}
```
Note: `TotalSegmentCount` = number of segment-type-prefix entries in all Segments arrays. `TotalPointCount` = number of time+value pairs. Count carefully — the model will fail to load if these are wrong.

### Verified Pattern 2: actionMap in model_dict.json
```json
{
  "name": "重音テト",
  "emotionMap": { "neutral": 0, "anger": 2, ... },
  "actionMap": {
    "hold-mic":  "SV Mic",
    "utau-mic":  "Utau Mic",
    "bread-out": "SV Baguette",
    "chibi":     "chibi",
    "hearts":    "Heart",
    "star-eyes": "Star Eye"
  },
  "motionMap": {
    "wave":  ["Talk", 0],
    "nod":   ["Talk", 1]
  }
}
```

### Verified Pattern 3: action_str construction (mirrors emo_str)
```python
# In Live2dModel.set_model():
self.emo_map = {k.lower(): v for k, v in self.model_info["emotionMap"].items()}
self.emo_str = " ".join([f"[{key}]," for key in self.emo_map.keys()])

action_map = self.model_info.get("actionMap", {})
self.action_map = {k.lower(): v for k, v in action_map.items()}
action_str = " ".join([f"[{key}]," for key in self.action_map.keys()])
self.full_action_str = (self.emo_str + " " + action_str).strip()
```

### Verified Pattern 4: body-bob extension to Option A patch (lappmodel.ts)
```typescript
// Add to field declarations:
private _speechRmsSmoothed: number = 0;

// In update(), after the VTube routing block from Option A:
if (this._lipsync && this._wavFileHandler) {
  const rms = Math.min(1.0, this._wavFileHandler.getRms() * 1.5);
  this._speechRmsSmoothed = this._speechRmsSmoothed * 0.85 + rms * 0.15;
  this._model.addParameterValueById(
    CubismFramework.getIdManager().getId("ParamBodyAngleY"),
    this._speechRmsSmoothed * 3.0
  );
}
```

---

## Project Constraints (from CLAUDE.md)

| Directive | Applies To Phase 4 |
|-----------|-------------------|
| Use `uv` for Python dependency management | Sidecar tool (D-07) |
| Use `loguru` for logging | Any new Python files |
| Use `Pydantic v2` for new config | Sidecar config, actionMap schema if validated |
| Use `ruff check .` + `ruff format .` | All Python source files |
| Factory + interface pattern for engines | Not applicable (no new engine in Phase 4) |
| Configuration in `conf.yaml` / `config_templates/` | actionMap is in model_dict.json, not conf.yaml — this is consistent with existing emotionMap pattern |
| `model_dict.json` is the per-model config location | Confirmed: actionMap goes here |
| `characters/` for character YAML configs | Not changed in Phase 4 |
| `loguru` not `print` | All new Python |

---

## Sources

### Primary (HIGH confidence)
- Verified from source code: `src/open_llm_vtuber/agent/output_types.py` — Actions dataclass exact shape
- Verified from source code: `src/open_llm_vtuber/live2d_model.py` — emo_str pattern, extract_emotion, remove_emotion_keywords
- Verified from source code: `src/open_llm_vtuber/agent/transformers.py` — actions_extractor decorator logic
- Verified from source code: `src/open_llm_vtuber/utils/stream_audio.py` — volumes computed via pydub.rms at 20ms chunks
- Verified from bundle analysis: `frontend/assets/main-CKgUHFa9.js` — audio pipeline, expressions dispatch, volumes field unused for body-bob, wavFileHandler RMS drives lipsync, startRandomMotion("Talk") called on each audio message
- Verified from asset files: `live2d-models/重音テト/Motions/IDLE.motion3.json` — 36 pinned parameters, 1s loop, 30 FPS
- Verified from asset files: `live2d-models/重音テト/Motions/Sleep.motion3.json` — 7 animated params, 6.8s, 60 FPS
- Verified from asset files: `live2d-models/重音テト/重音テト.vtube.json` — 22 ParameterSettings entries confirmed
- Verified from asset files: `live2d-models/重音テト/Expressions/*.exp3.json` — 15 expression files confirmed, parameter names verified
- Verified from asset files: `live2d-models/重音テト/重音テト.model3.json` — motion groups and expression manifest confirmed
- [CubismSpecs motion3.json spec](https://github.com/Live2D/CubismSpecs/blob/master/FileFormats/motion3.json.md) — schema confirmed (Version, Meta, Curves, Segments format)
- WebFetch of upstream lappmodel.ts — update() drag parameters confirmed, lipsync RMS path confirmed

### Secondary (MEDIUM confidence)
- [Open-LLM-VTuber-Web GitHub](https://github.com/Open-LLM-VTuber/Open-LLM-VTuber-Web) — Electron+Vite+React+TypeScript confirmed. Build commands: npm run build. Output: out/renderer/
- [NeuroSync Local API](https://github.com/AnimaVR/NeuroSync_Local_API) — Audio-to-blendshape local inference, 61-dim output, CC BY-NC 4.0 (multiple sources agree)
- [NVIDIA Audio2Face-3D](https://github.com/NVIDIA/Audio2Face-3D-Samples) — ARKit blendshapes output (52+16 tongue), gRPC API, NVIDIA license — verified from official GitHub

### Tertiary (LOW confidence)
- NeuroSync exact blendshape index ordering (indices 52-68 for head/emotion) — single forum source, needs calibration verification
- electron-vite exact output path when run in web-only context vs Electron context — needs build test

---

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — Node/npm/Python/uv all confirmed present; upstream Web repo build confirmed
- Architecture: HIGH — all four workstreams have specific verified implementation paths
- Authored motions: HIGH — IDLE pin list fully enumerated, safe parameters confirmed from Sleep.motion3.json
- Action vocabulary: HIGH — all 6 expression files confirmed present with parameter names verified
- Sidecar model survey: MEDIUM — NeuroSync confirmed OSS with local inference; blendshape index details need calibration
- Frontend audio pipeline: HIGH — bundle decompiled and audio path traced precisely
- Pitfalls: HIGH — all critical collision risks identified from source analysis

**Research date:** 2026-05-04
**Valid until:** 2026-06-04 (stable APIs; NeuroSync model weights location should be re-verified if more than 30 days pass)
