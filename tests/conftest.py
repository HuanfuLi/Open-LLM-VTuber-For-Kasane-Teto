"""Shared pytest fixtures for OpenLLM_Vtuber Phase 4 tests."""

from pathlib import Path
import pytest

FIXTURES_DIR = Path(__file__).parent / "fixtures"
TEST_MODEL_DICT = FIXTURES_DIR / "test_model_dict.json"
SAMPLE_WAV = FIXTURES_DIR / "sample_hello.wav"


@pytest.fixture
def test_model_dict_path() -> str:
    """Absolute path to the test model_dict.json fixture."""
    return str(TEST_MODEL_DICT)


@pytest.fixture
def sample_wav_path() -> str:
    """Absolute path to the sample 1s 16kHz mono WAV fixture."""
    return str(SAMPLE_WAV)


@pytest.fixture
def teto_model(test_model_dict_path):
    """Live2dModel instantiated with the TestTeto fixture."""
    from src.open_llm_vtuber.live2d_model import Live2dModel

    return Live2dModel(
        live2d_model_name="TestTeto",
        model_dict_path=test_model_dict_path,
    )
