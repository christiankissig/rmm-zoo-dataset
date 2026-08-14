# RC11 → C11  (C11 is strictly weaker)

**Distinguishing behaviour:** the broken SC semantics that RC11 repairs.

RC11 ("Repaired C11") is strictly stronger than the original C11: it fixes the
seq_cst axioms so that SC fences actually behave sequentially. The original C11
allowed an IRIW-shaped execution *even with an `seq_cst` fence between the two
reads on each observer* — an anomaly RC11 forbids.

`IRIW+scfences.litmus`: two writers (`x=1`, `y=1`, relaxed); two observers, each
reading the two variables in opposite order with an
`atomic_thread_fence(seq_cst)` in between. The outcome where the observers
disagree on the store order is the repaired behaviour:

```sh
herd7 -model rc11.cat     IRIW+scfences.litmus   # Never 0 15      (RC11 forbids)
herd7 -model c11_orig.cat IRIW+scfences.litmus   # Sometimes 1 15  (original C11 allows)
```

`c11_orig.cat` is herd7's encoding of the original (pre-repair) C11 model;
`rc11.cat` is the repaired model. This is precisely the class of bug Lahav et al.
set out to remove.

**Reference:** Lahav, Vafeiadis, Kang, Hur, Dreyer, *Repairing Sequential
Consistency in C/C++11*, PLDI 2017.
