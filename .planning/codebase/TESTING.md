# Testing Patterns

**Analysis Date:** 2025-05-04

## Test Framework

**Current State:** 
- No formal automated test suite (e.g., `pytest`, `unittest`) is currently integrated into the repository.
- No `tests/` directory or `test_*.py` files were detected in the source tree.

**Infrastructure:**
- CI/CD (GitHub Actions) currently focuses on linting (`ruff`) and security scanning (`CodeQL`, `fossa_scan`), but does not execute a test suite.

## Manual Testing Strategy

Given the real-time, interactive nature of the application (voice-in, voice-out, Live2D animation), testing is primarily performed manually:

**Web Tool Testing:**
- Developers use the built-in web tool (`web_tool/`) to test the full pipeline:
  1. ASR (Speech-to-Text) accuracy and latency.
  2. LLM response generation and stream handling.
  3. TTS (Text-to-Speech) quality and playback.
  4. Live2D expression extraction and synchronization.

**Integration Scripts:**
- Scripts like `scripts/run_bilibili_live.py` are used to test specific integrations (e.g., Bilibili live stream interaction) in a semi-automated or monitored fashion.

**Configuration Validation:**
- The Pydantic-based `config_manager` (`src/open_llm_vtuber/config_manager/`) provides built-in validation of user configurations on startup, acting as a "smoke test" for settings.

## Performance Testing

**Key Metric:**
- End-to-end latency: User speaks -> AI voice heard.
- **Target:** Below 500ms.

**Current Approach:**
- Developers monitor logs (`loguru`) to track the time taken by each component (ASR, LLM, TTS).
- `BasicMemoryAgent` and other agents log response times and component latencies.

## Future Testing Goals

To improve reliability, the following patterns are recommended for future implementation:

1.  **Unit Tests for Logic:**
    - Test `sentence_divider.py`, `tts_preprocessor.py`, and other utility modules.
    - Test configuration validation in `config_manager/`.
2.  **Mocking External APIs:**
    - Use `unittest.mock` or `pytest-mock` to simulate LLM (OpenAI/Claude) and TTS providers.
3.  **Integration Tests:**
    - Test the FastAPI server endpoints using `httpx.AsyncClient` or `fastapi.testclient`.
4.  **WebSocket Testing:**
    - Use a headless WebSocket client to verify message flow without the browser frontend.

## Common Manual Patterns

**Logging Observation:**
```bash
# Observe real-time component performance
uv run run_server.py
# Check logs for "Agent received pre-formatted tools" or latency metrics
```

**Cache Inspection:**
- Check the `cache/` directory to verify that generated audio files are being stored and served correctly.

---

*Testing analysis: 2025-05-04*
