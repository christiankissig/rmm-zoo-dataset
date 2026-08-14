# TSO → RVWMO  (RVWMO is strictly weaker)

**Distinguishing behaviour:** store→store reordering.

RISC-V's RVWMO is weaker than TSO: it allows the store→store (and load→load)
reorderings TSO forbids. `MP.litmus` is message passing with two plain stores;
the reader observing `y=1, x=0` requires the writer's stores to be seen out of
order.

```sh
herd7 -model ../../models/abstract-tso.cat MP.litmus   # Never 0 3      (forbidden by TSO)
herd7 -model riscv.cat                     MP.litmus   # Sometimes 1 3  (allowed by RVWMO)
```

`riscv.cat` is herd7's RVWMO model. A `fence w,w` (or full `fence rw,rw`) between
the writer's stores restores ordering. Note RISC-V *also* offers `fence.tso` and a
Ztso extension that recover full TSO — see `incomparable/ARMv8-vs-RVWMO`.

**Reference:** *The RISC-V Instruction Set Manual* (RVWMO chapter); Pulte,
Pichon-Pharabod, Kang, Lee, Hur, *Promising-ARM/RISC-V*, PLDI 2019.
