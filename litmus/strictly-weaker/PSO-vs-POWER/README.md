# PSO → POWER  (POWER is strictly weaker)

> **Reclassified** from `incomparable` to `strictly_weaker` based on the evidence
> below; `models.json` now records `PSO → POWER`.

**Distinguishing behaviour — POWER allows, PSO forbids:** load→load reordering.

`MP+sync+po.litmus` fences the writer (so its two stores are ordered in both
models) and leaves the reader's two loads plain. Observing `y=1, x=0` then
requires the reader to reorder its loads:

```sh
herd7 -model ../../models/abstract-pso.cat MP+sync+po.litmus   # Never 0 3      (PSO: loads stay ordered)
herd7 -model ppc.cat                       MP+sync+po.litmus   # Sometimes 1 3  (POWER: loads reorder)
```

This is exactly a strictly-weaker witness: the outcome is allowed by the weaker
model (POWER) and forbidden by the stronger one (PSO).

## Why this edge was reclassified: the *other* direction has no witness

We searched for a PSO-allowed / POWER-forbidden behaviour by running
`abstract-pso.cat` and `ppc.cat` over the standard litmus families (`SB`, `MP`,
`LB`, `2+2W`, `S`, `R`, `WRC`, `ISA2`, with dependency and fence variants) and
found **none**. Every behaviour PSO permits, POWER also permits:

* PSO relaxes only `W→R` (store buffer) and `W→W`; POWER relaxes those *plus*
  `R→R` and `R→W`, and is additionally non-multi-copy-atomic.
* So PSO's set of allowed reorderings is a subset of POWER's.

Empirically, then, **PSO ⊆ POWER** (PSO is strictly *stronger*), so the
`models.json` edge is typed `strictly_weaker` (PSO → POWER). The remaining
theoretical wrinkle is that the two models are defined over different instruction
sets (SPARC `MEMBAR`/`STBAR` vs POWER `sync`/`lwsync`), so a purely formal
"incomparable over disjoint alphabets" reading is defensible — but there is no
*behavioural* witness for the PSO-allows/POWER-forbids direction.

**Reference:** *SPARC Architecture Manual v8/v9*; Sarkar et al., *Understanding
POWER Multiprocessors*, PLDI 2011; Alglave et al., *Herding Cats*, TOPLAS 2014.
