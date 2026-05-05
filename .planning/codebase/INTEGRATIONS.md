# External Integrations

**Analysis Date:** 2025-05-04

## APIs & External Services

**LLM Providers (The "Brain"):**
- **OpenAI:** GPT-3.5/4/o1 via `openai` SDK.
- **Anthropic:** Claude models via `anthropic` SDK.
- **Groq:** Fast inference for Llama/Mixtral via `groq` SDK.
- **Ollama:** Local LLM inference via `ollama` API (handled in `src/open_llm_vtuber/agent/stateless_llm/ollama_llm.py`).
- **Llama.cpp:** Local inference via `llama-cpp-python` (handled in `src/open_llm_vtuber/agent/stateless_llm/llama_cpp_llm.py`).

**ASR Services (Speech-to-Text):**
- **Offline:** 
  - Sherpa ONNX (`sherpa_onnx_asr.py`)
  - Faster Whisper (`faster_whisper_asr.py`)
  - FunASR (`fun_asr.py`)
  - Whisper.cpp (`whisper_cpp_asr.py`)
- **Online:**
  - Azure Cognitive Services (`azure_asr.py`)
  - Groq Whisper (`groq_whisper_asr.py`)
  - OpenAI Whisper (`openai_whisper_asr.py`)

**TTS Services (Text-to-Speech):**
- **Offline:**
  - Piper (`piper_tts.py`)
  - Bark (`bark_tts.py`)
  - Coqui TTS (`coqui_tts.py`)
  - CosyVoice / CosyVoice 2 (`cosyvoice_tts.py`)
  - MeloTTS (`melo_tts.py`)
  - Sherpa ONNX (`sherpa_onnx_tts.py`)
  - pyttsx3 (`pyttsx3_tts.py`)
- **Online:**
  - Azure TTS (`azure_tts.py`)
  - Cartesia (`cartesia_tts.py`)
  - Edge TTS (`edge_tts.py`)
  - ElevenLabs (`elevenlabs_tts.py`)
  - Fish API (`fish_api_tts.py`)
  - MiniMax (`minimax_tts.py`)
  - OpenAI TTS (`openai_tts.py`)
  - SiliconFlow (`siliconflow_tts.py`)
  - Spark TTS (`spark_tts.py`)

## Data Storage

**Databases:**
- None (State is managed in-memory or via file system).

**File Storage:**
- **Local filesystem:** 
  - `cache/`: Temporary audio files.
  - `avatars/`: Static avatar images.
  - `live2d-models/`: Live2D model assets.
  - `backgrounds/`: Background images for the UI.
  - `chat_history/`: Persisted conversation logs.

**Caching:**
- Local directory `cache/` used for generated TTS audio files.

## Authentication & Identity

**Auth Provider:**
- **Custom/None:** Primarily designed for local use.
- API Keys for external services (OpenAI, Anthropic, etc.) are stored in `conf.yaml`.

## Monitoring & Observability

**Error Tracking:**
- None.

**Logs:**
- **Loguru:** Console and file logging (configured via `src/open_llm_vtuber/server.py` and other modules).

## CI/CD & Deployment

**Hosting:**
- Primarily local execution.
- Docker support available via `dockerfile`.

**CI Pipeline:**
- GitHub Actions (detected in `.github/workflows/`):
  - `ruff.yml`: Linting.
  - `docker-blacksmith.yml`: Docker builds.
  - `create_release.yml`: Release management.

## Environment Configuration

**Required env vars:**
- None strictly required if using `conf.yaml`.
- API keys for integrated services are typically provided in `conf.yaml`.

**Secrets location:**
- `conf.yaml` (User-managed, excluded from git).

## Webhooks & Callbacks

**Incoming:**
- **WebSocket:** `/client-ws` for frontend communication (`src/open_llm_vtuber/routes.py`).
- **Live Streaming:** Bilibili Live room messages integration (`src/open_llm_vtuber/live/bilibili_live.py`).

**Outgoing:**
- **WebSocket:** Sends audio data, transcription, and Live2D expressions to the frontend.

## Frontend Integration

**Live2D:**
- **Implementation:** The backend processes emotion tags (e.g., `[joy]`) and sends corresponding expression/motion IDs to the frontend via WebSockets.
- **Model Loading:** Frontend loads model assets directly from the `/live2d-models` static mount.

---

*Integration audit: 2025-05-04*
