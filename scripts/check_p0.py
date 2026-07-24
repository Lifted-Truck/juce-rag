#!/usr/bin/env python3
"""P0 sanity gate: repo structure, manifest, goldens schema.

Layer-0, deterministic, no network, no LLM. Called by ./verify fast.
Scope is honest: this validates the *shape* of the project, not retrieval
quality — retrieval metrics arrive at P3 and live in a separate script.
Exit 0 green, 1 red, per the verify contract.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

REQUIRED_PATHS = [
    "CLAUDE.md",
    "ROADMAP.md",
    "DECISIONS.md",
    "README.md",
    "project.manifest.json",
    "docs/design-spec.md",
    "goldens/juce-goldens.v0.yaml",
    "traces",
    ".claude/settings.json",
]

RUNGS = {"single-thread", "thread+subagents", "organ-fleet"}
FAILURE_MODES = {
    "version-drift", "deprecated-api", "hallucinated-sig",
    "rt-safety", "absent-api", "host-contract",
}
DOC_TYPES = {"class-ref", "breaking-changes", "tutorial", "forum", "source", "external"}

errors: list[str] = []


def check_structure() -> None:
    for rel in REQUIRED_PATHS:
        if not (ROOT / rel).exists():
            errors.append(f"structure: missing {rel}")


def check_manifest() -> None:
    try:
        m = json.loads((ROOT / "project.manifest.json").read_text())
    except Exception as e:  # noqa: BLE001 — any parse failure is the same red
        errors.append(f"manifest: unparseable ({e})")
        return
    for key in ("name", "description", "survey", "status"):
        if key not in m:
            errors.append(f"manifest: missing top-level key '{key}'")
    rung = m.get("survey", {}).get("q2_architecture_rung", {}).get("choice")
    if rung not in RUNGS:
        errors.append(f"manifest: architecture rung '{rung}' not in {sorted(RUNGS)}")


def check_goldens() -> None:
    try:
        import yaml
    except ImportError:
        errors.append("goldens: pyyaml not installed (pip install pyyaml)")
        return
    try:
        doc = yaml.safe_load((ROOT / "goldens/juce-goldens.v0.yaml").read_text())
    except Exception as e:  # noqa: BLE001
        errors.append(f"goldens: unparseable YAML ({e})")
        return
    entries = (doc or {}).get("goldens")
    if not isinstance(entries, list) or not entries:
        errors.append("goldens: no 'goldens' list found")
        return

    seen_ids: set[str] = set()
    confirmed = negative = 0
    for i, g in enumerate(entries):
        gid = g.get("id", f"<entry {i}>")
        if not isinstance(gid, str) or not gid.startswith("G-"):
            errors.append(f"goldens {gid}: id must match 'G-NNN'")
        if gid in seen_ids:
            errors.append(f"goldens {gid}: duplicate id")
        seen_ids.add(gid)

        for field in ("query", "failure_mode", "expected_source", "must_contain", "confirmed"):
            if field not in g:
                errors.append(f"goldens {gid}: missing '{field}'")
        if g.get("failure_mode") not in FAILURE_MODES:
            errors.append(f"goldens {gid}: unknown failure_mode '{g.get('failure_mode')}'")

        src = g.get("expected_source", {})
        if isinstance(src, dict):
            if src.get("doc_type") not in DOC_TYPES:
                errors.append(f"goldens {gid}: unknown doc_type '{src.get('doc_type')}'")
            # Field contract: a null URL may never claim verification, and a
            # verified claim requires an actual URL. Guards the do-not-invent rule.
            if src.get("url") is None and src.get("link_verified"):
                errors.append(f"goldens {gid}: url is null but link_verified is true")
        mc = g.get("must_contain")
        if not isinstance(mc, list) or not all(isinstance(s, str) and s for s in mc):
            errors.append(f"goldens {gid}: must_contain must be a non-empty string list")

        if g.get("confirmed") is True:
            confirmed += 1
        if g.get("failure_mode") == "absent-api":
            negative += 1

    n = len(entries)
    print(f"goldens: {n} entries, {confirmed} confirmed, "
          f"{negative} negative ({negative / n:.0%} — target ~20%)")
    if confirmed == 0:
        print("goldens: 0 confirmed — retrieval gating disabled until P1 (by design)")


def main() -> int:
    check_structure()
    check_manifest()
    check_goldens()
    if errors:
        for e in errors:
            print(f"check_p0: FAIL — {e}", file=sys.stderr)
        return 1
    print("check_p0: OK (structure + manifest + goldens schema)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
