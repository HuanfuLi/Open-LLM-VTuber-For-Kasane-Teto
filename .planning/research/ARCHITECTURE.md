# Architecture Patterns: Action Triggering

**Domain:** Live2D Integration
**Researched:** 2024-03-20

## Recommended Architecture

The system uses a **Pipeline Pattern** (implemented via Python decorators) to process the LLM's output stream.

### Component Boundaries

| Component | Responsibility | Communicates With |
|-----------|---------------|-------------------|
| `BasicMemoryAgent` | Orchestrates the LLM call and the transformation pipeline. | LLM, Transformers |
| `SentenceDivider` | Splits raw token stream into logical sentences. | Transformers |
| `actions_extractor` | Scans text for tags and populates `Actions` object. | `Live2dModel`, `Actions` |
| `Live2dModel` | Provides the mapping from text tags to model indices. | `model_dict.json` |
| `TTSTaskManager` | Combines audio, text, and actions into a single WebSocket payload. | `WebSocketHandler` |

### Data Flow

1.  **LLM** yields a stream of tokens.
2.  **`SentenceDivider`** buffers tokens and yields `SentenceWithTags` when a full sentence is detected.
3.  **`actions_extractor`** takes a sentence, finds `[tag]`, and updates an `Actions` object.
4.  **`tts_filter`** cleans the text for TTS (removing tags).
5.  **`TTSTaskManager`** triggers TTS generation and prepares the final payload:
    ```json
    {
      "type": "audio",
      "audio": "...",
      "volumes": [...],
      "display_text": {"text": "..."},
      "actions": {"expressions": [index]}
    }
    ```
6.  **Frontend** receives the payload and executes the actions in sync with audio.

## Patterns to Follow

### Pattern: Transformer Decorators
**What:** Using decorators to wrap the agent's chat function into a processing pipeline.
**When:** When you need to perform sequential transformations on a stream of data (Tokens -> Sentences -> Actions -> TTS).
**Example:**
```python
@tts_filter(config)
@display_processor()
@actions_extractor(live2d_model)
@sentence_divider()
async def chat_func(...):
    ...
```

## Anti-Patterns to Avoid

### Anti-Pattern: Blocking the Stream
**What:** Performing heavy computation (like complex regex or external API calls) inside the token stream loop.
**Why bad:** Increases "Time to First Byte" (TTFB) and causes stuttering in the character's response.
**Instead:** Keep extraction simple (index-based or simple regex) and perform heavy tasks (like TTS) in parallel.

## Scalability Considerations

| Concern | At 100 users | At 10K users | At 1M users |
|---------|--------------|--------------|-------------|
| Action Extraction | Negligible | Negligible | Negligible (CPU-bound, very fast) |
| Config Loading | Cache in memory | Use a DB for model metadata | Use a distributed cache (Redis) |

## Sources

- `src/open_llm_vtuber/agent/transformers.py`
- `src/open_llm_vtuber/agent/agents/basic_memory_agent.py`
