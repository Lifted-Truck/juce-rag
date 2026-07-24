# juce-rag

**A deterministic grounding layer over the JUCE framework's documentation,
built for coding agents — not humans.**

*Last verified current: 2026-07-24. Status: P0 spin-up — design drafted,
goldens drafted, no retrieval code yet. The status table below is honest;
nothing here claims to work before its phase gate is green.*

## The problem

Coding agents writing JUCE audio-plugin code fail in a specific, well-shaped
way: **confident invention**. Method signatures that don't exist, JUCE 7 idioms
in a JUCE 8+ project, and realtime-safety violations whose only documentation
is a prose warning attached to a symbol. The failure is worst precisely where
the stakes are highest — code that compiles, passes functional tests, and
drops audio intermittently in a user's session.

JUCE 9.0.0 shipped in July 2026. Every LLM's trained JUCE knowledge now trails
the current major version — which makes retrieval-grounding against the real,
version-pinned documentation the difference between plausible code and correct
code.

## The approach

This is a **grounding layer, not a knowledge base**. It locates and evidences;
it never adjudicates:

- Every answer is a **verbatim span** from a real source file, carrying
  provenance that resolves back to it — or an explicit, well-formed
  **not-found**. Never a paraphrase; never a nearest-neighbour substitute
  presented as an answer.
- **Lexical-first retrieval.** The corpus is bounded, static, and structured;
  the dominant query is exact symbol lookup, where BM25 beats embeddings.
  Dense retrieval is admitted only when a measured golden failure demands it.
  No component enters the pipeline without a golden it fixes.
- **Eval-first development.** A human-confirmed golden set of predicted (and
  eventually transcript-harvested) agent failures gates every phase.
  Deterministic metrics (recall@k, MRR, substring assertions, negative-golden
  refusal) run CI-blocking with no LLM in the grading path.
- **Structure-aware chunking** whose load-bearing rule is that a documented
  warning is never split from the symbol it qualifies.
- Served over **MCP**, so any agent-capable editor can consume it.

Full design rationale: [docs/design-spec.md](docs/design-spec.md).
Decisions and their reasoning: [DECISIONS.md](DECISIONS.md).

## Status

| Phase | Deliverable | State |
|---|---|---|
| P0 | Spin-up: manifest, charter, oracle skeleton, JUCE pin | **in progress** |
| PA | Prior-art landscape | open |
| P1 | Golden set confirmed (≥20 entries, ~20% negative) | blocked on version-scope ratification |
| P2 | Header extraction + symbol index | not started |
| P3 | Breaking-changes + docs ingestion, lexical retrieval, Layer-0 gate | not started |
| P4 | MCP server | not started |
| P5 | Hybrid/dense/rerank — only if P3 leaves measured gaps | may never open (that's success) |
| P6 | Behavioural (Layer-E) harness + failure-harvest loop | not started |

Single source of truth for the queue: [ROADMAP.md](ROADMAP.md).

## Repository conventions

- `./verify fast` — deterministic, seconds, CI-blocking (structure, manifest,
  goldens schema; retrieval metrics from P3). `./verify full` — the whole
  gate. Exit code is the truth.
- `goldens/` — the eval set. Entries gate nothing until a human marks them
  `confirmed: true`. Null URLs stay null until actually resolved — inventing
  a link in an anti-hallucination project would be a little too ironic.
- The built index is **never committed**: JUCE is dual-licensed
  (AGPLv3/commercial), so this public repo carries extractors, goldens, and
  measured results — each clone rebuilds the index locally from the pinned
  JUCE checkout.
- `traces/` — append-only provenance for every merged change.

## Why this exists (portfolio note)

This repo is also a worked example of a development methodology: eval-gated
phases, deterministic oracles with no LLM in the grading path, decisions
recorded with their reasoning before they become load-bearing, and honest
status reporting (unbuilt things are labelled unbuilt). If the retrieval
pipeline is the product, the discipline around it is the point.
