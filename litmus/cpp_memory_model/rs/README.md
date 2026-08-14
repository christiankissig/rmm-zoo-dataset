# Release-sequence message-passing tests (`rs/`)

The release-sequence (`rs`) litmus family from
**`gonzalobg/cpp_memory_model`** (<https://github.com/gonzalobg/cpp_memory_model>),
vendored verbatim with the upstream `.expected` outputs. They exercise the one
construct whose definition changed across C++ standard versions — the **release
sequence** — and are checked against the C++-version `cat` models in
`../../models/cpp/`.

Each test is a message-passing shape: a release store publishes data, a later
store of the same flag continues (or fails to continue) the release sequence, and
an acquiring reader either does or does not synchronise. The filename suffixes are
upstream conventions: `.cpp11` / `.cpp17` mark a test whose verdict pins a
particular standard version; `.undef` marks an outcome that is a data race (hence
undefined) once the relaxed store no longer carries release.

## Verified results (herd7 7.58)

`Sometimes` = outcome allowed, `Never` = forbidden; `*` = the allowing model
reports the execution as a data race (`Flag *undef*`).

```
test                            cpp11      cpp17      cpp2w
mp-rs-add-eadd                  Never      Never      Never
mp-rs-add-est-atomic            Sometimes  Sometimes  Never       <- P0982: C++20 forbids
mp-rs-add-est.undef             Sometimes* Sometimes* Sometimes*
mp-rs-add                       Never      Never      Never
mp-rs-add-st.cpp11              Never      Sometimes* Sometimes*   <- C++17 narrowing
mp-rs-add-st.cpp17.undef        Never      Sometimes* Sometimes*
mp-rs.cpp11                     Never      Sometimes* Sometimes*   <- C++17 narrowing
mp-rs.cpp17.undef               Never      Sometimes* Sometimes*
mp-rs-eadd                      Never      Never      Never
mp-rs-est.undef                 Sometimes* Sometimes* Sometimes*
mp-rs-st-eadd-atomics.cpp11     Never      Sometimes  Never        <- only C++17 allows
mp-rs-st-eadd-atomics.cpp17     Never      Never      Never
mp-rs-st-eadd.undef             Sometimes* Sometimes* Sometimes*
mp-rs-st-est-atomics            Sometimes  Sometimes  Never        <- P0982: C++20 forbids
mp-rs-st-est.undef              Never*     Sometimes* Sometimes*
mp-rs-strel                     Never      Never      Never
```

Reproduce:

```sh
cd ../..                     # litmus/
for m in cpp11 cpp17 cpp2w; do
  herd7 -model models/cpp/$m.cat cpp_memory_model/rs/mp-rs-add-est-atomic.litmus
done
```

## Why this matters for the zoo

The three versions are pairwise distinguishable, and the distinctions run in
*both* directions (C++17 allows things C++11 forbids; C++20 forbids things C++17
allows). That is mechanical evidence for the two-sided `C++20 ⋈ C11` edge — and it
replaces the earlier hand-encoded `RS+cpp20.litmus` workaround (which simulated the
C++20 release-sequence semantics inside the *program* because no C++20 `cat` model
was on hand) with a check against a genuine C++20 model, `cpp2w.cat`. See
`../../incomparable/C++20-vs-C11/README.md`.
