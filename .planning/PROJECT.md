# Project: Vivid Actions

## Overview
Enhance the AI's physical expressiveness by allowing the LLM to trigger specific Live2D motions (animations) in addition to facial expressions. This makes the interaction more lifelike and "vivid".

## Goals
- Add support for motion tags (e.g., `[wave]`, `[nod]`) in LLM responses.
- Implement a backend pipeline to extract these tags and map them to Live2D motion indices/names.
- Update the system prompts to teach the AI how to use these new physical actions.

## Success Criteria
- [ ] LLM can trigger a motion by including a tag in its response.
- [ ] Backend correctly identifies and removes motion tags from TTS/display text.
- [ ] Frontend receives motion data in the `actions` payload.
- [ ] Motion mapping is configurable per Live2D model in `model_dict.json`.
