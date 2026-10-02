# sMRD -> C11  (C11 is strictly weaker)

Symbolic MRD (sMRD) is an event-structures memory model for C/C++ relaxed
atomics, the symbolic successor to Modular Relaxed Dependencies (MRD): it is the
first thin-air-free semantics that still admits aggressive compiler
optimisations (alias analysis, freedom from undefined behaviour, extrinsic
choices such as over-alignment), exports a semantic-dependency relation into the
C/C++ model, allows the standard atomics compilation mappings, and matches the
ISO C/C++ desiderata. C11 is the axiomatic ISO/IEC 14882:2011 (and C 2011)
concurrency model. sMRD is strictly stronger than C11: the two agree everywhere
except on out-of-thin-air (OOTA) reads, which C11's axioms fail to forbid and
sMRD rules out, so C11 permits a strict superset of behaviours.

## Direction -- C11 allows, sMRD forbids: out-of-thin-air

`LB-oota.litmus` is the canonical thin-air load-buffering program (`LB+datas`):
P0 reads `x` into `r1` and stores `r1` to `y`; P1 reads `y` into `r2` and stores
`r2` to `x`. The target outcome `r1=r2=42` requires the value 42 to appear even
though no thread ever writes a literal 42 -- it can only be justified by a cyclic
chain of relaxed reads-from edges. The C11 standard's text does not forbid this:
the original *Mathematizing C++ Concurrency* axioms (and the ISO standard they
formalise) admit the execution, which is the motivating instance of the thin-air
problem. sMRD inherits MRD's repair: it computes a semantic dependency `sd` from
each load to the store that depends on it, the OOTA candidate then contains a
cycle in `rf union sd`, and sMRD discards it. Because sMRD preserves the standard
atomics compilation mappings and the ISO semantic-dependency desiderata, it does
not lose any non-thin-air behaviour, so the only separating outcomes are OOTA
ones -- making C11 strictly weaker.

A MoRDor-syntax companion `LB-oota.lit` encodes the same value-invention shape
with the embedded assertion `forbid (r0 = 42 && r1 = 42)`, matching the MRD/sMRD
`avoidoota` test style.

## Running

Both verdicts are **cited, not executed** in this repo. herd7 cannot *exhibit*
the C11 permission: its candidate-execution generation ties every read to a value
actually written, so it never constructs an OOTA execution and reports

```sh
herd7 -c11 LB-oota.litmus     # Observation LB-oota Never 0 4
```

`Never` here reflects the tool's inability to build the execution, not a C11
prohibition -- the permission is a property of the C11 axioms as written. On the
sMRD side, no sMRD/MoRDor checker is bundled in this repository, so the
`forbid (r0 = 42 && r1 = 42)` verdict on `LB-oota.lit` is documented from the
paper rather than machine-run.

**Reference:** Jay Richards, Daniel Wright, Simon Cooksey, Mark Batty,
*Symbolic MRD: Dynamic Memory, Undefined Behaviour, and Extrinsic Choice*,
PACMPL 9 (OOPSLA1), Article 146, 2025 (doi:10.1145/3721089); Marco Paviotti,
Simon Cooksey, Anouk Paradis, Daniel Wright, Scott Owens, Mark Batty,
*Modular Relaxed Dependencies in Weak Memory Concurrency*, ESOP 2020
(doi:10.1007/978-3-030-44914-8_22); Mark Batty, Scott Owens, Susmit Sarkar,
Peter Sewell, Tjark Weber, *Mathematizing C++ Concurrency*, POPL 2011
(doi:10.1145/1926385.1926394); ISO/IEC 14882:2011.
