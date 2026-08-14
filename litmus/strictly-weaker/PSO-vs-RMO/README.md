# PSO → RMO  (RMO is strictly weaker)

**Distinguishing behaviour:** load→store (and load→load) reordering.

PSO relaxes only store→store; loads still execute in program order. RMO, the
weakest SPARC model, additionally relaxes the load side. `LB.litmus` (load
buffering) needs each thread's load to be reordered past its store: `[R];po;[W]`
is preserved by PSO but not by RMO.

```sh
herd7 -model ../../models/abstract-pso.cat LB.litmus   # Never 0 3      (forbidden by PSO)
herd7 -model ../../models/abstract-rmo.cat LB.litmus   # Sometimes 1 3  (allowed by RMO)
```

RMO preserves only genuine dependencies; a `MEMBAR #LoadStore` (or a data/address
dependency) between the load and the store restores ordering. A companion
load→load variant, `MP+dmb.sy+po`, is described in `RMO-vs-Coherence` and the
abstract-model verification.

**Reference:** *The SPARC Architecture Manual, Version 9* (1994); Alglave,
*A Shared Memory Poetics* (2010).
