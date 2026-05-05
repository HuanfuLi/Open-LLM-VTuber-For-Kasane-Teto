# Coding Conventions

**Analysis Date:** 2025-05-04

## Naming Patterns

**Files:**
- Use `snake_case` for all Python files: `basic_memory_agent.py`, `service_context.py`.

**Functions:**
- Use `snake_case` for functions and methods: `create_agent()`, `load_from_config()`.

**Variables:**
- Use `snake_case` for variables: `llm_provider`, `system_prompt`.
- Use `_prefix` for private attributes in classes: `self._memory`, `self._live2d_model`.

**Types:**
- Use `PascalCase` for classes and Type aliases: `AgentInterface`, `Config`, `TTSPreprocessorConfig`.

## Code Style

**Formatting:**
- **Tool:** Ruff (`ruff format`).
- **Enforcement:** Managed via `.pre-commit-config.yaml` and GitHub Actions `.github/workflows/ruff.yml`.
- **Target Version:** Python 3.10.

**Linting:**
- **Tool:** Ruff (`ruff check`).
- **Settings:** Configured in `pyproject.toml`.
- **Rules:** General PEP 8 adherence with specific ignores (e.g., E402 ignored in `scripts/run_bilibili_live.py`).

## Type Hints

**Required:**
- All function and method signatures (arguments and return values) MUST have accurate type hints.

**Patterns:**
- **Modern Syntax:** Target Python 3.10+.
- **Unions:** Use `|` instead of `Optional` or `Union`. (e.g., `str | None`).
- **Generics:** Use built-in generics like `list[int]`, `dict[str, float]` instead of `typing.List`, `typing.Dict`.
- *Note: Some legacy code still uses `typing` imports, but new code must follow the modern pattern.*

## Docstrings

**Format:**
- **Google Python Style** is mandatory for all public modules, functions, classes, and methods.
- **Language:** Must be in English.

**Structure:**
1. Summary line.
2. `Args:` section with parameter descriptions and types.
3. `Returns:` section with return value description and type.
4. `Raises:` (optional) section for exceptions.

**Example:**
```python
def create_agent(
    conversation_agent_choice: str,
    agent_settings: dict,
    **kwargs,
) -> Type[AgentInterface]:
    """Create an agent based on the configuration.

    Args:
        conversation_agent_choice: The type of agent to create
        agent_settings: Settings for different types of agents
        **kwargs: Additional arguments

    Returns:
        The instantiated agent class.
    """
```

## Error Handling

**Patterns:**
- Raise descriptive exceptions (e.g., `ValueError` with clear messages) when configuration or initialization fails.
- Use `try...except` blocks in async contexts, especially around external API calls.
- Graceful fallbacks or clear error messages for platform-specific features (e.g., CUDA).

## Logging

**Framework:** `loguru`

**Patterns:**
- Use `logger.info()`, `logger.debug()`, `logger.warning()`, `logger.error()`.
- Messages should be in English, clear, and informative.
- Emojis are encouraged to make logs more readable (e.g., `logger.info("Initializing agent: ...")`).

## Module Design

**Exports:**
- Explicit imports are preferred over `from module import *`.
- Standard library, third-party, and local modules should be grouped and sorted (PEP 8).

**Barrel Files:**
- `__init__.py` files are used to manage package exports (e.g., `src/open_llm_vtuber/config_manager/__init__.py`).

## Technology-Specific Patterns

**FastAPI:**
- Heavy use of `async`/`await` for non-blocking operations.
- Pydantic models for request/response validation and configuration management.

**Pydantic:**
- Models defined in `src/open_llm_vtuber/config_manager/`.
- Use `Field` with `alias` and `default` values.
- Internationalization support via `I18nMixin` and `Description` objects.

---

*Convention analysis: 2025-05-04*
