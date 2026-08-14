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

[Unreleased]: https://github.com/christiankissig/rmm-zoo-dataset/compare/v1.2.0...HEAD
[1.2.0]: https://github.com/christiankissig/rmm-zoo-dataset/releases/tag/v1.2.0
