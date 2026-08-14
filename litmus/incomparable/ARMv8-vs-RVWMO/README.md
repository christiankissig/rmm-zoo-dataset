# ARMv8 ↔ RVWMO  (incomparable — at the instruction level)

ARMv8 (`aarch64.cat`) and RISC-V RVWMO (`riscv.cat`) are both multi-copy atomic
and were designed to be close — RVWMO's preserved-program-order was modelled on
ARMv8's. Their incomparability does not show up on plain accesses.

## What the sweep shows

The same `diycross7` sweep used for ARM/POWER (60+ matched 2-/3-thread tests with
all dependency and fence variants) was run under `aarch64.cat` and `riscv.cat`.
**The two models agree on every test.** On the common instruction set they are
behaviourally indistinguishable here.

## The instruction-level witness — `SB+fence.tso.litmus`

RISC-V provides `fence.tso`, a single fence with exactly TSO semantics: it orders
`R→R, R→W, W→W` but **not** `W→R`. ARMv8 has no single instruction with that
precise semantics (its `DMB SY` is a full barrier; acquire/release are RCsc).

```sh
herd7 -model riscv.cat SB+fence.tso.litmus   # Sometimes 1 3  (RVWMO: fence.tso permits store-buffering)
```

So RVWMO can express a store-buffering-permitting fence that ARMv8 cannot name.
The two architectures also differ in their atomics annotations (ARMv8 LDAR/STLR
are RCsc; RISC-V `.aq/.rl` and the `lr/sc` pairing differ), another instruction-
level source of incomparability. As with ARM/POWER, the separation is in what
each ISA can *say*, not in how plain accesses reorder.

**Reference:** *RISC-V Unprivileged ISA*, RVWMO chapter; Pulte, Pichon-Pharabod,
Kang, Lee, Hur, *Promising-ARM/RISC-V*, PLDI 2019; Pulte et al., *Simplifying ARM
Concurrency*, POPL 2018.
