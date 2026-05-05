# Research Summary: Live2D Motion and Expression Triggering

**Domain:** Live2D Integration / AI Interaction
**Researched:** 2024-03-20
**Overall confidence:** HIGH

## Executive Summary

The Open-LLM-VTuber project uses a tag-based system to trigger Live2D expressions from the LLM's text output. When the LLM generates a response, it can include emotional markers in brackets, such as `[joy]` or `[sadness]`. The backend processes these markers using a transformer pipeline that extracts them before the text is sent to the TTS engine and the frontend.

The system relies on a mapping defined in `model_dict.json`, which links these text-based tags to specific expression indices or IDs supported by the Live2D model. While expressions are dynamically driven by the LLM, motions (like waving or nodding) are currently handled primarily by the frontend as either idle animations or reactive "tap" animations triggered by user interaction, rather than direct LLM commands.

## Key Findings

**Stack:** Python backend (FastAPI/WebSockets) with a React-based frontend. Expression mapping is handled via a JSON configuration file (`model_dict.json`).
**Architecture:** A decorator-based "transformer" pipeline in the agent layer extracts actions from text streams.
**Critical pitfall:** The current extraction logic is strictly based on matching keys in `emotionMap`. If an LLM uses a synonym not in the map, no expression is triggered.

## Implications for Roadmap

Based on research, suggested phase structure:

1.  **Expression Refinement** - Improve the robustness of expression triggering.
    -   Addresses: Handling synonyms or natural language emotion detection instead of strict bracketed tags.
    -   Avoids: Failed triggers when LLM deviates from strict tag format.

2.  **LLM-Driven Motions** - Extend the `Actions` system to support explicit motion triggering.
    -   Addresses: Allowing the LLM to perform specific animations (e.g., `[wave]`, `[bow]`).
    -   Requires: Updating `Actions` dataclass and `actions_extractor` to support a `motions` field.

**Phase ordering rationale:**
-   Expressions are already implemented but could be more robust.
-   Motions require architectural changes to the `Actions` object and frontend integration.

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Expression Extraction | HIGH | Clearly visible in `live2d_model.py` and `transformers.py`. |
| Communication Protocol | HIGH | WebSocket payload structure verified in `stream_audio.py`. |
| Motion Control | MEDIUM | Backend lacks explicit motion extraction; frontend hints suggest they are handled locally. |

## Gaps to Address

-   Exact frontend implementation of motion playback (requires research into the React frontend repository).
-   Support for multi-modal actions (e.g., triggering a sound effect via LLM tag).
