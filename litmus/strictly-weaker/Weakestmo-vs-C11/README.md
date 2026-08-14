# Weakestmo -> C11  (C11 is strictly weaker)

> **Reclassified.** This edge was previously recorded as `C11 ↔ Weakestmo
> incomparable`. The primary source shows it is a strict order: Weakestmo is
> *stronger* than C11. See the note in [`../../README.md`](../../README.md).

**Weakestmo** (Chakraborty & Vafeiadis, *Grounding Thin-Air Reads with Event
Structures*, POPL 2019) grounds thin-air reads using event structures that encode
multiple conflicting executions. The authors place it precisely: it is "stronger
than C11 (which allows OOTA) and weaker than RC11," and the identity mapping from
weakRC11 to Weakestmo is correct (Theorem 5). Every behaviour Weakestmo admits is
a C11 behaviour, while C11 admits thin-air outcomes Weakestmo forbids -- so C11 is
strictly weaker, exactly like the sibling `MRD-vs-C11` and `sMRD-vs-C11` edges.

## Direction -- C11 allows, Weakestmo forbids: out-of-thin-air

`LB-oota.litmus` is the canonical thin-air load buffering (`LB+datas`), outcome
`r1=r2=42`. C11 permits it -- no acyclicity on `rf ∪ dependency`. Weakestmo forbids
it: the cyclic OOTA configuration is never justified in its event structure (the
self-justifying value has no write the construction is forced to provide).

A second, sharper witness in the same direction is the paper's **"random number
generator" (RNG)** example (§2.2, Fig. 2): a program whose only C11-consistent
extra outcome reads a value (`X=99`) out of nothing. C11 admits it; Weakestmo
discards the bogus extracted execution because the enabling load event is
*invisible*. Both witnesses point the same way: **there is no behaviour Weakestmo
allows that C11 forbids.**

## Running

This is a value-inventing thin-air outcome, so herd7 cannot construct it; the
verdicts are **cited, not machine-run**:

```sh
herd7 -c11 strictly-weaker/Weakestmo-vs-C11/LB-oota.litmus   # Observation LB-oota Never 0 4
```

The `Never` reflects herd7's inability to *build* an OOTA execution, not a C11
prohibition (C11 permits it by its axioms). Weakestmo has no herd7 `cat` model --
it is an event-structure semantics with its own mechanisation -- so its forbidding
verdict is cited.

**Reference:** Soham Chakraborty, Viktor Vafeiadis, *Grounding Thin-Air Reads with
Event Structures*, POPL 2019, doi:10.1145/3290383 (§2.1 placement between C11 and
RC11; §2.2 RNG / Fig. 2; §6.1 Theorem 5). C11: Mark Batty, Scott Owens, Susmit
Sarkar, Peter Sewell, Tjark Weber, *Mathematizing C++ Concurrency*, POPL 2011,
doi:10.1145/1926385.1926394. The thin-air problem: Batty et al., *The Problem of
Programming Language Concurrency Semantics*, ESOP 2015,
doi:10.1007/978-3-662-46669-8_12.
