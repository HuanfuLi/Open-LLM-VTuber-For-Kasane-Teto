# Architecture

**Analysis Date:** 2024-05-04

## Pattern Overview

**Overall:** Modular Service-Oriented Backend with a decoupled React Frontend.

**Key Characteristics:**
- **Asynchronous & Real-time:** Built on `FastAPI` and `WebSockets` for low-latency full-duplex communication.
- **Service Hub Pattern:** The `ServiceContext` acts as a central coordinator for pluggable engines (ASR, TTS, Agent, VAD).
- **Factory Pattern:** Heavily uses factories to instantiate specific engine implementations based on configuration.

## Layers

**Communication Layer (API/WebSocket):**
- Purpose: Handles incoming WebSocket connections, message routing, and static file serving.
- Location: `src/open_llm_vtuber/server.py`, `src/open_llm_vtuber/routes.py`, `src/open_llm_vtuber/websocket_handler.py`
- Contains: FastAPI app definition, WebSocket routing, message parsing, and session management.
- Depends on: `ServiceContext`, `ChatGroupManager`
- Used by: External clients (Web UI)

**Service Coordination Layer:**
- Purpose: Manages the lifecycle and state of various AI services for each client session.
- Location: `src/open_llm_vtuber/service_context.py`
- Contains: `ServiceContext` class which holds instances of ASR, TTS, and Agent engines.
- Depends on: Engine Factories, Interface definitions.
- Used by: `WebSocketHandler`

**Engine Layer (Providers):**
- Purpose: Implements specific AI functionalities (ASR, TTS, LLM).
- Location: `src/open_llm_vtuber/asr/`, `src/open_llm_vtuber/tts/`, `src/open_llm_vtuber/agent/`, `src/open_llm_vtuber/vad/`
- Contains: Concrete implementations (e.g., `openai_tts.py`, `faster_whisper_asr.py`) and factory classes.
- Depends on: External SDKs and local model loaders.
- Used by: `ServiceContext`

**Frontend Layer:**
- Purpose: Provides the user interface for interacting with the VTuber.
- Location: `frontend/` (Compiled artifacts from a Git submodule)
- Contains: React components, Live2D rendering logic, audio recording/playback.
- Communication: Connects to backend via `/client-ws`.

## Data Flow

**User Voice Interaction Flow:**

1. **Input:** Client streams audio data over WebSocket to `/client-ws`.
2. **Detection:** `VAD` (Voice Activity Detection) identifies speech segments in `src/open_llm_vtuber/websocket_handler.py`.
3. **Transcription:** `ASR` (Automatic Speech Recognition) converts audio to text.
4. **Processing:** `Agent` (LLM) receives text, processes it with persona context, and generates a response.
5. **Synthesis:** `TTS` (Text-to-Speech) converts response text to audio.
6. **Output:** Backend sends audio URL and Live2D animation signals back to the client.
7. **Playback:** Client fetches audio from `/cache` and renders Live2D animations.

**State Management:**
- **Server-side:** Managed per-session in `ServiceContext`. Client-specific state (history, character config) is stored in memory and indexed by `client_uid`.
- **Client-side:** React state manages the UI, model rendering, and audio queue.

## Key Abstractions

**Engine Interfaces:**
- Purpose: Defines the contract for all engine types to ensure pluggability.
- Examples: `src/open_llm_vtuber/asr/asr_interface.py`, `src/open_llm_vtuber/tts/tts_interface.py`.
- Pattern: Abstract Base Classes (ABC).

**Factories:**
- Purpose: Decouples engine selection from their implementation.
- Examples: `src/open_llm_vtuber/asr/asr_factory.py`, `src/open_llm_vtuber/tts/tts_factory.py`.

## Entry Points

**Server Entry:**
- Location: `run_server.py`
- Triggers: Manual execution via `python run_server.py`.
- Responsibilities: Loads config, initializes `WebSocketServer`, and starts the Uvicorn server.

**API Initialization:**
- Location: `src/open_llm_vtuber/server.py`
- Triggers: Called by `run_server.py`.
- Responsibilities: Configures FastAPI, mounts static directories, and registers routes.

## Error Handling

**Strategy:** Graceful degradation and informative logging.

**Patterns:**
- **Graceful Fallback:** If an optional component (like Live2D) fails to load, the system proceeds without it.
- **WebSocket Error Messages:** Errors are captured and sent back to the client as JSON messages of type `error`.
- **Loguru Logging:** Centralized logging with rotation and different levels in `logs/`.

## Cross-Cutting Concerns

**Logging:** Uses `loguru` for structured logging across all modules.
**Validation:** `Pydantic v2` models in `src/open_llm_vtuber/config_manager/` for strict configuration validation.
**Authentication:** Not currently implemented for the core WebSocket (local-first focus).

---

*Architecture analysis: 2024-05-04*
