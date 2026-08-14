# C++20 ↔ C11  (incomparable)

C++20 reworked the C/C++ memory model in two normative ways that pull in opposite
directions, so it neither contains nor is contained in the original
C11/C++11/14/17 model.

## Direction 1 — C++20 forbids, C11 allows: the seq_cst repair (P0668)

C++11/14/17 `seq_cst` fences are too weak to forbid the
independent-reads-of-independent-writes outcome even with an SC fence between each
reader's loads — a long-known defect. C++20 adopted Lahav et al.'s repaired
sequential consistency (Boehm, Giroux & Vafeiadis, **P0668**), which forbids it.
`IRIW+scfences.litmus` is the witness:

```sh
herd7 -model rc11.cat     IRIW+scfences.litmus   # Never 0 15      (C++20's repaired SC forbids)
herd7 -model c11_orig.cat IRIW+scfences.litmus   # Sometimes 2 30  (C11/C++17 allow)
```

(`rc11.cat` models exactly the repaired-SC fragment C++20 took from RC11; on this
SC-only test it gives the C++20 verdict.)

## Direction 2 — C11 forbids, C++20 allows: weakened release sequences (P0982)

C++ **weakened release sequences** across versions (Boehm, **P0982** — the C++20
endpoint of a change that began at C++17): a release sequence is now continued only
by read-modify-writes, no longer by later *relaxed stores of the same thread*. So a
pattern that synchronised under C++11 stops synchronising under C++20.

This direction is now checked against genuine per-version `cat` models —
`cpp11.cat` / `cpp17.cat` / `cpp2w.cat` in `../../models/cpp/`, vendored from
[`gonzalobg/cpp_memory_model`](https://github.com/gonzalobg/cpp_memory_model)
(Cooksey & Brito, 2025, on Lahav et al.'s RC11). `RS.litmus` is the witness — a
`release` store followed by a same-thread `relaxed` store of `2`, with the reader
acquiring `2`:

```sh
herd7 -model ../../models/cpp/cpp11.cat RS.litmus   # Never      (C++11: relaxed store is in the release sequence)
herd7 -model ../../models/cpp/cpp2w.cat RS.litmus   # Sometimes  (C++20: it is not, so no synchronisation -- the data read now races)
```

The *same program* flips verdict between the two real models — replacing the old
workaround (`RS+cpp20.litmus`, kept for reference) that simulated the C++20
semantics inside the program by making the heading store non-releasing, because no
C++20 `cat` model was on hand. The C++20 outcome is a data race (`Flag *undef*`):
losing the synchronisation is exactly what turns this once-defined program
undefined.

### Direction 2′ — the cleaner, all-atomic witness: C++20 forbids

The release-sequence change cuts *both* ways within the `rs/` family, and one
direction is witnessed without any race. `cpp_memory_model/rs/mp-rs-add-est-atomic`
is all-atomic and **allowed under C++11 and C++17 but forbidden under C++20**:

```sh
herd7 -model ../../models/cpp/cpp11.cat ../../cpp_memory_model/rs/mp-rs-add-est-atomic.litmus  # Sometimes
herd7 -model ../../models/cpp/cpp2w.cat ../../cpp_memory_model/rs/mp-rs-add-est-atomic.litmus  # Never
```

So C++20 both forbids an outcome C++11 allows (this test, cleanly) and allows one
C++11 forbids (`RS.litmus`, at the cost of a race) — a mechanised, two-sided
incomparability on the release-sequence axis alone. See
`../../cpp_memory_model/rs/README.md` for the full per-version matrix.

## What is and isn't machine-checked

The release-sequence direction is now fully machine-checked against dedicated
C++11/17/20 models (above). The SC-repair direction (P0668) still uses `rc11.cat`
(whose repaired SC is precisely what C++20 adopted) for the C++20 verdict and
`c11_orig.cat` for the C11 verdict, because the vendored `cpp*` models all inherit
RC11's repaired SC and so cannot exhibit the broken-SC behaviour C11 allows. C++20
is *also* strictly weaker than RC11 — see `../../strictly-weaker/RC11-vs-C++20`
(thin-air, which C++20 leaves unresolved).

**Reference:** Boehm, Giroux, Vafeiadis, *Revising the C++ Memory Model* (WG21
P0668R5), 2018; Boehm, *Weaken Release Sequences* (WG21 P0982R1), 2018; Lahav,
Vafeiadis, Kang, Hur, Dreyer, *Repairing Sequential Consistency in C/C++11*, PLDI
2017 (DOI 10.1145/3062341.3062352); ISO/IEC 14882:2020.
