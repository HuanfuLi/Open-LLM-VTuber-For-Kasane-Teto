"""Tests for Phase 4 D-06/D-10/D-13 action vocabulary extraction.

These tests are RED until Plan 03 lands (action_map, action_str,
extract_action, remove_action_tags on Live2dModel).
"""


def test_action_map_loaded(teto_model):
    assert hasattr(teto_model, "action_map"), "Plan 03 must add action_map attribute"
    assert set(teto_model.action_map.keys()) == {
        "hold-mic",
        "utau-mic",
        "bread-out",
        "chibi",
        "hearts",
        "star-eyes",
    }
    assert teto_model.action_map["hold-mic"] == "SV Mic"
    assert teto_model.action_map["bread-out"] == "SV Baguette"


def test_action_str_format(teto_model):
    assert hasattr(teto_model, "action_str"), "Plan 03 must add action_str attribute"
    # Must mirror emo_str format: "[key], [key], ..."
    for tag in (
        "[hold-mic],",
        "[utau-mic],",
        "[bread-out],",
        "[chibi],",
        "[hearts],",
        "[star-eyes],",
    ):
        assert tag in teto_model.action_str, f"action_str missing {tag!r}"


def test_full_action_str_includes_emotions_and_actions(teto_model):
    assert hasattr(teto_model, "full_action_str"), "Plan 03 must add full_action_str"
    # Both emotion tags AND action tags must appear in the prompt-ready string
    assert "[neutral]," in teto_model.full_action_str
    assert "[hold-mic]," in teto_model.full_action_str


def test_extract_action_returns_expression_name(teto_model):
    assert hasattr(teto_model, "extract_action"), (
        "Plan 03 must add extract_action method"
    )
    assert teto_model.extract_action("hello [hold-mic] world") == ["SV Mic"]


def test_extract_action_multiple_tags(teto_model):
    assert teto_model.extract_action("[chibi] cute and [hearts]") == ["chibi", "Heart"]


def test_extract_action_unknown_tag_ignored(teto_model):
    # D-08/REQUIREMENTS.md robustness: unknown tags are ignored, not errors
    assert teto_model.extract_action("hello [nonexistent] world") == []


def test_remove_action_tags_strips_action_brackets(teto_model):
    assert hasattr(teto_model, "remove_action_tags"), (
        "Plan 03 must add remove_action_tags"
    )
    result = teto_model.remove_action_tags("hi [hold-mic] there")
    # Tag and brackets removed; whitespace handling matches remove_emotion_keywords
    assert "[hold-mic]" not in result
    assert "hi" in result and "there" in result


def test_action_extraction_lowercase_insensitive(teto_model):
    # kebab-case-lowercase tag convention — extractor lowercases input
    assert teto_model.extract_action("[Hold-Mic]") == ["SV Mic"]
