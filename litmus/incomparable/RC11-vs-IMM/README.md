# RC11 ↔ IMM  (incomparable)

IMM (the Intermediate Memory Model) is a compilation target between language
models and hardware. herd7 does **not** ship IMM — it lives as a Coq development —
so only the RC11 side is machine-checked here; the IMM side is cited.

## Verified separating direction — IMM allows, RC11 forbids: plain load buffering

RC11 enforces a strong *no-thin-air* axiom, `acyclic (po ∪ rf)`, which forbids
**all** load-buffering shapes, even dependency-free ones. That axiom is known to
be too strong to compile efficiently to hardware (hardware does perform LB), which
is precisely why IMM drops it in favour of tracking *syntactic dependencies*: IMM
forbids only genuine dependency cycles (real OOTA), and so **allows plain LB**.

`LB-relaxed.litmus` is plain relaxed load buffering:

```sh
herd7 -model rc11.cat     LB-relaxed.litmus   # Never 0 3      (RC11 forbids — verified)
herd7 -model c11_orig.cat LB-relaxed.litmus   # Sometimes 1 3  (original C11 allows, for contrast)
# IMM: allowed (Podkopaev, Lahav, Vafeiadis 2019) — run in the IMM Coq artifact
```

## The design-space framing

As with `PSO ↔ POWER`, the "incomparable" label is partly about the models living
at different points rather than a tidy two-sided behavioural witness:

* IMM keeps hardware-style dependency tracking (so it allows LB that RC11 forbids).
* RC11 is a programmer-facing model with first-class SC accesses/fences whose
  semantics IMM handles differently as a compilation IR.

The clean, checkable direction is IMM-allows / RC11-forbids (above). A precise
treatment of the reverse requires the IMM development itself.

## Running IMM

The IMM model and its compilation-correctness proofs are at
<https://github.com/weakmemory/imm> (Coq). The litmus shape above corresponds to
the `LB` family discussed in the paper.

**Reference:** Podkopaev, Lahav, Vafeiadis, *Bridging the Gap between Programming
Languages and Hardware Weak Memory Models*, POPL 2019; Lahav et al., *Repairing
Sequential Consistency in C/C++11*, PLDI 2017.
