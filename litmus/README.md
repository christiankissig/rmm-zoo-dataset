# Litmus tests for the memory-model ordering edges

This tree backs the ordering edges drawn in [`../src/models.json`](../src/models.json).
For every **strictly-weaker** edge `A → B` there is a litmus test whose
distinguishing outcome is **allowed by the weaker model `B`** and **forbidden by
the stronger model `A`**. For every **incomparable** edge there is a test that
separates the two models in at least one direction (and, where both directions
exist, in both).

The tests run mostly in [**herd7**](http://diy.inria.fr/herd/) (the `herdtools7`
suite). A handful use other systems where herd7 has no suitable model:

| System | Used for | How |
|---|---|---|
| herd7 | most hardware + C11/RC11 edges | `herd7 -model <model>.cat test.litmus` |
| [mordor](../../mordor) | the MRD (thin-air) side | `mordor run --single test.lit` |
| Java (JDK) | `SC → Java` | `javac SB.java && java SB` |
| OCaml ≥ 5 | `Java ↔ OCaml` | `ocaml sb.ml` |
| herd7 `-c11` (relaxed model) | scoped GPU edges `C11 → {OpenCL, CUDA, HRF}` | cross-scope sync ≡ `relaxed`; see those READMEs |
| herd7 + C++-version cat models | `C++20 ↔ C11` release-sequence axis | `herd7 -model models/cpp/{cpp11,cpp17,cpp2w}.cat test.litmus` (vendored from [`gonzalobg/cpp_memory_model`](https://github.com/gonzalobg/cpp_memory_model)) |
| cited / [memalloy](https://github.com/johnwickerson/memalloy) | `HRF ↔ ScopedC11`, `PTX ↔ AMDGPU`, `OpenCL ↔ Vulkan` | documented verdict + literature |

## Layout

```
litmus/
├── run.sh                 # runs & checks every herd7 test against its expected outcome
├── models/                # portable abstract cat models (SC, TSO, PSO, RMO, Coherence)
│   └── cpp/               # C++11/17/20 + RC11/RC17 cat models (vendored; see PROVENANCE.md)
├── cpp_memory_model/rs/   # release-sequence litmus family (vendored; per-version verdicts)
├── strictly-weaker/<A>-vs-<B>/   # A is stronger, B is weaker
└── incomparable/<A>-vs-<B>/
```

`<A>-vs-<B>` directory names follow the edge direction in `models.json`
(`from` = stronger, `to` = weaker). Each directory has its own `README.md` with
the exact commands and expected output.

## Quick start

```sh
opam install herdtools7      # one-time
eval $(opam env)
./run.sh                     # runs all herd7 tests, prints PASS/FAIL vs expected
```

Expected: `65 passed, 0 failed`. The suite runs on every push and pull request
(see [`.github/workflows/litmus.yml`](../.github/workflows/litmus.yml)). The
Java/OCaml/mordor tests, and the research-model pairs that have no herd7 model
(see below), are run or documented from their own directories (see those
READMEs).

## The abstract `cat` models

herd7 ships precise models for the *named* hardware (`x86tso.cat`, `aarch64.cat`,
`arm.cat`, `ppc.cat`, `riscv.cat`) and languages (`rc11.cat`, `c11_orig.cat`,
`-c11`). It does **not** ship the classical *abstract* lattice models, so this
repo provides small, portable, self-contained ones in [`models/`](models):

| File | Model | Preserved program order |
|---|---|---|
| `abstract-sc.cat` | Sequential Consistency | everything |
| `abstract-tso.cat` | Total Store Order | all but W→R |
| `abstract-pso.cat` | Partial Store Order | loads stay ordered; W→W relaxed |
| `abstract-rmo.cat` | Relaxed Memory Order | only dependencies |
| `abstract-coherence.cat` | bare cache coherence | nothing (per-location only) |

They are written in generic relations (`po`, `co`, `rf`, `fr`, `addr/data/ctrl`,
guarded fence sets) so the *same* cat file applies to an x86, AArch64, RISC-V or
PPC test. They encode the textbook definitions of these models, which is what the
zoo's abstract nodes refer to.

## What is and isn't machine-checked — read this

A few honest caveats, all detailed in the per-pair READMEs:

* **herd7 cannot exhibit out-of-thin-air (OOTA) executions.** Its candidate
  generation ties read values to actual stores, so OOTA outcomes never appear.
  This affects `MRD → C11` (the difference between them *is* thin-air): the MRD
  side is checked in mordor (which forbids it); the C11 permission is a property
  of the standard's axioms, cited rather than exhibited.

* **`PSO ↔ POWER` was not actually incomparable, and has been reclassified.**
  Across every standard litmus family we swept, every PSO-allowed behaviour is
  also POWER-allowed (PSO ⊆ POWER), while POWER allows load-load reordering PSO
  forbids. The reverse direction has no witness, so the `models.json` edge is now
  `strictly_weaker` (PSO → POWER) and the test lives under
  `strictly-weaker/PSO-vs-POWER/`.

* **`C11 ↔ Weakestmo` and `C11 ↔ CSRA` were not incomparable either, and have
  been reclassified.** Both Weakestmo (Chakraborty & Vafeiadis, POPL 2019) and
  CSRA (Pichon-Pharabod & Sewell, POPL 2016) are thin-air-free models the primary
  sources place *below* C11: Weakestmo is "stronger than C11 ... and weaker than
  RC11" (§2.1), and CSRA is "a subset of C/C++11 by design ... the converse is not
  to be expected" (§9). Every separating outcome is C11-allows / model-forbids
  (out-of-thin-air); neither admits a behaviour C11 forbids. So the `models.json`
  edges are now `strictly_weaker` (`Weakestmo → C11`, `CSRA → C11`) and the tests
  live under `strictly-weaker/Weakestmo-vs-C11/` and `strictly-weaker/CSRA-vs-C11/`,
  alongside the `MRD-vs-C11` / `sMRD-vs-C11` thin-air edges. The CSRA test uses a
  *control*-dependency (literal-valued) OOTA shape, so herd7 can actually exhibit
  the C11 permission (`Sometimes`); the Weakestmo test uses a data-flow shape, so
  herd7 reports `Never` as a tool artefact (see those READMEs).

* **The survey research models have no herd7 `cat` model; their verdicts are
  cited.** The newer language-level models drawn from Moiseenko–Podkopaev–Koznov's
  *Survey of Programming Language Memory Models* (2021) and the primary papers —
  `BMM`, `RMMOA`, `CRC`, `JAM`, `OHMM`, `Weakestmo`, `CSRA`, `WJES`, `GOS`,
  `JSMM`, `RMC`, `RAO`, `TSC`, plus `sMRD`/`MRD` — are not bundled in herd7. Where
  a model coincides with a bundled one we check it through that model
  (`BMM ≡ TSO`, `RMMOA ≡ PSO`, both fully machine-run); where the C11/RC11 side is
  herd7-expressible we run that side and cite the research model
  (`RC11-vs-sMRD`, `CRC-vs-C11`, `C11-vs-WJES` TC7, `C11-vs-RMC`, `CSRA-vs-C11`).
  The remainder ship the litmus test plus a documented verdict cited to the
  model's own artifact, following the same convention as `MRD-vs-C11` and
  `C11-vs-Promising`. A few separations are *reasoning-guarantee* differences
  (external DRF) or transformation-soundness differences rather than single
  litmus outcomes (`C11-vs-GOS`, `C11-vs-RAO`, `C11-vs-TSC`, `Promising-vs-CSRA`
  direction 2); those READMEs say so explicitly.

* **`ARM ↔ POWER` and `ARMv8 ↔ RVWMO` coincide on the common instruction set.**
  herd7's `arm.cat`/`ppc.cat` (resp. `aarch64.cat`/`riscv.cat`) agree on every
  one of 60+ swept tests. Their incomparability is *instruction-level*: POWER has
  `lwsync`, RISC-V has `fence.tso`, with no exact counterpart on the other side.
  We ship those instruction-specific witnesses and explain the limitation.

* **IMM and Promising are not in herd7.** `RC11 ↔ IMM` and `C11 ↔ Promising` ship
  the litmus test plus a documented expected result and a pointer to the model's
  own artifact (the IMM Coq development / the Promising tool).

* **C++20 ↔ C11 — the release-sequence axis is now mechanised; the SC-repair axis
  is still modelled by its closest bundled fragment.** C++20 differs from C11 in two
  normative ways pulling in opposite directions (hence `incomparable/C++20-vs-C11`).
  The release-sequence weakening (P0982) is now checked against genuine per-version
  models — `cpp11.cat` / `cpp17.cat` / `cpp2w.cat` in [`models/cpp/`](models/cpp)
  (vendored from `gonzalobg/cpp_memory_model`): the *same* program flips verdict
  across the real models, in both directions (the all-atomic `mp-rs-add-est-atomic`
  is allowed under C++11/17 but forbidden under C++20, while `RS.litmus` is
  forbidden under C++11 but allowed — as a race — under C++20). This replaces the
  earlier `RS+cpp20.litmus` workaround that simulated C++20 inside the program. The
  `seq_cst` repair (P0668) is still modelled with `rc11.cat` (whose repaired SC
  C++20 adopted verbatim) vs `c11_orig.cat`, because the `cpp*` models all inherit
  RC11's repaired SC and so cannot exhibit the broken-SC behaviour C11 allows. C++20
  leaves thin-air unresolved, so it is strictly weaker than RC11
  (`strictly-weaker/RC11-vs-C++20`), checked on the same plain-LB shape as
  `RC11-vs-IMM`.

* **herd7 has no scoped architecture, so the GPU edges are modelled.** herd7's `-c11`
  knows nothing of memory scopes. For the *strictly-weaker* scoped edges
  (`C11 → OpenCL`, `C11 → CUDA`, `C11 → HRF`) we use the fact that a release/acquire
  narrowed to a scope the two threads do **not** share carries no happens-before —
  it is semantically `relaxed`. So the C11 (strong) side is checked directly under
  `-c11` (forbidden) and the scoped (weak) side is checked as its relaxed equivalent
  (allowed); each test header carries the genuine scoped source. The remaining GPU
  pairs are model-definition or feature-level differences with no herd7 model:
  `HRF → ScopedC11` (the exact-match vs inclusion scope rule),
  `PTX ↔ AMDGPU` and `OpenCL ↔ Vulkan` (different scope sets, cache qualifiers, and
  availability/visibility ops). These ship the litmus test plus documented verdicts,
  cited to the model's own artifact and the `memalloy` model-comparison tool.

## Reading a herd7 result

```
Observation <name> Never 0 N        # outcome FORBIDDEN (0 of N executions match)
Observation <name> Sometimes k N    # outcome ALLOWED   (k of N executions match)
```

## References

Authors, venues and DOIs for every model are in the `references` block of
[`../src/models.json`](../src/models.json). Each pair README cites the specific
paper for its test.
