# Java ↔ OCaml  (incomparable)

Both the Java Memory Model and the OCaml 5 memory model are **DRF-SC**: a
data-race-free program behaves sequentially consistently. They differ in how they
treat *racy* programs, and neither's racy semantics contains the other's.

## Shared baseline — both allow weak racy behaviour

`../../strictly-weaker/SC-vs-Java/SB.java` and `sb.ml` here are the same
store-buffering race in each language. Both exhibit the SC-forbidden `(0,0)`,
confirming both models are weaker than SC on racy code:

```sh
# Java
( cd ../../strictly-weaker/SC-vs-Java && javac SB.java && java SB )
# OCaml (>= 5.0)
ocaml sb.ml
# => rounds=2000000  (0,0) seen <many> times
#    => OCaml's model allows the SC-forbidden (0,0) for racy non-atomic accesses.
```

## The two incomparable directions (documented; no common checker)

There is no single tool that hosts both models, so the separating behaviours are
stated from the literature:

* **OCaml allows, Java forbids — bounded races vs. happens-before causality.**
  OCaml's racy non-atomic reads may return a *recent but stale* value with no
  happens-before justification; its guarantee is operational locality ("bounded
  in space and time"), not a causal-cycle prohibition. The JMM instead pins down
  a happens-before/causality order and a commitment semantics that disallows some
  of these uncommitted outcomes.

* **Java allows, OCaml forbids — out-of-thin-air.** The JMM is famously *unable*
  to cleanly forbid all OOTA executions (the causality rules are known to be
  flawed). OCaml's model **provably forbids OOTA**: a racy read always returns a
  value actually written to that location, so values cannot be forged. This
  memory-safety property is essential for a language with unboxed/pointer values.

Together these give behaviour in each model that the other rejects — hence
incomparable, despite the shared DRF-SC headline.

## Verifying rigorously

* OCaml: the model and its `herd`-style operational rules are in Dolan et al.; the
  multicore runtime here *exhibits* the racy behaviour but is not a model checker.
* Java: use [jcstress](https://github.com/openjdk/jcstress) for controlled
  stress testing; the causality test cases are JMM "causality test cases 1–20".

**Reference:** Dolan, Sivaramakrishnan, Madhavapeddy, *Bounding Data Races in
Space and Time*, PLDI 2018; Manson, Pugh, Adve, *The Java Memory Model*,
POPL 2005; JSR-133 causality test cases.
