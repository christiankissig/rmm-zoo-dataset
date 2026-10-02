# MRD -> sMRD  (sMRD is strictly weaker)

**Distinguishing behaviour:** false dependencies that only *symbolic* reasoning
can remove.

Modular Relaxed Dependencies (MRD) and its symbolic successor sMRD are both
thin-air-free C/C++ relaxed-atomics models built on event structures: each
computes a *semantic dependency* relation and discards any candidate execution
with a cycle in `dp ∪ rf`. They agree on every genuine thin-air program. They
diverge on programs whose syntactic dependency is **semantically false** -- where
a sound compiler is entitled to delete the dependency. sMRD adds exactly the
machinery to detect these: reasoning about undefined behaviour, dynamic memory /
aliasing, and extrinsic choice such as over-alignment. So sMRD permits a strict
superset of MRD's behaviours -- MRD is strictly stronger.

## Direction -- sMRD allows, MRD forbids: the UB-masked false dependency

`LB+UB+data.litmus` is sMRD **Example 1.1a** (`LB+UB+data`). P0 reads `x` into
`r1`, then stores to `y` the value `1/!r1` -- which is *defined only when r1==0*
(otherwise division by zero, i.e. undefined behaviour). A standard compiler may
assume the program is well-defined, conclude `r1==0`, constant-fold the store to
a plain `y=1`, and thereby **break** the `read(x)->write(y)` dependency. P1 reads
`y` into `r2` and stores `r2` to `x`. The outcome `r1=1 /\ r2=1` then becomes
reachable.

* **sMRD allows it.** Its symbolic dependency calculus reasons about the UB
  guard, sees the dependency is semantically false, removes it, and with no `dp`
  edge there is no `dp ∪ rf` cycle to discard. sMRD is "the first [model] to
  correctly permit the optimisation demonstrated in Example 1.1a, without
  granting it undefined behaviour" -- matching what GCC and Clang actually do.
* **MRD forbids it.** MRD computes dependencies over **concrete** locations and
  values from program syntax and is UB-unaware, so it keeps the
  `read(x)->write(y)` data dependency, retains the `dp ∪ rf` cycle, and rules the
  outcome out.

The same separation appears in sMRD's over-alignment (Example 1.3,
`if (r1 % 16 == 0) y=1` folded to `y=1`) and dynamic-memory/aliasing (Example
1.4) examples; `LB+UB+data` is the one the paper headlines.

## Running

Neither model has a herd7 `cat` formalisation, and no sMRD/MoRDor checker is
bundled in this repository, so **both verdicts are cited, not machine-run.**
`LB+UB+data.lit` carries the MoRDor-family program with the embedded
`allow (r0 = 1 && r1 = 1)` (sMRD's verdict; MRD forbids the same outcome).

For completeness the C rendering runs in herd7 (with `1/!r1` written as the
herd-parseable, two-valued-equivalent `1/(1-r1)`):

```sh
herd7 -c11 strictly-weaker/MRD-vs-sMRD/LB+UB+data.litmus   # Observation LB+UB+data Never 0 3
```

As elsewhere, `Never` reflects herd7's inability to *construct* a
dependency-cycle execution (it ties reads to written values), **not** a verdict
of either model -- the MRD/sMRD difference is a property of their dependency
calculi, exhibited in the paper rather than by herd7.

**Reference:** Jay Richards, Daniel Wright, Simon Cooksey, Mark Batty, *Symbolic
MRD: Dynamic Memory, Undefined Behaviour, and Extrinsic Choice*, PACMPL 9
(OOPSLA1) Article 146, 2025, doi:10.1145/3721089 -- §1 Examples 1.1a / 1.3 / 1.4,
§6 Related Work. Base model: Marco Paviotti, Simon Cooksey, Anouk Paradis, Daniel
Wright, Scott Owens, Mark Batty, *Modular Relaxed Dependencies in Weak Memory
Concurrency*, ESOP 2020, doi:10.1007/978-3-030-44914-8_22.
