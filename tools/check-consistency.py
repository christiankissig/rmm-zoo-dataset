#!/usr/bin/env python3
"""Fail-fast consistency checks for the zoo's graph data.

Turns the manual audit into an automatic gate. Run via `make check` (and as a
dependency of `make build`/`make deploy`). Exits non-zero on any violation.

What it guarantees, so the dataset cannot silently drift from its claims:

  STRUCTURE (models.json)
    1. every edge endpoint is a real node; every edge carries a declared
       provenance and evidence; every node has a property vector and a
       cat-specifiability entry (status + basis + note + a resolvable citation);
       the kat-specifiability map is well formed where it is populated
    2. strictly_weaker is a DAG (no cycles)
    3. no pair is both ordered and incomparable -- neither directly nor via the
       transitive closure of strictly_weaker (a deduced order must not contradict
       a drawn incomparable edge)

  DATA <-> WITNESSES (litmus/ tree, run.sh)
    4. evidence loop: every litmus/{strictly-weaker,incomparable}/<A>-vs-<B>
       directory matches an edge of the right TYPE and DIRECTION in models.json;
       every litmus/memalloy/kater-provenance ordering edge has such a directory
       (kater proves containment, never strictness -- the witness is still owed);
       and every kater-provenance edge, of any type, has the query file that
       backs it, over endpoints katSupport marks kat-specified
    5. separation loop: every pair that run.sh exercises on both sides exhibits a
       genuine Never+Sometimes split (a witness that actually distinguishes the
       models, not two identical verdicts)

  OPTIONAL (only if the tool is available)
    6. herd7 on PATH: run litmus/run.sh and require 0 failures -- the dynamic
       closed loop that the hardcoded Never/Sometimes expectations still hold
       under the checker
    7. the kater image pulled locally: run litmus/kater/run.sh and require 0
       failures -- the same closed loop for the machine-checked containments

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
PROVENANCE_OK = {"literature", "litmus", "completion", "memalloy", "kater"}
for e in edges:
    for ep in (e["from"], e["to"]):
        if ep not in ids:
            err(1, f"edge endpoint '{ep}' is not a model id ({e['from']}->{e['to']})")
    pv = e.get("provenance")
    if pv not in PROVENANCE_OK:
        err(1, f"edge {e['from']}->{e['to']} has invalid/missing provenance {pv!r} "
               f"(expected one of {sorted(PROVENANCE_OK)})")
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

# kat specifiability: the same axis for kater's (narrower) input language. Unlike
# catSupport this map is PARTIAL by design -- absence means "not assessed", not
# "no" -- so it is validated where present rather than required to be total. The
# one hard requirement is check 4's: a kater-provenance edge needs both endpoints
# marked kat-specified, since the check is only as meaningful as the .kat files.
KAT_STATUS_OK = CAT_STATUS_OK
KAT_BASIS_OK = {"kat-model", "cited", "extrapolated"}
ks = MODELS.get("katSupport", {})
for nid in sorted(ks):
    if nid not in ids:
        err(1, f"katSupport names unknown model '{nid}'")
        continue
    e = ks[nid]
    if not isinstance(e, dict):
        err(1, f"katSupport[{nid}] is not an object")
        continue
    if e.get("status") not in KAT_STATUS_OK:
        err(1, f"katSupport[{nid}] has invalid/missing status {e.get('status')!r} "
               f"(expected one of {sorted(KAT_STATUS_OK)})")
    if e.get("basis") not in KAT_BASIS_OK:
        err(1, f"katSupport[{nid}] has invalid/missing basis {e.get('basis')!r} "
               f"(expected one of {sorted(KAT_BASIS_OK)})")
    if not (e.get("note") or "").strip():
        err(1, f"katSupport[{nid}] has no note justifying its status")
    if e.get("ref") not in MODELS.get("references", {}):
        err(1, f"katSupport[{nid}] cites unknown reference {e.get('ref')!r}")
    # a per-execution predicate is a precondition for both languages, so the
    # narrower one cannot claim more than the wider one.
    if e.get("status") in ("specified", "expressible") and \
            (cs.get(nid) or {}).get("status") == "not-expressible":
        err(1, f"katSupport[{nid}] is {e['status']!r} while catSupport says "
               f"'not-expressible' -- kater's fragment is narrower than cat's")

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

# every litmus/memalloy/kater-provenance ordering edge must have a witness
# directory. kater is included deliberately: it decides the CONTAINMENT half of a
# strictly_weaker claim and can never establish strictness, so such an edge still
# owes the separating witness -- dropping the directory would quietly turn a
# proved order into a proved inclusion.
for e in edges:
    if e["type"] not in ("strictly_weaker", "incomparable"):
        continue
    if e.get("provenance") not in ("litmus", "memalloy", "kater"):
        continue
    a, b = e["from"], e["to"]
    if e["type"] == "strictly_weaker":
        ok = (a, b) in dir_pairs["strictly-weaker"]
    else:
        ok = (a, b) in dir_pairs["incomparable"] or (b, a) in dir_pairs["incomparable"]
    if not ok:
        err(4, f"edge {a} {e['type']} {b} (provenance={e['provenance']}) has no litmus directory")

# every kater-provenance edge -- of any type, ordering or not -- must name the
# query that backs it, and both endpoints must be kat-specified. The file name is
# derived from the edge, so a renamed model or a retyped edge orphans its proof
# here rather than on the site.
KATER_Q = LITMUS / "kater" / "queries"
for e in edges:
    if e.get("provenance") != "kater":
        continue
    a, b = e["from"], e["to"]
    q = KATER_Q / f"{e['type'].replace('_', '-')}-{a}-vs-{b}.kat"
    if not q.is_file():
        err(4, f"edge {a} {e['type']} {b} (provenance=kater) has no query at "
               f"{q.relative_to(ROOT)}")
    for ep in (a, b):
        if (ks.get(ep) or {}).get("status") != "specified":
            err(4, f"edge {a} {e['type']} {b} is provenance=kater but katSupport[{ep}] "
                   f"is not 'specified' -- the check needs a .kat for both endpoints")

# ...and the converse: a query in queries/ that backs no kater-provenance edge is
# a proof nothing claims. That is the failure mode where the query lands and the
# edge upgrade is dropped -- the suite goes on proving it, green, while the
# dataset still records the weaker provenance. Queries that are NOT claims live
# in open/ (parked obstacles) and controls/ (must-fail), which are not scanned.
kater_edge_files = {
    f"{e['type'].replace('_', '-')}-{e['from']}-vs-{e['to']}.kat"
    for e in edges if e.get("provenance") == "kater"
}
if KATER_Q.is_dir():
    for q in sorted(KATER_Q.glob("*.kat")):
        if q.name not in kater_edge_files:
            err(4, f"{q.relative_to(ROOT)} backs no provenance=kater edge -- either "
                   f"the edge was not upgraded, or the query belongs in open/")


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


# ---- 7. optional dynamic check: run the kater suite ----------------------
# Gated on the image already being local: pulling ~700MB inside `make check`
# would be rude, and CI pulls it in its own step before calling us.
KATER_RUN = LITMUS / "kater" / "run.sh"
# The pin lives in run.sh (one place), so read the image reference back out of it
# rather than repeating the digest here where the two could drift apart.
m = re.search(r"KATER_IMAGE:-([^}\s]+)", KATER_RUN.read_text())
KATER_IMAGE = m.group(1) if m else "genmc/kater"
ran_kater = False
if shutil.which("docker") and subprocess.run(
        ["docker", "image", "inspect", KATER_IMAGE],
        capture_output=True).returncode == 0:
    proc = subprocess.run(["bash", str(KATER_RUN)], capture_output=True, text=True)
    ran_kater = True
    tail = proc.stdout.strip().splitlines()[-1] if proc.stdout.strip() else ""
    if proc.returncode != 0 or "0 failed" not in proc.stdout:
        err(7, f"litmus/kater/run.sh did not pass cleanly: {tail or proc.stderr[-200:]}")


# ---- report --------------------------------------------------------------
NCHECKS = 7
if fail:
    print(f"check-consistency: FAILED ({len(fail)} violation(s))\n")
    for c, msg in fail:
        print(f"  [check {c}] {msg}")
    sys.exit(1)
skipped = []
if not ran_suite:
    skipped.append("6: herd7 not on PATH")
if not ran_kater:
    skipped.append(f"7: {KATER_IMAGE.split('@')[0]} image not pulled")
print(f"check-consistency: OK -- {len(ids)} nodes, {len(edges)} edges, "
      f"all {NCHECKS} checks pass"
      + ("" if not skipped else " (skipped check " + "; check ".join(skipped) + ")"))
