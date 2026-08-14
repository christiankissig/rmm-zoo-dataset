# C11 <-> RMC  (incomparable)

The **Relaxed Memory Calculus (RMC)** (Crary & Sullivan, *A Calculus for Relaxed
Memory*, POPL 2015) takes a different approach to ordering: instead of per-access
memory-order annotations, the programmer writes explicit **visibility** (`VEDGE` /
`vo`) and **execution** (`XEDGE` / `xo`) constraints in the source. The approach
is highly generic and subsumes C11's annotation lattice, but the underlying model
is very weak and permits thin-air (it proves only internal/SC-DRF). C11 and RMC
are incomparable: each constrains and relaxes things the other does not.

## Direction 1 -- C11 allows, RMC forbids: ordered message passing

`MP+relaxed.litmus` is relaxed message passing, stale-data outcome `r0=1 /\ r1=0`.
With all-relaxed C11 atomics there is no happens-before, so C11 **allows** it
(`herd7 -c11` => `Sometimes`). The same program written in RMC with a `VEDGE` from
the data write to the flag write and an `XEDGE` on the reader **forbids** the
stale read -- RMC's explicit edges impose ordering that C11's relaxed mode does
not. So RMC-with-edges rules out an outcome C11-all-relaxed admits.

## Direction 2 -- RMC allows, C11 forbids: model-level, no canonical litmus

RMC is "strictly more relaxed than any existing architecture": it admits
leapfrogging-write / write-forwarding and arbitrary speculation, with no
"weaker-than-relaxed" mode in C11 to express the resulting outcomes. This makes
RMC permit behaviours C11 forbids, but the literature states it at the model
level -- there is no single crisp litmus isolating one such outcome against C11 --
so this direction is documented rather than exhibited. (Out-of-thin-air does
**not** separate the two: both permit it.)

## Running

```sh
herd7 -c11 incomparable/C11-vs-RMC/MP+relaxed.litmus   # Observation MP+relaxed Sometimes 1 3
```

Only the C11 side of Direction 1 is machine-run (wired into `../../run.sh`). RMC
has no herd7 model -- it is a source-level calculus with its own type system and
operational semantics -- so its verdicts are cited.

**Reference:** Karl Crary, Michael J. Sullivan, *A Calculus for Relaxed Memory*,
POPL 2015, doi:10.1145/2676726.2676984. C11: Mark Batty et al., *Mathematizing
C++ Concurrency*, POPL 2011, doi:10.1145/1926385.1926394.
