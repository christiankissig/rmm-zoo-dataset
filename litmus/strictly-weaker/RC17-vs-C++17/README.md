# RC17 → C++17  (strictly weaker)

RC17 and C++17 share the same (C++17) release-sequence definition; they differ in
one axiom. RC17 inherits RC11's **no-thin-air** axiom `acyclic(po | rf)`, which
C++17 does not have. So C++17 permits plain relaxed load-buffering / out-of-thin-air
reads that RC17 forbids, and forbids nothing RC17 allows (RC17 is literally C++17
plus that one axiom). A strict order by construction — the same relationship the
zoo already records between RC11 and C11.

## Witness

The plain relaxed load-buffering shape `LB-relaxed.litmus` (shared with
`../RC11-vs-C++20`), against the `cat` models in `../../models/cpp/`:

```sh
herd7 -model ../../models/cpp/rc17.cat  LB-relaxed.litmus  # Never      (RC17's acyclic(po|rf) forbids LB)
herd7 -model ../../models/cpp/cpp17.cat LB-relaxed.litmus  # Sometimes  (C++17 leaves thin-air unresolved)
```

The lattice around here is a small diamond: `RC11 → {C11, RC17}`, `RC11 → RC17 →
C++17`, and `C11 → C++17`, so C++17 is the weakest of the four — below both C11 and
RC17, which are themselves below RC11.

**Reference:** Lahav et al., PLDI 2017 (the no-thin-air axiom); ISO/IEC 14882:2017;
Cooksey & Brito Gadeschi, `cpp_memory_model`, 2025.
