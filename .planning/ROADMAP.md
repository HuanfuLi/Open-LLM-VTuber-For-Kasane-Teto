# Roadmap: Vivid Actions

## Phase 1: Core Backend Implementation
- [ ] Task 1.1: Expand `Actions` dataclass to include `motions: Optional[List[str]]`.
- [ ] Task 1.2: Update `Live2dModel` to handle `motionMap` and provide `extract_motion`.
- [ ] Task 1.3: Update `actions_extractor` decorator to extract both expressions and motions.
- [ ] Task 1.4: Update `Live2dModel.remove_emotion_keywords` (or rename to `remove_action_tags`) to clean both expressions and motions.

## Phase 2: Configuration & Prompts
- [ ] Task 2.1: Update `model_dict.json` with sample `motionMap` for existing models.
- [ ] Task 2.2: Update `prompts/utils/live2d_expression_prompt.txt` to include motion instructions.
- [ ] Task 2.3: Ensure `Live2dModel.emo_str` (or a new `action_str`) includes motions for the prompt.

## Phase 3: Validation & Refinement
- [ ] Task 3.1: Create a test script or unit tests for motion extraction.
- [ ] Task 3.2: Verify the combined extraction of expressions and motions.
- [ ] Task 3.3: (Optional) Verify frontend receives the payload correctly using logs.

### Phase 4: Vivid actions

**Goal:** Make the Kasane Teto rig feel visibly closer to Neuro-sama than baseline OLVT — bundle continuous-input liveliness (cursor/audio → params), authored ambient gestures, richer LLM action vocabulary (mic/baguette/chibi/hearts/star-eyes props), and a sidecar audio→param research prototype. Vibes-graded success per CONTEXT.md D-03.
**Requirements:** D-01..D-15 (locked decisions in 04-CONTEXT.md serve as the requirement set; D-04 frontend rebuild, D-05 authored Teto motions, D-06+D-08+D-10+D-13 action vocabulary backend, D-07 sidecar adapter)
**Depends on:** Phase 3 (Phase 4 plans note Phase-3-independent fallbacks — see individual PLAN.md files)
**Plans:** 6/6 plans executed — Phase 4 complete

Plans:
- [x] 04-01-PLAN.md — Wave 0 test infrastructure: pytest install, fixtures (test_model_dict, sample WAV), 8 RED action-extraction tests
- [x] 04-02-PLAN.md — Wave 1 (D-05/D-14): 7 authored motion3.json files for Teto + model3.json motion-group update + collision-prevention test
- [x] 04-03-PLAN.md — Wave 1 (D-06/D-08/D-10/D-13): backend action vocabulary (action_map, extract_action, transformers wiring, Teto actionMap, prompt template)
- [x] 04-04-PLAN.md — Wave 1 (D-07): standalone sidecar audio→params adapter (NeuroSync wrapper + DSP fallback) + smoke test
- [x] 04-05-PLAN.md — Wave 2 (D-04/D-15): frontend rebuild from upstream Open-LLM-VTuber-Web with Option A vtube-routing patch + TTS head-IN sway + bundle regression test
- [x] 04-06-PLAN.md — Wave 3 (D-01/D-03): integrated manual smoke + D-03 vibes verdict — PASS with two polish items deferred
