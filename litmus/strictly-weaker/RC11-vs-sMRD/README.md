# RC11 -> sMRD  (sMRD is strictly weaker)

Repaired C11 (RC11, Lahav et al. PLDI 2017) kills out-of-thin-air the blunt way:
it adds the axiom **`acyclic(po ∪ rf)`** over *all* accesses. That forbids every
load->store reordering, thin-air or not -- which is sound but **too strong**, as
the RC11 authors themselves note: it makes constant-folding a relaxed store
unsound. Symbolic MRD (sMRD, Richards et al. OOPSLA 2025) forbids thin-air more
surgically: it bans only `dp ∪ rf` cycles, where `dp` is a *semantic* dependency.
Where a dependency is semantically false (so a real compiler removes it), sMRD
removes it too and permits the resulting load->store reordering. So sMRD allows
LB outcomes RC11 forbids: RC11 is strictly stronger.

## Direction -- sMRD allows, RC11 forbids: load->store reordering on LB

`LB.litmus` is the false-dependency load-buffering program of sMRD Example 1.2,
shown with the store already constant-folded to `y=1` (the optimisation sMRD
justifies and RC11 forbids). P0 reads `x` into `r1` then stores `y=1`; P1 reads
`y` into `r2` then stores `r2` to `x`. The outcome `r1=1 /\ r2=1` is a **genuine
coherent execution** -- `y=1` is really written, nothing is conjured -- reachable
only by letting P0's load observe P1's store before P0's own store commits.

* **RC11 forbids it.** `acyclic(po ∪ rf)` rejects the cycle
  `load(x) →po store(y) →rf load(y) →po store(x) →rf load(x)`.
* **sMRD allows it.** The `read(x)->write(y)` dependency is semantically false
  (the value stored does not depend on `r1` once folded), so there is no `dp`
  edge, no `dp ∪ rf` cycle, and the outcome stands -- exactly as in C11 and in
  real GCC/Clang output.

## Running

Unlike a value-inventing thin-air test, this outcome is a real execution herd7
**can construct**, so the RC11 verdict is genuinely machine-checked, not a
tool artefact:

```sh
herd7 -model rc11.cat      strictly-weaker/RC11-vs-sMRD/LB.litmus   # Observation LB Never 0 3      (RC11 forbids)
herd7 -model c11_orig.cat  strictly-weaker/RC11-vs-sMRD/LB.litmus   # Observation LB Sometimes 1 3  (C11 allows; sMRD matches)
```

The first line is RC11's actual axiom rejecting the constructed cycle. The second
is the permissive side: C11 (`c11_orig.cat`) admits the outcome, and **sMRD
agrees with C11 here** (it removes the false dependency rather than the whole
load->store edge). sMRD has no herd7 model, so its matching verdict is cited; the
RC11/C11 separation is machine-run. Both lines are wired into `../../run.sh`.

**Reference:** Jay Richards, Daniel Wright, Simon Cooksey, Mark Batty, *Symbolic
MRD: Dynamic Memory, Undefined Behaviour, and Extrinsic Choice*, PACMPL 9
(OOPSLA1) Article 146, 2025, doi:10.1145/3721089 (§1, Example 1.2; the
"acyclic(po ∪ rf) is too strong on LB" observation). Ori Lahav, Viktor Vafeiadis,
Jeehoon Kang, Chung-Kil Hur, Derek Dreyer, *Repairing Sequential Consistency in
C/C++11*, PLDI 2017, doi:10.1145/3062341.3062352 (the `acyclic(po ∪ rf)` axiom).
