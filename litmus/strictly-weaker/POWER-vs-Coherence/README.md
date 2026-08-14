# POWER → Coherence  (bare coherence is strictly weaker)

**Distinguishing behaviour:** ignoring an address dependency.

POWER is a very weak hardware model, but it still enforces per-location coherence
and preserves genuine dependencies. Bare coherence preserves neither across
locations. `MP+sync+addr.litmus` uses a `sync`-fenced writer and an
address-dependent reader (`r1 = y; r2 = x[addr dep on r1]`):

```sh
herd7 -model ppc.cat                             MP+sync+addr.litmus   # Never 0 3      (POWER)
herd7 -model ../../models/abstract-coherence.cat MP+sync+addr.litmus   # Sometimes 1 3  (Coherence)
```

`r1=1, r2=0` is allowed by bare coherence and forbidden by POWER. Same shape as
`RMO-vs-Coherence` / `ARM-vs-Coherence`, in PPC assembly with `lwzx` providing the
address-dependent load.

**Reference:** Sarkar, Sewell, Alglave, Maranget, Williams, *Understanding POWER
Multiprocessors*, PLDI 2011; Adve & Hill, ISCA 1990.
