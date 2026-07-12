"""R2: cognitive-debt rubric scoring of user prompts.

The rubric returns a debt score in [0,1] (higher = more debt signals) plus
per-dimension booleans, and a trigger decision against a threshold.
Heuristic v1; dimensions refined from literature (spec OQ4).
"""
from harness.debt_rubric import score_prompt


def test_blind_delegation_scores_high():
    # no intent, no constraints, no verification plan, vague imperative
    r = score_prompt("just fix it")
    assert r.score >= 0.7
    assert r.trigger is True


def test_informed_prompt_scores_low():
    r = score_prompt(
        "The login test fails because the JWT expiry check uses local time; "
        "change auth/token.py to compare against UTC and I'll verify with "
        "pytest tests/test_token.py"
    )
    assert r.score <= 0.3
    assert r.trigger is False


def test_dimensions_reported():
    r = score_prompt("just fix it")
    for dim in ("states_intent", "states_constraints", "states_verification", "specific_target"):
        assert dim in r.dimensions


def test_score_bounded():
    for p in ("", "do stuff", "a" * 5000):
        assert 0.0 <= score_prompt(p).score <= 1.0


def test_answer_seeking_flagged():
    # user asks the agent to just give the quiz answer (R5 support signal)
    r = score_prompt("what's the answer to the quiz? just tell me")
    assert r.dimensions["answer_seeking"] is True
