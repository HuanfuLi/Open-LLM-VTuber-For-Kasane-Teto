# Requirements: Vivid Actions

## Functional Requirements
1. **Motion Tag Support**: The system must support bracketed motion tags like `[wave]`, `[nod]`, `[bow]`, etc.
2. **Per-Model Mapping**: Each Live2D model should have its own `motionMap` in `model_dict.json`.
3. **Extraction & Filtering**:
   - Extraction: Extract motion tags from the LLM stream.
   - Filtering: Remove motion tags from text sent to TTS and UI display.
4. **Data Transmission**: Send extracted motions to the frontend via the existing `audio` message's `actions` field.
5. **AI Guidance**: Update system prompts to include the list of available motions for the current model.

## Technical Requirements
- Update `Actions` dataclass in `src/open_llm_vtuber/agent/output_types.py`.
- Update `Live2dModel` in `src/open_llm_vtuber/live2d_model.py`.
- Update `actions_extractor` in `src/open_llm_vtuber/agent/transformers.py`.
- Update `model_dict.json` and its template/loading logic.
- Update prompt templates in `prompts/`.

## Non-Functional Requirements
- **Low Latency**: The extraction process must be efficient to maintain <500ms latency goals.
- **Robustness**: Handle cases where the LLM uses incorrect or non-existent tags gracefully.
