# MRD → C11  (C11 is strictly weaker)

**Distinguishing behaviour:** out-of-thin-air (OOTA) reads.

Modular Relaxed Dependencies (MRD) is proposed as a replacement for C11's relaxed
atomics that *forbids* thin-air reads, which the C11 standard's text fails to
rule out. The whole difference between the two models is exactly OOTA, so the
separating test must be an OOTA test.

`LB-oota.lit` (mordor syntax) is a value-invention load-buffering program: the
value `42` can only appear by being speculated into existence. The embedded
assertion is `forbid (r0 = 42 && r1 = 42)`.

```sh
cd ../../../mordor          # the MoRDor checker
./_build/default/cli/main.exe run --single \
    ../rmm-zoo.kissig.org/litmus/strictly-weaker/MRD-vs-C11/LB-oota.lit --error
# => Valid: true   (mordor's result MATCHES the 'forbid' assertion: MRD forbids the OOTA outcome)
```

The C11 side **cannot be exhibited in herd7**: herd's candidate-execution
generation ties every read to a value actually written, so it never produces an
OOTA execution — running

```sh
herd7 -c11 LB-oota.c11.litmus     # Observation LB-oota Never 0 4
```

reports `Never` not because C11 forbids it but because the tool cannot *construct*
it. The permission is a property of the C11 axioms as written (it is the
motivating example of the thin-air problem), which is the whole reason MRD exists.

> So: this edge is verified in the *forbidding* direction (MRD, in mordor) and
> documented (with citation) in the *allowing* direction (C11). No single tool
> shows both, because the only tool that exhibits OOTA is one that adopts a model
> that permits it.

**Reference:** Paviotti, Cooksey, Paradis, Wright, Owens, Batty, *Modular Relaxed
Dependencies in Weak Memory Concurrency*, ESOP 2020; Batty, Memarian, Nienhuis,
Pichon-Pharabod, Sewell, *The Problem of Programming Language Concurrency
Semantics*, ESOP 2015 (the thin-air problem). The `LB-oota.lit` shape is from the
MoRDor / SMRD `avoidoota` suite.
