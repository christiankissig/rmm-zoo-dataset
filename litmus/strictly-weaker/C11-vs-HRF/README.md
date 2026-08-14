# C11 → HRF  (HRF is strictly weaker)

**Distinguishing behaviour:** synchronisation through scopes the two threads do
not share, turning a C11-ordered message pass into a scoped data race.

HRF (Heterogeneous-Race-Free) generalises the DRF-SC contract to a *scope
hierarchy*: a release and an acquire order one another only when they name a
**common** scope. Restricted to a single global scope it reproduces C11's DRF-SC
guarantee; with sub-global scopes a program can be *heterogeneous-race-free* only
if every pair of communicating operations shares a scope. `MP+relacq.litmus` is
message passing whose release/acquire synchronise under C11's single scope —
forbidden. `MP+scoped-relaxed.litmus` is the same shape where the producer
releases at its own work-group's scope and the consumer acquires at *its* own:
no common scope, hence a scoped race, hence the weak outcome is admitted.

```sh
# C11 (single global scope): release/acquire synchronise, program is DRF
herd7 -c11 MP+relacq.litmus          # Never 0 2      (forbidden)
# HRF with non-shared scopes: scoped data race, no ordering (modelled relaxed)
herd7 -c11 MP+scoped-relaxed.litmus  # Sometimes 1 3  (allowed)
```

## What is and isn't machine-checked

HRF is a *framework* (a race-freedom contract parameterised by a scope lattice),
not a herd7 `cat` model. Its prediction for a program with no shared
synchronisation scope is exactly that of an unsynchronised/relaxed program — which
is what the `-c11` run of `MP+scoped-relaxed.litmus` exhibits. The genuine scoped
source is in that file's header. The C11 *forbids* direction is checked directly;
the HRF *allows* direction is the relaxed model of a scoped race, cited to Hower
et al.

**Reference:** Hower, Hechtman, Beckmann, Gaster, Hill, Reinhardt, Wood,
*Heterogeneous-Race-Free Memory Models*, ASPLOS 2014 (DOI
10.1145/2541940.2541981).
