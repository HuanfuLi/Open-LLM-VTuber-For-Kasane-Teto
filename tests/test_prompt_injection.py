"""Phase 4 D-10 — verify the prompt template gets the merged
emotion + action vocabulary auto-injected at load time."""

from pathlib import Path


def test_prompt_template_uses_action_placeholder():
    text = Path("prompts/utils/live2d_expression_prompt.txt").read_text(
        encoding="utf-8"
    )
    assert "<insert_action_keys>" in text, (
        "prompt template must use <insert_action_keys> placeholder for D-10"
    )


def test_full_action_str_contains_all_six_d13_tags(teto_model):
    # Ensures the auto-injected vocabulary string contains every D-13 tag
    for tag in (
        "[hold-mic]",
        "[utau-mic]",
        "[bread-out]",
        "[chibi]",
        "[hearts]",
        "[star-eyes]",
    ):
        assert tag in teto_model.full_action_str, f"missing {tag} in full_action_str"


def test_full_action_str_also_contains_emotions(teto_model):
    # full_action_str = emo_str + " " + action_str; both halves must appear
    for emotion_tag in ("[neutral]", "[anger]", "[joy]", "[sadness]"):
        assert emotion_tag in teto_model.full_action_str
