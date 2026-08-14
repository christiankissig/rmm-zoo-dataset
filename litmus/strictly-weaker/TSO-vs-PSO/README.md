# TSO → PSO  (PSO is strictly weaker)

**Distinguishing behaviour:** store→store reordering to different addresses.

PSO extends TSO by letting a thread's writes to distinct locations drain from the
store buffer out of program order. `MP.litmus` is message passing with two plain
stores on the writer and two plain loads on the reader: the reader sees the
"flag" `y=1` but the "data" `x=0`, which requires the writer's two stores to be
observed out of order.

```sh
herd7 -model ../../models/abstract-tso.cat MP.litmus   # Never 0 3      (forbidden: TSO keeps W;W)
herd7 -model ../../models/abstract-pso.cat MP.litmus   # Sometimes 1 3  (allowed)
```

The two abstract models differ only in whether `[W];po;[W]` is in preserved
program order. On real SPARC PSO an `STBAR` (store barrier) between the two
writes restores the TSO behaviour.

**Reference:** *The SPARC Architecture Manual, Version 8* (1992); Alglave,
*A Shared Memory Poetics* (PhD thesis, 2010).
