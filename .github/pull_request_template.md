## What

…

## Why

…

## Verification

```sh
make check    # 8 consistency checks; runs the litmus suite if herd7 is on PATH
```

- [ ] `make check` passes
- [ ] Regenerated files are committed (`make models` after a `src/` edit,
      `make litmus` after a `litmus/` edit)

---

<details>
<summary>There are task-specific templates for the common kinds of change</summary>

GitHub applies this default template automatically; the specific ones are opt-in.
Append `&template=<file>` to the PR-creation URL, or use
`gh pr create --template <file>`:

| Change | Template |
|---|---|
| Add a memory model | `add-model.md` |
| Correct a memory model | `correct-model.md` |
| Correct a relation between models | `correct-relation.md` |
| Add metadata properties | `add-properties.md` |
| Add litmus tests | `add-litmus-tests.md` |

They live in [`.github/PULL_REQUEST_TEMPLATE/`](PULL_REQUEST_TEMPLATE/) and each
one lists the data files, the invariants `make check` enforces, and the
regeneration steps for that kind of change.

</details>
