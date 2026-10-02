# Promising <-> Weakestmo  (incomparable)

The **Promising Semantics** (Kang et al., POPL 2017) and **Weakestmo** (Chakraborty
& Vafeiadis, POPL 2019) are both thin-air-free relaxed-memory models, but built on
very different machines: Promising uses per-message timestamps with future
promises and certification; Weakestmo uses event structures that encode multiple
conflicting executions. The Weakestmo paper states the relationship directly --
"weakestmo and PS are incomparable" (§4.3) -- and gives a concrete witness in each
direction.

## Direction 1 -- Promising allows, Weakestmo forbids: an incoherent cycle

`Coh-CYC.litmus` is the paper's Fig. 3 three-thread program; the target outcome is
a coherence cycle. Promising **allows** it: per-message timestamps let the
certification of a write pick a *smaller* timestamp than a later use, producing an
incoherent cycle the paper itself calls "dubious ... not observable on any
machine." Weakestmo **forbids** it: it records a modification order in the event
structure and rejects the incoherent configuration.

## Direction 2 -- Weakestmo allows, Promising forbids: RMW load buffering (FADD)

`FADD.litmus` is the paper's Fig. 6: a load-buffering shape through a relaxed
fetch-and-add. Weakestmo (and ARMv8 hardware) **allow** it. Promising **forbids**
it: realising `Y=1` requires *promising* `Y=1`, but the promise cannot be
certified under every future memory (one in which `Z` already holds a large value
forces a different `Y`). This is exactly the unsoundness that forced a `dmb.ld`
after every RMW in the Promising->ARMv8 compilation (Podkopaev et al., POPL 2019).

Because each model allows a behaviour the other forbids, they are incomparable.

This edge is about **PS 1.0**, the model the Weakestmo paper compares against.
PS 2.0 (`Promising2`, Lee et al., PLDI 2020) added *reservations* to fix the
RMW mapping problem that FADD exposes, so its compilation to ARMv8 needs no extra
fence after RMWs. Whether Direction 2 still separates PS 2.0 from Weakestmo is
not established, so `Promising2` has no edge to Weakestmo.
(Orthogonally, the survey notes Promising 1.0 lacks SC accesses while Weakestmo
supports them -- a feature gap -- but FADD and Coh-CYC are the clean behavioural
witnesses.)

## Running

Neither model is a herd7 `cat` model (Promising is operational with promises/
certification; Weakestmo is an event-structure model), so neither side is
exhibited in herd7 -- the verdicts are **cited**, to be reproduced in each model's
own artifact. The `.litmus` files document the program shapes.

**Reference:** Soham Chakraborty, Viktor Vafeiadis, *Grounding Thin-Air Reads with
Event Structures*, POPL 2019, doi:10.1145/3290383 (§2.3-2.4 Coh-CYC and FADD,
Fig. 3 / Fig. 6; §4.3 incomparability). Jeehoon Kang, Chung-Kil Hur, Ori Lahav,
Viktor Vafeiadis, Derek Dreyer, *A Promising Semantics for Relaxed-Memory
Concurrency*, POPL 2017, doi:10.1145/3009837.3009850. The PS->ARMv8 RMW
unsoundness: Anton Podkopaev, Ori Lahav, Viktor Vafeiadis, *Bridging the Gap
between Programming Languages and Hardware Weak Memory Models*, POPL 2019,
doi:10.1145/3290382.
