# TSO -> RMMOA  (RMMOA is strictly weaker)

**RMMOA** -- *Relaxed Memory Models: an Operational Approach* (Boudol & Petri,
POPL 2009) -- gives an operational semantics for relaxed memory built on an
abstract machine with a main memory and a **hierarchy of store buffers** in which
writes to *different locations* may propagate to memory **out of order**. That is
exactly the SPARC PSO store->store relaxation, and the authors prove the external
DRF theorem. The `PSO -> RMMOA` edge in `models.json` is `equivalent`: RMMOA and
PSO coincide on this relaxation. TSO, by contrast, keeps W->W in program order,
so TSO is strictly stronger -- it forbids the store-store reordering RMMOA permits.

## Direction -- RMMOA allows, TSO forbids: store->store reordering (MP)

`MP.litmus` is message passing with two plain stores on the writer (`x` then `y`)
and two plain loads on the reader (`y` then `x`). The outcome `1:r0=1 /\ 1:r1=0`
(the reader sees the flag `y=1` but the stale `x=0`) requires the writer's two
stores to reach memory out of program order. TSO forbids it: its preserved
program order includes W;po;W. RMMOA allows it: its per-location buffers let the
store to `y` drain to memory before the store to `x`.

## Running

RMMOA has no dedicated herd7 model, but it coincides with PSO on this relaxation,
so it is checked through the portable `models/abstract-pso.cat`; TSO through
`models/abstract-tso.cat`:

```sh
herd7 -model models/abstract-tso.cat strictly-weaker/TSO-vs-RMMOA/MP.litmus   # Observation MP Never 0 3      (TSO forbids)
herd7 -model models/abstract-pso.cat strictly-weaker/TSO-vs-RMMOA/MP.litmus   # Observation MP Sometimes 1 3  (RMMOA allows)
```

Both are wired into `../../run.sh`.

**Reference:** Gérard Boudol, Gustavo Petri, *Relaxed Memory Models: An
Operational Approach*, POPL 2009, doi:10.1145/1480881.1480930. The SPARC PSO
definition: *The SPARC Architecture Manual, Version 9*, Prentice Hall 1994.
