# C11 <-> TSC  (incomparable)

The **Theory of Speculative Computation (TSC)** (Boudol & Petri, *A Theory of
Speculative Computation*, ESOP 2010) is a general framework for studying the
effect of speculation in a shared-memory setting, defined as a lambda/imperative
calculus whose only synchronisation primitive is an explicit `with ℓ do` lock.
It analyses speculation *abstractly* rather than proposing a concrete language
model. C11 and TSC are incomparable, but the separation is subtle and entirely
documented -- there is no herd7-runnable C11-vs-TSC litmus, because TSC has no
relaxed/release/acquire access modes to align with C11.

## Correction: thin-air does NOT separate them

TSC does **not** forbid out-of-thin-air. Speculation is unrestricted, so TSC
explicitly *permits* the self-fulfilling thin-air outcome (`LB+ctrl.litmus`,
citing the Java spec). C11 permits the same relaxed control-dependent LB. The
survey accordingly places TSC in the out-of-thin-air class (no-OOTA = "−"). So the
naive "C11 allows, TSC forbids OOTA" separation does not exist.

## The real asymmetry -- external DRF under speculation

TSC's sharpest difference from C11 is a *reasoning* property, not a litmus
outcome. Under unrestricted speculation TSC's **external DRF theorem fails**: a
program that is data-race-free under interleaving can still exhibit a non-SC
speculative outcome (Boudol & Petri give `p:=ff; if !p then q:=tt  ||  q:=ff; if
!q then p:=tt` reaching `p=tt=q`). The **internal** DRF theorem still holds. C11,
by contrast, forces every DRF program to behave sequentially consistently. TSC's
"restriction" is a program-side robustness property (speculatively-DRF programs
are robust), not a model-side ban on any behaviour. Because TSC is strictly more
general than most hardware models on one side and lacks C11's mode system on the
other, neither is a subset of the other.

## Running

Not machine-run in either direction: TSC is a speculation calculus with locks and
no C11-style access modes, so no single litmus adjudicates the two, and OOTA --
the one shape both express -- is allowed by both. `LB+ctrl.litmus` documents the
self-fulfilling speculative shape. All verdicts are **cited / model-level**.

**Reference:** Gérard Boudol, Gustavo Petri, *A Theory of Speculative
Computation*, ESOP 2010, doi:10.1007/978-3-642-11957-6_10. C11: Mark Batty et al.,
*Mathematizing C++ Concurrency*, POPL 2011, doi:10.1145/1926385.1926394. The
external/internal DRF distinction: Batty et al., *The Problem of Programming
Language Concurrency Semantics*, ESOP 2015, doi:10.1007/978-3-662-46669-8_12.
