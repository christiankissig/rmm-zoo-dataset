# Contributing to the Relaxed Memory Model Zoo

Thanks for considering a contribution. This repository *is* the zoo: `models.json`
is the source of truth, and everything beside it either checks that data or backs
it with evidence. The site at <https://rmm-zoo.kissig.org> renders what is
published from here. Contributions are welcome on the data and the witnesses.

The one rule everything else follows from: **every claim carries its evidence.**
An ordering edge says how it is known, a property cell says where its value came
from, and a claim no tool can check says so out loud rather than quietly looking
machine-verified.

## What belongs here

- **Models** — a memory model with a primary source, positioned relative to at
  least one model already in the zoo.
- **Relations** — a strictly-weaker, incomparable, equivalent or compilation
  edge, with a containment argument and (where one exists) a witness.
- **Corrections** — a wrong year, a misattributed model, a misclassified edge.
  These are especially welcome; the zoo has shipped and corrected several
  (`PSO-vs-POWER`, `Weakestmo-vs-C11`, `CSRA-vs-C11` were all reclassified after
  a sweep failed to find the witness their `incomparable` classification implied).
- **Witnesses** — litmus tests that machine-check an edge currently resting on a
  citation, and kater queries that machine-check the containment half a litmus
  test cannot reach.
- **Properties** — new columns in the property table, with provenance per cell.

## Quick start

```sh
git clone git@github.com:christiankissig/rmm-zoo-dataset.git
cd rmm-zoo-dataset
make check            # the gate your PR has to pass
```

Only Python 3 is needed — no bundler, no `node_modules`, no dependencies to
install.

To run the litmus suite you also need herd7:

```sh
opam install herdtools7.7.58     # the version CI pins and the verdicts assume
eval $(opam env)
bash litmus/run.sh               # per-test PASS/FAIL vs the expected verdicts
```

Without herd7 everything still works — `make check` skips the dynamic suite and
tells you it did.

To re-prove the containments recorded as `provenance: kater` you need docker and
kater's image:

```sh
docker pull genmc/kater          # ~700MB; run.sh pins it by digest
make kater                       # per-claim PASS/FAIL
```

Same deal: `make check` folds the suite in once the image is local, and says so
when it skips. [`litmus/kater/README.md`](litmus/kater/README.md) is the runbook —
read it before adding a query.

## Layout

```
models.json        the dataset: models, edges, references, properties
                   (its version/date are placeholders — see Releases below)
CITATION.cff.in    citation metadata template, rendered and published by the
                   build; the rendered CITATION.cff is not committed
litmus.json        the witness tree baked into one JSON (generated, committed)
litmus/            witnesses: one directory per edge, plus run.sh
litmus/kater/      machine-checked containments: one query per kater-provenance
                   edge, plus run.sh and the runbook
tools/             the consistency gate, the litmus generator, and the version
                   resolver + template renderer used by the build
```

**This repository holds only the data.** The site that renders it — the map, the
property table's presentation, the per-model pages — lives separately in
`rmm-zoo.kissig.org`. You do not need it to contribute here: `make check` is the
whole gate, and the site picks up your data once it is published.

One consequence worth knowing: the **tier layout** (which row a model is drawn
in) is a presentation choice and lives in the site repo. Adding a model here does
not require placing it — it renders in a fallback tier, and the site's own check
flags it for placement. That is a site-side task, not a blocker on your PR.

## The dataset

`models.json` holds more than a node list, and a change to one block usually
implies a change to another:

| Block | What it holds |
|---|---|
| `models` | id, name, abbrev, year, authors, description, references, tags, hardware, languages |
| `edges` | `from`, `to`, `type`, `provenance`, `evidence`, `note` |
| `references` | citation entries keyed by id: title, authors, venue, year, doi |
| `propertySchema` | the property table's groups and columns |
| `modelProperties` | one property vector per model |
| `modelPropertyProvenance` | per model: `survey` or `extrapolated` |
| `modelPropertyCitations` | per cell: `ref` + `note`, where one is owed |
| `catSupport` | per model: `status`, `basis`, `ref`, `note` |
| `katSupport` | the same axis for kater's narrower fragment — partial by design: absence means *not assessed* |

**Edge vocabularies.** `type` is `strictly_weaker` (`from` = stronger, `to` =
weaker), `incomparable`, `equivalent` or `compilation`. `provenance` is
`literature`, `litmus`, `completion`, `memalloy` or `kater`. `evidence` is
`machine_run`, `by_construction`, `cited` or `deduced` — and it must be honest:
`machine_run` means a tool in this repo actually produces the verdict.

**`kater` provenance** is the strongest mechanical one, and the narrowest: kater
decides *containment* by language inclusion, unbounded, where memalloy searches
only up to an event bound. It says nothing about strictness, so a
`strictly_weaker` edge marked `kater` still owes its separating witness — check 4
enforces both halves. Adding one means adding
`litmus/kater/queries/<type>-<from>-vs-<to>.kat`, and both endpoints must be
`specified` in `katSupport`.

This matters more than it looks. herd7 ties read values to actual stores, so it
**cannot** exhibit out-of-thin-air executions; models it does not ship (IMM,
Promising, and the survey research models) cannot be run at all. Those edges are
cited, and `litmus/README.md` documents each caveat. Do not paper over a gap by
labelling a cited edge `machine_run`.

## Invariants

`make check` is the gate — it runs before `make build` and `make deploy`, and in
CI on every push and PR. It enforces:

| # | Check |
|---|---|
| 1 | Every edge endpoint is a real node; every edge has a declared `provenance` and `evidence`; every node has a property vector and a complete `catSupport` entry with a resolvable citation; `katSupport` is well formed where populated |
| 2 | `strictly_weaker` is a DAG |
| 3 | No pair is both ordered and incomparable — including via the transitive closure, so a *deduced* order must not contradict a drawn `incomparable` edge |
| 4 | Every `litmus/{strictly-weaker,incomparable}/<A>-vs-<B>/` directory matches an edge of that type and direction, and every litmus-, memalloy- or kater-provenance ordering edge has one; every kater-provenance edge also has its query file, over kat-specified endpoints |
| 5 | A pair exercised on both sides in `run.sh` shows a real `Never` + `Sometimes` split |
| 6 | `litmus/run.sh` passes with zero failures (skipped if herd7 is absent) |
| 7 | `litmus/kater/run.sh` passes with zero failures (skipped if the kater image is not pulled) |

Check 3 is the one that surprises people: an edge you add may contradict an
`incomparable` edge drawn somewhere else entirely, through a chain of orderings
neither edge mentions.

## Generated files

One committed file is generated: `litmus.json`, baked from the `litmus/` tree by
`make litmus`. Edit the tests, re-run the target, commit the result.

After a `litmus/` edit: `make litmus`, then `make check`. After a `models.json`
edit: `make check` alone. Everything the *site* derives from this data — the
crawlable catalogue, the per-model pages, the counts quoted in its prose, the
social-preview image — regenerates in the site repo on its next build. You do not
run those, and they are not committed here.

## Making a change

1. Branch off `master`.
2. Make the change, including the data files the invariants tie to it.
3. Regenerate and run `make check` (and `bash litmus/run.sh` if you touched
   `litmus/`, `make kater` if you touched `litmus/kater/`).
4. Open a PR using the template for that kind of change. GitHub applies the
   default template automatically; pick a specific one by appending
   `&template=<file>` to the PR-creation URL or with `gh pr create --template <file>`:

   | Change | Template |
   |---|---|
   | Add a memory model | `add-model.md` |
   | Correct a memory model | `correct-model.md` |
   | Correct a relation between models | `correct-relation.md` |
   | Add metadata properties | `add-properties.md` |
   | Add litmus tests | `add-litmus-tests.md` |

   Each one lists the files that kind of change touches, the invariants that
   apply, and the regeneration steps.

CI (`.github/workflows/litmus.yml`) runs the litmus suite and `make check` on
every push to `master` and every PR, with herdtools7 pinned to 7.58.

## Citing a claim

Anything asserted about a model needs a source a reader can follow: a paper with
a DOI, an official specification, or a tool artifact. Add it to the `references`
block and refer to it by id. Where a value is author-assigned rather than taken
from a source — much of the property table is — say so via
`modelPropertyProvenance` / `propertyProvenance` and state the reasoning. An
argued extrapolation is fine; an unmarked one is not.

## Releases

The dataset is versioned and cited by version + tag + commit — the git tag is the
only place the version lives, and the build stamps it into the published
`models.json` and `CITATION.cff`. Do not hand-write a version into `models.json`;
`make check` rejects it. See [`RELEASING.md`](RELEASING.md).

## Questions

Open an issue. For a change you are unsure belongs in the zoo — a model of
uncertain scope, a relation you can argue but not witness — an issue first will
save you work.

For the **site** rather than the data — a rendering bug, a layout complaint, a
feature for the map — open an issue on `rmm-zoo.kissig.org` instead. The UI is
maintained separately and is not open to pull requests.
