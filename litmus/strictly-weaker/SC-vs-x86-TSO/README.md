# SC → x86-TSO  (x86-TSO is strictly weaker)

**Distinguishing behaviour:** store→load reordering (the *store buffer*).

Same store-buffering test as `SC-vs-TSO`, kept as a separate edge because
`models.json` lists `x86-TSO` (the *formal, hardware-validated* x86 model of
Sewell et al.) as a distinct node from the abstract `TSO`. `SB.litmus` is allowed
by x86-TSO and forbidden by SC.

```sh
herd7 -model sc.cat     SB.litmus   # Observation SB Never 0 3      (forbidden)
herd7 -model x86tso.cat SB.litmus   # Observation SB Sometimes 1 3  (allowed)
```

To restore SC on real x86 you place an `MFENCE` between the store and the load,
or use a `LOCK`-prefixed RMW; both add the `[W];po;[MFENCE];po;[R]` edge that
`x86tso.cat` treats as ordered.

**Reference:** Sewell, Sarkar, Owens, Zappa Nardelli, Myreen, *x86-TSO: A
Rigorous and Usable Programmer's Model for x86 Multiprocessors*, CACM 2010.
