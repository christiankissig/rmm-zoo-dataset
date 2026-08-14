# RC11 → RC17  (strictly weaker)

RC17 is RC11 updated to the **C++17 release-sequence** definition: identical to
RC11 (repaired seq_cst, no out-of-thin-air via `acyclic(po | rf)`) except that a
release sequence is continued only by read-modify-writes, no longer by later
same-thread relaxed stores. Exactly as in the `C11 → C++17` case, that narrowing
only removes happens-before edges, so RC17 admits a non-synchronising outcome RC11
forbids and forbids nothing RC11 allows — a strict order by construction.

## Witness

`mp-rs-add-est-atomic.litmus` (all-atomic, clean), against the `cat` models in
`../../models/cpp/` (vendored from
[`gonzalobg/cpp_memory_model`](https://github.com/gonzalobg/cpp_memory_model)):

```sh
herd7 -model ../../models/cpp/rc11.cat mp-rs-add-est-atomic.litmus  # Never      (RC11 forbids)
herd7 -model ../../models/cpp/rc17.cat mp-rs-add-est-atomic.litmus  # Sometimes  (RC17 allows)
```

This mirrors the `C11 → C++17` edge one level up the lattice (both keep the
no-thin-air axiom; RC17 → C++17 is where that axiom is dropped — see
`../RC17-vs-C++17`).

**Reference:** Lahav, Vafeiadis, Kang, Hur, Dreyer, *Repairing Sequential
Consistency in C/C++11*, PLDI 2017; Cooksey & Brito Gadeschi, `cpp_memory_model`,
2025.
