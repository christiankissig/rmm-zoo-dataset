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

- **`litmus/models/wra.cat`**, completing the trio. Modification order is
  deliberately unused: `hb|loc`, not `mo`, decides which of two writes to a
  location is the later, which is exactly what costs WRA its SC-per-location.
- **`litmus/strictly-weaker/RA-vs-WRA/`** with all three of Lahav & Boker's
  Ex. 3.7 witnesses — `WW`, `Oscillating` and `SF`, every one a *single-location*
  program. `sra.cat` is run alongside and agrees with `ra.cat` on all three, which
  is what shows this axis is orthogonal to the 2+2W one.
- **`litmus/strictly-weaker/SC-vs-SRA/`** with `IRIW`. Both models admit 15
  executions and differ on exactly the witness.

### Changed

- **The dataset is now edited as one file per thing.** `models.json` is compiled
  from a new `src/` tree by `make models` and is a build artifact from here on —
  generated and committed, like `litmus.json`, never hand-edited. A model is
  `src/models/<id>.json` and carries everything it asserts (its entry, its
  property vector and provenance, per-cell citations, cat- and
  kat-specifiability); an edge is `src/edges/<from>-vs-<to>.json`, named for its
  pair the way its witness directory already is. The bibliography, the property
  schema and the file's own prose header are `src/references.json`,
  `src/properties.json` and `src/dataset.json`, and `src/models/_order.txt`
  carries the strength order the models are published in. Changing a model now
  touches that model's file and changing an edge touches that edge's file, so
  work on different corners of the zoo no longer meets in one 4000-line diff.
  `make check` runs the generator in `--check` mode first and fails while the
  committed `models.json` differs from the sources.

  **The published dataset is unchanged** — same models, same edges, same blocks,
  same schema. Consumers fetch `models.json` exactly as before; only the edge
  list is written in a different (pair-name) order, which it never carried
  meaning in.
- **`RA → WRA`** and **`SC → SRA`** upgraded from `literature`/`cited` to
  `litmus`/`machine_run`. Every strictly-weaker edge among SC, SRA, RA and WRA is
  now decided by herd7. Containment stays cited in both cases (Prop. 3.2 for the
  first); herd7 decides the strictness half only.
- **`ra.cat` and `sra.cat` now state the initialisation ordering explicitly** —
  `hb` puts the init events before every thread event, as Lahav & Boker do. Their
  verdicts are unchanged, because `mo` already relates `IW` to every write and
  their coherence axioms fire anyway. It is stated because **WRA has no `mo`**:
  without it, `weak-read-coherence` can never fire against an initial value and
  WRA wrongly *allows* message passing (`MP+relacq`: `Never 0 3` → `Sometimes 1 3`)
  — i.e. is not causally consistent at all, contradicting the model's purpose. The
  `MP+relacq` control caught this on the first run of the draft model. Stating it
  in all three keeps them line-for-line comparable rather than leaving RA and SRA
  correct by accident.


## [1.4.1] — 2026-08-23

### Added

- **`CCv → WFR`**, `by_construction`. Unlike the sibling edge from `Causal` this
  is a derivation, not a citation: CCv includes `CausalArbitration` (`hb ⊆ ar`)
  with `hb = (so ∪ vis)+`, and WritesFollowReads is `(vis; so|rd→wr) ⊆ ar`, so
  the composite lies in `hb ⊆ ar` and CCv satisfies WFR by construction.

### Changed

- **`PSI → RC11` and `SI → RC11` retargeted onto `RA`.** Both notes already
  ended "the target is the RA fragment of RC11" — Raad, Lahav & Vafeiadis build
  the reference implementations over the release-acquire fragment, not over full
  RC11. There was no RA node to point at until 1.4.0; now there is, and the edges
  say what their notes always said.

### Fixed

- **The `WFR` description repeated the same false equality** the `Causal → WFR`
  note carried — `causal = PRAM ∧ writes-follow-reads`, which no source states.
  Corrected the same way, and it now records the CCv route as well.
- **`POCausal` and `EC` descriptions named the wrong causal neighbour.** Both
  place themselves below "causal consistency", but their ordering edges run to
  `CCv`; neither has any edge to `Causal`. Disambiguated, as `CausalPlus` and
  `RTCausal` were in 1.4.0. (`Coherence`, `PC` and `PRAM` also say "causal
  consistency" where they mean causal memory, but those are *correct* — the
  `Causal` node is CM and those are its Steinke–Nutt edges — so they are left
  as they are.)
- **`Causal → WFR` was mis-cited.** The note claimed Brzeziński et al. proved
  `causal = PRAM ∧ writes-follow-reads`, citing Viotti & Vukolić Eq. 25. Eq. 25
  is the *definition* of `WritesFollowReads`, not a theorem about causal
  consistency, and both sources assert only the implication — causal consistency
  "requires and includes" the four session guarantees. The equality was never
  established; whether the converse holds is now #11. The edge itself stands:
  the implication is all a `strictly_weaker` edge needs, and Brzeziński et al.'s
  data-centric models are the classical shared-memory taxonomy, so their causal
  consistency is causal memory and the edge was on the right node — unlike the
  `CausalPlus` and `RTCausal` edges corrected in 1.4.0.


## [1.4.0] — 2026-08-22

### Added

- **`SRA` (strong release-acquire)**, Lahav, Giannarakis & Vafeiadis, POPL
  2016 — the strengthening of C/C++11's release-acquire fragment that replaces
  write-coherence (`mo;hb` irreflexive, a *local* agreement between modification
  order and happens-before) with strong-write-coherence (`(hb ∪ mo)+`
  irreflexive, a *global* one). It forbids 2+2W at no implementation cost: the
  same local optimisations stay sound and the x86-TSO and POWER compilation
  schemes are unchanged.
- **`RA`** and **`WRA`**, completing the chain `SRA ⊐ RA ⊐ WRA`. RA had been
  referenced by four existing edge notes ("the release-acquire (RA) fragment of
  RC11", on PSI, SI, RAR and CRC) without ever being a node. WRA drops
  modification order entirely and, unlike RA and SRA, does not provide
  SC-per-location.
- **`CC` (weak causal consistency)**, Bouajjani et al. — the weakest causal
  variant, strictly weaker than both CM and CCv, completing that triangle.
- **`SRA ≡ CCv`** (`fragment_restricted`, modulo RMWs) and **`WRA ≡ CC`**.
  These are the point of the whole addition: until now the distributed
  causal-consistency cluster reached the rest of the zoo only through `SC` and
  `Coherence`. It now connects to the C11 family through the release-acquire
  models, on Lahav & Boker's equivalences.
- **`SRA → POWER`** and **`SRA → x86-TSO`** compilation edges. The POWER mapping
  is *complete* as well as sound — SRA is exactly what POWER provides for
  programs compiled from the RA fragment, which is why SRA cannot be
  strengthened further without an implementation cost.
- **`RC11 ≡ RA`** (`fragment_restricted`, `by_construction`), **`SC → SRA`**,
  **`Causal → CC`**, **`CCv → CC`**, and references **`Lahav2016`**,
  **`LahavBoker2020`**, **`LahavBoker2022`**.
- **`litmus/models/ra.cat`** and **`litmus/models/sra.cat`** — authored for this
  dataset (not vendored), rendering Lahav & Boker's Table 1 over herd7's C
  vocabulary. They are line-for-line identical except for the one axiom that
  separates the models: `irreflexive mo;hb` against `acyclic hb | mo`.
- **`litmus/strictly-weaker/SRA-vs-RA/`** with `2+2W.litmus`, which herd7 decides
  `Sometimes 1 8` under RA and `Never 0 5` under SRA.

- **`CCv` (causal convergence)** as its own node, splitting apart two
  incomparable models that had been sharing the `Causal` node. `Causal` is
  Ahamad et al.'s **causal memory (CM)** — Steinke & Nutt restate that
  definition verbatim (Def. 2.5), characterise it as a per-process serial view
  over the causal relation (Thm. 3.6) and place it as GPO+GWO (Thm. 4.18), and
  their "weaker than SC, stronger than PRAM, incomparable to processor and cache
  consistency" is exactly the node's four Steinke–Nutt edges. But four *other*
  edges on the node came from Viotti & Vukolić, whose `Causality` (Eq. 26,
  `CausalVisibility ∧ CausalArbitration ∧ RVal`) is Burckhardt's causal
  consistency — what Bouajjani et al. name **CCv**, and what Perrin et al.
  proved **incomparable** to CM. A global arbitration order and a per-site
  unrevised serialisation are different requirements; neither implies the other.
- **`Causal ⋈ CCv`** with both witnesses from Bouajjani et al. Fig. 2: history
  (2a) is CM but not CCv, history (2b) is CCv but not CM.
- **`SC → CCv`**, and references **`Bouajjani2017`** and **`Perrin2016`**.

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
- **`litmus/memalloy/run.sh`** and **`make memalloy`** — the memalloy suite had a
  runbook but no runner, so its verdicts could not be re-decided the way the
  kater ones can. Every case states the solution count it expects, and the suite
  ends with **controls that must find something** (the known-buggy OpenCL→PTX
  mapping; ARMv8 not contained in RVWMO): a containment run that is clean
  because the search was broken otherwise looks exactly like one that is clean
  because the containment holds.
- **`litmus/memalloy/derive-hw-fragment.sh`** — restricts memalloy's
  arch-specific `x86tso.cat` and `aarch64.cat` to its generic `Basic_HW` arch,
  which is the vocabulary the two ISAs share. The comparator takes one `-arch`
  for both operands, so cross-ISA pairs were not runnable at all; on the
  fragment they are. Every term the script drops is *empty* there rather than
  weakened away, so the derived models are exact restrictions — and the script,
  not prose, is the record of what the common fragment is.
- **`litmus/memalloy/models/zoo_hw_rvwmo.cat`** — a RISC-V RVWMO model authored
  for this dataset, from the thirteen `ppo` rules of the RVWMO chapter of the
  RISC-V unprivileged spec, annotating each rule it renders and each that is
  empty on the fragment. memalloy ships no RISC-V model, which is why `TSO →
  RVWMO` could not be checked at all.
- **`litmus/kater/controls/`** and a `refute` case in `run.sh`: queries that are
  only doing their job while they **fail**. A compilation query
  `source::psc <= target::<ordering>*` holds trivially if the target's ordering
  relation contains everything, and `kat/power-weak.kat`'s does — its `ar`
  carries `eco*;po?;eco*`, `eco*` contains the identity, so `ar ⊇ po` and
  `po <= power-weak::ar+` holds outright. The controls assert that the targets
  the suite treats as proofs are not degenerate in that way.

### Changed

- **`SRA → RA`** upgraded from `literature`/`cited` to `litmus`/`machine_run`.
  Because both cat models are hand-written rather than vendored, the pair is
  bracketed by controls that `run.sh` runs alongside the witness — a model that
  forbade everything, or constrained nothing, would otherwise produce the same
  split as a correct one. `MP+relacq` must be forbidden by both; `IRIW` must be
  allowed by both, and that expectation is checked against the literature rather
  than intuition (Lahav & Boker Ex. 3.5 marks IRIW allowed under WRA, RA and SRA
  alike). Both models return identical counts on IRIW, which is what says the
  strengthening bites on 2+2W specifically rather than pruning executions at
  large. Containment stays the cited one-axiom argument; herd7 decides the
  strictness half only.

- **`CausalPlus → POCausal`… re-homed onto `CCv`.** `CausalPlus → Causal`,
  `RTCausal → Causal` and `Causal → POCausal` all rest on the
  visibility/arbitration framework, so their containments are against CCv, not
  causal memory. They are now `CausalPlus → CCv`, `RTCausal → CCv` and
  `CCv → POCausal`. `Causal → WFR` deliberately stays on CM: Brzeziński et al.
  is a shared-memory session-guarantees result in the same lineage as PRAM and
  Steinke–Nutt, and it is V-V's restatement of it inside their framework that is
  the loose step.

  All three of LKMM's global ordering axioms — `acyclic(hb)`, the `prop;ppo*`
  work-around, and coherence — are proved to follow from SC's `acyclic(sc)`,
  unbounded. Query:
  [`litmus/kater/queries/strictly-weaker-SC-vs-LKMM.kat`](litmus/kater/queries/strictly-weaker-SC-vs-LKMM.kat).
  Strictness stays with the existing witness.
- **`SC → LKMM`** upgraded from `literature`/`cited` to `kater`/`machine_run`.
- **`TSO → ARMv8`** and **`TSO → RVWMO`** upgraded from `litmus` to `memalloy`.
  Both were provisional on a one-sided witness plus a cross-ISA monotonicity
  argument; both halves are now decided by memalloy over the common `Basic_HW`
  fragment — witness at 4 events, containment clean exhaustively to 7. Bounded
  evidence, not a theorem, and scoped to the fragment: it decides the edges over
  the vocabulary the ISAs share, not over the full instruction sets.
- **`katSupport["LKMM"]`** corrected: the note said LKMM was usable as a
  checking target but not as a comparison operand. It was neither; it is now the
  latter, against the derived rendering the note names.
- **`katSupport["POWER"]`** records which of kater's four Power renderings can
  actually carry a comparison. Three (`power-weak`, `power-fm-simpl`,
  `power-fm-simpl-full`) are degenerate as above; only `power-fm` and
  `power-fm-orig` are not.

### Fixed

- **`CausalPlus → Causal` and `RTCausal → Causal` were false**, not merely
  mis-cited, and are now `incomparable`. Both models are contained in CCv
  (`Causal+ = CCv ∧ StrongConvergence`, `RealTimeCausality = CCv ∧ RealTime`),
  so both forbid history (2a), which is CM — the strictness half held. The
  *containment* half did not. History (2b) is CCv and not CM, and it reads each
  of x, y and z exactly once, so StrongConvergence (V-V Eq. 17, which constrains
  only reads with equal visible-write sets) is vacuous on it: (2b) is causal+
  and not CM. For real-time causal, (2b) also admits a schedule — pa's writes
  all completing before pb starts — whose arbitration order extends `rb`, and
  RealTime (Eq. 9, `rb ⊆ ar`) constrains arbitration only, not visibility, so
  `rd(z)▷0` may still miss `wr(z,1)`.

- **`litmus/kater/open/compilation-IMM-vs-POWER.kat`** was parked on a
  misdiagnosis. The refutation was a query-shape error — the assert was against
  a single `ar` step where the sibling TSO and ARMv8 queries take the closure —
  and not the "manual rotations" obstacle it was attributed to. Fixing the shape
  does not close the edge either, because it then holds vacuously; the query is
  now stated against a non-degenerate rendering, where it is refuted on a real
  fence-vocabulary gap. The edge stays `provenance: literature`.
- **`tools/check-consistency.py`** check 4 gains the converse of its kater rule:
  a query in `litmus/kater/queries/` that backs no `kater`-provenance edge is now
  an error. Only one direction was checked, so a query could land while its edge
  upgrade was dropped — the suite would go on proving it, green, while the
  dataset still recorded the weaker provenance. `open/` and `controls/`, which
  hold queries that are deliberately not claims, are not scanned.
- **`litmus/memalloy/README.md`** said the base repo had no model to compare TSO
  and ARMv8 "at the right level of abstraction". It has one — the generic
  `Basic_HW` arch — and the obstacle was the single `-arch` flag, not a missing
  model. It also listed obtaining a Vulkan Alloy model as the blocker for the
  GPU edges; Khronos publishes one, and it is not comparator input (its own
  `sig Exec`, ~40 fields, no `co`), so the work there is a port to memalloy's
  execution signature, not an acquisition.
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

[Unreleased]: https://github.com/christiankissig/rmm-zoo-dataset/compare/v1.4.1...HEAD
[1.4.1]: https://github.com/christiankissig/rmm-zoo-dataset/compare/v1.4.0...v1.4.1
[1.4.0]: https://github.com/christiankissig/rmm-zoo-dataset/compare/v1.3.0...v1.4.0
[1.3.0]: https://github.com/christiankissig/rmm-zoo-dataset/compare/v1.2.0...v1.3.0
[1.2.0]: https://github.com/christiankissig/rmm-zoo-dataset/releases/tag/v1.2.0
