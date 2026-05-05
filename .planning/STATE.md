# Project State: Vivid Actions

## Current Phase: 04-vivid-actions | Plan 5 of 6

## Active Tasks
- None

## Recently Completed
- Project Initialization
- Codebase Mapping
- Domain Research
- Phase 04 Plan 01: Test Infrastructure Bootstrap (DONE)
- Phase 04 Plan 02: Teto Motion Authoring (DONE)
- Phase 04 Plan 03: Richer LLM Action Vocabulary (DONE)
- Phase 04 Plan 04: Audio-to-Params Sidecar (DONE)

## Blockers
- None

## Accumulated Context

### Roadmap Evolution
- Phase 4 added: Vivid actions

### Decisions
- pytest 9.0.3 installed as dev dependency via uv add --dev pytest
- tests/ is a Python package for clean imports on Windows
- TestTeto fixture uses exact D-13 actionMap vocabulary (6 entries)
- 8 RED tests shipped in Plan 01 to define Plan 03 implementation target
- Linear segments (type 0) only for authored motions — no bezier curves needed for small-amplitude ambient gestures
- Gaze motions (Gaze1/2/3) are Loop:false so they play once and return to Idle group selection
- FORBIDDEN_PARAM_IDS cross-checked against IDLE.motion3.json at runtime via drift-guard test
- D-06: action tags ride the existing actions.expressions wire field — no new channel needed
- asyncio_mode=auto in pyproject.toml so @pytest.mark.asyncio tests auto-detect
- Backwards-compat: both [<insert_emomap_keys>] and [<insert_action_keys>] substituted in service_context.py
- Teto tapMotions removed: referenced non-existent motion files (per D-15 discretion)
- tools/__init__.py added to make tools/ a Python package for -m invocation support
- infer_neurosync raises NotImplementedError stub; DSP fallback covers CI path
- try/except relative import in main.py supports both direct and -m invocation

### Pending Todos
- [Multi-expression composition — face emotion + action prop](todos/pending/2026-05-05-multi-expression-composition-face-plus-action-prop.md) — phase 5+ enhancement, captured 2026-05-05 from manual smoke

### Performance Metrics
| Phase | Plan | Duration | Tasks | Files |
|-------|------|----------|-------|-------|
| 04 | 01 | ~8 min | 3/3 | 8 created, 2 modified |
| 04 | 02 | ~10 min | 3/3 | 8 created, 1 modified |
| 04 | 03 | ~12 min | 3/3 | 2 created, 6 modified |
| 04 | 04 | ~10 min | 3/3 | 9 created, 0 modified |

### Session Log
- 2026-05-04 — Phase 4 context gathered. Resume from `.planning/phases/04-vivid-actions/04-CONTEXT.md`.
- 2026-05-05 — Plan 04-01 complete. pytest installed, fixtures created, 8 RED tests landed. Stopped at: Completed 04-01-PLAN.md.
- 2026-05-04 — Plan 04-02 complete. 7 motion3.json files authored, model3.json updated, 7 tests GREEN. Stopped at: Completed 04-02-PLAN.md.
- 2026-05-05 — Plan 04-03 complete. actionMap loading, extract_action, actions_extractor merge, prompt injection — 23 tests GREEN. Stopped at: Completed 04-03-PLAN.md.
- 2026-05-05 — Plan 04-04 complete. D-07 sidecar: tools/audio_to_params/ DSP fallback pipeline — 28 tests GREEN (5 new). Stopped at: Completed 04-04-PLAN.md.
