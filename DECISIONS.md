# DECISIONS — juce-rag

Append-only. One entry per settled (or explicitly open) decision, newest last.
A `[PROPOSED]` entry is not load-bearing until ratified by the human; an
`[OPEN]` entry blocks the phase it names. Spec references are to
`docs/design-spec.md`.

---

## D-001 — Architecture rung: single thread `[RATIFIED 2026-07-24]`

One lead session, phase-gated, no routine subagent delegation. Matches spec §9:
P0–P3 are strictly sequential and the available parallelism (per-source
extractors) does not justify coordination overhead at this size. The harness's
read-only `verifier`/`critic` agents remain available ad hoc without escalating
the rung. Revisit only if a dense-retrieval comparison sweep materialises (P5).

## D-002 — Public repo; scrub personal/sibling context `[RATIFIED 2026-07-24]`

The repo is public and doubles as a portfolio piece. Committed docs are
scrubbed of personal names and sibling-project identifiers; originals of
incoming artifacts stay untracked in `_incoming/` (gitignored). The leak gate
in `./verify` enforces the machine-path half of this on every run.

## D-003 — Built index is never committed `[PROPOSED]`

The system's premise is verbatim JUCE spans. JUCE is dual-licensed
(AGPLv3/commercial); a built index full of verbatim header/doc content pushed
to a public repo is redistribution of that content. Therefore: commit
extractors, goldens, schema, server code, and measured results; the built
index and any bulk verbatim JUCE-derived data are gitignored and rebuilt
locally from the pinned JUCE checkout. Short `must_contain` substrings in
goldens (a few words each) are fine. The JUCE pin itself is a submodule
gitlink — a pointer, not redistribution.

## D-004 — Version scope: target JUCE 9.0.0, drift baseline 8.x-and-earlier `[PROPOSED]`

Supersedes the spec/goldens header assumption (target 8.x, baseline 7.x),
which was already stale at spin-up: **JUCE 9.0.0 was released 2026-07-21**
(three days before this repo existed) with its own `BREAKING_CHANGES.md`
§"Version 9.0.0". Evidence for the choice:
- The consuming sibling project pins JUCE 8.0.13 with a stated
  "update to latest stable before each new phase" policy — consumers are
  heading to 9.x, not staying on 8.x.
- A brand-new major version is where LLM drift is worst: every model's
  training data predates it, so *all* trained JUCE knowledge is now the drift
  baseline. This maximises the system's value.
- The 7.x→8.x goldens (e.g. FontOptions) remain valid drift cases under a 9.0
  target — agents still emit pre-8 idioms; the baseline widens, nothing is lost.
Consequences: pin the JUCE submodule at tag `9.0.0`; goldens are re-verified
against 9.0 docs at P1 (docs.juce.com/master now tracks 9); `juce_version` is
carried on every chunk from day one so multi-version indexing later (D-008) is
additive, not a migration.

## D-005 — Stack: Python 3.12+, minimal gated dependencies `[PROPOSED]`

Python for the pipeline, index, evals, and MCP server (native MCP SDK,
tree-sitter bindings, mature lexical-retrieval libraries). Dependency
discipline mirrors the retrieval discipline: start stdlib + `pyyaml`; every
further dependency (tree-sitter, a BM25 implementation, the MCP SDK) enters
with the phase that needs it and is recorded here.

## D-006 — Forum: out for v1 `[PROPOSED — spec §3; blocks P3]`

No provenance guarantee, no version tagging, and 2021-correct answers read
identically to current ones — a confidently-wrong source inside a system whose
premise is that confident wrongness is the enemy. If admitted later: separate
index, `trust: unverified` surfaced in every result, never a sole answer.

## D-007 — Headers over generated HTML as primary extraction source `[PROPOSED — spec §3; blocks P2]`

JUCE headers are the actual source of truth, carry the doc comments Doxygen
renders, are version-pinned by the submodule, and parse cleanly with
tree-sitter. Generated HTML is a lossy derivative with an unstable, branch-
dependent URL scheme (`_1_1` separators, `class` vs `struct` prefixes). Fetch
HTML only to resolve canonical URLs for citation.

## D-008 — Single-version pin vs multi-version index `[OPEN — blocks P2]`

D-004 pins 9.0.0 as the sole indexed version for v1. Indexing 8.x and 9.x
side-by-side (with `juce_version` as a first-class filter) is what makes
`breaking_changes(from, to)` genuinely answerable at symbol granularity, at
real ingestion cost. Decide when P2's extractor exists and the cost is
measurable. The chunk schema already carries `juce_version` either way.

## D-009 — External SDK boundary (clap-juce-extensions) `[OPEN — blocks P3]`

`clap-juce-extensions` is in the corpus at priority 4 with `trust: external`.
Where exactly the boundary sits (README only? headers too? its examples?) is
undecided. Relevant to sibling CLAP-native plugin work.
