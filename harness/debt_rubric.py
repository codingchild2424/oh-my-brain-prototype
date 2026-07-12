"""R2: heuristic cognitive-debt rubric over a single user prompt.

Dimensions (v1, refined from literature per spec OQ4):
- states_intent: does the prompt say WHY / what outcome is wanted?
- states_constraints: does it mention files, APIs, conditions, or causes?
- states_verification: does it say how the result will be checked?
- specific_target: does it name a concrete artifact (path, function, error)?
- answer_seeking: is the user asking to be given an intervention answer outright?

Debt score = weighted share of missing understanding signals. LLM-based
scoring can replace this behind the same interface.
"""
from __future__ import annotations

import re
from dataclasses import dataclass

_INTENT = re.compile(r"\b(because|so that|in order to|to (?:make|ensure|avoid|support)|goal|want|need)\b", re.I)
_CONSTRAINTS = re.compile(r"\b(only|must|should|except|when|if|use|using|without|due to|caused by)\b", re.I)
_VERIFICATION = re.compile(r"\b(test|verify|check|assert|pytest|expect|confirm|reproduce)\b", re.I)
_TARGET = re.compile(r"(\.\w{1,4}\b|/|\b[a-z_]+\([)]?|`[^`]+`|\b(?:function|class|module|endpoint|file|line \d+)\b)", re.I)
_ANSWER_SEEKING = re.compile(r"\b(what'?s the answer|just tell me|give me the answer|정답|답 알려)\b", re.I)

_WEIGHTS = {
    "states_intent": 0.25,
    "states_constraints": 0.2,
    "states_verification": 0.3,
    "specific_target": 0.25,
}
TRIGGER_THRESHOLD = 0.5


@dataclass(frozen=True)
class RubricResult:
    score: float
    trigger: bool
    dimensions: dict


def score_prompt(prompt: str) -> RubricResult:
    text = prompt.strip()
    dims = {
        "states_intent": bool(_INTENT.search(text)),
        "states_constraints": bool(_CONSTRAINTS.search(text)),
        "states_verification": bool(_VERIFICATION.search(text)),
        "specific_target": bool(_TARGET.search(text)),
        "answer_seeking": bool(_ANSWER_SEEKING.search(text)),
    }
    score = sum(w for k, w in _WEIGHTS.items() if not dims[k])
    score = min(1.0, max(0.0, score))
    return RubricResult(score=score, trigger=score > TRIGGER_THRESHOLD, dimensions=dims)
