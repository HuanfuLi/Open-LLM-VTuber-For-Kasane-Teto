---
phase: 04-vivid-actions
plan: "01"
subsystem: test-infrastructure
tags: [pytest, fixtures, tdd, red-tests, wave-0]
dependency_graph:
  requires: []
  provides: [test-framework, teto-fixture, wav-fixture, red-action-extraction-tests]
  affects: [04-03-PLAN]
tech_stack:
  added: [pytest==9.0.3, iniconfig==2.3.0, pluggy==1.6.0]
  patterns: [tdd-red-green, shared-conftest, fixture-json]
key_files:
  created:
    - tests/__init__.py
    - tests/conftest.py
    - tests/fixtures/__init__.py
    - tests/fixtures/test_model_dict.json
    - tests/fixtures/sample_hello.wav
    - tests/test_action_extraction.py
  modified:
    - pyproject.toml
    - uv.lock
decisions:
  - "pytest 9.0.3 installed as dev dependency via uv add --dev pytest"
  - "addopts=-x --tb=short in [tool.pytest.ini_options] for fast fail during development"
  - "tests/ is a Python package (tests/__init__.py) for clean imports on Windows"
  - "TestTeto fixture uses exact D-13 actionMap vocabulary (6 entries, kebab-case-lowercase)"
  - "sample_hello.wav: 1s 16kHz 16-bit mono PCM, 220Hz sine with half-sine envelope, ~32KB deterministic"
  - "8 RED tests shipped intentionally; they gate Plan 03 implementation"
metrics:
  duration: "~8 minutes"
  completed: "2026-05-05"
  tasks_completed: 3
  tasks_total: 3
  files_created: 8
  files_modified: 2
---

# Phase 4 Plan 01: Test Infrastructure Bootstrap Summary

Bootstrapped the Phase 4 pytest infrastructure from scratch. Installed pytest 9.0.3, created the shared conftest with `teto_model` / `test_model_dict_path` / `sample_wav_path` fixtures, generated a valid 16 kHz WAV for Plan 04's sidecar smoke, and landed 8 RED tests that define the Plan 03 implementation target for `action_map` / `action_str` / `extract_action` / `remove_action_tags` on `Live2dModel`.

## What Was Built

### Task 1: pytest install + directory layout
- `uv add --dev pytest` → pytest 9.0.3 (+ iniconfig 2.3.0, pluggy 1.6.0)
- `[tool.pytest.ini_options]` added to `pyproject.toml`:
  - `testpaths = ["tests"]`, `addopts = "-x --tb=short"`
- `tests/__init__.py` created (empty; makes tests a Python package for Windows import resolution)
- Commit: `c2456a8`

### Task 2: Fixtures + conftest
- `tests/fixtures/test_model_dict.json`: Minimal TestTeto entry with 4-key `emotionMap` and 6-key `actionMap` (exact D-13 vocabulary: `hold-mic→SV Mic`, `utau-mic→Utau Mic`, `bread-out→SV Baguette`, `chibi→chibi`, `hearts→Heart`, `star-eyes→Star Eye`)
- `tests/fixtures/sample_hello.wav`: 1.0s, 16000 Hz, 16-bit mono PCM. 220 Hz sine wave with half-sine amplitude envelope. Deterministic (no RNG). Verified: `getnframes()==16000`, `getframerate()==16000`.
- `tests/conftest.py`: Shared fixtures:
  - `test_model_dict_path() -> str` — absolute path to test_model_dict.json
  - `sample_wav_path() -> str` — absolute path to sample_hello.wav
  - `teto_model(test_model_dict_path)` — `Live2dModel("TestTeto", model_dict_path=...)`
- Commit: `cb49ad1`

### Task 3: 8 RED action-extraction tests
- `tests/test_action_extraction.py` — 8 test functions targeting Plan 03 surface area:

| Test | Tests | RED because |
|------|-------|-------------|
| `test_action_map_loaded` | `action_map` dict with 6 D-13 keys | `Live2dModel` has no `action_map` yet |
| `test_action_str_format` | `action_str` contains all 6 `[tag],` entries | `Live2dModel` has no `action_str` yet |
| `test_full_action_str_includes_emotions_and_actions` | `full_action_str` has both `[neutral],` and `[hold-mic],` | `Live2dModel` has no `full_action_str` yet |
| `test_extract_action_returns_expression_name` | `extract_action("[hold-mic]")` → `["SV Mic"]` | No `extract_action` method |
| `test_extract_action_multiple_tags` | multi-tag → ordered list | No `extract_action` method |
| `test_extract_action_unknown_tag_ignored` | unknown tag → `[]` | No `extract_action` method |
| `test_remove_action_tags_strips_action_brackets` | strips `[hold-mic]` from string | No `remove_action_tags` method |
| `test_action_extraction_lowercase_insensitive` | `[Hold-Mic]` → `["SV Mic"]` | No `extract_action` method |

- Commit: `0837ef9`

## Verification Results

```
uv run pytest tests/ --collect-only -q
  → 8 tests collected in 0.03s  (exit 0)

uv run pytest tests/test_action_extraction.py -x --tb=line
  → 1 FAILED (test_action_map_loaded) — exit 1 (RED, intentional)

uv run pytest --version
  → pytest 9.0.3

uv run ruff check tests/
  → All checks passed!

uv run ruff format --check tests/
  → 4 files already formatted
```

WAV fixture: `getnframes()==16000`, `getframerate()==16000` — valid 1s 16kHz mono WAV.

## Deviations from Plan

None — plan executed exactly as written.

The only observation: `uv run pytest tests/ --collect-only -q` exits with code 5 when there are zero tests collected (pytest's "no tests found" exit code). After Task 3 lands, it exits 0 with 8 tests. The plan's Task 1 acceptance criterion "exits 0" is effectively satisfied at the plan-completion level when all 3 tasks are done.

## Known Stubs

None — this is test infrastructure only. No UI rendering, no data flow stubs.

## Self-Check: PASSED

- `tests/__init__.py` — FOUND
- `tests/conftest.py` — FOUND (ruff-formatted)
- `tests/fixtures/__init__.py` — FOUND
- `tests/fixtures/test_model_dict.json` — FOUND (JSON valid, 6 actionMap keys verified)
- `tests/fixtures/sample_hello.wav` — FOUND (16000 frames @ 16000 Hz verified)
- `tests/test_action_extraction.py` — FOUND (8 tests collected)
- Commit c2456a8 — FOUND in git log
- Commit cb49ad1 — FOUND in git log
- Commit 0837ef9 — FOUND in git log
