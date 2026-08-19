---
name: Correct a relation between models
about: Add, remove, redirect or reclassify an edge
---

## The relation

- **Models:** `A` … and `B` …
- **Currently:** *(edge type + direction, or "no edge")* …
- **Should be:** …

`type` is one of `strictly_weaker` (drawn `from` = stronger → `to` = weaker),
`incomparable`, `equivalent`, or `compilation`.

## Why

For a **strictly-weaker** claim, both halves need an argument: that every
behaviour the weaker model allows the stronger one allows too (containment), and
that the containment is *strict* (a witness the weaker model allows and the
stronger forbids).

For an **incomparable** claim: a behaviour each model allows that the other
forbids — ideally in both directions; if only one direction has a witness, say
so explicitly.

Containment argument:

…

Separating behaviour:

…

## Evidence

- **`provenance`:** `litmus` (a test in this repo) / `memalloy` / `kater` /
  `completion` / `literature`
- **`evidence`:** `machine_run` (a tool here actually runs it) /
  `by_construction` / `cited` / `deduced`
- **`note`:** one or two sentences naming the source or the witness

If `provenance` is `litmus`, `memalloy` or `kater`, check 4 requires a witness
directory — see the *Add litmus tests* template. `kater` additionally requires
the query file `litmus/kater/queries/<type>-<from>-vs-<to>.kat` and a
`katSupport` entry for both endpoints: kater proves containment only, so a
`strictly_weaker` edge still owes the separating witness that makes it strict.
See `litmus/kater/README.md`.

## Invariants this has to respect

The consistency gate rejects an edge that breaks any of these:

- [ ] `strictly_weaker` stays a **DAG** — no cycle introduced (check 2)
- [ ] No pair is both **ordered and incomparable**, including via the transitive
      closure of `strictly_weaker` — a deduced order must not contradict a drawn
      incomparable edge (check 3)
- [ ] **Tier monotonicity:** `tier[from] < tier[to]` for every `strictly_weaker`
      edge, so the arrow descends on screen. Retiering one model to fit a new
      edge can break others — re-run `make check` after (check 5)
- [ ] Witness directory name matches the edge's **type and direction**, `from`
      = stronger (check 6)
- [ ] A pair exercised on both sides in `run.sh` shows a real **`Never` +
      `Sometimes`** split, not two identical verdicts (check 5)

## Reclassification

If this changes an existing edge's type, the witness tree has to move with it —
e.g. `litmus/incomparable/A-vs-B/` → `litmus/strictly-weaker/A-vs-B/`, the
directory README rewritten to argue the new claim, and `litmus/run.sh` updated.
`PSO-vs-POWER`, `Weakestmo-vs-C11` and `CSRA-vs-C11` are worked examples.

- [ ] Not a reclassification / witness tree and `run.sh` moved with it
- [ ] `litmus/README.md` updated if the change is one the "what is and isn't
      machine-checked" section describes

## Verification

```sh
bash litmus/run.sh      # per-test PASS/FAIL, if the witness is herd7-runnable
make litmus             # regenerate litmus.json (committed) if litmus/ changed
make check
```

- [ ] `make check` passes
- [ ] Regenerated files are committed
