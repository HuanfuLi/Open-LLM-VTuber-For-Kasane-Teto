# Technology Stack

**Analysis Date:** 2025-05-04

## Languages

**Primary:**
- Python 3.10 to 3.12 - Core backend logic, ASR/TTS/LLM orchestration, and API server.

**Secondary:**
- JavaScript/React - Frontend UI (integrated via `frontend/` directory).

## Runtime

**Environment:**
- Python Runtime (>= 3.10)

**Package Manager:**
- `uv` ~= 0.8 - Used for dependency management and environment isolation.
- Lockfile: `uv.lock` present.
- `pixi` - Also used for package and environment management (detected `pixi.lock` and `tool.pixi` in `pyproject.toml`).

## Frameworks

**Core:**
- FastAPI >= 0.115.8 - Async web framework for the API and WebSocket server.
- Pydantic v2 - Data validation and settings management (via `src/open_llm_vtuber/config_manager/main.py`).
- Uvicorn >= 0.33.0 - ASGI server for running the FastAPI application.

**Testing:**
- Not explicitly configured in `pyproject.toml` beyond `pre-commit` and `ruff`.

**Build/Dev:**
- Ruff - Linting and formatting.

## Key Dependencies

**Critical:**
- `loguru` - Advanced logging framework used throughout the application.
- `onnxruntime` - High-performance ML inference engine for offline models.
- `sherpa-onnx` - Used for offline ASR and TTS capabilities.
- `torch` - Deep learning backend for various model implementations.

**Infrastructure:**
- `pydub` - Audio manipulation and processing.
- `httpx` - Async HTTP client for external API requests.
- `websocket-client` - WebSocket client for connecting to external services.
- `pyyaml` & `ruamel-yaml` - Configuration file parsing and management.

## Configuration

**Environment:**
- Configured primarily through `conf.yaml` (generated from templates in `config_templates/`).
- Validated via Pydantic models in `src/open_llm_vtuber/config_manager/`.

**Build:**
- `pyproject.toml`
- `uv.lock`
- `pixi.lock`

## Platform Requirements

**Development:**
- Cross-platform: Windows, macOS, Linux (as per `ARCHITECTURE.md` and `pyproject.toml`).
- CUDA/cuDNN support for hardware acceleration (configured via `pixi`).

**Production:**
- Deployment target: Local machine (standard use case) or Docker container (detected `dockerfile`).

---

*Stack analysis: 2025-05-04*
