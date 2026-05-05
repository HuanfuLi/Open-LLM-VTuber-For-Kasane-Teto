# Codebase Structure

**Analysis Date:** 2024-05-04

## Directory Layout

```
openllm_vtuber/
├── src/open_llm_vtuber/    # Core Python source code
│   ├── agent/             # LLM/Agent implementations and factories
│   ├── asr/               # Speech-to-Text engine implementations
│   ├── tts/               # Text-to-Speech engine implementations
│   ├── vad/               # Voice Activity Detection implementations
│   ├── config_manager/    # Pydantic models for configuration
│   ├── conversations/     # Conversation handling logic (single/group)
│   ├── mcpp/              # Model Context Protocol integration
│   ├── translate/         # Translation service integrations
│   ├── utils/             # Shared helper utilities
│   ├── server.py          # FastAPI server setup
│   ├── routes.py          # API and WebSocket route definitions
│   ├── websocket_handler.py # Main WebSocket logic and message routing
│   └── service_context.py # Central service hub for client sessions
├── frontend/               # Built React frontend assets (submodule)
├── avatars/               # User avatar images
├── backgrounds/           # Background images for the UI
├── live2d-models/         # Live2D model assets
├── config_templates/      # Default configuration templates
├── logs/                  # Application logs
├── cache/                 # Temporary storage for generated TTS audio
├── run_server.py          # Application entry point
└── conf.yaml              # Active user configuration (generated)
```

## Directory Purposes

**src/open_llm_vtuber/agent/:**
- Purpose: Interfaces and implementations for different LLM backends (OpenAI, Ollama, Claude, etc.).
- Key files: `agent_factory.py`, `agents/basic_memory_agent.py`.

**src/open_llm_vtuber/asr/:**
- Purpose: Audio transcription engines.
- Key files: `asr_factory.py`, `sherpa_onnx_asr.py`, `faster_whisper_asr.py`.

**src/open_llm_vtuber/tts/:**
- Purpose: Speech synthesis engines.
- Key files: `tts_factory.py`, `openai_tts.py`, `edge_tts.py`, `piper_tts.py`.

**src/open_llm_vtuber/config_manager/:**
- Purpose: Configuration validation using Pydantic.
- Key files: `main.py` (entry for validation), `system.py`, `character.py`.

**src/open_llm_vtuber/mcpp/:**
- Purpose: Implementation of Model Context Protocol for tool use.
- Key files: `mcp_client.py`, `tool_manager.py`.

## Key File Locations

**Entry Points:**
- `run_server.py`: Main script to launch the backend and serve the frontend.
- `src/open_llm_vtuber/server.py`: Defines the `WebSocketServer` class that wraps the FastAPI app.

**Configuration:**
- `conf.yaml`: The primary configuration file used by the server.
- `config_templates/conf.default.yaml`: The base template for generating `conf.yaml`.

**Core Logic:**
- `src/open_llm_vtuber/websocket_handler.py`: The "brain" of the server, routing WebSocket events.
- `src/open_llm_vtuber/service_context.py`: Maintains the state of all engines for a specific session.

**Testing:**
- Not detected in the standard `tests/` directory; likely integrated or separate.

## Naming Conventions

**Files:**
- `snake_case.py`: Used for all Python modules (e.g., `message_handler.py`).

**Directories:**
- `snake_case`: Used for all package directories.

**Classes:**
- `PascalCase`: Follows PEP 8 (e.g., `ServiceContext`, `WebSocketHandler`).

## Where to Add New Code

**New LLM Backend:**
- Primary code: Create a new file in `src/open_llm_vtuber/agent/stateless_llm/` or `src/open_llm_vtuber/agent/agents/`.
- Integration: Register the new agent in `src/open_llm_vtuber/agent/agent_factory.py`.

**New TTS/ASR Engine:**
- Primary code: Create a new implementation in `src/open_llm_vtuber/tts/` or `src/open_llm_vtuber/asr/`.
- Integration: Add it to the corresponding factory (e.g., `tts_factory.py`).

**New API Endpoint:**
- Implementation: Add to `src/open_llm_vtuber/routes.py`.
- Mounting: If it's a static directory, mount it in `src/open_llm_vtuber/server.py`.

**New Configuration Option:**
- Implementation: Add the field to the relevant Pydantic model in `src/open_llm_vtuber/config_manager/`.
- Templates: Update both `config_templates/conf.default.yaml` and `config_templates/conf.ZH.default.yaml`.

## Special Directories

**frontend/:**
- Purpose: Contains the production build of the React frontend.
- Generated: Yes (built from separate repository).
- Committed: No (as a Git submodule).

**cache/:**
- Purpose: Stores generated audio files temporarily.
- Generated: Yes (at runtime).
- Committed: No (ignored by git).

---

*Structure analysis: 2024-05-04*
