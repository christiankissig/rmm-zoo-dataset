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

A new model is one new file, `src/models/<id>.json`, carrying everything the
model asserts about itself:

- [ ] The entry: `id` (matching the file name), `name`, `abbrev`, `year`,
      `authors`, `description`, `references`, `tags`, `hardware`, `languages`
- [ ] Every id in `references` resolves to an entry in `src/references.json`
      (add it if new: `title`, `authors`, `venue`, `year`, `doi`)
- [ ] `properties` — the full property vector (check 1 rejects a model without
      one)
- [ ] `propertyProvenance` — `survey` if the row comes from the
      Moiseenko–Podkopaev–Koznov survey, `extrapolated` if author-assigned
- [ ] `propertyCitations` for any cell that needs a per-cell source
- [ ] `catSupport` — `status` (`specified` / `expressible` /
      `not-expressible`), `basis` (`cat-model` / `cited` / `extrapolated`),
      `ref`, and a `note` saying why (check 1 requires all four)
- [ ] `katSupport` if the model has, or could have, a kater `.kat` — optional
      (the map is partial by design), but required for either endpoint of a
      `provenance: kater` edge

And beside it:

- [ ] `src/models/_order.txt` — the id placed in the strength order (a model
      left out still ships, at the end of the list, with a warning)
- [ ] At least one `src/edges/<from>-vs-<to>.json` relating the model to an
      existing one

You do **not** need to place the model in the map's tier layout — that lives in
the site repo, and an unplaced model renders in a fallback tier until it is
positioned there.

Witnesses, if any new edge has `provenance: litmus`, `memalloy` or `kater`:

- [ ] `litmus/<strictly-weaker|incomparable>/<A>-vs-<B>/` directory exists, named
      in edge direction (`from` = stronger), with the test and a `README.md`
      (check 4) — see the *Add litmus tests* template
- [ ] for `kater`, also `litmus/kater/queries/<type>-<from>-vs-<to>.kat`, and the
      claim passes `make kater` — see `litmus/kater/README.md`

## Verification

```sh
make models             # recompile models.json from src/ (commit the result)
make check              # all 6 checks; runs the litmus suite if herd7 is on PATH
```

- [ ] `make check` passes
- [ ] Regenerated files are committed (`models.json`; `litmus.json` too, if
      `litmus/` changed)
