---
phase: 04-vivid-actions
plan: 03
subsystem: backend-action-vocabulary
tags: [live2d, action-extraction, tts, llm-actions, prompt-injection]
dependency_graph:
  requires: [04-01, 04-02]
  provides: [action-map-loading, extract-action, actions-extractor-merge, prompt-action-keys]
  affects: [service_context, transformers, live2d_model]
tech_stack:
  added: [pytest-asyncio>=1.3.0]
  patterns: [emo_str-mirror-pattern, decorator-async-generator, expression-wire-field-reuse]
key_files:
  created:
    - tests/test_actions_extractor.py
    - tests/test_prompt_injection.py
  modified:
    - src/open_llm_vtuber/live2d_model.py
    - src/open_llm_vtuber/agent/transformers.py
    - src/open_llm_vtuber/service_context.py
    - model_dict.json
    - prompts/utils/live2d_expression_prompt.txt
    - pyproject.toml
decisions:
  - "D-06: action tags ride the existing actions.expressions wire field — no new channel"
  - "asyncio_mode=auto in pyproject.toml so @pytest.mark.asyncio tests auto-detect"
  - "Backwards-compat: both [<insert_emomap_keys>] and [<insert_action_keys>] substituted in service_context.py"
  - "Teto tapMotions removed: referenced non-existent motion files (per D-15 discretion)"
metrics:
  duration: ~12 min
  completed: 2026-05-05
  tasks: 3/3
  files_created: 2
  files_modified: 6
---

# Phase 4 Plan 3: Richer LLM Action Vocabulary Summary

**One-liner:** Six D-13 action tags ([hold-mic], [utau-mic], [bread-out], [chibi], [hearts], [star-eyes]) resolve through actionMap to Teto expression Name strings and ride the existing actions.expressions wire field with auto-injected prompt vocabulary.

## What Was Built

### Task 1: Live2dModel action_map extensions (commit bf39094)

Five new attributes/methods added to `src/open_llm_vtuber/live2d_model.py`:

- **`action_map: dict`** — lowercased keys from `model_info["actionMap"]`; optional, defaults to `{}` when absent
- **`action_str: str`** — space-joined `"[key],"` format mirroring `emo_str` exactly (e.g., `"[hold-mic], [utau-mic],"`)
- **`full_action_str: str`** — `(emo_str + " " + action_str).strip()` — the merged vocabulary string injected into prompts
- **`extract_action(str_to_check)`** — bracket-tag scanner returning expression Name strings from actionMap; unknown tags silently dropped; case-insensitive
- **`remove_action_tags(target_str)`** — mirrors `remove_emotion_keywords`; strips action tag brackets so TTS doesn't speak them

Code location: `set_model` lines 58-66 (attribute init); `extract_action` lines 197-224; `remove_action_tags` lines 226-252.

Backwards compatible: mao_pro (no actionMap key) loads cleanly with `action_map=={}`, `action_str==""`, `full_action_str==emo_str`.

### Task 2: Wire extract_action into actions_extractor (commit 144a8b7)

**`src/open_llm_vtuber/agent/transformers.py`** lines 90-93 extended:

```python
action_expressions = live2d_model.extract_action(sentence.text)
merged = (expressions or []) + (action_expressions or [])
if merged:
    actions.expressions = merged
```

Previously only `extract_emotion` was called; now both run in parallel and merge results into `Actions.expressions` (D-06: reuse existing wire field — no new channel).

**`tests/test_actions_extractor.py`** created with 5 tests:
- 3 model-level merge tests (validate merge logic shape)
- 2 async decorator-level tests (end-to-end through real `actions_extractor` wrapper)
  - `test_decorator_pipes_action_through_to_actions_expressions` — load-bearing: confirms `[hold-mic]` flows through the real decorator and lands as `actions.expressions == ["SV Mic"]`

Added `pytest-asyncio>=1.3.0` as dev dep; `asyncio_mode = "auto"` in `pyproject.toml` so `@pytest.mark.asyncio` tests auto-detect.

### Task 3: model_dict.json + prompt template + substitution code (commit e8e11e1)

**`model_dict.json`** — Teto entry updated:
- Added 6-entry `actionMap`: `hold-mic→SV Mic`, `utau-mic→Utau Mic`, `bread-out→SV Baguette`, `chibi→chibi`, `hearts→Heart`, `star-eyes→Star Eye`
- Removed broken `tapMotions` block (referenced non-existent motion files: `tap_body`, `flick_head`, `shake`, `pinch_in`, `pinch_out`)
- mao_pro entry unchanged (keeps its working tapMotions block)

**`prompts/utils/live2d_expression_prompt.txt`** — placeholder migrated from `[<insert_emomap_keys>]` to `[<insert_action_keys>]`; examples updated to include D-13 tags like `[hold-mic]`, `[chibi]`, `[hearts]`.

**`src/open_llm_vtuber/service_context.py`** lines 457-469 — dual substitution:
```python
# Backwards-compat: legacy placeholder (emo_str only)
prompt_content = prompt_content.replace("[<insert_emomap_keys>]", self.live2d_model.emo_str)
# Phase 4 D-10: new placeholder (merged emo_str + action_str)
prompt_content = prompt_content.replace("[<insert_action_keys>]", self.live2d_model.full_action_str)
```

**`tests/test_prompt_injection.py`** created with 3 tests verifying D-10 prompt injection.

## Final Test Count

| Test File | Count | Status |
|-----------|-------|--------|
| tests/test_action_extraction.py | 8 | GREEN (Plan 01 RED → GREEN) |
| tests/test_actions_extractor.py | 5 | GREEN (new) |
| tests/test_motion_files.py | 7 | GREEN (Plan 02, no regression) |
| tests/test_prompt_injection.py | 3 | GREEN (new) |
| **Total** | **23** | **all GREEN** |

## Deviations from Plan

None — plan executed exactly as written. The transformers.py file already had `SentenceWithTags` and `TagState` imported at line 8 (no missing import to add). The model_dict.json Teto entry had malformed JSON (missing closing brace properly) which was resolved by rewriting the entire file as specified.

## Known Stubs

None — all action tags are fully wired from LLM output → extract_action → actions.expressions → existing wire field to frontend.

## Commits

| Task | Commit | Message |
|------|--------|---------|
| Task 1 | bf39094 | feat(04-03): extend Live2dModel with action_map, action_str, extract_action, remove_action_tags |
| Task 2 | 144a8b7 | feat(04-03): wire extract_action into actions_extractor; add async tests |
| Task 3 | e8e11e1 | feat(04-03): add Teto actionMap to model_dict.json; update prompt placeholder |

## Self-Check: PASSED

- tests/test_actions_extractor.py: FOUND
- tests/test_prompt_injection.py: FOUND
- Commit bf39094 (Task 1): FOUND
- Commit 144a8b7 (Task 2): FOUND
- Commit e8e11e1 (Task 3): FOUND
