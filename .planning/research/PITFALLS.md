# Domain Pitfalls: Live2D Action Triggering

**Domain:** Live2D Integration
**Researched:** 2024-03-20

## Critical Pitfalls

### Pitfall 1: Tag Leakage into TTS
**What goes wrong:** The AI literally says "[joy] Hello there!" because the tag wasn't removed before being sent to the TTS engine.
**Why it happens:** The extraction logic runs after the text is sent to TTS, or the filter fails to catch the tag.
**Prevention:** Use the `tts_filter` transformer to strip all bracketed tags and "think" blocks before TTS generation.

### Pitfall 2: Out-of-Sync Actions
**What goes wrong:** The AI looks sad while saying something happy because the action from the previous sentence was applied to the current one.
**Prevention:** Ensure the `Actions` object is tightly coupled with the `SentenceOutput` in the `TTSTaskManager` to maintain strict ordering and association.

## Moderate Pitfalls

### Pitfall 1: Case Sensitivity in Tags
**What goes wrong:** LLM outputs `[Joy]` but the map only has `joy`, leading to no expression being triggered.
**Prevention:** Always normalize tags to lowercase before lookup (already implemented in `Live2dModel.extract_emotion`).

### Pitfall 2: Invalid Expression Indices
**What goes wrong:** `model_dict.json` points to an expression index that doesn't exist in the `.model3.json` file.
**Prevention:** The frontend should handle missing indices gracefully. Backend validation could be added to check against the actual model files.

## Minor Pitfalls

### Pitfall 1: Tag Overlap
**What goes wrong:** `[joy]` and `[joyful]` might conflict if not handled carefully.
**Prevention:** The current implementation uses the longest match or unique keys in the map.

## Phase-Specific Warnings

| Phase Topic | Likely Pitfall | Mitigation |
|-------------|---------------|------------|
| Motion Support | Motion duration vs Sentence duration | Implement a "motion completion" signal or let the frontend handle blending. |
| Multi-modal actions | Action payload size | Avoid sending large assets (images/sounds) inside the WebSocket message; send URLs instead. |

## Sources

- `src/open_llm_vtuber/live2d_model.py`
- `src/open_llm_vtuber/utils/tts_preprocessor.py`
