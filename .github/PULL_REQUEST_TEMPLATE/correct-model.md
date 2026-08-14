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

- [ ] `models.json` entry updated (`description`, `year`, `authors`,
      `tags`, `hardware`, `languages`, `references` as applicable)
- [ ] Any new citation added to the `references` block and referenced by id
- [ ] If the *properties* changed: `modelProperties`, and
      `modelPropertyProvenance` / `modelPropertyCitations` updated to match —
      see the *Add metadata properties* template
- [ ] If `catSupport` changed: `status`, `basis`, `ref` and `note` all still
      agree with each other
- [ ] If the correction changes where the model sits relative to others, the
      edge changes are in a separate PR (or listed below) — see the
      *Correct a relation* template

**Changing the `id` is a rename, not an edit.** It has to be updated in the same
commit in: `models`, every `edges` entry, `modelProperties`,
`modelPropertyProvenance`, `modelPropertyCitations`, `catSupport`, and every
`litmus/**/<A>-vs-<B>/` directory name that mentions it. (The site's tier layout
also names ids; that side is handled in the site repo, not here.)

- [ ] Not a rename / rename fully propagated

## Verification

```sh
make check
```

- [ ] `make check` passes
- [ ] Regenerated files are committed
