# RC11 → C++20  (C++20 is strictly weaker)

**Distinguishing behaviour:** out-of-thin-air / plain load buffering.

C++20 adopted RC11's repaired sequential consistency (Boehm, Giroux & Vafeiadis,
P0668) but **not** RC11's second repair — the no-thin-air axiom
`acyclic(po ∪ rf)`. The C++20 committee deliberately left the thin-air problem
unresolved (only a non-normative note discourages it), so C++20's relaxed-atomic
fragment is unchanged from C11 and still permits load-buffering reads that RC11
forbids. Hence RC11 is strictly stronger.

`LB-relaxed.litmus` is plain relaxed load buffering — no dependencies, no value
invention. RC11's blanket `acyclic(po ∪ rf)` forbids *all* LB shapes; C++20 (like
C11/C++17 and IMM) allows it.

```sh
herd7 -model rc11.cat     LB-relaxed.litmus   # Never 0 3      (RC11 forbids — verified)
herd7 -model c11_orig.cat LB-relaxed.litmus   # Sometimes 1 3  (C++20, via the unchanged C11 fragment)
```

## What is and isn't machine-checked

herd7 ships no dedicated C++20 model. For this test that does not matter: C++20
leaves C11's relaxed/thin-air fragment untouched, so the original C11 model
(`c11_orig.cat`) is a faithful stand-in for the C++20 verdict here (it is the same
plain LB allowed by `incomparable/RC11-vs-IMM`). The RC11 *forbids* direction is
verified directly. This is the **same** thin-air gap discussed in
`../../strictly-weaker/MRD-vs-C11` and `../../incomparable/RC11-vs-IMM`, now placed
against C++20.

**Reference:** Lahav, Vafeiadis, Kang, Hur, Dreyer, *Repairing Sequential
Consistency in C/C++11*, PLDI 2017 (DOI 10.1145/3062341.3062352); Boehm, Giroux,
Vafeiadis, *Revising the C++ Memory Model* (WG21 P0668R5), 2018; Batty et al.,
*The Problem of Programming Language Concurrency Semantics*, ESOP 2015 (the
thin-air problem).
