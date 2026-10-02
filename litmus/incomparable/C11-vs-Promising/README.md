# C11 ↔ Promising  (incomparable)

This edge is about **PS 1.0** (Kang et al., POPL 2017), the `Promising` node.
PS 2.0 (`Promising2`) is its own node and has no edge to C11 yet.

Promising Semantics is an *operational* relaxed-memory model (threads may make a
"promise" to write a value in the future and must later certify it). It is not a
herd7 `cat` model, so neither side is exhibited in herd7 here; results are cited.

## Direction 1 — C11 allows, Promising forbids: out-of-thin-air

C11's text fails to forbid thin-air reads; Promising **forbids** them, because a
promised write must be *certified* by a thread-local execution that produces the
value without already assuming it — a circular thin-air value can never be
certified. `LB-oota.litmus` is the canonical thin-air load buffering (`r1=r2=42`
out of nothing):

```sh
herd7 -c11 LB-oota.litmus    # Never 0 4  -- NOT a verdict: herd7 cannot construct OOTA
# C11:        allowed  (the thin-air problem; ISO C11 axioms)
# Promising:  forbidden (Kang et al. 2017) -- run in the Promising artifact
```

(As in `../../strictly-weaker/MRD-vs-C11`, herd7 reporting `Never` here only means
it cannot *build* an OOTA execution, not that C11 forbids it.)

## Direction 2 — Promising allows, C11 forbids: optimisation-justified behaviour

Promising was designed to be sound for a *larger* set of compiler optimisations
than the C11 axioms permit. Its promise mechanism legitimises certain
read-after-write and reordering outcomes (e.g. results of redundant-load
elimination across relaxed atomics) that the per-execution C11
model rejects. These are the behaviours Promising adds in the other direction,
making the two genuinely incomparable rather than one a subset of the other.

## Running Promising

The Coq model and an executable checker are at
<https://github.com/snu-sf/promising-coq> (PS 1.0) and
<https://github.com/snu-sf/promising2> (PS 2.0). The thin-air and
optimisation-soundness litmus tests are worked through in the papers.

**Reference:** Kang, Hur, Lahav, Vafeiadis, Dreyer, *A Promising Semantics for
Relaxed-Memory Concurrency*, POPL 2017; Lee, Cho, Podkopaev, Chakraborty, Hur,
Lahav, Vafeiadis, *Promising 2.0*, PLDI 2020.
