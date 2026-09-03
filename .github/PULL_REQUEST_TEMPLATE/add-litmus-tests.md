---
name: Add litmus tests
about: Add or update a witness under litmus/
---

## The pair

- **Directory:** `litmus/<strictly-weaker|incomparable>/<A>-vs-<B>/`
- **Edge it witnesses:** `A` … `B` …

The directory name follows the edge's own file name,
`src/edges/<from>-vs-<to>.json`: `from` (stronger) first, `to` (weaker) second. Check 6 rejects a directory whose name, type or direction
disagrees with the edge.

## The distinguishing behaviour

Which shape (MP, SB, LB, IRIW, WRC, …), which relaxation it probes, and why that
outcome separates these two models:

…

## Verdicts

| Model | Command | Expected |
|---|---|---|
| A (stronger) | `herd7 -model … A.litmus` | `Never` |
| B (weaker) | `herd7 -model … B.litmus` | `Sometimes` |

A pair exercised on both sides must show a genuine `Never` + `Sometimes` split —
two identical verdicts witness nothing, and check 5 rejects them.

## Checklist

- [ ] `.litmus` file(s) in the pair directory
- [ ] `README.md` in the directory: the distinguishing behaviour, the exact
      `herd7` commands, the observed output, and the citation for the claim
- [ ] `litmus/run.sh` — a `check` line per side, with the expected verdict
- [ ] If it needs a `cat` model the repo doesn't have: added under
      `litmus/models/` with a comment on what it encodes, or vendored with
      `PROVENANCE.md` + upstream licence
- [ ] `make litmus` run and `litmus.json` committed (the page fetches it)
- [ ] The edge's `evidence` in `src/edges/<A>-vs-<B>.json` upgraded if this
      makes it `machine_run` (then `make models`)

**If herd7 cannot exhibit it,** say so instead of forcing a verdict. herd7 ties
read values to actual stores, so it cannot produce out-of-thin-air executions;
models it does not ship (IMM, Promising, the survey research models) are cited
rather than run. Those pairs still ship the test plus a documented verdict, and
`run.sh` lists them under "Not run here". `litmus/README.md` has the full set of
caveats — extend it if this PR adds a new kind.

- [ ] Machine-run / documented-and-cited, and `litmus/README.md` says which

## Verification

```sh
bash litmus/run.sh      # per-test PASS/FAIL against the expected verdicts
make check              # check 6 re-runs the suite and requires 0 failures
```

- [ ] `bash litmus/run.sh` reports 0 failures
- [ ] Pass count in `litmus/README.md` updated if the suite grew
- [ ] `make check` passes

CI runs both on every push and PR (`.github/workflows/litmus.yml`), pinned to
herdtools7 7.58 — the version these verdicts are recorded against.
