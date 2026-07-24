# JUCE RAG — build spec

**Status:** draft imported at spin-up (2026-07-24). Not yet a committed design —
commit follows the prior-art pass (ROADMAP Q-001).
**Note:** the version-scope assumption below (target 8.x) was superseded at
spin-up by DECISIONS.md D-004 (target 9.0.0) — JUCE 9.0.0 shipped days before
this repo existed. Marker resolution status lives in `DECISIONS.md`; this
document preserves the design rationale.

Anything marked **[DECIDE]** is an open question requiring a human call before
the affected phase starts. Anything marked **[PROPOSAL]** is a recommendation,
not a settled decision — it lands in `DECISIONS.md` as accepted or rejected,
with reasoning, before it becomes load-bearing.

---

## 1. Problem statement

Coding agents building VST3 and AU plugins produce JUCE code that is
*plausible and wrong*. The failure is not ignorance of JUCE — it is confident
invention: method signatures that do not exist, JUCE 7 idioms in a JUCE 8
project, and violations of realtime constraints that are documented only in
prose warnings attached to symbols.

This system exists to make that failure mode retrievable-against. It is a
**grounding layer**, not a knowledge base.

### Success condition

An agent asking a JUCE question gets back a verbatim, provenance-carrying span
from the real documentation, or an explicit statement that no such span exists.
It never gets a paraphrase, and it never gets a nearest-neighbour substitute
presented as an answer.

### Non-goals

- Answering JUCE questions in natural language. This system **locates and
  evidences; it does not adjudicate**.
- General C++ or DSP knowledge. Out of scope.
- Serving humans. The consumer is an agent; optimise the interface for that.
- Being a code-generation assistant. It returns evidence, not implementations.

---

## 2. Inherited doctrine

This project is governed by the author's cross-project development doctrine.
The following are non-negotiable:

- **AI/deterministic boundary.** Retrieval scoring, ranking, and gate
  evaluation are deterministic code. No LLM sits in the grading path for
  Layer-0. Any LLM use (e.g. contextual chunk annotation at ingest) happens
  offline, is seeded, and its output is committed as data — not regenerated at
  query time.
- **Oracle discipline.** `./verify fast|full` from day one. Gates never
  weakened. Passing ≠ done.
- **Reduce, never invent.** Every returned span is a substring of a real
  source file, with a resolvable pointer back to it.
- **Right-sized agent architecture.** Resolved: single thread (D-001).

### Specifically inherited from a prior evidence-retrieval project

The following concepts transfer, and are lifted rather than rebuilt:

| Prior concept | Use here |
|---|---|
| "Locate and evidence, never adjudicate" | The core retrieval contract, unchanged |
| Provenance chain (chunk → source span) | Chunk → doc section / header declaration |
| Zero-hallucination oracle | Refusal to answer beyond retrieved evidence |
| Layer-0 deterministic CI-blocking | Retrieval metrics against goldens |
| Layer-E behavioural | Whether agents then write correct JUCE |

The Layer-0/Layer-E split is the most important inheritance. Retrieval quality
is deterministic and cheap to measure; downstream code correctness is neither.
Keeping them in separate files with separate gates is what makes the fast gate
actually fast.

---

## 3. Corpus

The corpus is heterogeneous in a way that resists a single pipeline. Treating
it as one undifferentiated pile is the standard failure. Each source gets its
own extractor and its own chunking strategy; they share only the chunk schema.

| Source | Type | Structure | Trust | Priority |
|---|---|---|---|---|
| `BREAKING_CHANGES.md` | Markdown, versioned sections | High | Canonical | **1** |
| Doxygen class reference | Generated HTML | High | Canonical | **1** |
| JUCE headers (`modules/**/*.h`) | C++ declarations + doc comments | High | Canonical | 2 |
| Tutorials | Prose HTML | Medium | Canonical | 3 |
| JUCE examples (`examples/**`) | C++ | Medium | Canonical | 3 |
| `clap-juce-extensions` | Markdown + C++ | Medium | External | 4 |
| JUCE forum | Threaded prose | Low | **Unverified** | **[DECIDE]** → D-006 |

### Why `BREAKING_CHANGES.md` is priority 1

It is an enumerated list of exactly the thing the agent will write that no
longer works. It is the single highest-value document in the corpus for the
stated failure mode, and it is small. Index it at section granularity, treat
each entry as atomic, and attach its version boundary as metadata.

### Doxygen extraction — known hazard

The docs are served under two branches with **different URL conventions**:

```
docs.juce.com/master/   classjuce_1_1AudioProcessorValueTreeState.html
docs.juce.com/develop/  classAudioProcessorValueTreeState.html
```

`_1_1` is the `::` separator for nested symbols. Structs take a `struct` prefix
rather than `class`. **URL canonicalisation must be branch-aware from the first
commit** or roughly half of the golden set's expected-source links rot silently.

**[PROPOSAL → D-007]** Prefer parsing the JUCE headers directly over scraping
generated HTML. The headers are the actual source of truth, they carry the doc
comments Doxygen renders, they are version-pinned by the submodule, and they
parse cleanly with tree-sitter. Generated HTML is a lossy derivative with an
unstable URL scheme. Fetch the HTML only to resolve canonical URLs for citation.

### **[DECIDE → D-006]** Forum: in or out?

This is the genuine fork in the design.

- **In favour:** the answers to the hardest questions live only there.
- **Against:** no provenance guarantee, no version tagging, high noise, and
  answers that were correct in 2021 read identically to answers correct today.
  Admitting it means admitting a source that can be confidently wrong, into a
  system whose entire premise is that confident wrongness is the enemy.

**[PROPOSAL]** Out for v1. If admitted later, it goes in a separate index with
a distinct `trust: unverified` flag that the MCP tool surfaces in every result,
and it is never returned as a sole answer.

---

## 4. Retrieval architecture

### Core position: lexical first, prove the need for dense

The corpus is bounded, static, and highly structured. The dominant query shape
is *exact symbol lookup* — `AudioProcessorValueTreeState`, `getRawParameterValue`,
`ParameterID`. Embeddings are weak at rare tokens; BM25 is excellent at them.

**Build in this order, and gate each addition on measured improvement against
the goldens:**

1. **Symbol index.** Fully-qualified-name → declaration span + doc comment +
   canonical URL. Exact and prefix match. This alone may answer the majority of
   real agent queries.
2. **BM25 over chunks.** Standard lexical retrieval across all sources.
3. **Hybrid fusion (RRF).** Only if 1+2 leave measurable gaps.
4. **Dense retrieval.** Only where a golden fails at steps 1–3 *and* a dense
   run demonstrably closes it. Not by default.
5. **Reranking.** Cross-encoder over the fused candidate pool, if precision@k
   is the bottleneck rather than recall@k.

The discipline: **no component enters the pipeline without a golden it fixes.**
Each addition is a `DECISIONS.md` entry citing the specific recall or precision
delta that justified it.

This inverts the usual tutorial order deliberately. The usual order produces a
vector pipeline nobody can debug, tuned against no measurement.

### Chunking — the load-bearing decision

Two constraints dominate:

**(a) Warnings must never be separated from the symbol they qualify.**

Goldens G-004 and G-009 both encode a constraint living in prose attached to a
method rather than in its signature. If the chunker splits these, an entire
class of golden fails simultaneously — and these are precisely the failures
that pass every functional test and surface as intermittent dropouts in a
user's session. A symbol chunk is *declaration + full doc comment + all
attached warnings*, atomically. Never split mid-symbol.

**(b) Nested symbols are unresolvable when chunked bare.**

`SliderAttachment` is meaningless without `AudioProcessorValueTreeState::`.
Every chunk carries its fully-qualified name; the symbol index keys on the FQN,
never the leaf.

**[PROPOSAL]** Structure-aware chunking throughout — tree-sitter for C++
headers, heading-boundary splits for Markdown and tutorials. No fixed-size
splitting anywhere in the pipeline. Consider parent-document retrieval
(match small, return enclosing symbol or section) if precision suffers.

### Chunk schema

Every chunk, regardless of source, carries:

```
id                  stable, content-addressed
text                verbatim substring of source — never rewritten
fqn                 fully-qualified symbol name, if applicable
source_path         repo-relative path or URL
source_span         line range or DOM path — must resolve back
doc_type            class-ref | breaking-changes | tutorial | source | example | external
juce_version        the pinned version this was extracted from
deprecated          bool + replacement FQN if known
rt_unsafe           bool — flagged where docs say so explicitly
trust               canonical | external | unverified
```

`deprecated` and `rt_unsafe` are **first-class filters, not free text.** The
whole point is that an agent asking a neutral question ("set a font size")
gets the deprecation surfaced unprompted. That requires it be structured.

`juce_version` is likewise a filter, not metadata for display. Version drift is
the top failure mode; the retriever must be able to scope by it.

---

## 5. Interface

**[PROPOSAL]** MCP server. The consumer is a coding agent; MCP is the native
surface.

Proposed tools — small, sharp, and honest about absence:

| Tool | Purpose |
|---|---|
| `lookup_symbol(fqn)` | Exact declaration + doc comment + URL. Returns explicit not-found. |
| `search_docs(query, doc_type?, version?)` | Ranked spans with provenance. |
| `check_deprecated(fqn)` | Is this deprecated, and what replaces it? |
| `breaking_changes(from_version, to_version)` | Enumerated diff. |

Every response carries provenance and never paraphrases. **Not-found is a
first-class, well-formed answer** — this is the entire content of golden G-007,
and a tool that cannot say "no such API" is the tool that lets agents invent one.

Tool descriptions matter enormously here — they are the only thing telling the
consuming agent when to reach for this instead of guessing. Budget real effort
on the docstrings; treat them as part of the deliverable, not documentation of it.

---

## 6. Evaluation

### Layer-0 — deterministic, CI-blocking, `./verify fast`

Runs against the goldens. No LLM in the path.

- **recall@k** — did the expected span make the candidate pool at all
- **MRR** — was it ranked usefully
- **`must_contain` assertions** — substring checks proving the right span came
  back; deterministic and fast
- **symbol resolution** — exact FQN lookups resolve to the correct declaration
- **negative goldens** — `absent-api` entries return not-found, not a neighbour

**[PROPOSAL]** Initial thresholds, to be ratcheted and never loosened:
recall@10 ≥ 0.90, MRR ≥ 0.70, negative goldens 100%. Set the real floor from
the first measured run rather than from these numbers.

### Layer-E — behavioural, `./verify full`

Does an agent given this tool write correct JUCE? Necessarily LLM-in-the-loop,
necessarily slower, necessarily noisier. Separate file, separate gate, does not
block the fast path.

### Golden set governance

- `goldens.v0.yaml` ships with 10 draft entries, **none confirmed**. Nothing
  gates until `confirmed: true`.
- Two entries (G-003, G-008) carry `url: null` — real gaps, deliberately left
  unfilled rather than guessed. Resolve before they count.
- **Every entry is a predicted failure, not an observed one.** The set becomes
  genuinely valuable as transcript-harvested failures displace the predictions.
- **[PROPOSAL]** Build the harvest loop early: when an agent produces bad JUCE,
  that incident becomes a golden. This is the mechanism by which the eval set
  tracks reality instead of predictions.
- Target ~20% negative goldens. Currently 10%.
- Known coverage gaps: AU-specific contracts, the DSP module, forum-sourced
  entries.

---

## 7. Phase gates

| Phase | Deliverable | Exit criterion |
|---|---|---|
| **P0** | Spin-up: manifest, layered `CLAUDE.md`, `./verify` skeleton, JUCE pinned as submodule | `./verify fast` runs green on an empty suite |
| **P1** | Goldens confirmed; `url: null` entries resolved; ≥20 entries | Human-confirmed, committed, gate wired |
| **P2** | Header extraction + symbol index | 100% of golden FQN lookups resolve |
| **P3** | `BREAKING_CHANGES.md` + Doxygen ingestion, structure-aware chunking | Layer-0 thresholds met on lexical alone |
| **P4** | MCP server + tool docstrings | An agent session consumes it end to end |
| **P5** | Hybrid / dense / rerank — **only if P3 left measured gaps** | Each addition cites the golden it fixed |
| **P6** | Layer-E behavioural harness | Baseline established |

P5 may legitimately never happen. That is a successful outcome, not a shortfall.

---

## 8. Open decisions

Tracked in `DECISIONS.md` (D-004, D-006..D-009); resolve before the dependent
phase begins.

---

## 9. Agent architecture

Resolved: single thread (D-001), per the reasoning now recorded there.

---

## 10. First action

Do not start with ingestion.

Start with the golden set: confirm the version scope, resolve the two `null`
URLs, and get the count to twenty. Everything downstream — chunking strategy,
whether embeddings are needed at all, where the thresholds sit — is determined
by that file. It is also the piece most projects skip, which is why most of them
end up tuning blind.
