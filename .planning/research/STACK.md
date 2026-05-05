# Technology Stack: Live2D Action Triggering

**Project:** Open-LLM-VTuber
**Researched:** 2024-03-20

## Recommended Stack

### Core Logic
| Technology | Version | Purpose | Why |
|------------|---------|---------|-----|
| Python | >= 3.10 | Backend processing | Asynchronous handling of LLM streams and TTS generation. |
| FastAPI | latest | WebSocket Server | High-performance communication with the frontend. |

### Live2D Mapping
| Technology | Version | Purpose | Why |
|------------|---------|---------|-----|
| JSON | N/A | Configuration | `model_dict.json` provides a simple, human-readable way to map emotions to model-specific indices. |
| Pydantic v2 | ^2.0 | Validation | Used to validate configuration and model settings. |

### Supporting Libraries
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| `loguru` | latest | Logging | For debugging extraction and communication issues. |
| `pysbd` | latest | Sentence Splitting | Used in `SentenceDivider` to provide clean boundaries for action extraction. |

## Installation

```bash
# Core dependencies are managed by uv
uv add fastapi loguru pysbd pydantic
```

## Sources

- `src/open_llm_vtuber/live2d_model.py`
- `src/open_llm_vtuber/agent/transformers.py`
- `model_dict.json`
