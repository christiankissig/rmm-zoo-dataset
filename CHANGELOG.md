# Changelog

Notable changes to the Relaxed Memory Model Zoo dataset. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/); versions are semver,
where MAJOR is a breaking schema change, MINOR adds models, edges or fields, and
PATCH corrects data.

Each released version is published at
<https://rmm-zoo.kissig.org/data/models.json> and stamped into its own
`version`/`date` fields and into
<https://rmm-zoo.kissig.org/data/CITATION.cff>.

## [Unreleased]

### Added

- **LKMM as a kater comparison operand**, via
  [`litmus/kater/derive-lkmm.sh`](litmus/kater/derive-lkmm.sh). kater's
  `kat/lkmm2.kat` is written over internal (`-imm`) relations, which kater
  rejects **in every mode** — including when that file is the one it was handed
  — so as shipped it loads neither as an operand nor as a checking target. The
  relations it redefines from their `-imm` counterparts are all in kater's
  builtin theory, so the script restates it over those at run time. It is
  generated rather than committed because it derives from a GPL-3.0 file and
  this dataset is BSD-3, the same reason the `kat/*.kat` models are not
  vendored.
- **`litmus/kater/controls/`** and a `refute` case in `run.sh`: queries that are
  only doing their job while they **fail**. A compilation query
  `source::psc <= target::<ordering>*` holds trivially if the target's ordering
  relation contains everything, and `kat/power-weak.kat`'s does — its `ar`
  carries `eco*;po?;eco*`, `eco*` contains the identity, so `ar ⊇ po` and
  `po <= power-weak::ar+` holds outright. The controls assert that the targets
  the suite treats as proofs are not degenerate in that way.

### Changed

- **`SC → LKMM`** upgraded from `literature`/`cited` to `kater`/`machine_run`.
  All three of LKMM's global ordering axioms — `acyclic(hb)`, the `prop;ppo*`
  work-around, and coherence — are proved to follow from SC's `acyclic(sc)`,
  unbounded. Query:
  [`litmus/kater/queries/strictly-weaker-SC-vs-LKMM.kat`](litmus/kater/queries/strictly-weaker-SC-vs-LKMM.kat).
  Strictness stays with the existing witness.
- **`katSupport["LKMM"]`** corrected: the note said LKMM was usable as a
  checking target but not as a comparison operand. It was neither; it is now the
  latter, against the derived rendering the note names.
- **`katSupport["POWER"]`** records which of kater's four Power renderings can
  actually carry a comparison. Three (`power-weak`, `power-fm-simpl`,
  `power-fm-simpl-full`) are degenerate as above; only `power-fm` and
  `power-fm-orig` are not.

### Fixed

- **`litmus/kater/open/compilation-IMM-vs-POWER.kat`** was parked on a
  misdiagnosis. The refutation was a query-shape error — the assert was against
  a single `ar` step where the sibling TSO and ARMv8 queries take the closure —
  and not the "manual rotations" obstacle it was attributed to. Fixing the shape
  does not close the edge either, because it then holds vacuously; the query is
  now stated against a non-degenerate rendering, where it is refuted on a real
  fence-vocabulary gap. The edge stays `provenance: literature`.
- **`litmus/kater/open/`** gains the LKMM edges that are now runnable but still
  unsettled (`compilation-LKMM-vs-x86-TSO.kat`, `incomparable-C11-vs-LKMM.kat`),
  each recording the verdict it produces.

## [1.3.0] — 2026-08-19

Adds a second mechanical provenance, and with it the first **proofs** in the
dataset: kater decides model containment by language inclusion, so the claims it
backs hold for executions of every size rather than up to an event bound.

### Added

- **`kater` provenance**, with the runbook, queries and runner in
  [`litmus/kater/`](litmus/kater/). kater (Kokologiannakis, Lahav & Vafeiadis,
  POPL 2023) reduces "is M weaker than N?" to language inclusion between regular
  languages — decidable and **unbounded**, unlike memalloy's search up to an
  event bound. It settles the **containment** half of an ordering claim, the half
  a litmus test can never reach; the strictness half stays with the separating
  witness, and check 4 requires both.
- **`katSupport`** — cat-specifiability's axis narrowed to kater's fragment
  (conjunctions of irreflexivity/emptiness constraints over regular expressions).
  Deliberately a separate map from `catSupport`, since the fragment is narrower,
  and deliberately **partial**: absence means *not assessed*, not *no*. Nine
  models are kat-specified today.
- **`litmus/kater/run.sh`** — one PASS/FAIL line per claim, the image pinned by
  digest the way `litmus/run.sh` pins herd7 to 7.58. It fails on a refutation, on
  a kater error, **and** on `Ignoring unsupported assumption`: kater drops a
  premise it cannot use, says so, and still exits 0, so an unguarded check could
  rest on something the tool silently ignored.
- **`make kater`**, and a **kater job in CI** running the suite on every push and
  pull request.
- **Check 7** (run the kater suite, skipped unless the image is local) and two
  extensions to the gate: every edge's `provenance` must be one of the five
  declared values (check 1), and every `kater` edge must have the query file that
  proves it, over endpoints `katSupport` marks specified (check 4).
- **`litmus/kater/open/`** — the three queries that do *not* pass, kept runnable
  so the obstacle is reproducible rather than folklore: the cross-ISA
  `TSO → ARMv8` comparison (no mapping between the instruction sets), `SC → LKMM`
  (kater rejects `lkmm2.kat` as an include), and `IMM → POWER` (Power needs the
  manual rewriting the paper describes).

### Changed

- **Five edges re-evidenced against kater**, none of them re-classified — the
  relations are as they were, but now decided rather than cited:
  `SC → TSO`, `SC → C11` and `RC11 → C11` (containment proved; strictness still
  the litmus witness), and the compilation edges `IMM → ARMv8` and
  `IMM → x86-TSO`, which move from `cited` to `machine_run`.
- Evidence counts are now 42 `machine_run` / 84 `cited` / 19 `by_construction`;
  provenance counts 125 `literature`, 11 `litmus`, 5 `kater`, 4 `memalloy`.

## [1.2.0] — 2026-08-14

First release of the dataset as a standalone repository, split out of the
combined site/paper repository it grew up in.

### Contents

101 models, 145 edges (59 strictly-weaker, 35 equivalent, 26 incomparable, 25
compilation) and 112 references, with a per-model property table, per-cell
provenance, and cat-specifiability for every model.

### Added

- **BSD 3-Clause licence** (`LICENSE`), and `license:` in the citation metadata.
- **Citation metadata published with the data.** `CITATION.cff.in` is rendered by
  the build and served at `/data/CITATION.cff`, beside the dataset it describes.
- **Tag-driven versioning.** The git tag is the single source of the version:
  `tools/version.py` resolves it (with `VERSION`/`DATE` overrides and a dev
  version off-tag), `tools/render.py` stamps it into the published `models.json`
  and `CITATION.cff`, and `make deploy` refuses to publish a dev version.
- **`evidence` axis on every edge** — `machine_run` / `cited` / `by_construction`
  (40 / 86 / 19), orthogonal to `provenance` and gate-validated, so a mechanised
  verdict is distinguishable from a cited one.
- **Per-model property provenance** (`modelPropertyProvenance`) and per-cell
  citations (`modelPropertyCitations`), separating survey-sourced values from
  author-extrapolated ones.
- **`fragment_restricted` flag** on equivalences whose transport is sound only on
  a fragment, so deductions resting on one can be counted separately.
- **Multicopy atomicity (`mca`) property** and a **`formalism` facet**
  (axiomatic / mechanistic / operational / event-structure / reordering), from Su
  & Colvin, *Weak Memory Model Formalisms* (CCPE 38(2), 2026).
- **Steinke–Nutt classical consistency lattice** (JACM 51(5), 2004) — processor,
  PRAM, causal, slow and local, with cited-theorem edges. Coherence is identified
  as Goodman's cache consistency, and local, not coherence, is the bottom.
  Deliberately no cross-paradigm edges to the modern HW/PL models.
- **memalloy provenance** for the scoped-GPU edges, with a reproducible
  Dockerfile and runbook (`litmus/memalloy/`). `OpenCL→PTX` is verified by run:
  sound, 0 counterexamples up to 4/6 events, with a buggy-mapping control that
  yields a witness.

### Changed

- Every edge carries `provenance` (`literature` 130, `litmus` 11, `memalloy` 4),
  with one-sided-litmus edges drawn lighter on the map to mark them as argued
  rather than mechanised.
- `PSO→POWER` reclassified; `PSO→POWER`, `TSO→ARMv8` and `TSO→RVWMO` are flagged
  provisional — cross-ISA monotonicity arguments, not theorems.

### Repository

The published history starts here: the paper and site sources this repository
once carried live in `rmm-zoo-tool-paper` and `rmm-zoo.kissig.org`, and the
history was squashed at the split. Releases before 1.2.0 were made from the
combined repository and are not itemised here.

[Unreleased]: https://github.com/christiankissig/rmm-zoo-dataset/compare/v1.3.0...HEAD
[1.3.0]: https://github.com/christiankissig/rmm-zoo-dataset/compare/v1.2.0...v1.3.0
[1.2.0]: https://github.com/christiankissig/rmm-zoo-dataset/releases/tag/v1.2.0
