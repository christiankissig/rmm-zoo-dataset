# SRA → RA  (release-acquire is strictly weaker than strong release-acquire)

**Distinguishing behaviour:** a cycle in `hb ∪ mo` that no single `mo;hb` step closes.

RA and SRA differ in exactly one axiom (Lahav & Boker, TOPLAS 2022, Table 1):

| | RA | SRA |
|---|---|---|
| | `irreflexive mo;hb` (write-coherence) | `acyclic hb \| mo` (strong-write-coherence) |

RA asks only that modification order and happens-before agree *locally*, one step
at a time; SRA asks that they agree *globally*. Everything else — `irr-hb`,
read-coherence, RMW atomicity — is shared, so containment is immediate and only
strictness needs a witness.

`2+2W.litmus` is that witness, the separating program of Lahav et al., POPL 2016
(Ex. 3.6 in Lahav & Boker). Each thread writes both locations and then reads the
other thread's write to the location it wrote *second*:

```
P0: x :=rel 1 ; y :=rel 2 ; r0 :=acq y   // 1
P1: y :=rel 1 ; x :=rel 2 ; r1 :=acq x   // 1
```

Reading `r0 = r1 = 1` forces `W(y,2) --mo--> W(y,1)` and `W(x,2) --mo--> W(x,1)`,
closing the cycle

```
W(x,1) --po--> W(y,2) --mo--> W(y,1) --po--> W(x,2) --mo--> W(x,1)
```

SRA forbids the cycle. RA does not: neither `mo` step is followed by `hb` back to
its own source, so write-coherence is satisfied at every step.

```sh
herd7 -model ../../models/ra.cat  2+2W.litmus   # Sometimes 1 8   (RA)
herd7 -model ../../models/sra.cat 2+2W.litmus   # Never 0 5       (SRA)
```

## Controls

`ra.cat` and `sra.cat` are written for this dataset, not vendored, so the split
above is only meaningful if neither model is degenerate. Two controls, both run
by `run.sh`:

```sh
herd7 -model ../../models/ra.cat  MP+relacq.litmus   # Never 0 3       (must forbid)
herd7 -model ../../models/sra.cat MP+relacq.litmus   # Never 0 3       (must forbid)
herd7 -model ../../models/ra.cat  IRIW.litmus        # Sometimes 1 15  (must allow)
herd7 -model ../../models/sra.cat IRIW.litmus        # Sometimes 1 15  (must allow)
```

`MP+relacq` is the negative control: a model that constrained nothing would allow
it, and would then also "allow" 2+2W for no reason. `IRIW` is the positive
control, and it is checked against the literature rather than against intuition —
Lahav & Boker Ex. 3.5 marks the IRIW outcome allowed under WRA, RA **and** SRA.
Both models return identical counts on it, which is what says the strengthening
in `sra.cat` bites on 2+2W specifically rather than pruning executions at large.

**Reference:** Ori Lahav, Nick Giannarakis, Viktor Vafeiadis, *Taming
Release-Acquire Consistency*, POPL 2016, [doi:10.1145/2837614.2837643](https://doi.org/10.1145/2837614.2837643);
Ori Lahav, Udi Boker, *What's Decidable about Causally Consistent Shared
Memory?*, TOPLAS 44(2), 2022, [doi:10.1145/3505273](https://doi.org/10.1145/3505273).
