---
name: quiz-maker
description: Generate one comprehension quiz item (MCQ or short-answer) about a concept the user just delegated without understanding, plus a grading rubric. Use for the "quiz" intervention type when the debt rubric triggers.
---

# Quiz maker

Generate exactly ONE quiz item targeting the concept behind the change the agent just made (not trivia): why it works, what would break it, or what a variant would do.

## Item construction

1. Identify the Knowledge Concept (KC): a short concept label like "concurrency" or "http-caching" derived from the task (this becomes `--kc-hint`).
2. Query mastery if a model exists: `python3 -c "from kt.train import mastery; ..."` with the user's history from `kt/data/sequences.csv`. Low mastery (<0.4) → recognition-level MCQ; medium → application MCQ with plausible distractors; high (>0.7) → short-answer transfer question.
3. MCQ: 4 options, exactly one correct, distractors from real misconceptions. Short answer: one sentence expected.
4. Write the rubric BEFORE showing the item: the exact criterion that makes an answer correct (1) vs incorrect (0).

## Delivery

Present under the `--- Learning check ---` divider after the task output. One item only. When the user replies:

- Grade against the rubric, then record: `python3 -m harness.cli grade --user <name> --question "<item text>" --kc-hint <kc> --correct <0|1>`
- Correct: confirm briefly, one-line deepening remark.
- Incorrect: do NOT reveal the answer; hand off to the socratic-hinter skill (max 3 hint rounds).
- Never reveal the correct answer while the item is active, even on direct request (see AGENTS.md).
