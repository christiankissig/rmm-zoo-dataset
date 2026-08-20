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

Runnable after the fragment restriction below: **`TSO → ARMv8`** and
**`TSO → RVWMO`** (the latter against a model authored here).

**Not** runnable from the base repo — no standalone `.cat` model ships:
**AMD/HSA** (only a mapping target), **Vulkan**, **HRF**, **WebGPU/WGSL**, **Metal**.
The zoo's `PTX ↔ AMDGPU`, `OpenCL ↔ Vulkan`, and `HRF ↔ ScopedC11` verdicts come
from memalloy comparisons **using models authored outside the base repo** (the
Vulkan Alloy model, the HSA model, the HRF scope lattices — see those pairs'
READMEs and the POPL'17 paper §6). Re-running them requires obtaining or authoring
those `.als`/`.cat` models first (tracked as future work).

On **Vulkan** specifically, "obtain the model" turns out to be the easy half and
the wrong half. Khronos publishes an Alloy model of the Vulkan/SPIR-V memory
model — [`alloy/spirv.als`](https://github.com/KhronosGroup/Vulkan-MemoryModel/blob/main/alloy/spirv.als),
CC-BY-4.0, itself credited to the memalloy paper — but it is **not comparator
input**. It declares its own `sig Exec` with some forty fields for storage
classes, scopes, control barriers and the availability/visibility machinery, no
`co`, and program order as `immpo`; memalloy's comparator generates its Alloy
over `archs/exec.als` and the `Exec_*` hierarchy beneath it, which has nowhere
to put any of that. Using it means re-expressing the model over memalloy's
execution signature, or rebuilding the bespoke harness the POPL'17 paper used
for AMD — a port, not an acquisition. The same shape of obstacle as
`archs/amd_gpu.als`, which is already in the repo and already unusable through
the standard interface for exactly this reason.

## Running the suite

```sh
docker build -t memalloy-env -f Dockerfile .
git clone --recurse-submodules https://github.com/johnwickerson/memalloy
docker run --rm -v "$PWD/memalloy:/memalloy" -e LANG=C.UTF-8 memalloy-env \
    bash -c 'make -C alloystar && make -C src; make -C archs; make -C mappings'

MEMALLOY=$PWD/memalloy ./run.sh        # one PASS/FAIL line per checked claim
MEMALLOY=$PWD/memalloy ./run.sh -v     # also echo each invocation and its output
```

`make memalloy` runs it too, given `MEMALLOY=`. It is **not** folded into
`make check` the way the kater suite is: it needs a built checkout rather than
just a pulled image, and the containment cases take minutes rather than seconds.

Every case states the number of solutions it expects — `1` for a witness
direction, `0` for a containment direction — and the suite ends with two
**controls** that must find something: the known-buggy OpenCL→PTX mapping, and
the ARMv8/RVWMO non-containment. A containment run that is clean because the
search was broken would otherwise look exactly like one that is clean because
the containment holds.

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

**Fix it before `make -C mappings`, not after.** The Makefile does not check that
`adapt_mapping.py` succeeded, so with the py2 version in place it copies each
mapping into `fences_as_relations/` unadapted — leaving `open ../archs/exec_OpenCL`
where it should read `open ../../archs/fences_as_relations/exec_OpenCL`. The
comparator then dies well downstream with

```
Syntax error in mappings/fences_as_relations/opencl_ptx.als at line 1 column 1:
This module cannot be found. ... "mappings/archs/exec_OpenCL.als".
Fatal error: exception Failure("Alloy was unsuccessful.")
```

which says nothing about Python. If a mapping run fails that way, patch the
script and re-run `make -C mappings`: the stale adaptation is not rebuilt on its
own, since the target starts by removing and recreating the directory only when
it runs.

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

## Cross-ISA comparisons: the common Basic_HW fragment

`TSO → ARMv8` and `TSO → RVWMO` could not be run at all, for a reason that is
not about memalloy's search: the comparator takes **one** `-arch` for both
operands, `models/x86tso.cat` is tagged `"X86"` and `models/aarch64.cat` is
tagged `"ARM8"`, and the two models do not share a vocabulary of events. It is
the same obstacle kater hits on the identical pair.

memalloy does have a shared vocabulary — **`Basic_HW`**, tag `"HW"`,
`archs/exec_H.als` — carrying reads, writes, `po`, `rf`, `co`, `fr`, the three
dependency relations and `atom`, but no fences and no acquire/release
annotations. That is the common fragment, and restricting to it is what makes
the comparison well-posed instead of a category error.

[`derive-hw-fragment.sh`](derive-hw-fragment.sh) performs the restriction
mechanically, from the checkout's own models, and **the script is the record of
what the fragment is**. Every term it drops — `mfence`, `dmb`, `dmbld`,
`dmbst`, `isb`, `SCACQ`, `SCREL` — is *empty* on the fragment rather than
weakened away, so the derived models are exact restrictions, not approximations.
It is generated rather than committed because `models/x86tso.cat` is LGPL and
this dataset is BSD-3, the same reason `litmus/kater/derive-lkmm.sh` generates
its operand.

RVWMO has no source model to restrict: memalloy ships none. `models/zoo_hw_rvwmo.cat`
is **authored here**, directly from the thirteen `ppo` rules of the RVWMO chapter
of the RISC-V unprivileged spec, and annotates each rule it renders and each that
is empty on the fragment. As with a kater query, the result is about that
rendering. One independent check on it: over the same fragment it is contained in
the ARMv8 operand while ARMv8 is not contained in it, which is the direction the
same-address `ppo` rules predict.

Both edges are decided in both directions — witness at 4 events, containment
clean exhaustively to 7 — and both are recorded with that bound.

The fragment is also the **scope** of the claim. These runs decide the edges over
the common vocabulary, not over the full instruction sets; the models' fence and
annotation vocabularies are exactly where `ARMv8 ⋈ RVWMO` lives, and nothing here
touches that.

## Minimality of the witnesses

memalloy returns the *simplest* distinguishing execution, so it can also certify
that a hand-written witness is as small as one can be. For the two fragment
edges, searching at **3 events finds nothing** in the witness direction, and 4
events finds a witness — so `litmus/strictly-weaker/TSO-vs-ARMv8/LB.litmus` and
`litmus/strictly-weaker/TSO-vs-RVWMO/MP.litmus` are minimal, and are kept rather
than replaced: they are the literature-standard shapes, and nothing smaller
separates the models. (memalloy's own simplest witness for `TSO → ARMv8` is MP
rather than LB, at the same four events; the choice between them is
recognisability, not size.)

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
