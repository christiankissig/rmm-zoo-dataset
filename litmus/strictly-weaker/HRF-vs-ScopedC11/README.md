# HRF → Scoped C11 / HRF-Relaxed  (HRF-Relaxed is strictly weaker)

**Distinguishing behaviour:** synchronisation between *different but
inclusion-related* scopes — legal under HRF-Relaxed, not recognised by HRF.

The original HRF models fix how two scoped operations may synchronise:
**HRF-direct** requires the release and the acquire to name the **same** scope;
**HRF-indirect** additionally allows explicit *transitive chains* of matching
scopes. Gaster, Hower & Howes's **HRF-Relaxed** drops exact matching in favour of
scope **inclusion** — a release at a larger scope synchronises with an acquire at
any scope contained in it. That admits strictly more synchronisation patterns, and
hence more programs with defined, weakly-ordered behaviour, than HRF: every HRF
behaviour is an HRF-Relaxed behaviour, but not conversely.

`MP+inclusion-scopes.litmus` is the canonical witness: a `device`-scoped release
paired with a `work_group`-scoped acquire on a thread inside that device. Under
HRF-direct/indirect the scopes do not match, so the program is a scoped race;
under HRF-Relaxed the inclusion makes the pair synchronise.

## What is and isn't machine-checked

This edge is a **model-definition** difference — the scope-matching rule itself —
not a reordering of plain accesses, and herd7 ships no scoped model, so neither
side is exhibited here (as with `incomparable/RC11-vs-IMM` and
`incomparable/C11-vs-Promising`). The genuine scoped source and the two models'
verdicts are documented in the test header and worked through in the paper, whose
formal scope lattices were explored with the **memalloy** model-comparison tool
(<https://github.com/johnwickerson/memalloy>).

**Reference:** Gaster, Hower, Howes, *HRF-Relaxed: Adapting HRF to the Complexities
of Industrial Heterogeneous Memory Models*, ACM TACO 12(1), 2015 (DOI
10.1145/2701618); Hower, Hechtman, Beckmann, Gaster, Hill, Reinhardt, Wood,
*Heterogeneous-Race-Free Memory Models*, ASPLOS 2014.
