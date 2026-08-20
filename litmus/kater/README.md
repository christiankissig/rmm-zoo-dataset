# Verifying edges with kater

[kater](https://plv.mpi-sws.org/kater/paper.pdf) (Kokologiannakis, Lahav &
Vafeiadis, *Kater: Automating Weak Memory Model Metatheory and Consistency
Checking*, POPL 2023) answers the question the zoo's ordering is built on —
**"is model M weaker than model N?"** — by reducing it to **language inclusion
between regular languages**, which is decidable.

That is what herd7 and memalloy cannot do. A litmus test witnesses one
direction and can never establish containment; memalloy searches only up to an
event bound, and the kater paper says so of every prior tool (§8: *"all other
approaches are not sound … can thus provide no formal guarantees about whether
the property holds"*). A kater pass is **unbounded**: a proof, not a
no-counterexample-yet.

Edges whose containment comes from kater carry `"provenance": "kater"` in
`models.json`, and one query file here per edge, named for it.

## The division of labour

kater settles **containment**. It cannot settle **strictness**, and its
refutations are not proofs either:

| | proves | does not prove |
|---|---|---|
| kater **holds** | every N-consistent execution is M-consistent — unbounded | that the inclusion is strict |
| kater **refutes** | nothing on its own: the counterexample is a path over the NFA alphabet, and the inclusion checks are sound but *incomplete* (paper §4.3, §4.5), so the path need not be realisable | — |

So a `strictly_weaker` edge is only fully mechanised by **both** tools: kater
proves the containment half, and the herd7 witness in
`litmus/strictly-weaker/<A>-vs-<B>/` proves the strict half. `make check`
enforces that pairing — a `kater`-provenance ordering edge still owes its
witness directory.

A refutation is a *lead*: turn the counterexample path into a litmus test and
run it under herd7. That is the intended way to grow `litmus/strictly-weaker/`.

## Running the suite

```sh
docker pull genmc/kater      # ~700MB
./run.sh                     # one PASS/FAIL line per checked claim
./run.sh -v                  # also echo each invocation and kater's output
```

`run.sh` derives the LKMM operand from the image before it starts (see below)
and cleans it up afterwards. `make check` runs the suite too, but only if the
image is already pulled — it says so when it skips. CI pulls the image and runs it on every push and pull request.

`run.sh` pins the image **by digest**, the way `litmus/run.sh` pins herd7 to
7.58: these verdicts are evidence recorded in `models.json`, so the tool that
produced them is pinned exactly. `KATER_IMAGE=` overrides it, `DOCKER=podman`
swaps the runtime.

A check fails on a refutation (exit 6), on a kater error (exit 5), **and** on
`[Warning] Ignoring unsupported assumption` — kater drops a premise it cannot
use, prints that line, and still exits 0, so an unguarded "proof" could rest on
something the tool silently ignored.

## Writing a query

The models are kater's own `kat/*.kat`, taken from inside the image rather than
vendored here: they are GPL-3.0 to this dataset's BSD-3, and the image is the
version of record anyway. `run.sh` mounts this directory at `/root/kater/zoo`,
so a query reaches them at `../../kat/`. kater resolves an include against the
directory of the file it was handed, which is also why a query must be invoked
by a path with a directory component.

Name the file after the edge it backs — `<type>-<from>-vs-<to>.kat`, with the
edge type in kebab case — and `make check` will find it. Then state the claim
as an inclusion between the two models' constraint relations:

| Zoo edge | Query shape | Reading |
|---|---|---|
| `strictly_weaker` A → B | `assert B::<axiom relation> <= A::<axiom relation>+` | B's constraints follow from A's, so every A-consistent execution is B-consistent — B is weaker |
| `equivalent` A ↔ B | `assert A::<rel> = B::<rel>` | the two renderings define the same relation |
| `compilation` M → H | `assert M::psc <= H::<ordering>*`, plus `assume`s encoding the mapping | no target execution breaks the source semantics |

```kat
// Zoo edge: SC -> TSO (strictly_weaker) — containment half.
include "../../kat/sc.kat"
include "../../kat/tso.kat"

assert tso::tso <= sc::sc+
```

Two constraints on what can be checked at all, both enforced by `make check`:

- both endpoints need a `.kat` — recorded in `models.json`'s `katSupport`, which
  is the cat-specifiability axis narrowed to kater's fragment (conjunctions of
  irreflexivity/emptiness constraints over regular expressions; no `po ∩ sameloc`
  except through an incomplete rewriting procedure);
- the query proves something about **that `.kat` rendering**, not about the model
  in the abstract — so the edge's note names the file, exactly as `catSupport`
  notes name a concrete `.cat`.

## LKMM: the operand kater does not ship

`kat/lkmm2.kat` is written over kater's **internal** (`-imm`) relations, and
kater rejects those outright:

```
$ kater kat/lkmm2.kat
kat/lkmm2.kat:3.14-19: forbidden use of internal relation (mo-imm)
```

That is with the file handed to kater **directly**, and it fails the same way
under `-e`. So the shipped model does not load in any mode: LKMM is not a
comparison operand, and not a checking target either.

Every relation it redefines from an `-imm` counterpart — `po`, `po-loc`, `mo`,
`fr`, `rmw`, `ctrl`, `addr`, `data` — is already in kater's builtin theory, so
the restatement is mechanical. [`derive-lkmm.sh`](derive-lkmm.sh) performs it,
and [`run.sh`](run.sh) generates the result into a scratch directory mounted at
`/root/kater/derived` for the duration of the run. Queries reach it as
`../../derived/lkmm.kat`.

It is generated rather than committed for the same reason the `kat/*.kat` models
are not vendored: the derived file is a derivative of a GPL-3.0 one, and this
dataset is BSD-3. The script documents the rewrite line by line, and refuses to
emit a file in which any `-imm` survived.

With that in place `SC → LKMM` is proved and lives in `queries/`. The remaining
five LKMM edges are not — see the table below.

## Controls: a passing query is not automatically a proof

`controls/` holds queries that are only doing their job while they **fail**, and
`run.sh` asserts the refutation. They exist because a compilation query has the
shape `source::psc <= target::<ordering>*`, which holds trivially if the target's
ordering relation has grown coarse enough to contain everything — and one of
kater's own models has. `kat/power-weak.kat` defines `ar` with the term
`eco*;po?;eco*`; `eco*` contains the identity, so `ar` contains `po`, and

```
assert po     <= power-weak::ar+     // HOLDS
assert sc::sc <= power-weak::ar+     // HOLDS
```

Any query against that model passes for free. The controls check the targets the
suite *does* treat as proofs — `po <= tso::tso+` and `po <= arm8::ob+` are both
refuted, as they must be. If one ever starts holding, every compilation query
against that target has silently become vacuous, and the suite says so.

SC is exempt by construction: it is the top of the order, so `po <= sc::sc+`
holding is the point, not a defect.

## What is parked, and why

`open/` holds queries that do not pass and are not claims — each is a known
obstacle, kept runnable so the obstacle is reproducible:

| Query | Status |
|---|---|
| `strictly-weaker-TSO-vs-ARMv8.kat` | Refuted on `[DEP] data` — a **cross-ISA** comparison with no mapping: ARM's dependency and `ISB`/`DMB.ST` vocabulary has no TSO counterpart. Needs `assume`s encoding the mapping, the way the compilation queries do. The zoo edge stays `provenance: litmus`. Same obstacle as memalloy in #2. |
| `compilation-IMM-vs-POWER.kat` | Two obstacles, not one. The original refutation was a **shape** error: the assert was against a single `ar` step where the sibling TSO/ARMv8 queries take the closure. Fixing that makes it pass — **vacuously**, because `power-weak`'s `ar` contains `po` (above). The two renderings that are not degenerate, `power-fm` and `power-fm-orig`, refute it on a fence-vocabulary gap: IMM's `psc` relates two SC fences directly (`FSC ; po ; FSC`), Power's `sync` is stated between accesses. Settling it needs Power's fence ordering restated — the manual rewriting of §3.7 — not a closure. |
| `compilation-LKMM-vs-x86-TSO.kat` | Runnable now, not settled. LKMM's derived relations leave their endpoints untyped (`acq-po` is `[ACQ];po`, where IMM writes `[R];(deps\|rfi)+;[W]`), so TSO's `[R];po` does not cover it and the query is refuted on `[Marked&ACQ] po [Marked]`. Supplying the typing as premises does not discharge it: kater's handling of generic `a <= b` assumptions is heuristic, and it reports `Ignoring unsupported assumption` for the natural forms. The fix belongs in the LKMM rendering, not the query. `LKMM → ARMv8` is refuted identically; `LKMM → POWER` runs into the vacuity above; `LKMM → RVWMO` has no kater model at all. |
| `incomparable-C11-vs-LKMM.kat` | Not an obstacle so much as a limit: kater cannot establish incomparability at all, since that needs a refutation in each direction and its refutations prove nothing. Both directions do refute, which corroborates the recorded verdict without evidencing it. The edge stays `provenance: literature`. |

## Reference

Michalis Kokologiannakis, Ori Lahav, Viktor Vafeiadis. *Kater: Automating Weak
Memory Model Metatheory and Consistency Checking.* Proc. ACM Program. Lang. 7
(POPL), Article 19, 2023. [doi:10.1145/3571212](https://doi.org/10.1145/3571212).
Source mirror: [MPI-SWS/kater](https://github.com/MPI-SWS/kater) (GPL-3.0); the
language manual ships in the image at `/root/kater/doc/manual.pdf`.
