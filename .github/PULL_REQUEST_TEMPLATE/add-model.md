---
name: Add a memory model
about: Add a new node to the zoo
---

## The model

- **Id** (used everywhere; short, stable): `…`
- **Name / abbreviation:** …
- **Year, authors:** …
- **Primary source** (paper + DOI): …

One paragraph on what the model is and what makes it distinct from its
neighbours in the zoo:

…

## Where it sits

Which existing models is it stronger or weaker than, and why? A node with no
edges floats unattached, so a new model needs at least one relation.

…

## Checklist

`models.json`:

- [ ] Entry in `models`: `id`, `name`, `abbrev`, `year`, `authors`,
      `description`, `references`, `tags`, `hardware`, `languages`
- [ ] Every id in `references` resolves to an entry in the `references` block
      (add it if new: `title`, `authors`, `venue`, `year`, `doi`)
- [ ] `modelProperties["<id>"]` — the full property vector (check 1 rejects a
      model without one)
- [ ] `modelPropertyProvenance["<id>"]` — `survey` if the row comes from the
      Moiseenko–Podkopaev–Koznov survey, `extrapolated` if author-assigned
- [ ] `modelPropertyCitations["<id>"]` for any cell that needs a per-cell source
- [ ] `catSupport["<id>"]` — `status` (`specified` / `expressible` /
      `not-expressible`), `basis` (`cat-model` / `cited` / `extrapolated`),
      `ref`, and a `note` saying why (check 1 requires all four)
- [ ] At least one edge in `edges` relating the model to an existing one

You do **not** need to place the model in the map's tier layout — that lives in
the site repo, and an unplaced model renders in a fallback tier until it is
positioned there.

Witnesses, if any new edge has `provenance: litmus` or `memalloy`:

- [ ] `litmus/<strictly-weaker|incomparable>/<A>-vs-<B>/` directory exists, named
      in edge direction (`from` = stronger), with the test and a `README.md`
      (check 6) — see the *Add litmus tests* template

## Verification

```sh
make check              # all 6 checks; runs the litmus suite if herd7 is on PATH
```

- [ ] `make check` passes
- [ ] Regenerated files are committed (`litmus.json`, if `litmus/` changed)
