# Relaxed Memory Model Zoo — dataset

The data behind <https://rmm-zoo.kissig.org>: hardware and programming-language
memory models, the ordering relations between them, the per-model property
table, and the litmus witnesses that back the ordering claims.

This repository is the **source of truth and the contribution surface**. The site
that renders it lives separately in `rmm-zoo.kissig.org` and consumes the
published artifacts — nothing here knows how the graph is drawn.

## Layout

```
models.json        the dataset: models, edges, references, property table,
                   per-cell provenance, cat- and kat-specifiability, version + date
                   (the build fills version/date in from the git tag)
CITATION.cff.in    citation metadata template; the build renders it to
                   CITATION.cff and publishes it with the data
litmus.json        the witness tree baked into one JSON (generated, committed)
litmus/            witnesses: one directory per edge, plus run.sh
litmus/kater/      the machine-checked containments: one query per kater edge,
                   plus run.sh and the runbook
tools/             the consistency gate, the litmus generator, the version
                   resolver (version.py) and the template renderer (render.py)
```

## The one rule

**Every claim carries its evidence.** An ordering edge records how it is known
(`provenance` + `evidence`), a property cell records where its value came from,
and a claim no tool can check says so out loud rather than quietly looking
machine-verified. `make check` enforces as much of this as is mechanisable.

## Checks

```sh
make check            # runs before build/deploy too
```

Checks: 
1. every edge endpoint is a real model with a property vector and a sourced cat-support entry
2. `strictly_weaker` is a DAG
3. every edge has a unique type
4. every edge type and direction matches the witness by folder name, and every `kater` edge has the query that proves it
5. every `strictly_weaker` or `incomparable` edge is supported by distinguishing behaviour(s)
6. if herd7 is on `PATH`, the litmus suite itself passes
7. if the kater image is pulled, the containment suite itself passes

Running the dynamic suite needs herd7:

```sh
opam install herdtools7.7.58     # the version CI pins and the verdicts assume
eval $(opam env)
bash litmus/run.sh               # per-test PASS/FAIL vs the expected verdicts
```

Without it `make check` skips that check and says so.

The containment half of the evidence — the ordering claims machine-checked with
[kater](https://plv.mpi-sws.org/kater/paper.pdf), which decides model inclusion
*unbounded*, where a litmus test only ever witnesses one direction — needs docker:

```sh
docker pull genmc/kater          # ~700MB, pinned by digest in the runner
make kater                       # per-claim PASS/FAIL
```

[`litmus/kater/README.md`](litmus/kater/README.md) is the runbook. Every push and
pull request runs both suites in GitHub Actions — see
[`.github/workflows/litmus.yml`](.github/workflows/litmus.yml).

## Build and publish

```sh
make version          # the version + date this build would stamp in
make build            # stamps the version, stages dist/data/{models.json,litmus.json,CITATION.cff}
make deploy           # sync to s3://kissig-org-rmm-zoo/data/ + invalidate CloudFront
```

The dataset is served from the site's origin under `/data/`:

- <https://rmm-zoo.kissig.org/data/models.json>
- <https://rmm-zoo.kissig.org/data/litmus.json>
- <https://rmm-zoo.kissig.org/data/CITATION.cff>

`make deploy` publishes the dataset to the website.

## What is *not* here

The tier layout (`tierMap` / `tierOrder` / `tierLabels`) is a presentation
choice and lives in the site repository. A model added here renders in a fallback
tier until the site places it — a site-side task, not a blocker on a data PR.

## Contributing

Models, relations, corrections, witnesses and property columns are all welcome.
[`CONTRIBUTING.md`](CONTRIBUTING.md) covers the dataset's structure, the
invariants `make check` enforces, and which files are generated; the PR templates
in [`.github/PULL_REQUEST_TEMPLATE/`](.github/PULL_REQUEST_TEMPLATE) walk through
each kind of change.

## Citing / versioning

The git tag `vX.Y.Z` is the **single source of the version**. The build stamps it,
with the release date, into both published files — `models.json` (`version` /
`date`) and `CITATION.cff` — so a release is cut by tagging. `make version` shows
what a build would stamp in.

The citation file is served from the website, beside the data it describes:

- <https://rmm-zoo.kissig.org/data/CITATION.cff>

Cite the pinned version + tag + commit. See [`RELEASING.md`](RELEASING.md) for
cutting a release.

## License

The dataset is released under the [3-Clause BSD License](LICENSE) —
`SPDX-License-Identifier: BSD-3-Clause`. Attribution belongs to the primary
literature as much as to this repository: every model, edge and property cell
carries its own citation, and reusing a claim means citing its source.
