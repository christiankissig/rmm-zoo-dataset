# RC11 -> JAM  (JAM is strictly weaker)

**Java Access Modes (JAM)** (Bender & Palsberg, *A Formalization of Java's
Concurrent Access Modes*, OOPSLA 2019) formalises the JDK 9 VarHandle access
modes -- plain, opaque, release/acquire, volatile. It is explicitly modelled on
RC11 and **adopts RC11's out-of-thin-air fix** -- the `acyclic(po ∪ rf)`
requirement -- but, crucially, **only for opaque-or-stronger accesses**. For
*plain* (non-atomic) accesses JAM deliberately does not tackle thin-air. RC11, by
contrast, imposes `acyclic(po ∪ rf)` over **all** accesses. So at the plain level
JAM permits thin-air cycles RC11 forbids: along this edge JAM is strictly weaker.

## Direction -- JAM allows, RC11 forbids: thin-air at plain mode (cyc_na)

`LB-oota.litmus` is the canonical thin-air load-buffering program (JAM's `cyc_na`,
shown with relaxed atomics standing in for the access-mode annotation). The
outcome `r1=r2=42` invents 42 from a cycle in `po ∪ rf`.

* **RC11 forbids it.** Its blanket `acyclic(po ∪ rf)` rejects the cycle for every
  access, plain included. (RC11 added this for sound POWER compilation.)
* **JAM allows it at plain mode.** JAM's acyclicity requirement applies only to
  opaque mode or stronger; the plain-mode program keeps the `po ∪ rf` cycle, so
  JAM admits the thin-air outcome. The JAM paper states this directly: "The JAM
  allows this cycle in plain mode ... because its acyclicity requirement only
  applies to opaque mode or stronger accesses," whereas "the RC11 model breaks
  with C11 by including an acyclicity requirement for `po | rf` for all memory
  accesses" (§6). The all-**opaque** (relaxed) companion of the same program is
  forbidden by *both* models, isolating the separation to the plain level.

## Running

This is a value-inventing thin-air outcome, so herd7 cannot construct it; both
verdicts are **cited, not machine-run**:

```sh
herd7 -model rc11.cat strictly-weaker/RC11-vs-JAM/LB-oota.litmus   # Observation LB-oota Never 0 3
```

The `Never` reflects herd7's inability to *build* an OOTA execution; RC11's
prohibition is its `acyclic(po ∪ rf)` axiom and JAM's permission is a property of
its plain-mode rules. JAM has no herd7 model (its mechanisation is the Coq
development accompanying the paper).

> Note: the *overall* RC11/JAM relationship has more than one dimension -- JAM
> also lacks C11/RC11 release sequences -- so some treatments call them
> incomparable. The edge recorded in `models.json` is the headline one above:
> RC11's all-access thin-air axiom makes it strictly stronger than JAM, whose
> plain accesses are left unconstrained.

**Reference:** John Bender, Jens Palsberg, *A Formalization of Java's Concurrent
Access Modes*, PACMPL 3 (OOPSLA) Article 142, 2019, doi:10.1145/3360568 -- §6
"Comparison with RC11" (the `cyc_na` / `lb` tests, Fig. 16), §8.2. Ori Lahav,
Viktor Vafeiadis, Jeehoon Kang, Chung-Kil Hur, Derek Dreyer, *Repairing
Sequential Consistency in C/C++11*, PLDI 2017, doi:10.1145/3062341.3062352 (the
all-access `acyclic(po ∪ rf)` axiom).
