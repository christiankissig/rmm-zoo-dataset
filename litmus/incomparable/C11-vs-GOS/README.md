# C11 <-> GOS  (incomparable)

**Generative Operational Semantics (GOS)** (Jagadeesan, Pitcher, Riely,
*Generative Operational Semantics for Relaxed Memory Models*, ESOP 2010) fixes the
JMM by constraining speculative execution with *stratification* conditions that
rule out thin-air values. It forbids out-of-thin-air (which C11 allows) and proves
the external DRF theorem (which C11 does not), so the two are incomparable.

## Direction 1 -- C11 allows, GOS forbids: out-of-thin-air

`LB-oota.litmus` is thin-air load buffering (`LB+datas`), outcome `r1=r2=1`. C11
permits it (no acyclicity on `rf ∪ dependency`). GOS forbids it: speculation must
be non-self-justifying and *initial*, and in the LB+data cycle the un-speculated
branch can only write 0, so the speculation never finalises.

## Direction 2 -- GOS allows / C11 forbids: a reasoning guarantee, not a litmus

The reverse direction is **not** a single runnable litmus outcome. GOS validates
store->store reordering, load->load elimination, and roach-motel reordering and
proves the **external DRF** theorem; C11 provides only internal DRF. GOS's own
separating examples for these transformations are stated against the *JMM* and use
locks, outside the C11 relaxed-atomics fragment, so there is no clean
GOS-over-C11 litmus that herd7 can exhibit. The honest statement of the second
direction is therefore the reasoning asymmetry (GOS: external DRF + extra sound
transformations; C11: neither) rather than a separating execution. This is why
the edge is recorded as incomparable with one runnable side.

## Running

```sh
herd7 -c11 incomparable/C11-vs-GOS/LB-oota.litmus   # Observation LB-oota Never 0 3
```

The `Never` is herd7's inability to construct an OOTA execution, not a C11
prohibition (C11 permits the outcome by its axioms). GOS has no herd7 model -- it
is an operational semantics defined in the paper -- so both its verdicts are
cited.

**Reference:** Radha Jagadeesan, Corin Pitcher, James Riely, *Generative
Operational Semantics for Relaxed Memory Models*, ESOP 2010,
doi:10.1007/978-3-642-11957-6_17. C11: Mark Batty et al., *Mathematizing C++
Concurrency*, POPL 2011, doi:10.1145/1926385.1926394. The thin-air problem and the
external/internal DRF distinction: Batty et al., *The Problem of Programming
Language Concurrency Semantics*, ESOP 2015, doi:10.1007/978-3-662-46669-8_12.
