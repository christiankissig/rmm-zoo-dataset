# Verifying edges with memalloy

[memalloy](https://github.com/johnwickerson/memalloy) (Wickerson, Batty, Sorensen
& Constantinides, *Automatically Comparing Memory Consistency Models*, POPL 2017)
**automates** the comparison the zoo otherwise does by hand: given two axiomatic
models it searches (via Alloy → SAT) for an execution that one model allows and the
other forbids, bounded by a number of events `N`. It either returns the **simplest
distinguishing litmus test** or finds **none up to `N` events**.

This is the tool behind the zoo's scoped-GPU verdicts. Edges whose verdict comes
from memalloy carry `"provenance": "memalloy"` in `models.json`
(`HRF → ScopedC11`, `PTX ↔ AMDGPU`, `OpenCL ↔ Vulkan`).

## The recipe (per edge type)

memalloy's comparator takes `-violates <STRONG>.cat -satisfies <WEAK>.cat`: it
looks for an execution that is **inconsistent under STRONG** but **consistent under
WEAK**. `-expect 1` asserts such a witness exists; `-expect 0` asserts none does up
to the bound.

| Zoo edge | Direction A (witness) | Direction B (containment) | Verdict |
|---|---|---|---|
| **strictly-weaker** `M → N` | `-violates M -satisfies N` → `expect 1` | `-violates N -satisfies M` → `expect 0` | strict order iff A finds a witness **and** B finds none up to `N` |
| **incomparable** `M ⋈ N` | `-violates M -satisfies N` → `expect 1` | `-violates N -satisfies M` → `expect 1` | incomparable iff a witness in **each** direction |
| **compilation** `M → H` (Q4) | `-arch <M> -arch2 <H> -mapping <map>.als` | — | sound iff no target execution breaks the source semantics |

Bump `-events` until the answer stabilises or the solver times out; record the bound.

## What is runnable with the base repo (and what is not)

memalloy bundles `.cat` models for **C11**, **OpenCL** (incl. `opencl_scoped`), and
**PTX**, plus the `opencl_ptx` / `opencl_amd` compiler mappings. So directly
reproducible:

- **`C11 → OpenCL`** (strictly-weaker): `c11_simp.cat` vs `opencl_scoped.cat`.
- **`OpenCL → PTX`**, **`OpenCL → AMDGPU`** (compilation, Q4): the bundled mappings.

**Not** runnable from the base repo — no standalone `.cat` model ships:
**AMD/HSA** (only a mapping target), **Vulkan**, **HRF**, **WebGPU/WGSL**, **Metal**.
The zoo's `PTX ↔ AMDGPU`, `OpenCL ↔ Vulkan`, and `HRF ↔ ScopedC11` verdicts come
from memalloy comparisons **using models authored outside the base repo** (the
Vulkan Alloy model, the HSA model, the HRF scope lattices — see those pairs'
READMEs and the POPL'17 paper §6). Re-running them requires obtaining or authoring
those `.als`/`.cat` models first (tracked as future work).

## Example commands

```sh
# Build (see "Environment" below), then from the memalloy checkout:

# C11 -> OpenCL, direction A: does scoped OpenCL allow an MP a flat C11 forbids?
./comparator -desc "c11_not_opencl_A" -arch OpenCL \
    -violates models/c11_simp.cat -satisfies models/opencl_scoped.cat \
    -events 7 -expect 1
# direction B (containment): is every C11 behaviour an OpenCL behaviour?
./comparator -desc "c11_not_opencl_B" -arch OpenCL \
    -violates models/opencl_scoped.cat -satisfies models/c11_simp.cat \
    -events 7 -expect 0

# OpenCL -> PTX compiler mapping (Q4):
./comparator -desc "compile_opencl_ptx" -arch OpenCL -arch2 PTX -fencerels \
    -violates models/opencl_scoped.cat -satisfies models/ptx_orig.cat \
    -mapping mappings/fences_as_relations/opencl_ptx.als \
    -events 5 -events2 5 -expect 0
```

A returned witness lands in `png/` and `xml/`; lift it to a `.litmus`/`.lit` and
drop it in the matching `litmus/.../<A>-vs-<B>/` directory next to the edge.

## Caveat: bounded, and (here) not a proof

"No witness up to `N` events" is **bounded-exhaustive evidence, not a proof**. The
six-event small-model theorem (Mador-Haim et al.) that *would* make the bound a
proof applies only to **multi-copy-atomic, architecture-level** models; the GPU
scoped models are neither, so a clean run yields "checked exhaustively up to `N`
events", with `N` recorded — stronger than a hand-picked one-sided test, but not a
theorem. memalloy also times out beyond ~8–15 events.

## Environment — use the Docker image (verified working)

memalloy targets an old stack (JDK 8, OCaml ~4.07, ant). Rather than fight host
versions, build the [`Dockerfile`](Dockerfile) here and run the comparator in it:

```sh
docker build -t memalloy-env -f Dockerfile .
git clone --recurse-submodules https://github.com/johnwickerson/memalloy
docker run --rm -v "$PWD/memalloy:/memalloy" -e LANG=C.UTF-8 memalloy-env bash -c '\
    make -C alloystar && make -C src ; \
    ./comparator -desc smoke -arch C -violates models/sc.cat \
      -satisfies models/c11_nodrf.cat -satisfies models/c11_normws.cat \
      -satisfies models/c11_onlysc.cat -events 4 -expect 1 '
```

This is **confirmed working**: Alloy\* builds (`alloystar/dist/alloy4.2.jar`), the
OCaml `comparator` builds, and the smoke comparison returns `Alloy found 1
solutions`. See the [`Dockerfile`](Dockerfile) header for the three gotchas
(`LANG=C.UTF-8`; ignore the `src` `doc`-target Python error; don't run the
top-level `make comparator`).

## Verified run: `OpenCL → PTX` is sound

This `compilation` edge is verified by an **actual memalloy run** (not just cited).
The Q4 mapping mode needs the `fences_as_relations` adaptation generated first; one
Python-2 leftover (`etc/adapt_mapping.py`) must be ported to Python 3:

```sh
# in the memalloy checkout, fix the one py2-ism:
sed -i 's/string\.replace(\(lines\[line_num\]\), before, after)/\1.replace(before, after)/' \
    etc/adapt_mapping.py
```

Then, in the container (image from the [`Dockerfile`](Dockerfile), which includes
Python):

```sh
make -C alloystar && make -C src && make -C archs && make -C mappings

# sound mapping -> expect NO counterexample:
./comparator -desc oclptx_sound -arch OpenCL -arch2 PTX -fencerels \
  -violates models/opencl_scoped.cat -satisfies models/ptx_orig.cat \
  -mapping mappings/fences_as_relations/opencl_ptx.als -events 4 -events2 6 -expect 0
#   => "Alloy found 0 solutions"   (sound up to 4 OpenCL / 6 PTX events)

# discrimination control: the KNOWN-BUGGY mapping -> expect a counterexample:
./comparator -desc oclptx_buggy -arch OpenCL -arch2 PTX -fencerels \
  -violates models/opencl_scoped.cat -satisfies models/ptx_cumul.cat \
  -mapping mappings/fences_as_relations/opencl_ptx_buggy.als -events 5 -events2 5 -expect 1
#   => "Alloy found 1 solutions"   (the check genuinely discriminates sound from buggy)
```

Both ran as shown; `OpenCL → PTX` is therefore tagged `provenance: memalloy` on the
strength of this run, with the bound recorded in the edge `note`.

## Status: what else is and isn't verified

* **The tool runs in Docker** — pipeline confirmed end-to-end, and the
  `OpenCL → PTX` mapping is verified as above.
* **The three edges tagged `provenance: memalloy` from prior work**
  (`HRF↔ScopedC11`, `PTX↔AMDGPU`, `OpenCL↔Vulkan`) are **not** re-run here: the base
  repo ships no standalone AMD/HSA, Vulkan, or HRF `.cat` model, so reproducing them
  needs those models obtained/authored first. Those tags record the **documented**
  memalloy verdicts (POPL'17 paper + the per-pair READMEs), not a re-run.
* **`OpenCL → AMDGPU`** is *not* runnable through the standard `comparator`
  interface: the AMD target is a bespoke Alloy model (`archs/amd_gpu.als`, with its
  own `Loc`/`Val` sigs), there is no AMD entry in the arch enum, no AMD `.cat`
  consistency model, and no AMD case in `tests.sh`. The POPL'17 OpenCL→AMD result
  (§6.1) used a custom harness, and it reports the *original* mapping was **unsound**.
  So this edge is left `provenance: literature`; verifying it would mean rebuilding
  that bespoke harness, and the real-world edge concerns the *corrected* compiler,
  not the original mapping memalloy refuted.
* **Bounded, not a proof** for these scoped models (no MCA small-model theorem) —
  record the event bound `N` with every result.
