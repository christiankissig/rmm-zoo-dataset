# ARM ↔ POWER  (incomparable — at the instruction level)

ARM (here ARMv7, herd7's `arm.cat`) and POWER (`ppc.cat`) are both
non-multi-copy-atomic and very weak. Their incomparability is **not** visible on
plain accesses with dependencies.

## What the sweep shows

We generated matched test families for both architectures with `diycross7`
(2- and 3-thread cycles: `MP`, `LB`, `SB`, `WRC`, `ISA2`, `S`, `R`, `Z6`, `RSW`,
`PPOCA`, … with every dependency and full-fence variant — 60+ tests) and ran
each under its native model. **The two models agree on every test.** Over the
common instruction set, herd7's ARMv7 and POWER models are behaviourally
indistinguishable; the literature likewise treats them with essentially the same
`cat` skeleton differing only in fence definitions.

## The instruction-level witness — `SB+lwsync.litmus`

The real asymmetry is the *barrier instruction sets*. POWER has `lwsync`, a
cumulative *lightweight* barrier that orders `R→R, R→W, W→W` but **not** `W→R`.
ARMv7 has no such instruction: its only general barrier, `dmb`, is a full barrier
that also orders `W→R`.

```sh
herd7 -model ppc.cat SB+lwsync.litmus   # Sometimes 1 3  (POWER: lwsync doesn't stop store-buffering)
```

There is no ARMv7 program with `lwsync` to compare against, and the ARM analogue
(`SB+dmb`) is `Never`. So:

* POWER can express an ordering (store-buffering still allowed under a lightweight
  cumulative barrier) that ARMv7 cannot.
* Conversely ARMv7's only fence is at least as strong as anything ARMv7 can write,
  so it has no behaviour POWER lacks on the shared instruction set.

This instruction-set difference — not a reordering of plain accesses — is the
practical source of the "incomparable" label. (A fully formal two-sided witness
would require comparing the models over a common alphabet, which the two ISAs do
not share.)

**Reference:** Sarkar, Sewell, Alglave, Maranget, Williams, *Understanding POWER
Multiprocessors*, PLDI 2011; Alglave, Maranget, Sewell, *Herding Cats*,
TOPLAS 2014; Maranget, Sarkar, Sewell, *A Tutorial Introduction to the ARM and
POWER Relaxed Memory Models* (2012).
