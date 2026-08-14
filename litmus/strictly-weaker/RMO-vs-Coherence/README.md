# RMO → Coherence  (bare coherence is strictly weaker)

**Distinguishing behaviour:** ignoring an address dependency (while still
respecting per-location coherence).

Cache coherence only requires that writes to a *single* location are seen in one
order by everyone; it constrains nothing across locations — not even
dependencies. RMO is much stronger: it preserves genuine address/data/control
dependencies. `MP+addr.litmus` separates them with a *dependency-respecting,
thin-air-free* test:

* Writer: `x=1; DMB; y=1` (fence fixes the store order in both models).
* Reader: `r1 = y; r2 = x[address depends on r1]`.

Getting `r1=1, r2=0` requires the address-dependent second load to be satisfied
before the first — RMO forbids this (the dependency is preserved), bare coherence
allows it (dependencies mean nothing).

```sh
herd7 -model ../../models/abstract-rmo.cat       MP+addr.litmus   # Never 0 3      (RMO)
herd7 -model ../../models/abstract-coherence.cat MP+addr.litmus   # Sometimes 1 3  (Coherence)
```

> **Why not a thin-air / `LB+deps` test?** The cleanest theoretical separator is a
> dependency *cycle* (out-of-thin-air), but herd7 cannot exhibit OOTA executions
> (it never invents the value). `MP+addr` gives a genuinely observable separation
> using only real stored values. The same test separates ARM and POWER from
> coherence (next two directories).

**Reference:** Adve & Hill, *Weak Ordering — A New Definition*, ISCA 1990;
Alglave, Maranget, Tautschnig, *Herding Cats*, TOPLAS 2014 (for the `cat`
treatment of coherence and dependencies).
