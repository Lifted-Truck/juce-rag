# 2026-08-18 — manifest ratified

**Origin:** juce-rag resident session, 2026-08-18, human ratification of
`project.manifest.json` (requested at spin-up close, 2026-07-24).

**What changed.** `project.manifest.json` → `status.ratified: "2026-08-18"`,
note reduced to `"see ROADMAP"` (kit Decision 28: the manifest carries a
ratification date, never status prose — prose there drifts against ROADMAP,
which owns phase state). ROADMAP: ratification line updated, decision-log
entry added, Q-000 criterion 2 split so the satisfied half and the open half
are visible separately rather than blurred into "in progress".

**Why.** The survey answers are now settled fact rather than a proposal: what
this project is (pipeline + MCP service for agent consumers), the
single-thread rung, the deterministic domain core, strict-pinned-goldens
oracle shape, provider posture, knowledge-loop tags, long-lived/interactive
lifespan.

**What this does NOT settle.** D-003 (built index never committed), D-004
(JUCE 9.0.0 scope), D-005 (Python stack) remain `[PROPOSED]`. They, not the
manifest, block the JUCE submodule pin (Q-000.3) and P1 golden confirmation
(Q-002). Recorded explicitly because "manifest ratified" is easy to misread
as "P0 decisions ratified".

**Evidence.** Human ratification in session, 2026-08-18.

**Verify:** `./verify fast` green. Git hash: this commit.
