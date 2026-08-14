# Releasing & archiving the RMM Zoo dataset

The dataset is versioned so a downstream consumer can cite a **pinned, immutable
snapshot** rather than the live site.

The **git tag `vX.Y.Z` is the single source of the version.** Nothing in the
repository carries a literal version: `models.json` ships `"version": "@VERSION@"`
and `"date": "@DATE@"`, and the citation metadata lives in `CITATION.cff.in`.
`tools/render.py` resolves the version once (`tools/version.py`: the tag on HEAD,
dated by that commit) and stamps it into the published copies under `dist/data/`.
There is nothing to keep in sync, so nothing can drift.

`make check` enforces that: it fails if `models.json` has a hand-written version
instead of the placeholders.

```sh
make version    # what a build would stamp in, and where it came from
```

Off a tag — or on a dirty tree — the resolver yields a **dev** version
(`1.2.0-dev.3+gabc1234`). `make build` will happily stamp one; `make deploy`
refuses to publish it (`ALLOW_DEV=1` overrides). `VERSION=` / `DATE=` override
the resolver entirely, for CI or a build outside a git checkout.

## Cutting a release

1. **Land the data changes** and make sure the tree is clean — a dirty tree is a
   dev build by construction.
2. **Write the entry.** Move `[Unreleased]` in [`CHANGELOG.md`](CHANGELOG.md) to
   the new version + date, and update the compare links at the bottom. The tag
   should contain its own changelog entry.
3. **Verify.** `make check && make build`.
4. **Tag** the release commit (MAJOR for breaking schema changes, MINOR for added
   models/edges/fields, PATCH for corrections):
   ```sh
   git tag -a v1.3.0 -m "RMM Zoo dataset v1.3.0"
   git push origin v1.3.0
   ```
5. **Deploy** from the tagged commit: `make deploy`. This stamps `v1.3.0` into
   `models.json` and `CITATION.cff` and publishes both.

The published citation file is served beside the data it describes:

- <https://rmm-zoo.kissig.org/data/CITATION.cff>

so a reader who fetches the dataset always gets citation metadata naming that
exact version. It is deliberately *not* committed — a checked-in copy could name
a version other than the deployed one.

The dataset is cited by **version + tag + commit**, an immutable, reproducible
reference.
