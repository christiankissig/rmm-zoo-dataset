---
name: Correct a memory model
about: Fix a model's metadata, description, or classification
---

## What is wrong

Model id: `…`

What the zoo currently says:

…

What it should say:

…

## Source

The correction has to be traceable to something citable — a paper, an official
specification, or an erratum. Quote the passage that settles it.

> …

Reference: … (DOI: …)

## Checklist

- [ ] `src/models/<id>.json` updated (`description`, `year`, `authors`,
      `tags`, `hardware`, `languages`, `references` as applicable)
- [ ] Any new citation added to `src/references.json` and referenced by id
- [ ] If the *properties* changed: the same file's `properties`, and
      `propertyProvenance` / `propertyCitations` updated to match — see the
      *Add metadata properties* template
- [ ] If `catSupport` changed: `status`, `basis`, `ref` and `note` all still
      agree with each other
- [ ] If the correction changes where the model sits relative to others, the
      edge changes are in a separate PR (or listed below) — see the
      *Correct a relation* template

**Changing the `id` is a rename, not an edit.** In the same commit: rename
`src/models/<id>.json` and its `id` field, rename every
`src/edges/<A>-vs-<B>.json` that names it (and the `from`/`to` inside), update
`src/models/_order.txt`, and rename every `litmus/**/<A>-vs-<B>/` directory and
`litmus/kater/queries/*.kat` that mentions it. `make models` fails on each half
you miss. (The site's tier layout also names ids; that side is handled in the
site repo, not here.)

- [ ] Not a rename / rename fully propagated

## Verification

```sh
make models
make check
```

- [ ] `make check` passes
- [ ] Regenerated files are committed
