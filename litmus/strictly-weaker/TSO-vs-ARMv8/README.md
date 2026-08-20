# TSO → ARMv8  (ARMv8 is strictly weaker)

**Distinguishing behaviour:** load→store reordering (load buffering).

ARMv8 is multi-copy-atomic like TSO, but it relaxes far more program order. The
simplest separator is load buffering: each thread reads one location then writes
the other, and both reads return the *new* value `1`. This needs each thread's
load to be reordered after its store — `[R];po;[W]` is preserved by TSO but not by
ARMv8.

```sh
herd7 -model ../../models/abstract-tso.cat LB.litmus   # Never 0 3      (forbidden by TSO)
herd7 -model aarch64.cat                   LB.litmus   # Sometimes 1 3  (allowed by ARMv8)
```

`aarch64.cat` is herd7's official ARMv8 / AArch64 model. Adding a `DMB SY`
(or making the load a `LDAR`) between the load and the store re-establishes the
ordering.

**Minimality (memalloy).** Over the common `Basic_HW` fragment the comparator
finds no distinguishing execution at **3 events** and one at **4**, so this
witness is as small as a separator for this pair can be. The containment half is
clean exhaustively to 7 events. See [`litmus/memalloy/`](../../memalloy/) — the
comparator's own simplest witness here is MP rather than LB, at the same four
events; LB is kept for recognisability, not size.

**Reference:** Pulte, Flur, Deacon, French, Sarkar, Sewell, *Simplifying ARM
Concurrency*, POPL 2018.
