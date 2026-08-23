# RA → WRA  (weak release-acquire is strictly weaker than release-acquire)

**Distinguishing behaviour:** loss of SC-per-location — on a *single* location.

WRA keeps only what causal consistency needs. Modification order plays no role in
it at all (Lahav & Boker, TOPLAS 2022, Table 1):

| | RA | WRA |
|---|---|---|
| coherence | `irreflexive mo;hb` + `irreflexive mo;hb;rf⁻¹` | `irreflexive hb\|loc;[W];hb;rf⁻¹` |
| atomicity | RMW reads its immediate mo-predecessor | no two RMWs read the same write |

RA decides which of two writes to a location is the later by `mo`, which is total
per location. WRA decides it by `hb|loc`, which is only partial — so two writes
that no happens-before relates are, to WRA, simply unordered. Containment holds
because write-coherence gives `[W];hb|loc;[W] ⊆ mo`, so read-coherence implies
weak-read-coherence (Prop. 3.2); only strictness needs witnesses.

All three witnesses are Lahav & Boker's Ex. 3.7, and all three are **single-location**
programs — which is the point: WRA does not provide sequential-consistency-per-location.

```sh
herd7 -model ../../models/ra.cat  WW.litmus            # Never 0 4       (RA)
herd7 -model ../../models/wra.cat WW.litmus            # Sometimes 2 6   (WRA)
herd7 -model ../../models/ra.cat  Oscillating.litmus   # Never 0 20
herd7 -model ../../models/wra.cat Oscillating.litmus   # Sometimes 2 28
herd7 -model ../../models/ra.cat  SF.litmus            # Never 0 4
herd7 -model ../../models/wra.cat SF.litmus            # Sometimes 2 6
```

- **WW** — two threads each write `x`, then each reads the *other's* value.
- **Oscillating** — a reader sees `x` go 1, 2, 1 while two writers write once each.
- **SF** — the store-forwarding shape. WRA allowing it is exactly what makes the
  rewrite of a repeated read to a constant sound under WRA; the paper notes the
  same rewrite is *unsound* for RA and SRA, since it would produce this outcome
  even under SC.

`sra.cat` agrees with `ra.cat` on all three (`Never`), as Ex. 3.7 records — the
SRA/RA split is 2+2W, in `../SRA-vs-RA/`, and is orthogonal to this one.

## A note on initialisation

`wra.cat` needs `hb` to order the initialisation events before every thread event,
and says so. Lahav & Boker put init po-before all events of every thread, so this
is faithful rather than a fudge — but it is load-bearing *only* for WRA. RA and SRA
reach identical verdicts without it, because `mo` already relates `IW` to every
write, so their coherence axioms fire anyway. WRA has no `mo`. Without the init
ordering, `weak-read-coherence` can never fire against an initial value, and WRA
wrongly **allows** message passing (`MP+relacq` goes `Never 0 3` → `Sometimes 1 3`)
— which would make WRA not causally consistent at all, contradicting the model's
whole purpose. That misbehaviour is what the `MP+relacq` control in `../SRA-vs-RA/`
catches, and it is why all three models state the init ordering explicitly rather
than leaving RA and SRA to get the right answer by accident.

**Reference:** Ori Lahav, Udi Boker, *What's Decidable about Causally Consistent
Shared Memory?*, TOPLAS 44(2), 2022, [doi:10.1145/3505273](https://doi.org/10.1145/3505273),
Table 1 and Ex. 3.7.
