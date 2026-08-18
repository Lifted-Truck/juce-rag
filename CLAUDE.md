# Agent Charter — juce-rag

Everything above §Domain is the invariant harness layer. Do not edit it
per-project. Project-specific facts live in §Domain and in ROADMAP.md.
**The global doctrine (imported via `~/.claude/CLAUDE.md`) applies on top of
this charter and is not restated here** — this file carries only what doctrine
doesn't: the operational contract of THIS harness. (Context budget: slimmed
2026-07-16, Decision 28.)

## Truth contract

- **ROADMAP.md is the single source of truth.** Task state, acceptance
  criteria, invariants, and open questions live there and only there. If the
  conversation and ROADMAP.md disagree, ROADMAP.md wins; if ROADMAP.md is
  wrong, fixing it is the first task.
- **Passing ≠ done.** Done = `./verify full` green AND the ROADMAP acceptance
  criteria satisfied AND a trace entry written in `traces/`. Never collapse
  these into each other.
- **Grounded refusal is a success class.** "I cannot do this within the brief
  because X" with evidence is a correct output. Guessing to appear productive
  is a failure.

## Provenance

- Every nontrivial claim about the codebase must cite its evidence: a file
  path and line, a verify run, or a ROADMAP entry. No provenance → phrase it
  as a hypothesis, not a fact.
- Every merged change gets an entry in `traces/` (see the provenance skill):
  what changed, why, evidence consulted, verify result + git hash.

## Delegation policy (lead session)

- The lead plans, delegates, integrates, and is the **only** writer of
  ROADMAP.md. Subagents never touch it.
- Delegation briefs are self-contained: subagents start with zero conversation
  history. Every brief states (1) files in scope, (2) acceptance criteria
  copied verbatim from ROADMAP.md, (3) the verify target, (4) what is
  explicitly out of scope.
- Use built-in Explore for codebase reconnaissance. Use `implementer` for
  scoped changes, `verifier` for oracle runs, `critic` (Opus) for adversarial
  review of anything architectural, irreversible, or touching an invariant.
- One queue item per implementer dispatch. Parallel dispatches only for items
  with disjoint file scopes.
- Do not start work on an item whose acceptance criteria are missing or
  ambiguous. Surface the gap to the human; that is the deliverable.

## Oracle discipline

- Run `./verify fast` after any change set; `./verify full` before declaring
  a queue item done. Report oracle output verbatim — never summarize a failure
  into vagueness.
- A red oracle halts forward work. Fix or revert; do not stack changes on red.
- Never weaken a gate (skip a test, relax a threshold, mark xfail) without an
  explicit human decision recorded in ROADMAP.md.

## Human gates

Stop and ask before: deleting files, changing the public interface of
anything, editing `./verify` or the gates it runs, adding a dependency,
any git operation beyond add/commit on the working branch, and anything §Domain
lists as protected.

---

## §Domain — juce-rag

**What this is.** A grounding layer over the JUCE framework's documentation,
for coding agents that produce plausible-but-wrong JUCE code (invented
signatures, version drift, realtime-safety violations). Form factor: ingestion
pipeline → deterministic retrieval index → MCP server. It **locates and
evidences; it never adjudicates** — every answer is a verbatim span with
provenance, or an explicit not-found. Consumers are agents, not humans.
Full design: `docs/design-spec.md`. This repo is public and doubles as a
portfolio piece.

**Stack & entrypoints.** Python 3.12+ (D-005, proposed). Runtime deps kept
minimal and each addition gated on a golden it fixes. Oracle: `./verify
fast|full` → `scripts/` checks. No build step yet; MCP server arrives at P4.

**Domain invariants.**
- Every returned span is a **verbatim substring of a real source file**, with
  a resolvable provenance pointer. Never rewritten, never paraphrased.
- **Not-found is a first-class, well-formed answer.** The system must be able
  to evidence absence (negative goldens); a nearest-neighbour substitute
  presented as an answer is the defining failure.
- **No LLM in the retrieval or grading path.** Deterministic scoring, seeded
  everything, reproducible outputs.
- `deprecated`, `rt_unsafe`, `juce_version`, and `trust` are **structured
  filters, not free text**.
- Chunking never separates a warning from the symbol it qualifies; chunks
  carry fully-qualified names.
- **No retrieval component enters the pipeline without a golden it fixes**,
  recorded in DECISIONS.md with the measured delta.
- **No verbatim JUCE-derived bulk content is committed** (D-003): the built
  index is rebuilt locally from the pinned JUCE checkout, never pushed to
  this public repo. Short `must_contain` substrings in goldens are fine.

**Protected paths.** `goldens/` (the eval set — human-confirmed entries are
ratified data), `verify` + `scripts/check_*.py` (the gates), 
`docs/design-spec.md` (design contract; changes are DECISIONS events),
`project.manifest.json`.

**Verify targets.** `fast` (~1s): leak gate + repo structure + manifest sanity
+ goldens schema. `full`: == fast until P3, then adds Layer-0 retrieval
metrics against confirmed goldens; Layer-E behavioural harness at P6 (never
CI-blocking).

<!-- MAILBOX:START (kit 2.1.0 — INTEGRATIONS §3 Scope) -->
## Mailbox

- **Briefs TO juce-rag land in `integrations/<sender>/` in THIS repo** — the
  only intake slot. Visitors write there and leave it uncommitted; committing
  is a resident act. (No consumer has filed yet; the directory appears with
  the first brief. Likely first senders: sibling JUCE-plugin projects wanting
  the MCP server at P4.)
- **Responses to OUR briefs live in the PROVIDER's tree**, not here — pull and
  read them there. Checking only our own mailbox cannot distinguish an answered
  brief from an ignored one.
- **Exchanges between two other repos are not our business.** Read freely
  (reads are never bounded), but never raise another repo's obligation to the
  human or act on it. If one concerns us, file a brief — acting through the
  protocol is always in bounds; if it concerns only the two parties, do
  nothing and say nothing.
<!-- MAILBOX:END -->

<!-- KNOWLEDGE-LOOP:START -->
## Self-Improving Knowledge Loop

Each session: read accumulated knowledge before acting, write distilled knowledge
after. This meta-layer sits on top of my primary role and never overrides it.

### Every session
1. **ORIENT** — Read INDEX.md in full (kept small on purpose). Pull ONLY the matching
   entries from LIBRARY.md into context. Never load all of LIBRARY by default.
2. **ACT** — Do the work, applying retrieved lessons. If a lesson proves wrong,
   correcting it outranks adding a new one.
3. **REFLECT** — Ask: "What did I learn that a future session needs and could not
   cheaply re-derive?" A lesson qualifies only if durable, evidenced (tied to a
   concrete trigger), and non-obvious. If nothing qualifies, write nothing.
4. **WRITE (atomic)** — Append the lesson to LIBRARY.md and a one-line pointer to
   INDEX.md in the same change. New lessons enter as `tier: candidate`; promote to
   `canonical` only on a second independent occurrence or human review.

### Write gate (anti-poisoning)
This loop feeds its own output back as input, so a wrong lesson, written once, is
retrieved and reinforced forever. Therefore: prefer not writing over writing
unverified; every lesson states what would falsify it; if a retrieved lesson
contradicts present evidence, trust the evidence and demote the lesson.

### Consolidation (periodic)
When LIBRARY exceeds ~30 entries, merge duplicates, delete superseded entries,
promote recurring candidates, tighten tags. Refactor it like code; don't grow it
like a log.

### LIBRARY entry template
`[Lxxxx] <title> | tier | added: YYYY-MM-DD | tags: … | lesson: … | evidence: … | falsifier: … | supersedes: …`
<!-- KNOWLEDGE-LOOP:END -->
