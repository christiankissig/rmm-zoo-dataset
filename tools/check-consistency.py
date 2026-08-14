#!/usr/bin/env python3
"""Fail-fast consistency checks for the zoo's graph data.

Turns the manual audit into an automatic gate. Run via `make check` (and as a
dependency of `make build`/`make deploy`). Exits non-zero on any violation.

What it guarantees, so the dataset cannot silently drift from its claims:

  STRUCTURE (models.json)
    1. every edge endpoint is a real node; every node has a property vector and a
       cat-specifiability entry (status + basis + note + a resolvable citation)
    2. strictly_weaker is a DAG (no cycles)
    3. no pair is both ordered and incomparable -- neither directly nor via the
       transitive closure of strictly_weaker (a deduced order must not contradict
       a drawn incomparable edge)

  DATA <-> WITNESSES (litmus/ tree, run.sh)
    4. direction loop: every litmus/{strictly-weaker,incomparable}/<A>-vs-<B>
       directory matches an edge of the right TYPE and DIRECTION in models.json,
       and every litmus/memalloy-provenance ordering edge has such a directory
    5. separation loop: every pair that run.sh exercises on both sides exhibits a
       genuine Never+Sometimes split (a witness that actually distinguishes the
       models, not two identical verdicts)

  OPTIONAL (only if herd7 is on PATH)
    6. run litmus/run.sh and require 0 failures -- the dynamic closed loop that
       the hardcoded Never/Sometimes expectations still hold under the checker

NOT checked here: how the graph is DRAWN. The tier layout (tierMap / tierOrder /
tierLabels) lives in the site repository, which owns presentation, and its
tools/check-layout.py enforces tier coverage and monotonicity against the
dataset this repo publishes. A model added here renders in a fallback tier until
the site places it -- that is a site-side task, not a blocker on a data PR.
"""
import json
import re
import shutil
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MODELS = json.loads((ROOT / "models.json").read_text())
LITMUS = ROOT / "litmus"

fail = []
def err(check, msg):
    fail.append((check, msg))

ids = {m["id"] for m in MODELS["models"]}
edges = MODELS["edges"]
sw = [(e["from"], e["to"]) for e in edges if e["type"] == "strictly_weaker"]
inc_pairs = {frozenset((e["from"], e["to"])) for e in edges if e["type"] == "incomparable"}


# ---- 1. endpoints + property vectors + edge evidence ---------------------
mp = MODELS.get("modelProperties", {})
EVIDENCE_OK = {"machine_run", "cited", "by_construction", "deduced"}
for e in edges:
    for ep in (e["from"], e["to"]):
        if ep not in ids:
            err(1, f"edge endpoint '{ep}' is not a model id ({e['from']}->{e['to']})")
    ev = e.get("evidence")
    if ev not in EVIDENCE_OK:
        err(1, f"edge {e['from']}->{e['to']} has invalid/missing evidence {ev!r} "
               f"(expected one of {sorted(EVIDENCE_OK)})")
    # equivalence edges declare whether the equivalence is fragment-restricted,
    # since transport across a fragment-restricted equivalence is only sound within
    # the shared fragment (paper §Deduction).
    if e["type"] == "equivalent" and not isinstance(e.get("fragment_restricted"), bool):
        err(1, f"equivalent edge {e['from']}->{e['to']} lacks a boolean "
               f"'fragment_restricted' flag")
pp = MODELS.get("modelPropertyProvenance", {})
PROP_PROV_OK = {"survey", "extrapolated"}
for nid in sorted(ids):
    if nid not in mp:
        err(1, f"model '{nid}' has no property vector in modelProperties")
    if pp.get(nid) not in PROP_PROV_OK:
        err(1, f"model '{nid}' has invalid/missing modelPropertyProvenance "
               f"{pp.get(nid)!r} (expected one of {sorted(PROP_PROV_OK)})")

# property schema + per-property / per-cell provenance integrity.
schema = MODELS.get("propertySchema", [])
SCHEMA_KEYS = {k for g in schema for k, _label in g.get("fields", [])}
# every key used in a model's vector must be declared in the shared schema, and
# vice versa the schema should not carry columns no model ever sets.
used_keys = {k for vec in mp.values() for k in vec}
for k in sorted(used_keys - SCHEMA_KEYS):
    err(1, f"property key '{k}' appears in modelProperties but not in propertySchema")
for k in sorted(SCHEMA_KEYS - used_keys):
    err(1, f"property key '{k}' is in propertySchema but no model sets it")
# per-column provenance notes must reference real columns.
for k in sorted(MODELS.get("propertyProvenance", {})):
    if k not in SCHEMA_KEYS:
        err(1, f"propertyProvenance names unknown property '{k}'")
# per-cell citations: model, property, and referenced literature must all exist.
refs = MODELS.get("references", {})
for nid, cells in MODELS.get("modelPropertyCitations", {}).items():
    if nid not in ids:
        err(1, f"modelPropertyCitations names unknown model '{nid}'")
        continue
    for k, cell in cells.items():
        if k not in SCHEMA_KEYS:
            err(1, f"modelPropertyCitations[{nid}] names unknown property '{k}'")
        if k not in mp.get(nid, {}):
            err(1, f"modelPropertyCitations[{nid}][{k}] cites a cell the model "
                   f"leaves unknown in modelProperties")
        rid = (cell or {}).get("ref")
        if rid not in refs:
            err(1, f"modelPropertyCitations[{nid}][{k}] cites unknown reference {rid!r}")

# cat specifiability: every model says whether it is / can be / cannot be
# written in herd7's cat language, with a basis, a justifying note, and a real
# citation — the datum is only useful if it is total and sourced.
CAT_STATUS_OK = {"specified", "expressible", "not-expressible"}
CAT_BASIS_OK = {"cat-model", "cited", "extrapolated"}
cs = MODELS.get("catSupport", {})
for nid in sorted(ids):
    e = cs.get(nid)
    if not isinstance(e, dict):
        err(1, f"model '{nid}' has no catSupport entry")
        continue
    if e.get("status") not in CAT_STATUS_OK:
        err(1, f"catSupport[{nid}] has invalid/missing status {e.get('status')!r} "
               f"(expected one of {sorted(CAT_STATUS_OK)})")
    if e.get("basis") not in CAT_BASIS_OK:
        err(1, f"catSupport[{nid}] has invalid/missing basis {e.get('basis')!r} "
               f"(expected one of {sorted(CAT_BASIS_OK)})")
    if not (e.get("note") or "").strip():
        err(1, f"catSupport[{nid}] has no note justifying its status")
    if e.get("ref") not in MODELS.get("references", {}):
        err(1, f"catSupport[{nid}] cites unknown reference {e.get('ref')!r}")
for nid in sorted(set(cs) - ids):
    err(1, f"catSupport names unknown model '{nid}'")

# dataset versioning (RELEASING.md): models.json is a TEMPLATE — the version and
# date are stamped in at build time by tools/render.py from the git tag, the one
# source of truth, so nothing here may hard-code a literal version. A version
# committed by hand would be the drift this gate exists to prevent: it would
# silently win over the tag for anyone reading the file straight out of the repo.
version = MODELS.get("version")
date = MODELS.get("date")
if version != "@VERSION@":
    err(1, f"models.json 'version' must be the placeholder '@VERSION@', not {version!r} "
           f"(the version is stamped from the git tag at build time; see RELEASING.md)")
if date != "@DATE@":
    err(1, f"models.json 'date' must be the placeholder '@DATE@', not {date!r} "
           f"(stamped from the tagged commit's date at build time; see RELEASING.md)")


# ---- transitive closure of strictly_weaker (reused by 2 and 3) -----------
succ = defaultdict(set)
for a, b in sw:
    succ[a].add(b)
changed = True
while changed:
    changed = False
    for a in list(succ):
        for b in list(succ[a]):
            for c in succ[b]:
                if c not in succ[a]:
                    succ[a].add(c); changed = True

# ---- 2. acyclic ----------------------------------------------------------
for a in succ:
    if a in succ[a]:
        err(2, f"strictly_weaker has a cycle through '{a}'")

# ---- 3. order vs incomparable contradiction ------------------------------
for a in succ:
    for b in succ[a]:
        if frozenset((a, b)) in inc_pairs:
            err(3, f"pair {{{a},{b}}} is ordered (A<B in closure) yet drawn incomparable")


# ---- 4. directory <-> edge direction loop --------------------------------
def split_pair(name):
    return tuple(name.split("-vs-", 1)) if "-vs-" in name else None

sw_set = set(sw)
dir_pairs = {"strictly-weaker": set(), "incomparable": set()}
for rel in ("strictly-weaker", "incomparable"):
    base = LITMUS / rel
    if not base.is_dir():
        continue
    for child in sorted(base.iterdir()):
        if not child.is_dir():
            continue
        p = split_pair(child.name)
        if not p:
            err(4, f"litmus/{rel}/{child.name}: directory name has no '-vs-'")
            continue
        a, b = p
        if a not in ids or b not in ids:
            err(4, f"litmus/{rel}/{child.name}: '{a}' or '{b}' is not a model id")
            continue
        dir_pairs[rel].add((a, b))
        if rel == "strictly-weaker":
            if (a, b) not in sw_set:
                why = "edge is recorded B->A (reversed)" if (b, a) in sw_set else "no such strictly_weaker edge"
                err(4, f"litmus/strictly-weaker/{child.name}: {why}")
        else:
            if frozenset((a, b)) not in inc_pairs:
                err(4, f"litmus/incomparable/{child.name}: pair is not an incomparable edge")

# every litmus/memalloy-provenance ordering edge must have a witness directory
for e in edges:
    if e["type"] not in ("strictly_weaker", "incomparable"):
        continue
    if e.get("provenance") not in ("litmus", "memalloy"):
        continue
    a, b = e["from"], e["to"]
    if e["type"] == "strictly_weaker":
        ok = (a, b) in dir_pairs["strictly-weaker"]
    else:
        ok = (a, b) in dir_pairs["incomparable"] or (b, a) in dir_pairs["incomparable"]
    if not ok:
        err(4, f"edge {a} {e['type']} {b} (provenance={e['provenance']}) has no litmus directory")


# ---- 5. run.sh separation loop -------------------------------------------
runsh = (LITMUS / "run.sh").read_text().splitlines()
check_re = re.compile(r'^\s*check\s+"[^"]*"\s+(Never|Sometimes)\b(.*)$')
path_re = re.compile(r'(strictly-weaker|incomparable)/([^/ ]+)/')
verds = defaultdict(set)
for ln in runsh:
    m = check_re.match(ln)
    if not m:
        continue
    tp = path_re.search(m.group(2))
    if tp:
        verds[(tp.group(1), tp.group(2))].add(m.group(1))
for (rel, pair), vs in sorted(verds.items()):
    if len(vs) >= 2 and not {"Never", "Sometimes"} <= vs:
        err(5, f"run.sh pair {rel}/{pair} has multiple checks but no Never+Sometimes "
               f"separation (got {sorted(vs)})")


# ---- 6. optional dynamic check: run the suite ----------------------------
ran_suite = False
if shutil.which("herd7"):
    proc = subprocess.run(["bash", str(LITMUS / "run.sh")],
                          capture_output=True, text=True)
    ran_suite = True
    tail = proc.stdout.strip().splitlines()[-1] if proc.stdout.strip() else ""
    if proc.returncode != 0 or "0 failed" not in proc.stdout:
        err(6, f"litmus/run.sh did not pass cleanly: {tail or proc.stderr[-200:]}")


# ---- report --------------------------------------------------------------
NCHECKS = 6
if fail:
    print(f"check-consistency: FAILED ({len(fail)} violation(s))\n")
    for c, msg in fail:
        print(f"  [check {c}] {msg}")
    sys.exit(1)
print(f"check-consistency: OK -- {len(ids)} nodes, {len(edges)} edges, "
      f"all {NCHECKS} checks pass"
      + ("" if ran_suite else " (check 6 skipped: herd7 not on PATH)"))
