"""Phase 4 D-06 — actions_extractor wires extract_action results
into Actions.expressions alongside extract_emotion.

Two test layers:
  * Model-level merge tests — verify Live2dModel.extract_action + the
    merge logic shape the wrapper uses.
  * Decorator-level async tests — wrap a mock upstream stream through
    the actual `actions_extractor(...)` decorator and assert the
    yielded Actions has the expected expressions populated. This is
    the load-bearing test for the must_haves truth "LLM output
    [hold-mic] flows through actions_extractor and lands in
    actions.expressions".
"""

from typing import AsyncIterator, Union, Dict, Any

import pytest

from src.open_llm_vtuber.agent.transformers import actions_extractor
from src.open_llm_vtuber.utils.sentence_divider import SentenceWithTags


# ── Model-level merge tests ──


def test_actions_extractor_extracts_action_alone(teto_model):
    expressions = teto_model.extract_emotion("hello [hold-mic] world")
    actions_exprs = teto_model.extract_action("hello [hold-mic] world")
    merged = (expressions or []) + (actions_exprs or [])
    assert merged == ["SV Mic"]


def test_actions_extractor_combines_emotion_and_action(teto_model):
    expressions = teto_model.extract_emotion("[joy] hi [hearts]")
    actions_exprs = teto_model.extract_action("[joy] hi [hearts]")
    merged = (expressions or []) + (actions_exprs or [])
    # Joy maps to whatever the test_model_dict has for "joy" (3); Heart is the actionMap value
    assert 3 in merged
    assert "Heart" in merged


def test_actions_extractor_unknown_action_tag_dropped(teto_model):
    expressions = teto_model.extract_emotion("[lean-left] foo")
    actions_exprs = teto_model.extract_action("[lean-left] foo")
    merged = (expressions or []) + (actions_exprs or [])
    assert merged == []


# ── Decorator-level async tests ──
# These exercise the ACTUAL actions_extractor wrapper with a fake
# upstream async generator. They are the load-bearing tests for
# must_haves truth #1.


async def _fake_upstream(
    items: list,
) -> AsyncIterator[Union[SentenceWithTags, Dict[str, Any]]]:
    """Fake upstream stream: yields the given items in order."""
    for it in items:
        yield it


@pytest.mark.asyncio
async def test_decorator_pipes_action_through_to_actions_expressions(teto_model):
    """End-to-end: text with [hold-mic] flows through the real
    decorator and lands as Actions.expressions == ['SV Mic']."""
    sentence = SentenceWithTags(text="hello [hold-mic] world", tags=[])

    @actions_extractor(teto_model)
    async def wrapped():
        async for it in _fake_upstream([sentence]):
            yield it

    outputs = []
    async for item in wrapped():
        outputs.append(item)

    assert len(outputs) == 1, f"expected 1 output, got {outputs}"
    assert isinstance(outputs[0], tuple) and len(outputs[0]) == 2
    out_sentence, out_actions = outputs[0]
    assert out_sentence.text == "hello [hold-mic] world"
    assert out_actions.expressions == ["SV Mic"], (
        f"action [hold-mic] did not flow through to actions.expressions: "
        f"got {out_actions.expressions!r}"
    )


@pytest.mark.asyncio
async def test_decorator_passes_through_dict_items(teto_model):
    """Decorator passes through dict items unchanged (existing contract)."""
    dict_item = {"type": "system", "payload": "ping"}

    @actions_extractor(teto_model)
    async def wrapped():
        async for it in _fake_upstream([dict_item]):
            yield it

    outputs = []
    async for item in wrapped():
        outputs.append(item)

    assert outputs == [dict_item]
