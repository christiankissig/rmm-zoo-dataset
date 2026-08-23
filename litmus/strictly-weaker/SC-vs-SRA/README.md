# SC → SRA  (strong release-acquire is strictly weaker than sequential consistency)

**Distinguishing behaviour:** two readers observing independent writes in opposite orders.

SRA is the strongest member of the release-acquire family — it strengthens RA until
it exactly matches what POWER provides for compiled RA programs, and cannot be
strengthened further without an implementation cost. It is still strictly weaker
than SC.

`IRIW.litmus` is the separating program, and the expectation is checked against the
literature rather than intuition: Lahav & Boker Ex. 3.5 marks the annotated IRIW
outcome allowed under WRA, RA **and** SRA. SRA's extra axiom over RA is
strong-write-coherence, `acyclic(hb | mo)`, and this execution closes no such cycle,
so the strengthening leaves it alone.

```sh
herd7 -model ../../models/abstract-sc.cat IRIW.litmus   # Never 0 15      (SC)
herd7 -model ../../models/sra.cat         IRIW.litmus   # Sometimes 1 15  (SRA)
```

Both models admit **15** executions and differ on exactly one — SC prunes the
witness and nothing else, which is the shape a correct separation should have.

## Control

```sh
herd7 -model ../../models/abstract-sc.cat MP+relacq-ok.litmus   # Sometimes 1 2
herd7 -model ../../models/sra.cat         MP+relacq-ok.litmus   # Sometimes 1 2
```

`MP+relacq-ok` asks for the message-passing outcome in which the reader *does* see
the data. Both models must allow it. An SC model that forbade everything would be
indistinguishable from a correct one on the IRIW split above; this rules that out.
`abstract-sc.cat` is not authored for this pair — it already backs `SC-vs-TSO`,
`SC-vs-C11` and `SC-vs-BMM` in `run.sh` — but `sra.cat` is, so the pair is bracketed
anyway. The complementary controls for `sra.cat` (it must forbid `MP+relacq`, and
must allow `IRIW`) live in `../SRA-vs-RA/`.

**Reference:** Ori Lahav, Nick Giannarakis, Viktor Vafeiadis, *Taming Release-Acquire
Consistency*, POPL 2016, [doi:10.1145/2837614.2837643](https://doi.org/10.1145/2837614.2837643);
Ori Lahav, Udi Boker, TOPLAS 44(2), 2022, [doi:10.1145/3505273](https://doi.org/10.1145/3505273), Ex. 3.5.
