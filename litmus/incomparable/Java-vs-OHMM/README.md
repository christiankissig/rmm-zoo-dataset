# Java (JMM) <-> OHMM  (incomparable)

The **Java Memory Model (JMM)** (Manson, Pugh, Adve, POPL 2005) and the
**Operational Happens-Before Model (OHMM)** (Zhang & Feng, 2016) are both
syntactic-dependency-preserving repairs of the out-of-thin-air problem: both
track syntactic dependencies and forbid the canonical thin-air outcome. But OHMM
was proposed precisely to *repair* the JMM, and the two end up incomparable --
each permits behaviour the other forbids.

## Direction 1 -- OHMM allows, JMM forbids: reordering of independent accesses

`MP-reorder.litmus` is message passing with two *independent* writes on P0 (`x`
then `y`) and two independent reads on P1 (`y` then `x`), no syntactic dependency
linking the pairs. OHMM's abstract machine holds events in a **global event
buffer** in which independent (non-dependent) events may be reordered before they
propagate into a global history-based memory, so the store to `y` can become
visible before the store to `x`, yielding `1:r1=1 /\ 1:r2=0`. The OHMM paper
states the model "is weaker than JMM for lockless programs ... such as the
reordering of independent memory accesses that is not valid in JMM." JMM forbids
this outcome: its commit-sequence causality rules do not justify the independent
reordering.

## Direction 2 -- JMM allows, OHMM forbids: causality over-permissiveness

The JMM is well known to be **over-permissive on causality** (and to validate a
different transformation profile): the survey's Table 2 records JMM and OHMM with
*different* soundness profiles -- for example OHMM validates all four redundant-
access eliminations (`Elim = + + + +`) while JMM does not (`Elim = + + + -`), and
their global/reasoning columns differ -- and the literature documents JMM
admitting causality-test outcomes that later operational repairs reject (Ševčík &
Aspinall, ECOOP 2008; survey §4.3.2, §A.5). OHMM's dependency-tracking machine,
built to *fix* the JMM, forbids these. So behaviours JMM permits via its weak
causality fall outside OHMM, and neither model's behaviours are a subset of the
other's.

## Running

Neither side is machine-run for the separating outcomes. OHMM has no herd7/`cat`
formalisation (it is an operational model defined by an abstract machine with a
global event buffer and a replay mechanism), the independent-access reordering of
`MP-reorder.litmus` is OHMM-specific rather than a JMM execution, and the JMM is
itself an axiomatic/operational model not bundled in herd7. The verdicts are
**cited** from the literature, not produced by a single checker. (The sibling
`../LKMM-vs-OHMM` pair separates OHMM from the *Linux* kernel model on the same
`MP-reorder` shape.)

**Reference:** Jeremy Manson, William Pugh, Sarita V. Adve, *The Java Memory
Model*, POPL 2005, doi:10.1145/1040305.1040336; Yang Zhang, Xinyu Feng, *An
Operational Happens-Before Memory Model*, Frontiers of Computer Science 10(1),
2016, doi:10.1007/s11704-015-4492-4; Jaroslav Ševčík, David Aspinall, *On Validity
of Program Transformations in the Java Memory Model*, ECOOP 2008; Evgenii
Moiseenko, Anton Podkopaev, Dmitrii Koznov, *A Survey of Programming Language
Memory Models*, Programming and Computer Software 47(6):439-456, 2021,
doi:10.1134/S0361768821060050 (Table 2; §4.3.2, §A.5).
