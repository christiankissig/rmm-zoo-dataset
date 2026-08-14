# C11 → C++17  (strictly weaker)

C++17 is **strictly weaker** than C11/C++11/14: it narrows release sequences. Under
C++11/14 a release sequence headed by a release store is continued by later
*relaxed stores of the same thread*; from C++17 it is continued only by
read-modify-writes. Removing that clause removes happens-before edges, so a
message-passing pattern that **synchronised** under C++11 **stops synchronising**
under C++17 — C++17 admits an outcome C++11 forbids. Because the change only ever
*removes* synchronisation (the C++17 release-sequence relation is a subset of the
C++11 one, everything else equal), it is monotone by construction: C++17 forbids
nothing C++11 allows. Hence a genuine strict order, not incomparability.

## Witness

`mp-rs-st-eadd-atomics.cpp11.litmus` (all-atomic, so no data race — a clean
witness), checked against the per-version `cat` models in `../../models/cpp/`
(vendored from [`gonzalobg/cpp_memory_model`](https://github.com/gonzalobg/cpp_memory_model)):

```sh
herd7 -model ../../models/cpp/cpp11.cat mp-rs-st-eadd-atomics.cpp11.litmus  # Never      (C++11 forbids: relaxed store still continues the release sequence)
herd7 -model ../../models/cpp/cpp17.cat mp-rs-st-eadd-atomics.cpp11.litmus  # Sometimes  (C++17 allows: it does not, so no synchronisation)
```

## Notes

* The zoo's `C11` node stands for C/C++11(/14); `cpp11.cat` models exactly that
  release-sequence semantics.
* This edge isolates the release-sequence axis. C++17's relationship to **C++20**
  is deliberately *not* drawn: it turns on where the standard places the
  release-sequence change (the `cpp_memory_model` models attribute the narrowing to
  C++17, while WG21 **P0982** is a C++20 paper), a version-boundary question the zoo
  does not adjudicate. See `../../incomparable/C++20-vs-C11/README.md`.

**Reference:** ISO/IEC 14882:2017; Boehm, *Weaken Release Sequences* (WG21 P0982R1);
Cooksey & Brito Gadeschi, `cpp_memory_model`, 2025.
