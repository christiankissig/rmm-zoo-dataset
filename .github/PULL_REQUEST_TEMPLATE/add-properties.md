---
name: Add metadata properties
about: Add or change a column in the property table
---

## The property

- **Field key** (used in `modelProperties`): `…`
- **Label** (shown in the table header): …
- **Group / sub-heading:** … *(e.g. Reordering / sound, Elimination / sound)*

What the property means, and what a `true` cell asserts about a model:

…

## Where the values come from

Say this plainly — the zoo distinguishes survey-sourced rows from
author-assigned ones, and the property panel quotes the split.

- [ ] Tabulated by the Moiseenko–Podkopaev–Koznov survey
- [ ] From a primary paper (which, and which result): …
- [ ] Author-assigned by argument from the model definitions

If cells are author-assigned, the reasoning has to be stated, not implied:

…

## Checklist

`models.json`:

- [ ] `propertySchema` — field added to the right `group` / `sub`, as
      `["<key>", "<Label>"]`
- [ ] `modelProperties` — **every** model carries the new key. A missing cell is
      not the same as `false`; if a model's value is genuinely unknown, say how
      the table renders that rather than defaulting it silently
- [ ] `propertyProvenance["<key>"]` — prose on where the column comes from, and
      for an author-assigned column, on what authority
- [ ] `modelPropertyCitations["<model>"]["<key>"]` — `ref` + `note` for each cell
      that rests on a specific result
- [ ] Any new citation added to the `references` block

A new column needs no site change: the map and the per-model pages both read
`propertySchema` from this file, so a column declared here renders itself. Only a
column needing presentation beyond a true/false cell does — say so in the PR and
it will be handled site-side.

## Verification

```sh
make check
```

- [ ] `make check` passes
- [ ] Regenerated files are committed
