# C++ standard-version `cat` models

Five `herd7`-runnable axiomatic models that mechanise the evolution of the
C/C++ memory model across standard versions, together with their companion
`.cfg` files.

## Source

Vendored verbatim from **`gonzalobg/cpp_memory_model`**
(<https://github.com/gonzalobg/cpp_memory_model>, *"C++ Memory Model and Forward
Progress Testing"*). The models build on Lahav et al.'s repaired C11 (RC11,
PLDI '17); the `cat` encodings are by **Simon Colin** (RC11) and **Simon Cooksey
& Gonzalo Brito** (the C++-version variants, 2025). Licence: see the upstream
repository.

## What each model is

| file        | models            | differs from its base by |
|-------------|-------------------|--------------------------|
| `rc11.cat`  | RC11 (PLDI '17)   | — (the baseline: no-thin-air axiom, full release sequences) |
| `cpp11.cat` | C++11/14          | RC11 minus the no-thin-air axiom; **external** writes break release sequences |
| `cpp17.cat` | C++17             | `cpp11` but a release sequence is **no longer** continued by later same-thread writes — only by RMWs |
| `cpp2w.cat` | C++20 (`2w`)      | `cpp17` plus the C++20 fix closing the `hb` gap for non-atomic operations (P0982-era) |
| `rc17.cat`  | RC11 + C++17 RS   | `rc11` with the C++17 release-sequence narrowing |

The single line that carries the headline release-sequence story is `let rs = …`:
`cpp11` extends a release sequence through same-thread relaxed stores; `cpp17`
and `cpp2w` extend it only through RMWs (`(rf; myrmw)*`).

## Verified under herd7

Reproduced with `herd7` 7.58 (this machine). The release-sequence message-passing
family in `../../cpp_memory_model/rs/` exercises the distinctions; the clean
(non-racy, all-atomic) witnesses are:

| test                          | cpp11 | cpp17 | cpp2w | reading |
|-------------------------------|-------|-------|-------|---------|
| `mp-rs-add-est-atomic`        | Sometimes | Sometimes | **Never** | C++20 forbids what C++11/17 allow |
| `mp-rs-st-est-atomics`        | Sometimes | Sometimes | **Never** | C++20 forbids what C++11/17 allow |
| `mp-rs-st-eadd-atomics.cpp11` | **Never** | Sometimes | **Never** | only C++17 allows it |
| `mp-rs.cpp11` / `mp-rs-add-st.cpp11` | **Never** | Sometimes* | Sometimes* | C++11 forbids; later versions allow (racy) |

(`*` = the later-version outcome is a data race / undefined, since the same-thread
relaxed store no longer carries release.)

These three versions are pairwise distinguishable, so they witness — mechanically —
the two-sided incomparability of C++20 against the original C11/C++11 model that the
zoo records as the `C++20 ⋈ C11` edge (see `../../incomparable/C++20-vs-C11/`).
