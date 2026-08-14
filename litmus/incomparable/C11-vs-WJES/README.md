# C11 <-> WJES  (incomparable)

**Well-Justified Event Structures (WJES)** (Jeffrey & Riely, *On Thin Air Reads*,
LICS 2016; extended LMCS 2019) grounds thin-air reads in event structures with a
notion of *well-justification* inspired by game semantics: a read may only take a
value the environment cannot avoid providing. This forbids out-of-thin-air, which
C11 allows -- but it also forbids a legal hardware behaviour C11 allows, so the
two are incomparable.

## Direction 1 -- C11 allows, WJES forbids: out-of-thin-air

`LB-oota.litmus` is thin-air load buffering (`LB+datas`), outcome `r1=r2=1`. C11
permits it: its relaxed-atomics axioms impose no acyclicity on `rf ∪ dependency`.
WJES forbids it: the cyclic configuration has no justifying write that the
environment is forced to provide, so it is never well-justified.

## Direction 2 -- WJES forbids, C11 allows: load->load reordering (TC7)

`TC7.litmus` is Pugh causality test case **TC7**, the load->load reordering
counterexample WJES's authors themselves exhibit. The outcome `r0=r1=r2=1` is a
*genuine* coherent execution (the value 1 originates at the real store `x=1` and
flows `x→y→z`); reaching it requires P0's two independent reads to be reordered.

* **C11 allows it** -- relaxed reads are unordered -- and so do ARMv7/ARMv8/POWER.
  `herd7 -c11` => `Sometimes`.
* **WJES forbids it** -- no well-justified configuration contains all three
  reads-of-1. WJES is *too strong* here, which is precisely why its naive
  compilation to ARM/POWER is non-optimal (extra fences/dependencies would be
  needed). The authors propose an "alt-well-justification" to admit TC7, but then
  the external-DRF proof is lost.

Because each model forbids a behaviour the other allows, they are incomparable.

## Running

```sh
herd7 -c11 incomparable/C11-vs-WJES/TC7.litmus       # Observation TC7 Sometimes 1 7   (C11 allows; WJES forbids)
herd7 -c11 incomparable/C11-vs-WJES/LB-oota.litmus   # Observation LB-oota Never 0 3    (tool cannot build OOTA; C11 permits by axiom)
```

The TC7 (Direction 2) C11 verdict is genuinely machine-run and is wired into
`../../run.sh`. WJES has no herd7 model (its mechanisation is the paper's own
development), so its forbidding verdicts are cited. The Direction-1 `Never` is the
usual herd7 limitation -- it ties reads to written values and never constructs an
OOTA execution -- not a C11 prohibition.

**Reference:** Alan Jeffrey, James Riely, *On Thin Air Reads: Towards an Event
Structures Model of Relaxed Memory*, LICS 2016, doi:10.1145/2933575.2934536
(extended: Logical Methods in Computer Science 15(1), 2019, arXiv:1707.05881) --
the TC7 counterexample and well-justification. C11: Mark Batty et al.,
*Mathematizing C++ Concurrency*, POPL 2011, doi:10.1145/1926385.1926394. Pugh's
causality test cases: <https://www.cs.umd.edu/~pugh/java/memoryModel/>.
