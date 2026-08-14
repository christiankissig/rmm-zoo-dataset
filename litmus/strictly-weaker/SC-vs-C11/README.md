# SC → C11  (C11 is strictly weaker)

**Distinguishing behaviour:** store→load reordering of `memory_order_relaxed`
atomics.

C11 guarantees SC only for data-race-free programs that use `seq_cst` atomics
(the DRF-SC theorem). With `relaxed` atomics it permits the store-buffering
outcome that SC forbids. `SB-relaxed.litmus` is the store-buffering shape with all
four accesses `relaxed`.

```sh
# SC: apply the portable abstract SC model to the C events
herd7 -model ../../models/abstract-sc.cat SB-relaxed.litmus   # Never 0 3      (forbidden)
# C11: herd7's built-in C11 model
herd7 -c11                                SB-relaxed.litmus   # Sometimes 1 3  (allowed)
```

Promoting the accesses to `memory_order_seq_cst` makes the outcome disappear
under `-c11` too — that is exactly the DRF-SC guarantee, i.e. the edge collapses
for the SC-atomic fragment.

**Reference:** Batty, Owens, Sarkar, Sewell, Weber, *Mathematizing C++
Concurrency*, POPL 2011; Boehm & Adve, *Foundations of the C++ Concurrency Memory
Model*, PLDI 2008.
