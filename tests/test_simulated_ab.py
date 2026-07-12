"""Simulated A/B evaluation: harness (interventions) vs control, post-test unaided."""
from eval.simulated_ab import build_conditions, run_experiment, summarize


def fake_session_llm(persona, condition, tasks, posttest):
    """Deterministic fake: harness condition adds +0.3 skill on intervened KCs."""
    boost = 0.3 if condition == "harness" else 0.0
    return {
        "intervention_answers": [1 if persona["skill"] >= 0.5 else 0 for _ in tasks]
        if condition == "harness" else [],
        "posttest_answers": [
            1 if (persona["skill"] + boost) >= q["difficulty"] else 0 for q in posttest
        ],
    }


def test_conditions_cover_all_personas_both_arms():
    conds = build_conditions()
    arms = {(c["persona"]["name"], c["condition"]) for c in conds}
    names = {c["persona"]["name"] for c in conds}
    assert len(arms) == 2 * len(names)


def test_run_experiment_produces_posttest_scores():
    results = run_experiment(llm=fake_session_llm)
    assert len(results) == len(build_conditions())
    for r in results:
        assert 0.0 <= r["posttest_accuracy"] <= 1.0
        assert r["condition"] in ("harness", "control")


def test_summarize_reports_arm_means_and_delta():
    results = run_experiment(llm=fake_session_llm)
    s = summarize(results)
    assert set(s) >= {"harness_mean", "control_mean", "delta", "n_per_arm"}
    # fake boosts harness arm, so delta must be positive
    assert s["delta"] > 0
