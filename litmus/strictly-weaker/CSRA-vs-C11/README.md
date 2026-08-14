# CSRA -> C11  (C11 is strictly weaker)

> **Reclassified.** This edge was previously recorded as `C11 ↔ CSRA
> incomparable`. The primary source shows it is a strict order: CSRA is a subset
> of C11 by design. See the note in [`../../README.md`](../../README.md).

**CSRA** -- *A Concurrency Semantics for Relaxed Atomics that Permits Optimisation
and Avoids Thin-Air Executions* (Pichon-Pharabod & Sewell, POPL 2016) -- pairs a
POWER-inspired memory subsystem with per-thread event structures. Its authors are
explicit that it is a subset of C/C++11: "it would be desirable to have all the
behaviours of our memory model ... be admitted by C/C++11. The converse is not to
be expected, of course, as the point of our model is to exclude the thin-air
executions that C/C++11 allows" (§9). So the only outcomes separating the two are
out-of-thin-air ones C11 admits -- making C11 strictly weaker, like the sibling
`MRD-vs-C11`, `sMRD-vs-C11`, and `Weakestmo-vs-C11` edges.

## Direction -- C11 allows, CSRA forbids: out-of-thin-air

`LB-oota.litmus` is CSRA's **Example 2**: each thread writes 42 *only* in the
branch taken once it has already read 42 (`if (r1==42) y=42` and `if (r2==42)
x=42`). The outcome `r1=r2=42` is self-justifying thin-air.

* **C11 allows it** -- its relaxed atomics do not forbid the cyclic justification
  (this is the standard's own thin-air note).
* **CSRA forbids it** -- because the store `x=42` is in only one branch, CSRA's
  deordering cannot hoist it ahead of the read that guards it, so both reads can
  only observe 0.

(CSRA's *Example 1*, where the store appears in *both* branches, *is* allowed by
CSRA -- and also by C11. The two share one C11 candidate execution, so C11 cannot
tell Examples 1 and 2 apart; that indistinguishability is CSRA's motivation, but
it is not a CSRA-allows / C11-forbids case. There is no such reverse case.)

## Running

Because each guarded store writes a **literal** 42 (a *control* dependency, not a
data dependency), herd7 can actually construct this self-fulfilling cycle -- so the
C11 permission is genuinely **machine-exhibited**, not merely cited:

```sh
herd7 -c11 strictly-weaker/CSRA-vs-C11/LB-oota.litmus   # Observation LB-oota Sometimes 1 1  (C11 allows OOTA)
```

herd7 reports the state `0:r1=42; 1:r2=42`, confirming C11 admits the out-of-thin-
air outcome. CSRA has no herd7 `cat` model -- it is an event-structure semantics
with a POWER-like storage subsystem -- so its *forbidding* verdict is cited from
the paper (§2.1 Example 2). The C11 `Sometimes` side is wired into `../../run.sh`.

(Contrast the data-flow OOTA tests elsewhere in this tree -- e.g.
`Weakestmo-vs-C11`, `sMRD-vs-C11` -- where the thin-air value *flows* through the
store, so herd7 cannot build the execution and reports `Never` as a tool artefact.
Here the value is a literal, so herd7 builds it and the C11 verdict is real.)

**Reference:** Jean Pichon-Pharabod, Peter Sewell, *A Concurrency Semantics for
Relaxed Atomics that Permits Optimisation and Avoids Thin-Air Executions*, POPL
2016, doi:10.1145/2837614.2837616 (§2.1 Examples 1-3; §9 "Relation to C/C++11").
C11: Mark Batty et al., *Mathematizing C++ Concurrency*, POPL 2011,
doi:10.1145/1926385.1926394.
