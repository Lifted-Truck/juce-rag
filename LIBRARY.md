# LIBRARY — durable lessons

Entries per the template in CLAUDE.md. Candidates promote to canonical on a
second independent occurrence or human review.

[L0001] JUCE releases outpace design assumptions; re-check at every phase start | candidate | added: 2026-07-24 | tags: golden-governance, corpus-quirks | lesson: The design spec assumed target JUCE 8.x / drift baseline 7.x; JUCE 9.0.0 had already shipped (2026-07-21, with its own BREAKING_CHANGES section) before the repo existed, invalidating the assumption at spin-up. Any phase that touches version-scoped artifacts (goldens, submodule pin, doc URLs) must start by checking the current JUCE release, not by trusting the last-written scope. | evidence: gh api repos/juce-framework/JUCE/releases/latest → 9.0.0 (2026-07-21), run 2026-07-24 during spin-up; DECISIONS.md D-004. | falsifier: if JUCE release cadence slows such that scope assumptions survive multiple phases unchanged, demote to note. | supersedes: —
