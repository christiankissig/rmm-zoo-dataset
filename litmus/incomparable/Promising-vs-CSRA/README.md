# Promising <-> CSRA  (incomparable)

The **Promising Semantics** (Kang et al., POPL 2017) and **CSRA** -- *A Concurrency
Semantics for Relaxed Atomics that Permits Optimisation and Avoids Thin-Air
Executions* (Pichon-Pharabod & Sewell, POPL 2016) -- are both thin-air-free C/C++
relaxed models on different machines: Promising uses timestamps/promises/
certification; CSRA pairs a POWER-like (non-multi-copy-atomic) memory subsystem
with per-thread event structures. Neither supports SC accesses, so an SC litmus
cannot separate them. The survey classes both as semantic-dependency preserving
and the two are incomparable -- though only one direction has a concrete published
program.

## Direction 1 -- CSRA allows, Promising forbids: relaxed-RMW load buffering

`LB+FADD.litmus` is the relaxed fetch-and-add load-buffering of *Bridging the Gap*
(Podkopaev et al., POPL 2019) Example 3.10, target `a=1 /\ b=1 /\ c=0`. CSRA
**allows** it -- its POWER-like storage admits the full load-buffering family and
it supports RMWs (CSRA §8). Promising **1.0 forbids** it: the `y=1` promise fails
certification under future-memory quantification (the documented PS-1.0->ARMv8 RMW
unsoundness). Note Promising **2.0** repairs the RMW case, so against PS-2.0 this
particular separation narrows.

## Direction 2 -- Promising allows, CSRA forbids: transformation-level only

This direction rests on the survey's transformation profiles, not a published
program: Promising 2.0 validates **register promotion** and **global value-range
analysis** (Lee et al., PLDI 2020) that CSRA does not establish. The literature
asserts `PS ⊄ CSRA` via these *global* transformations but gives **no concrete
separating litmus** -- a witness would have to be constructed and run against both
artifacts. This direction is documented as transformation-level only.

## Running

Neither model is a herd7 `cat` model, so neither side is exhibited in herd7; the
verdicts are **cited**, to be reproduced in each model's own artifact (and the
Direction-2 separation is transformation-level, with no runnable program). The
`LB+FADD.litmus` file documents the Direction-1 shape.

**Reference:** Jean Pichon-Pharabod, Peter Sewell, *A Concurrency Semantics for
Relaxed Atomics that Permits Optimisation and Avoids Thin-Air Executions*, POPL
2016, doi:10.1145/2837614.2837616 (§8 Power/ARM behaviour, RMWs). Jeehoon Kang et
al., *A Promising Semantics for Relaxed-Memory Concurrency*, POPL 2017,
doi:10.1145/3009837.3009850; Sung-Hwan Lee et al., *Promising 2.0: Global
Optimizations in Relaxed-Memory Concurrency*, PLDI 2020, doi:10.1145/3385412.3386010.
The RMW-certification separation: Anton Podkopaev, Ori Lahav, Viktor Vafeiadis,
*Bridging the Gap between Programming Languages and Hardware Weak Memory Models*,
POPL 2019, doi:10.1145/3290382 (Example 3.10).
