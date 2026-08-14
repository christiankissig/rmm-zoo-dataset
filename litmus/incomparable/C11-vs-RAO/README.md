# C11 <-> RAO  (incomparable)

**RAO** -- the survey's name for the *Relaxed Atomic + Ordering* model of
Saraswat, Jagadeesan, Michael & von Praun, *A Theory of Memory Models* (PPoPP
2007) -- explains relaxed behaviour by applying **reorderings/transformations over
a sequentially consistent execution**. It permits thin-air, yet *claims* the
external DRF guarantee -- a combination later shown incompatible in general (Batty
et al., ESOP 2015); the survey attributes the claim to a restricted input language
(notably, no general conditional statements). C11 and RAO are incomparable, but --
unusually for this tree -- neither direction has a crisp runnable separating
program.

## Direction 1 -- C11 allows, RAO forbids: the claimed external-DRF guarantee

RAO claims external DRF: race-free programs may only show SC outcomes. Where that
holds it forbids non-SC behaviour that C11-relaxed admits. But it holds only on
RAO's restricted language, and the survey itself doubts the claim, so there is no
robust runnable witness -- this direction is documented from the survey's property
table with the eDRF caveat.

## Direction 2 -- RAO allows, C11 forbids: transformations over SC

`LB.litmus` is plain load buffering, outcome `r1=r2=1`. RAO admits it by reordering
each independent read/write over an SC execution. Plain LB is *also* allowed by
C11-all-relaxed, so this exact program does not separate them; the separation
appears only when C11 uses stronger (non-atomic / SC) modes that forbid the
reorder while RAO -- mode-free, uniform transformations -- still admits it. This
is a model-level statement, not an isolated litmus outcome.

## Running

Out-of-thin-air does **not** separate the two (both permit it), and neither side
has a herd7 model or a published single-program witness, so both verdicts are
**cited / model-level**. `LB.litmus` documents the load-buffering shape RAO
relaxes over SC; it is not machine-adjudicated against either model here.

**Reference:** Vijay A. Saraswat, Radha Jagadeesan, Maged Michael, Christoph von
Praun, *A Theory of Memory Models*, PPoPP 2007, doi:10.1145/1229428.1229469. The
external-DRF-vs-thin-air incompatibility: Mark Batty, Kayvan Memarian, Kyndylan
Nienhuis, Jean Pichon-Pharabod, Peter Sewell, *The Problem of Programming Language
Concurrency Semantics*, ESOP 2015, doi:10.1007/978-3-662-46669-8_12. Survey:
Moiseenko, Podkopaev, Koznov, *A Survey of Programming Language Memory Models*,
2021, doi:10.1134/S0361768821060050.
