# RMO → Alpha  (DEC Alpha is strictly weaker)

**Distinguishing behaviour:** relaxing an *address dependency* between two loads.

SPARC RMO preserves genuine address/data/control dependencies: an
address-dependent load is ordered after the load that produces its address.
DEC Alpha is the one commodity architecture that does **not** — a dependent load
may read a stale value unless an explicit `mb`/`wmb` barrier separates the two
loads. This dependent-load relaxation is Alpha's defining feature and the
historical reason Linux needed `smp_read_barrier_depends()` / RCU barriers.

`MP+dmb+addr.litmus` is message passing with a **fenced writer** and an
**address dependency on the reader** (`r0 = y; r2 = x[address depends on r0]`):

* Writer: `x=1; DMB; y=1` (the full fence fixes the store order in both models).
* Reader: `r0 = y; r2 = x[address depends on r0]`.

Getting `1:X0=1, 1:X2=0` requires the address-dependent second load to be
satisfied before the first. RMO forbids it (the dependency is preserved); Alpha
allows it (dependencies carry no ordering).

```sh
herd7 -model ../../models/abstract-rmo.cat   MP+dmb+addr.litmus   # Never 0 3      (RMO)
herd7 -model ../../models/abstract-alpha.cat MP+dmb+addr.litmus   # Sometimes 1 3  (Alpha)
```

Observed (herdtools7): RMO `Never 0 3`, Alpha `Sometimes 1 3` — machine-run.

**Containment.** Alpha relaxes strictly more than RMO on two independent axes and
no less on any: (i) dependency preservation — RMO preserves addr/data/ctrl, Alpha
preserves none; (ii) store atomicity — RMO is multi-copy-atomic, Alpha is not. So
every Alpha-forbidden behaviour is RMO-forbidden (RMO ⊇ Alpha as a set of allowed
executions) and the witness above shows the containment is strict. This is the
`litmus`-tier monotonicity argument used elsewhere in the zoo (e.g.
`TSO-vs-ARMv8`, `PSO-vs-POWER`): a genuine strict order, argued by monotonicity
and corroborated by a witness, not an independently proven theorem.

## The abstract Alpha cat model

herd7 ships no Alpha model, so `../../models/abstract-alpha.cat` is a small,
portable one written in the generic Herding-Cats relations. It keeps
SC-per-location and no-thin-air, sets preserved program order to **empty** (no
dependency is globally ordered — the Alpha relaxation), takes cross-location
ordering only from `mb`/`wmb` fences, and uses the propagation/observation
decomposition rather than a single global happens-before (Alpha is
non-multi-copy-atomic). Sanity checks: `MP+dmb+dmb` is `Never` (barriers work),
plain `MP` is `Sometimes` (weak), `LB` shows no thin air.

**Reference:** Alglave, Maranget & Tautschnig, *Herding Cats: Modelling,
Simulation, Testing, and Data Mining for Weak Memory*, TOPLAS 2014, **p.18**
(Alpha uniquely relaxes dependent-load ordering); *The SPARC Architecture Manual,
Version 9* (1994) for RMO's dependency preservation; *Alpha Architecture Reference
Manual* for the `mb`/`wmb` barriers.
