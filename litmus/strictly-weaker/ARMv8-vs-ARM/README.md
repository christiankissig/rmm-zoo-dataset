# ARMv8 → ARM (ARMv7)  (ARMv7 is strictly weaker)

**Distinguishing behaviour:** non-multi-copy-atomic store propagation.

ARMv7's model is *non*-multi-copy-atomic: one thread can observe a store before
another thread does. ARMv8 was deliberately strengthened to be multi-copy atomic
(stores become visible to all observers at once). The separator is the WRC
("write-to-read causality") shape with address dependencies that rule out local
reordering, so the only way to get the target outcome is non-atomic store
propagation:

* P0 writes `x=1`.
* P1 reads `x=1`, then (address-dependent) writes `y=1`.
* P2 reads `y=1`, then (address-dependent) reads `x` — and gets `0`.

P2 seeing `y=1` but `x=0` means P0's write to `x` had *not* propagated to P2 even
though it had propagated to P1 and P1's dependent write reached P2.

Because herd7's `arm.cat` (ARMv7) and `aarch64.cat` (ARMv8) use different
assembly syntaxes, the test is given in both forms:

```sh
herd7 -model arm.cat     WRC+addrs.arm.litmus       # Sometimes 1 7  (ARMv7 allows: non-MCA)
herd7 -model aarch64.cat WRC+addrs.aarch64.litmus   # Never 0 7      (ARMv8 forbids: MCA)
```

(An `IRIW+addrs` four-thread test separates them the same way.)

**Reference:** Pulte, Flur, Deacon, French, Sarkar, Sewell, *Simplifying ARM
Concurrency: Multicopy-atomic Axiomatic and Operational Models for ARMv8*,
POPL 2018; Alglave, Maranget, Sarkar, Sewell, *Understanding POWER
Multiprocessors* / *Herding Cats* for the non-MCA framing.
