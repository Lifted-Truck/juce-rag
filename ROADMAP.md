# ROADMAP — juce-rag

Single source of truth. Only the lead session (or the human) edits this file.
State lives here; conversations are ephemeral. Design rationale:
`docs/design-spec.md`. Settled/open decisions: `DECISIONS.md`.

## Status

- **Phase:** P0 spin-up (scaffolding complete; JUCE submodule pin pending
  D-004 ratification)
- **Oracle:** `./verify fast` = leak gate + structure + manifest sanity +
  goldens schema. `full` == fast (honest gap: no retrieval metrics until P3;
  no confirmed goldens yet, so nothing metric-gates). 
- **Last human ratification:** 2026-07-24 (rung + public-repo/scrub decisions;
  manifest and D-003..D-005 pending)

## Invariants under active protection

See CLAUDE.md §Domain. At risk right now: none — no retrieval code exists yet.
The public-repo redistribution invariant (D-003) is live from the first push.

## Queue

### Q-000 — P0: spin-up
- **Status:** in-progress
- **Scope:** repo root, `.claude/`, `verify`, `scripts/`, docs, goldens import
- **Acceptance criteria:**
  1. `./verify fast` green (structure + manifest + goldens schema checks run,
     leak gate passes)
  2. Manifest ratified by the human; D-003/D-004/D-005 accepted or rejected
  3. JUCE pinned as a submodule at the ratified version tag (D-004)
  4. Initial commit pushed to github.com/Lifted-Truck/juce-rag
- **Out of scope:** any ingestion or retrieval code
- **Open questions:** D-003, D-004, D-005 ratification

### Q-001 — PA: prior-art landscape
- **Status:** open
- **Scope:** `docs/prior-art.md` (new)
- **Acceptance criteria:**
  1. Survey of existing JUCE-doc retrieval/MCP tooling (docs MCP servers,
     llms.txt efforts, Context7-style services, any JUCE-specific tooling),
     dated and cited in `docs/prior-art.md`
  2. An explicit "what this changes about the design" section — even if the
     answer is "nothing"
- **Rationale:** kit Decision 30 (prior-art bookends). The design spec is a
  draft, not yet committed; commit it only after this pass. A pre-ship IP
  re-scan recurs before any public v1 announcement.

### Q-002 — P1: goldens confirmed
- **Status:** blocked (D-004 ratification)
- **Scope:** `goldens/juce-goldens.v0.yaml` → `v1`
- **Acceptance criteria:**
  1. Version scope in the goldens header matches ratified D-004
  2. Both `url: null` entries (G-003, G-008) resolved against real pages —
     never reconstructed; `link_verified: true` only after actual resolution
  3. All URLs re-verified against JUCE 9.0 docs (docs.juce.com/master now
     tracks 9)
  4. ≥20 entries; ~20% negative (`absent-api`) goldens; AU-specific and DSP
     coverage gaps addressed
  5. Every counting entry `confirmed: true` by the human; gate wired into
     `./verify full`
- **Out of scope:** retrieval implementation

### Q-003 — P2: header extraction + symbol index
- **Status:** blocked (Q-002; D-007, D-008)
- **Acceptance criteria:**
  1. Tree-sitter extraction over pinned JUCE headers → chunks per the schema
     (spec §4): FQN-keyed, warnings never split from symbols
  2. Symbol index: exact + prefix FQN lookup → declaration span + doc comment
     + canonical URL
  3. 100% of confirmed golden FQN lookups resolve to the correct declaration
  4. Built index is gitignored (D-003) and rebuilt deterministically

### Q-004 — P3: BREAKING_CHANGES + Doxygen ingestion, lexical retrieval
- **Status:** blocked (Q-003; D-006, D-009)
- **Acceptance criteria:**
  1. BREAKING_CHANGES.md at section granularity, version boundary as metadata
  2. Branch-aware URL canonicalisation (spec §3 hazard) with tests
  3. BM25 over chunks; Layer-0 thresholds met on lexical alone (initial:
     recall@10 ≥ 0.90, MRR ≥ 0.70, negative goldens 100% — floors reset from
     the first measured run, then ratcheted, never loosened)
  4. `./verify full` runs Layer-0 metrics and gates on them

### Q-005 — P4: MCP server
- **Status:** blocked (Q-004)
- **Acceptance criteria:**
  1. Tools: `lookup_symbol`, `search_docs`, `check_deprecated`,
     `breaking_changes` — every response provenance-carrying, verbatim,
     not-found first-class
  2. Tool docstrings reviewed as a deliverable (they are the consuming agent's
     only routing signal)
  3. A Claude Code session consumes it end to end on a real task

### Q-006 — P5: hybrid / dense / rerank — only if P3 left measured gaps
- **Status:** blocked (may legitimately never open — that is success, not
  shortfall)
- **Acceptance criteria:** each addition cites, in DECISIONS.md, the specific
  golden it fixes and the measured delta

### Q-007 — P6: Layer-E behavioural harness
- **Status:** blocked (Q-005)
- **Acceptance criteria:**
  1. Harvest loop: agent-produced bad JUCE → new golden (the mechanism by
     which the eval set tracks reality instead of predictions)
  2. Behavioural baseline measured and recorded; never CI-blocking

## Decision log

- 2026-07-24 — Spin-up scaffolded; rung single-thread ratified; public repo +
  scrub ratified; D-003..D-009 recorded (see DECISIONS.md)

## Graduation criteria

This project graduates from interactive prototyping to autonomous queue work
when the remaining open questions are infrastructure problems rather than
judgment ones. Currently in the judgment column: golden confirmation (P1 is
human review by definition), forum admission (D-006), external-SDK boundary
(D-009), threshold floors after the first measured run.
