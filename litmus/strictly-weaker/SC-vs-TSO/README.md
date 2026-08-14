# SC → TSO  (TSO is strictly weaker)

**Distinguishing behaviour:** store→load reordering (the *store buffer*).

`SB.litmus` is the classic store-buffering shape: each thread writes its own
location then reads the other's. SC forbids both reads returning the old value
(`0,0`); TSO allows it, because each write sits in a per-thread FIFO store buffer
and the load can be satisfied before the write drains to memory.

```sh
herd7 -model sc.cat     SB.litmus   # Observation SB Never 0 3      (forbidden)
herd7 -model x86tso.cat SB.litmus   # Observation SB Sometimes 1 3  (allowed)
```

The test is written in x86 assembly; `x86tso.cat` is herd7's validated x86-TSO
model.

**Reference:** Owens, Sarkar, Sewell, *A Better x86 Memory Model: x86-TSO*,
TPHOLs 2009; Sewell et al., *x86-TSO*, CACM 2010.
