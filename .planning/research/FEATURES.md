# Feature Landscape: Live2D Actions

**Domain:** Live2D Integration
**Researched:** 2024-03-20

## Table Stakes

Features users expect in a VTuber AI.

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| Expression Triggering | AI should look happy when saying something joyful. | Medium | Currently implemented via `[tag]` extraction. |
| Lip Sync | Model's mouth should move with the audio. | High | Handled by sending volume data (`volumes`) in the audio payload. |
| Idle Animations | Model shouldn't be a static image when not talking. | Low | Handled by frontend via `idleMotionGroupName`. |

## Differentiators

Features that set this product apart.

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| LLM-Driven Motions | AI can wave, bow, or point based on context. | Medium | Not yet fully implemented for LLM control. |
| Per-Sentence Expressions | Expressions change mid-response based on sentence tone. | Medium | Currently supported by the transformer pipeline. |
| Interaction Reactivity | Model reacts to clicks/taps on different body parts. | Low | Implemented via `tapMotions` in config. |

## Anti-Features

Features to explicitly NOT build in the backend.

| Anti-Feature | Why Avoid | What to Do Instead |
|--------------|-----------|-------------------|
| Direct Model Rendering | Too heavy for the backend, requires GPU/Display. | Keep rendering in the frontend (Web browser). |
| Real-time Param Manipulation | High latency, complex sync. | Use high-level tags (Expressions/Motions) and let frontend interpolate. |

## Feature Dependencies

```
LLM Output -> Sentence Splitting -> Action Extraction -> Expression Mapping -> WebSocket Payload -> Frontend Rendering
```

## MVP Recommendation

Prioritize:
1.  **Strict Tag Extraction**: Ensure `[tag]` is always extracted and removed from TTS input to avoid AI reading the tags aloud. (Already implemented)
2.  **Lip Sync**: Volume-based lip sync is critical for immersion. (Already implemented)

Defer:
-   **Natural Language Emotion Detection**: Using a separate model to detect emotion without explicit tags. Defer due to latency concerns.

## Sources

- `src/open_llm_vtuber/agent/transformers.py`
- `src/open_llm_vtuber/utils/stream_audio.py`
