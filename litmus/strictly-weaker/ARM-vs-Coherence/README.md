# ARM → Coherence  (bare coherence is strictly weaker)

**Distinguishing behaviour:** ignoring an address dependency.

ARM (like every real architecture) enforces per-location coherence *and*
preserves address/data/control dependencies. Bare coherence does neither across
locations. `MP+dmb+addr.litmus` is the message-passing test with a fenced writer
and an address dependency on the reader (`r1 = y; r2 = x[addr dep on r1]`):

```sh
herd7 -model arm.cat                             MP+dmb+addr.litmus   # Never 0 3      (ARM)
herd7 -model ../../models/abstract-coherence.cat MP+dmb+addr.litmus   # Sometimes 1 3  (Coherence)
```

`r1=1, r2=0` is allowed by bare coherence (dependencies are invisible to it) and
forbidden by ARM (the address dependency orders the two reads). This is the same
shape as `RMO-vs-Coherence` and `POWER-vs-Coherence`, written in ARMv7 assembly.

**Reference:** Adve & Hill, *Weak Ordering — A New Definition*, ISCA 1990;
Alglave et al., *Herding Cats*, TOPLAS 2014.
