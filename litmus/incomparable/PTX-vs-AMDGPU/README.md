# PTX ↔ AMD GPU  (incomparable — at the feature level)

NVIDIA's PTX model and AMD's HSA-based GPU model are both scoped
release-consistency ISA models, and on their **common** feature set — plain
scoped release/acquire synchronisation — they coincide. Their incomparability is
**feature-level**, exactly like `incomparable/ARM-vs-POWER`: each ISA exposes
ordering machinery the other has no counterpart for.

## The shared shape — `MP+scoped.litmus`

A release/acquire message pass at a scope the two threads share is forbidden in
both models; narrowed below the shared scope it is allowed in both. No separation
lives here — this is the agreement baseline.

## The two feature-specific witnesses

* **PTX allows, AMD cannot express it.** PTX has the `.cta` / `.cluster` thread
  scopes and *proxy* fences (`membar.proxy`, `fence.proxy.alias`) that order
  accesses made through different memory *proxies* (generic vs surface/texture).
  AMD's model has no proxy notion, so this PTX-specific ordering has no AMD
  analogue.

* **AMD allows, PTX cannot express it.** AMD/HSA loads and stores carry
  cache-control qualifiers — `.glc` (globally coherent), `.slc`/`.dlc` (system /
  device-level coherent) — and split scopes into `work_group` / `agent` /
  `system`. These qualifiers order cache traffic in ways PTX's scope-only model
  does not name.

As with ARM/POWER, a fully formal two-sided witness would require a common
alphabet the two ISAs do not share; the separation is the asymmetry of their
ordering primitives, not a reordering of plain accesses.

## What is and isn't machine-checked

herd7 ships neither the PTX nor the AMD model. The PTX model is formalised and
machine-checked by Lustig et al. (an Alloy/`herd`-style artifact accompanies the
paper); both GPU models — and precisely this kind of cross-model separation — were
compared mechanically with the **memalloy** tool
(<https://github.com/johnwickerson/memalloy>) by Wickerson et al. The shared shape
above is shown in herd7 with relaxed atomics; the feature witnesses are cited.

**Reference:** Lustig, Sahasrabuddhe, Giroux, *A Formal Analysis of the NVIDIA PTX
Memory Consistency Model*, ASPLOS 2019 (DOI 10.1145/3297858.3304043); Wickerson,
Batty, Sorensen, Constantinides, *Automatically Comparing Memory Consistency
Models*, POPL 2017 (DOI 10.1145/3009837.3009838); Alglave et al., *GPU
Concurrency: Weak Behaviours and Programming Assumptions*, ASPLOS 2015; Gaster,
Hower, Howes, *HRF-Relaxed*, ACM TACO 2015 (the HSA/AMD scope framework).
