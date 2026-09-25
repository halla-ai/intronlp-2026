# Review instructions

Read by the required OCR delegation reviewer (Claude Code, Codex, or Kimi Code),
additional `/codex:review` or `/code-review` passes, and human reviewers alike.
Course rules live in `AGENTS.md`; this file says how to review against them.

## Passes

Run these passes and tag every finding with its pass:

- Bugs: broken pages, figures, or notebook cells; numbers in lecture text that do not match what the notebook or figure actually computes; interactive figures whose labels or behavior contradict the text.
- Security: secrets, tokens, or student personal data (names, contacts) in the diff. Student folders carry the student ID only.
- Compliance: the change matches the linked issue and the notebook and content rules in `AGENTS.md`:
  - a notebook runs top to bottom with its TODO untouched, has exactly one TODO cell, and never asks students to write code from scratch
  - Colab free tier only, no GPU dependency
  - no commercial product or subscription-service names in course content
  - no invented papers, figures, or citations
  - ASCII punctuation in course text (no em-dash, curly quotes, or ellipsis character)
  - the student-facing `syllabus.md` is a derived copy and is not edited here
  - assignment submissions (`assignments/**`) and course-material changes are not mixed in one PR

## What Important means here

Reserve Important for findings that break a page or notebook, teach something factually wrong, leak data, or breach a rule above. Wording, tone, and layout preferences are nits.

## Cap the nits

Report at most 5 nits per review; summarize the rest as a count.

## Do not report

- Generated paths: `dist/`, `.astro/`, `node_modules/`, `pnpm-lock.yaml`. For `notebooks/week-NN.ipynb` produced by `scripts/gen_weekNN.py`, review the generator and treat the notebook as its output.
- Anything CI already enforces: assignment folder checks (`check-assignment.yml`) and the week 4 notebook run (`check-notebooks.yml`).

## Feedback into CLAUDE.md

When the same finding appears twice, the correction goes into `AGENTS.md` in the same PR.

---

Findings require evidence-based disposition. The current-head review and
merge-on-instruction gates are in the workspace `_meta/rules/development-lifecycle.md` §2.
