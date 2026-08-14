# Java (JMM) ↔ JAM  (incomparable)

**Java Access Modes (JAM)** (Bender & Palsberg, *A Formalization of Java's
Concurrent Access Modes*, OOPSLA 2019) is a proposed revision of the Java Memory
Model built on the JDK 9 `VarHandle` access modes -- **plain, opaque,
release/acquire, volatile**. It is explicitly modelled on RC11 and adopts RC11's
out-of-thin-air fix, the `acyclic(po ∪ rf)` requirement, but **only for
opaque-or-stronger accesses**. The **original JMM** (Manson, Pugh & Adve, POPL
2005; JSR-133) instead has just two tiers -- ordinary and volatile -- and pins
down racy behaviour with a happens-before relation plus a *commitment*
causality semantics.

Neither model contains the other: JAM is **weaker on plain accesses** (it leaves
thin-air unconstrained where the JMM's commitment rules forbid it) and **stronger
on the new atomic tiers** (its `acyclic(po ∪ rf)` forbids reorderings the JMM's
ordinary accesses permit and that the JMM has no mode to express). Mapping the
shared tiers either way -- ordinary ↔ plain, volatile ↔ volatile -- leaves a
separating program in each direction.

## Direction 1 — JAM allows, JMM forbids: plain-mode thin-air (`cyc_na`)

`cyc_na.litmus` is the canonical thin-air load-buffering program (JAM's own
`cyc_na`, shown with relaxed atomics standing in for the plain access mode). The
outcome `r1=r2=42` invents 42 from a cycle in `po ∪ rf`.

* **JAM allows it at plain mode.** JAM's `acyclic(po ∪ rf)` requirement applies
  only to opaque mode or stronger; plain accesses keep the cycle, so JAM admits
  the thin-air value.
* **The JMM forbids it.** Killing exactly this OOTA is what the JMM's commitment
  semantics was designed for: a value is only committed when a well-behaved
  execution justifies it, and 42 has no such justification.

## Direction 2 — JMM allows, JAM forbids: opaque-mode reordering (`LB+opaque`)

`LB+opaque.litmus` is plain load buffering with **real** values, `r1=r2=1` (no
thin-air -- every value read is genuinely written). The relaxed atomics stand in
for JAM's **opaque** mode, a tier the JMM lacks.

* **JAM forbids it at opaque.** `r1=r2=1` closes a `po ∪ rf` cycle, and JAM
  enforces `acyclic(po ∪ rf)` for opaque-or-stronger -- precisely the ordering
  guarantee JDK 9 introduced opaque to provide.
* **The JMM allows it.** The JMM maps these fields to *ordinary* accesses, whose
  happens-before + commitment semantics permits the load/store reordering;
  `r1=r2=1` is a fully committed, well-behaved JMM execution. Having no opaque
  tier, the JMM cannot express the stronger ordering JAM enforces.

## Running

Neither direction is machine-run -- both verdicts are **cited**. There is no
shared checker: the original JMM is not a herd7 model (its causality semantics is
the JSR-133 commitment procedure), and JAM's mechanisation is the Coq development
accompanying the OOPSLA 2019 paper rather than a herd7 `.cat` file. herd7 also
cannot *construct* the Direction-1 OOTA in any case, since it ties reads to
written values. The `.litmus` files document the program shapes and record which
model permits each outcome.

> Note: JAM's own paper compares JAM with **RC11** (see
> `../../strictly-weaker/RC11-vs-JAM/`); the comparison with the *original* JMM
> here follows from JAM being a revision of it -- weaker on plain, stronger on the
> access-mode tiers. The headline recorded in `models.json` is that the two are
> incomparable.

**Reference:** John Bender, Jens Palsberg, *A Formalization of Java's Concurrent
Access Modes*, PACMPL 3 (OOPSLA) Article 142, 2019, doi:10.1145/3360568. Jeremy
Manson, William Pugh, Sarita V. Adve, *The Java Memory Model*, POPL 2005,
doi:10.1145/1040305.1040336; JSR-133 (Lea, Manson, Pugh), 2004. Evgenii
Moiseenko, Anton Podkopaev, Dmitrii Koznov, *A Survey of Programming Language
Memory Models*, Programming and Computer Software 47(6), 2021,
doi:10.1134/S0361768821060050.
